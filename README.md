# 🕌 Seerah Quiz — Islamic Knowledge Series

A multi-section Islamic quiz app covering 4,698+ questions across 7 worlds — from Foundations of Faith through Post-Islamic history. Built as static HTML files, hosted on GitHub Pages / Vercel.

---

## 🌍 Worlds

| # | World | Questions | Topics |
|---|---|---|---|
| 0 | 🕌 Foundations of Faith | 390 | Tawheed · 3 Principles · 5 Pillars · 6 Pillars of Eemaan · Taharah · Halal & Haram · Character |
| 1 | 🌌 Beginning of Time | 300 | Adam ﷺ · Iblis · Angels · Jinn · Creation |
| 2 | 📜 The Prophets | 1,028 | Hud → Isa ﷺ · Muhammad ﷺ · Prophethood theory |
| 3 | 🌍 Pre-Islam | 677 | Arabia · Rome · Persia · India · Ka'bah · Lineage |
| 4 | 🌟 Seerah | 1,532 | Birth → Revelation → Battles → Farewell |
| 5 | 🛡️ The Sahaabah | 548 | Companions · Men Around the Prophet |
| 6 | 🏛️ Post-Islam | 223 | Umayyads · Islamic Spain · Islamic History |

---

## 🚀 Hosting on GitHub + Vercel

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/seerah-quiz.git
git branch -M main
git push -u origin main
```

### Step 2 — Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) → **New Project**
2. Import your GitHub repo
3. Leave all settings as default → **Deploy**
4. Your site is live at `https://seerah-quiz.vercel.app`

---

## ➕ Adding New Questions

### 1. Prepare your Excel file and drop it into `new-questions/`

### 2. Run the update script
```bash
python3 scripts/update.py
```

### 3. Push to GitHub
```bash
git add .
git commit -m "Add new questions"
git push
```

Vercel auto-deploys in ~30 seconds.

---

## 📁 Project Structure

```
seerah-quiz/
├── index.html                   ← Home screen (world selector)
├── foundations-of-faith.html    ← World 0 (new — for new Muslims)
├── beginning-of-time.html       ← World 1
├── the-prophets.html            ← World 2
├── pre-islam.html               ← World 3
├── seerah.html                  ← World 4
├── the-sahaabah.html            ← World 5
├── post-islam.html              ← World 6
├── assets/
│   ├── style.css
│   ├── quiz.js
│   └── certificate.js
├── scripts/
│   ├── build_html.py            ← Builds HTML from JSON
│   └── update.py                ← Master update script
├── data/
│   ├── world0.json              ← Foundations of Faith questions
│   ├── world1.json through world6.json
└── new-questions/               ← Drop new .xlsx files here
```

---

## 📖 Sources (Ahlus Sunnah wal Jama'ah only)

- *Al-Bidaya wal-Nihaya* — Ibn Kathir
- *Kitab al-Tawheed* — Ibn Abd al-Wahhab
- *The Three Fundamental Principles* — Ibn Abd al-Wahhab
- *The Sealed Nectar* — al-Mubarakpuri
- *Men Around the Messenger* — Khalid Muhammad Khalid
- *Riyadh al-Saliheen* — al-Nawawi

No Sufi or Shia sources used.
