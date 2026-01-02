# Food.com Dataset Instructions

## 📥 Download the Dataset

1. **Go to Kaggle**: https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions

2. **Create Account** (if you don't have one)
   - Click "Register" 
   - Use Google/Email signup (takes 2 minutes)

3. **Download the File**
   - Click the "Download" button (top right)
   - It will download `archive.zip` (~230MB)

4. **Extract the File**
   - Unzip `archive.zip`
   - Find `RAW_recipes.csv` (this is what we need!)

5. **Place Here**
   - Put `RAW_recipes.csv` in this folder (`backend/data/raw/`)
   - Final path: `backend/data/raw/RAW_recipes.csv`

## ✅ Verify

After placing the file, you should have:
```
backend/data/raw/
├── README.md (this file)
└── RAW_recipes.csv (the dataset - ~50MB)
```

## 🚀 Next Steps

Once the file is here, run the importer:

```bash
# From backend directory
cd /path/to/MyFridge/backend
source venv/bin/activate

# Import 1,000 recipes (recommended for first run)
python scraper/batch_import_foodcom.py --limit 1000

# Or import more (takes longer)
python scraper/batch_import_foodcom.py --limit 5000
```

The importer will:
- ✅ Check for duplicates automatically
- ✅ Extract only recipe facts (legal)
- ✅ Generate original descriptions
- ✅ Skip recipes you already have
- ✅ Save progress incrementally

---

## 📊 Dataset Info

**Food.com Recipe Dataset**
- 230,000+ recipes
- Community-sourced
- Includes: ingredients, steps, tags, nutrition
- License: Public dataset for research/educational use

---

**Questions?** Just ask! 🎉

