"""PageRank-based social recipe recommendation.

This module models the MyFridge user base as a directed social graph and uses
the PageRank algorithm to estimate each profile's *influence* (a combination of
how well-connected they are in the follow network and how actively they engage
with recipes).

Recipes are then recommended to a user by aggregating the weighted engagement
signals (like / share / save / order / cook ...) of every other user, where
each user's contribution is scaled by their PageRank influence. The result is
that recipes endorsed by highly-influential, well-connected profiles bubble to
the top -- a social proof signal that complements the existing flavor-profile
recommender.

The implementation is intentionally dependency-free (pure-Python power
iteration) so it adds no new packages to the backend.
"""
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import (
    User, UserFollow, UserRecipeInteraction, Recipe,
)


# ------------------------------------------------------------------
# Engagement signal weights
# ------------------------------------------------------------------
# How strongly each interaction type counts as an endorsement of a recipe.
# "Follow-through cooking" and placing an order are the strongest signals of
# genuine intent; a passive view counts for very little.
INTERACTION_WEIGHTS: Dict[str, float] = {
    "view": 0.5,
    "like": 2.0,
    "save": 2.5,
    "shop": 3.0,
    "share": 3.0,
    "order": 3.5,
    "cook": 4.0,
    "cooked": 4.0,
}

# Negative / neutral signals never contribute to a recommendation.
IGNORED_INTERACTIONS = {"unlike"}

# PageRank hyper-parameters.
DAMPING = 0.85
MAX_ITER = 100
TOLERANCE = 1.0e-8

# Extra multiplier applied to endorsements coming from profiles that the
# requesting user already follows (direct social trust).
FOLLOWED_BOOST = 1.5


def _interaction_weight(interaction_type: str) -> float:
    return INTERACTION_WEIGHTS.get((interaction_type or "").lower(), 0.0)


def _user_activity_weights(db: Session) -> Dict[int, float]:
    """Total weighted engagement per user (used as the PageRank teleport bias).

    Active profiles -- those who like / save / share / order / cook a lot --
    receive a larger share of the random-teleport mass, so engagement feeds
    directly into the influence score alongside the follow-graph structure.
    """
    rows = (
        db.query(
            UserRecipeInteraction.user_id,
            UserRecipeInteraction.interaction_type,
            func.count(UserRecipeInteraction.id),
        )
        .group_by(UserRecipeInteraction.user_id, UserRecipeInteraction.interaction_type)
        .all()
    )
    activity: Dict[int, float] = defaultdict(float)
    for user_id, interaction_type, count in rows:
        activity[user_id] += _interaction_weight(interaction_type) * count
    return activity


def _build_follow_graph(db: Session) -> Tuple[List[int], Dict[int, List[int]]]:
    """Return (node_ids, out_links) for the user follow graph.

    ``out_links[u]`` is the list of users that ``u`` follows. In PageRank terms
    a node distributes its rank along its out-links, so influence flows from a
    follower to the profiles they follow.
    """
    node_ids = [u.id for u in db.query(User.id).all()]
    out_links: Dict[int, List[int]] = {uid: [] for uid in node_ids}

    node_set = set(node_ids)
    for follow in db.query(UserFollow).all():
        if follow.follower_id in node_set and follow.followee_id in node_set:
            out_links[follow.follower_id].append(follow.followee_id)
    return node_ids, out_links


def compute_influence(
    db: Session,
    damping: float = DAMPING,
    max_iter: int = MAX_ITER,
    tol: float = TOLERANCE,
) -> Dict[int, float]:
    """Compute a normalized PageRank influence score for every user.

    Uses personalized PageRank where the teleport distribution is biased toward
    profiles with high engagement activity. Dangling nodes (users who follow
    nobody) redistribute their mass according to the same teleport vector.

    Returns a mapping ``{user_id: influence_score}`` whose values sum to ~1.0.
    """
    node_ids, out_links = _build_follow_graph(db)
    n = len(node_ids)
    if n == 0:
        return {}

    # Personalization / teleport vector: base uniform mass + activity bias.
    activity = _user_activity_weights(db)
    total_activity = sum(activity.values())
    teleport: Dict[int, float] = {}
    if total_activity > 0:
        # Blend uniform prior with activity so brand-new users still get mass.
        for uid in node_ids:
            uniform = 1.0 / n
            active = activity.get(uid, 0.0) / total_activity
            teleport[uid] = 0.5 * uniform + 0.5 * active
    else:
        for uid in node_ids:
            teleport[uid] = 1.0 / n

    out_degree = {uid: len(links) for uid, links in out_links.items()}
    dangling = [uid for uid in node_ids if out_degree[uid] == 0]

    # Initialize ranks to the teleport distribution.
    rank: Dict[int, float] = dict(teleport)

    for _ in range(max_iter):
        dangling_mass = sum(rank[uid] for uid in dangling)
        new_rank: Dict[int, float] = {
            uid: (1.0 - damping) * teleport[uid] + damping * dangling_mass * teleport[uid]
            for uid in node_ids
        }
        for uid in node_ids:
            deg = out_degree[uid]
            if deg == 0:
                continue
            share = damping * rank[uid] / deg
            for target in out_links[uid]:
                new_rank[target] += share

        # Convergence check (L1 norm of the delta).
        delta = sum(abs(new_rank[uid] - rank[uid]) for uid in node_ids)
        rank = new_rank
        if delta < tol:
            break

    # Normalize so scores form a probability distribution.
    total = sum(rank.values()) or 1.0
    return {uid: score / total for uid, score in rank.items()}


def get_user_influence(db: Session, user_id: int) -> Optional[Dict]:
    """Return influence score, leaderboard rank and follow counts for a user."""
    influence = compute_influence(db)
    if user_id not in influence:
        return None

    # Rank by descending influence (1 = most influential).
    ordered = sorted(influence.items(), key=lambda kv: kv[1], reverse=True)
    rank = next((i + 1 for i, (uid, _) in enumerate(ordered) if uid == user_id), len(ordered))

    followers = (
        db.query(func.count(UserFollow.id))
        .filter(UserFollow.followee_id == user_id)
        .scalar()
    )
    following = (
        db.query(func.count(UserFollow.id))
        .filter(UserFollow.follower_id == user_id)
        .scalar()
    )

    return {
        "user_id": user_id,
        "influence_score": round(influence[user_id], 6),
        "rank": rank,
        "total_users": len(influence),
        "followers": int(followers or 0),
        "following": int(following or 0),
    }


def get_network_recommendations(
    db: Session,
    user_id: int,
    limit: int = 10,
    exclude_ids: Optional[List[str]] = None,
    followed_only: bool = False,
) -> List[Dict]:
    """Recommend recipes using influence-weighted social engagement.

    For every recipe, sum ``influence(u) * interaction_weight(type)`` over all
    users ``u`` (other than the requester) who engaged with it. Endorsements
    from profiles the requester follows receive an extra ``FOLLOWED_BOOST``.

    Recipes the requester has already interacted with are excluded, as are any
    ``exclude_ids``. Results are sorted by social score (descending).
    """
    influence = compute_influence(db)
    exclude_set = set(exclude_ids or [])

    # Users that the requester follows (for the direct-trust boost / filter).
    followed_ids = {
        f.followee_id
        for f in db.query(UserFollow).filter(UserFollow.follower_id == user_id).all()
    }

    # Recipes the requester already engaged with -> don't recommend again.
    seen_recipe_ids = {
        row[0]
        for row in db.query(UserRecipeInteraction.recipe_id)
        .filter(UserRecipeInteraction.user_id == user_id)
        .all()
    }

    # Aggregate weighted engagement per recipe.
    scores: Dict[int, float] = defaultdict(float)
    endorsers: Dict[int, set] = defaultdict(set)
    contributions: Dict[int, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
    signals: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    interactions = db.query(UserRecipeInteraction).all()
    for inter in interactions:
        if inter.user_id == user_id:
            continue
        if inter.recipe_id in seen_recipe_ids:
            continue
        if followed_only and inter.user_id not in followed_ids:
            continue

        weight = _interaction_weight(inter.interaction_type)
        if weight <= 0:
            continue

        user_influence = influence.get(inter.user_id, 0.0)
        if user_influence <= 0:
            continue

        boost = FOLLOWED_BOOST if inter.user_id in followed_ids else 1.0
        contribution = user_influence * weight * boost

        scores[inter.recipe_id] += contribution
        endorsers[inter.recipe_id].add(inter.user_id)
        contributions[inter.recipe_id][inter.user_id] += contribution
        signals[inter.recipe_id][inter.interaction_type.lower()] += 1

    if not scores:
        return []

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    # Pre-load the recipes and influencer users we actually need.
    recipe_ids = [rid for rid, _ in ranked]
    recipe_map = {
        r.id: r for r in db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
    }
    influencer_ids = {uid for rid, _ in ranked for uid in contributions[rid]}
    user_map = {
        u.id: u for u in db.query(User).filter(User.id.in_(influencer_ids)).all()
    }

    results: List[Dict] = []
    for recipe_id, score in ranked:
        recipe = recipe_map.get(recipe_id)
        if recipe is None or recipe.external_id in exclude_set:
            continue

        # Top 3 influencers driving this recommendation.
        top_contributors = sorted(
            contributions[recipe_id].items(), key=lambda kv: kv[1], reverse=True
        )[:3]
        influencers = []
        for uid, _ in top_contributors:
            u = user_map.get(uid)
            if u is None:
                continue
            influencers.append({
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "influence_score": round(influence.get(uid, 0.0), 6),
            })

        results.append({
            "recipe": recipe.to_dict(),
            "social_score": round(score, 6),
            "endorsements": len(endorsers[recipe_id]),
            "influencers": influencers,
            "signals": dict(signals[recipe_id]),
        })

        if len(results) >= limit:
            break

    return results
