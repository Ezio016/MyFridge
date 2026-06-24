# 📊 Recipe Matrix - Linear Algebra Module

This module converts recipe data into matrix form for teaching linear algebra concepts.

## 🎯 Learning Objectives

Students will learn:
1. **Matrix Construction** - How to represent real-world data as matrices
2. **Matrix-Vector Multiplication** - Finding recipes that match inventory
3. **Cosine Similarity** - Measuring recipe similarity
4. **SVD Decomposition** - Dimensionality reduction and data compression
5. **Recommendation Systems** - Using matrices for suggestions

---

## 📁 Files

| File | Description |
|------|-------------|
| `template_matrix.py` | **30 ingredients** - Basic matrix for handouts |
| `extended_matrix.py` | **145 ingredients** - Comprehensive coverage |
| `recipe_matrix.py` | **865 ingredients** - Full matrix (sparse) |
| `export_matrices.py` | Export matrices to CSV, NumPy, LaTeX |
| `Recipe_Matrix_Demo.ipynb` | Jupyter notebook for classroom use |
| `exports/` | Generated matrix files |

---

## 📊 Available Matrices

| Matrix | Dimensions | Sparsity | Best For |
|--------|-----------|----------|----------|
| **Template** | 225 × 30 | 81% | Handouts, small examples |
| **Extended** | 225 × 145 | 93% | Balanced coverage |
| **Full** | 225 × 865 | 97% | Complete analysis |

### Template Matrix (30 Ingredients)
```
Proteins (6):   chicken, beef, pork, fish, eggs, tofu
Dairy (4):      milk, butter, cheese, cream
Vegetables (8): onion, garlic, tomato, potato, carrot, pepper, mushroom, spinach
Grains (4):     rice, pasta, bread, flour
Oils (2):       olive_oil, vegetable_oil
Seasonings (6): salt, sugar, soy_sauce, vinegar, lemon, ginger
```

### Extended Matrix (145 Ingredients)
```
Proteins (20):   chicken, beef, pork, lamb, bacon, sausage, fish, shrimp, ...
Dairy (12):      milk, butter, cream, cheese, mozzarella, feta, yogurt, ...
Vegetables (25): onion, garlic, tomato, potato, carrot, celery, pepper, ...
Herbs (15):      parsley, cilantro, basil, thyme, rosemary, oregano, ...
Grains (12):     rice, pasta, noodles, bread, flour, breadcrumbs, ...
Oils (6):        olive_oil, vegetable_oil, sesame_oil, coconut_oil, ...
Seasonings (20): salt, black_pepper, sugar, paprika, cumin, cinnamon, ...
Sauces (15):     soy_sauce, fish_sauce, tomato_paste, vinegar, lemon_juice, ...
Nuts (8):        almonds, walnuts, peanuts, cashews, pine_nuts, ...
Legumes (6):     chickpeas, lentils, black_beans, white_beans, ...
Baking (6):      baking_powder, baking_soda, yeast, cornstarch, ...
```

---

## 🚀 Quick Start

### Generate All Matrices
```bash
cd linear_algebra

# Template Matrix (30 ingredients) - Best for classroom handouts
python template_matrix.py

# Extended Matrix (145 ingredients) - Comprehensive coverage
python extended_matrix.py

# Full Matrix (865 ingredients) - Complete but sparse
python recipe_matrix.py
```

### Load in Python
```python
import numpy as np

# Load template matrix (recommended for teaching)
R = np.load('exports/template_matrix.npy')           # Shape: (225, 30)
ingredients = np.load('exports/ingredient_names.npy') # 30 ingredient names
recipes = np.load('exports/recipe_names.npy')         # 225 recipe names

# Or load extended matrix for more detail
R_ext = np.load('exports/extended_matrix.npy')        # Shape: (225, 145)
```

### Open Jupyter Notebook
```bash
jupyter notebook Recipe_Matrix_Demo.ipynb
```

---

## 📐 Mathematical Concepts

### 1. Recipe-Ingredient Matrix (R)

$$R \in \{0,1\}^{n \times m}$$

Where:
- $n$ = number of recipes
- $m$ = number of unique ingredients
- $R_{ij} = 1$ if recipe $i$ contains ingredient $j$

**Example (5 recipes × 10 ingredients):**
```
              eggs milk bread butter flour rice pasta chicken veggies cheese
French Toast    1    1    1     1     0    0    0      0       0       0
Pancakes        1    1    0     1     1    0    0      0       0       0
Omelette        1    0    0     1     0    0    0      0       1       1
Fried Rice      1    0    0     0     0    1    0      1       1       0
Pasta           0    0    0     0     0    0    1      0       0       1
```

---

### 2. Inventory Matching (Matrix-Vector Product)

**Problem:** Which recipes can I make with my ingredients?

**Solution:**
$$\text{scores} = R \cdot \mathbf{v}$$

Where $\mathbf{v}$ is the inventory vector:
- $v_j = 1$ if user has ingredient $j$
- $v_j = 0$ otherwise

**Interpretation:** $\text{scores}_i$ = number of matching ingredients for recipe $i$

```python
# Example
inventory = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]  # eggs, milk, bread, butter
scores = R @ inventory  # [4, 4, 2, 1, 0]
# French Toast and Pancakes have all 4 ingredients!
```

---

### 3. Cosine Similarity

**Problem:** Which recipes are similar?

**Formula:**
$$\text{sim}(\mathbf{a}, \mathbf{b}) = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\| \cdot \|\mathbf{b}\|}$$

**For entire matrix:**
$$S = \hat{R} \cdot \hat{R}^T$$

Where $\hat{R}$ is row-normalized ($\|\hat{R}_i\| = 1$)

**Result:** $S_{ij}$ = similarity between recipe $i$ and recipe $j$

---

### 4. SVD Decomposition

$$R = U \Sigma V^T$$

- $U \in \mathbb{R}^{n \times k}$: Recipe embeddings
- $\Sigma \in \mathbb{R}^{k \times k}$: Singular values (importance)
- $V^T \in \mathbb{R}^{k \times m}$: Ingredient embeddings

**Applications:**
- **Compression:** Keep only top-$k$ components
- **Recommendations:** Use latent factors
- **Clustering:** Group similar recipes

---

## 📊 Sample Output

```
============================================================
DEMO 1: Recipe-Ingredient Matrix
============================================================

Matrix Shape: (225, 487)
  - 225 recipes (rows)
  - 487 unique ingredients (columns)

Matrix Properties:
  - Sparsity: 97.2% zeros
  - Average ingredients per recipe: 13.5
  - Most common ingredient appears in: 156 recipes

============================================================
DEMO 2: Matrix-Vector Multiplication (Recipe Matching)
============================================================

Your Inventory: ['eggs', 'butter', 'flour', 'sugar', 'milk']

🧮 Computing: scores = R @ v

Top 5 Recipes by Ingredient Match:
  1. Classic Pancakes: 5 matches (100%)
  2. French Toast: 4 matches (80%)
  3. Simple Cake: 4 matches (67%)
  ...
```

---

## 🎓 Classroom Activities

### Activity 1: Build Your Own Matrix
1. Pick 5 favorite recipes
2. List all ingredients
3. Create the binary matrix by hand
4. Verify dimensions: recipes × ingredients

### Activity 2: Inventory Matching
1. List what's in your fridge (inventory vector)
2. Compute $R \cdot \mathbf{v}$ by hand
3. Which recipe scores highest?

### Activity 3: Find Similar Recipes
1. Pick a recipe
2. Compute cosine similarity with 2 other recipes
3. Which is more similar? Why?

### Activity 4: SVD Exploration
1. Compute SVD of a 5×10 matrix
2. Plot singular values
3. How many components capture 90% of variance?

---

## 📚 Further Reading

- [Introduction to Linear Algebra (Strang)](https://math.mit.edu/~gs/linearalgebra/)
- [Netflix Prize and Matrix Factorization](https://www.netflixprize.com/)
- [Recommender Systems Handbook](https://link.springer.com/book/10.1007/978-1-4899-7637-6)

---

## 🛠️ Requirements

```bash
pip install numpy matplotlib seaborn jupyter
```
