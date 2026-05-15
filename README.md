# Cellshift — Smart Excel Transformations

> Upload. Analyze. Transform. Download. Built for Surrey, BC businesses.

## Quick Deploy (Free — Streamlit Community Cloud)

### Step 1: Create GitHub Repo
```bash
# Create a new repo called "cellshift" on github.com, then:
git init
git add app.py requirements.txt README.md
git commit -m "Initial commit — Cellshift MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cellshift.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud (Free)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your `cellshift` repo → `main` branch → `app.py`
5. Click "Deploy" — live in ~2 minutes
6. Your URL: `https://cellshift.streamlit.app`

### Step 3: Custom Domain (Optional)
- Buy `cellshift.io` or `cellshift.ca` (~$10-15/year)
- In Streamlit Cloud settings, add custom domain
- Update DNS: CNAME → your-app.streamlit.app

## Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

## File Structure
```
cellshift/
├── app.py              # Main Streamlit application (MVP)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── index.html          # Landing page / marketing website
└── docs/
    ├── Company_Blueprint.docx
    └── Lead_Generation_Playbook.docx
```

## Tech Stack
| Layer | Tech | Cost |
|-------|------|------|
| Frontend + Backend | Streamlit (Python) | $0 |
| Data Engine | Pandas + OpenPyXL | $0 |
| Hosting | Streamlit Community Cloud | $0 |
| Code | GitHub (free) | $0 |
| AI Operations | Claude Pro | $20/mo |

## Transformations Available
1. Remove Duplicates
2. Unpivot / Melt
3. Pivot & Aggregate
4. Clean Blanks
5. Standardize Dates
6. Split Columns
7. VLOOKUP Merge
8. Fix Data Types
9. Conditional Flagging
10. Audit Trail (auto-generated)

## License
Proprietary — Cellshift 2026
