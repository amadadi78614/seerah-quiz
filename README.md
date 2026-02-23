# 🕌 Seerah Quiz — Islamic Knowledge Series

A multi-section Islamic quiz app covering 3,600+ questions across 6 worlds — from the Beginning of Time to Post-Islam. Built as static HTML files, hosted on GitHub Pages / Vercel.

---

## 🌍 Worlds

| # | World | Questions | Topics |
|---|---|---|---|
| 0 | 🌌 Beginning of Time | 23 | Adam ﷺ · Idris ﷺ · Nuh ﷺ |
| 1 | 📜 The Prophets | 752 | Hud → Isa ﷺ · Muhammad ﷺ · Prophethood theory |
| 2 | 🌍 Pre-Islam | 677 | Arabia · Rome · Persia · India · Ka'bah · Lineage |
| 3 | 🌟 Seerah | 1,464 | Birth → Revelation → Battles → Farewell |
| 4 | 🛡️ The Sahaabah | 548 | Companions · Men Around the Prophet |
| 5 | 🏛️ Post-Islam | 223 | Umayyads · Islamic Spain · Islamic History |

---

## 🚀 Hosting on GitHub + Vercel

### Step 1 — Create a GitHub repo
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/seerah-quiz.git
git push -u origin main
```

### Step 2 — Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) → **New Project**
2. Import your GitHub repo
3. Leave all settings as default → **Deploy**
4. Your site is live at `https://seerah-quiz.vercel.app`

### Step 3 — Custom domain (optional)
In Vercel → Settings → Domains → add your domain (e.g. `seerahquiz.com`)

---

## ➕ Adding New Questions (Incremental Updates)

This is the key feature. To add new questions at any time:

### 1. Prepare your Excel file
Your `.xlsx` file should follow this format:
```
1. What was the name of the Prophet's father?
A) Abdullah
B) Abdul Muttalib
C) Abu Talib
D) Hamza
Answer: A

2. Next question...
```

Name your file to help the system classify it:
- `preislam_*.xlsx` → Pre-Islam world
- `prophets_*.xlsx` → The Prophets world
- `seerah_*.xlsx` → Seerah world
- `sahabah_*.xlsx` or `men_*.xlsx` → The Sahaabah world
- `bidaya_*.xlsx` or `nihaya_*.xlsx` → Al-Bidaya content

### 2. Drop the file into `new-questions/`
```
seerah-quiz/
└── new-questions/
    └── your-new-file.xlsx   ← put it here
```

### 3. Run the update script
```bash
python3 scripts/update.py
```

This will:
- Parse your new file
- Remove any duplicate questions automatically
- Sort questions chronologically
- Rebuild all HTML files

### 4. Push to GitHub
```bash
git add .
git commit -m "Add new questions from your-new-file.xlsx"
git push
```

Vercel auto-deploys in ~30 seconds. Done!

---

## 🏅 Certificates

Each world has a **Certificate of Completion** feature:
- Complete a quiz with **70% or higher** to unlock the certificate
- Click **"Get Certificate"** on the results screen
- Enter your name → a beautiful certificate is generated
- Download as a PNG image

---

## 📁 Project Structure

```
seerah-quiz/
├── index.html                  ← Home screen (world selector)
├── beginning-of-time.html      ← World 0
├── the-prophets.html           ← World 1
├── pre-islam.html              ← World 2
├── seerah.html                 ← World 3
├── the-sahaabah.html           ← World 4
├── post-islam.html             ← World 5
├── assets/
│   ├── style.css               ← Shared styles
│   ├── quiz.js                 ← Quiz engine (reference)
│   └── certificate.js          ← Certificate generator
├── scripts/
│   ├── update.py               ← ⭐ Master update script (run this)
│   ├── parse_all.py            ← Parses Excel → JSON
│   └── build_html.py           ← Builds HTML from JSON
├── data/
│   ├── world0.json             ← Question banks (auto-generated)
│   ├── world1.json
│   ├── world2.json
│   ├── world3.json
│   ├── world4.json
│   └── world5.json
└── new-questions/              ← Drop new .xlsx files here
```

---

## 🛠️ Requirements (for running scripts locally)

```bash
pip install openpyxl
```

Python 3.8+ required.

---

## 📖 Sources

Questions drawn from:
- *Stories of the Prophets* — Ibn Kathir
- *Knowing Allaah's Prophets & Messengers* — Muhammad al-Jibaly
- *The Sealed Nectar (Al-Raheeq Al-Makhtum)* — al-Mubarakpuri
- *The Noble Life of the Prophet* — al-Sallabi
- *Al-Bidaya wal-Nihaya* — Ibn Kathir
- *Men Around the Messenger* — Khalid Muhammad Khalid
