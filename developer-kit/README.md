# MyFridge Developer Kit

**Version:** 1.0  
**Purpose:** Development team tools and documentation  
**Status:** Production Ready

---

## 🎯 What is This?

This directory contains **developer-only** resources for the MyFridge development team. These files are **NOT** part of the production application—they're for maintaining and extending the codebase.

---

## 📦 What's Inside

### Documentation
- **DEVELOPER_KIT_INDEX.md** → Start here! Complete navigation guide
- **PACKAGE_SUMMARY.md** → Delivery summary and handoff notes

### Systems
- **ingredient-classification/** → Complete classification system docs and tools
  - README.md → Quick start guide
  - ALGORITHM.md → Technical specification
  - tools/ → Developer utilities

---

## 🚀 Quick Start

### For Product Managers
```
Read: PACKAGE_SUMMARY.md
Then: ingredient-classification/README.md
```

### For Developers
```
Read: DEVELOPER_KIT_INDEX.md
Then: ingredient-classification/ALGORITHM.md
Test: ingredient-classification/tools/classify_single_recipe.py
```

### For QA/Testing
```
Run: ingredient-classification/tools/export_for_review.py
Verify: backend/scraper/verify_classification.py
```

---

## 📋 Common Tasks

### Test Single Recipe
```bash
cd ingredient-classification/tools
python classify_single_recipe.py "Recipe Name"
```

### Export for Review
```bash
cd ingredient-classification/tools
python export_for_review.py --summary
```

### Re-Classify Database
```bash
cd ../backend
source venv/bin/activate
python scraper/classify_ingredients.py
```

### Verify Classification
```bash
cd ../backend
python scraper/verify_classification.py
```

---

## 🏗️ Directory Structure

```
developer-kit/
│
├── README.md                        # This file
├── DEVELOPER_KIT_INDEX.md          # Complete navigation
├── PACKAGE_SUMMARY.md              # Delivery notes
│
└── ingredient-classification/       # Classification system
    ├── README.md                    # System quick start
    ├── ALGORITHM.md                 # Technical spec
    │
    ├── tools/                       # Developer utilities
    │   ├── classify_single_recipe.py
    │   └── export_for_review.py
    │
    └── test-data/                   # Test datasets (create as needed)
```

---

## ⚠️ Important Notes

### This is NOT Production Code

- **Do not** include in production builds
- **Do not** deploy to production servers
- **Do not** package with application
- **Use** for development and testing only

### This IS for Development

- **Do** use for understanding the system
- **Do** use for testing and validation
- **Do** use for tuning and customization
- **Do** keep version controlled

---

## 📖 Documentation Map

| Need | Read This | Location |
|------|-----------|----------|
| Overview | DEVELOPER_KIT_INDEX.md | Root |
| Delivery summary | PACKAGE_SUMMARY.md | Root |
| Quick start | ingredient-classification/README.md | System |
| Full technical spec | ingredient-classification/ALGORITHM.md | System |
| Tool usage | Each tool has `--help` | tools/ |

---

## 🛠️ Tools Included

### classify_single_recipe.py
Test classification on one recipe with detailed scoring breakdown.

**Usage:**
```bash
python classify_single_recipe.py "French Toast"
python classify_single_recipe.py --recipe-id recipe_001
python classify_single_recipe.py --test  # Mock data
```

### export_for_review.py
Export recipes to CSV for team review and validation.

**Usage:**
```bash
python export_for_review.py --summary
python export_for_review.py --category dessert
python export_for_review.py --sample 50
```

---

## 💡 Support

### Questions?
- **Algorithm:** See ingredient-classification/ALGORITHM.md
- **Usage:** See ingredient-classification/README.md
- **Navigation:** See DEVELOPER_KIT_INDEX.md

### Issues?
- **Bug reports:** Include recipe name/ID and expected vs actual
- **Feature requests:** Describe use case and desired behavior
- **Performance:** Run verification script for metrics

---

## 🔄 Version History

### v1.0 (January 2026)
- Initial release
- Ingredient classification system v2.0
- Complete documentation (24,000+ words)
- Developer tools (450+ lines)
- Production ready

---

## 📝 License & Usage

**For:** Internal development team use only  
**Status:** Not part of production deployment  
**Modification:** Encouraged (customize for your needs)  
**Distribution:** Internal only

---

## 🎉 Ready to Start?

1. Read **DEVELOPER_KIT_INDEX.md** for complete navigation
2. Review **PACKAGE_SUMMARY.md** for delivery details
3. Explore **ingredient-classification/** for the main system
4. Try **tools/** for hands-on testing

---

**Have questions?** Start with DEVELOPER_KIT_INDEX.md for quick navigation to what you need.

