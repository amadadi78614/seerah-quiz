"""
build_html.py
=============
Generates one HTML file per world from the data/world*.json files.
Each world has a chronological level system with progressive unlocking (80% pass mark).

Usage:
  python3 scripts/build_html.py
"""

import json, os, re, hashlib
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

WORLDS_META = [
    { 'id':0, 'slug':'beginning-of-time',  'emoji':'🌌',
      'name':'Beginning of Time', 'arabic':'بِدَايَةُ الْخَلْق',
      'phase':'In the Beginning',
      'desc':'The Pen, the Throne, the heavens and earth, the angels, Jinn and Iblis — before and during the creation of the universe.',
      'color':'#4a3080', 'accent':'#9b6dff' },
    { 'id':1, 'slug':'the-prophets',        'emoji':'📜',
      'name':'The Prophets',      'arabic':'الْأَنْبِيَاء',
      'phase':'From Adam ﷺ to Isa ﷺ',
      'desc':'Stories, miracles, and lessons from all the prophets — from Adam ﷺ to Isa ﷺ.',
      'color':'#1a4a2a', 'accent':'#4caf50' },
    { 'id':2, 'slug':'pre-islam',           'emoji':'🌍',
      'name':'Pre-Islam',         'arabic':'مَا قَبْلَ الْإِسْلَام',
      'phase':'Before the Dawn',
      'desc':'Arabia, Rome, Persia, India — the state of the world before the Prophet ﷺ.',
      'color':'#3a2a10', 'accent':'#ff9800' },
    { 'id':3, 'slug':'seerah',              'emoji':'🌟',
      'name':'Seerah',            'arabic':'السِّيرَةُ النَّبَوِيَّة',
      'phase':'610–632 CE',
      'desc':'The life of the Prophet Muhammad ﷺ — birth through farewell.',
      'color':'#1a2a4a', 'accent':'#64b5f6' },
    { 'id':4, 'slug':'the-sahaabah',        'emoji':'🛡️',
      'name':'The Sahaabah',      'arabic':'الصَّحَابَة',
      'phase':'After the Prophet ﷺ',
      'desc':'The lives, sacrifices, and contributions of the Companions.',
      'color':'#3a1a10', 'accent':'#ef5350' },
    { 'id':5, 'slug':'post-islam',          'emoji':'🏛️',
      'name':'Post-Islam',        'arabic':'مَا بَعْدَ الْإِسْلَام',
      'phase':'7th–20th Century',
      'desc':'Umayyads, Abbasids, the Ottoman Empire, and the spread of Islamic civilisation.',
      'color':'#1a3a3a', 'accent':'#26c6da' },
]

# ── Chronological level order per world ─────────────────────────────────────
LEVEL_ORDER = {
    0: [  # Beginning of Time — creation topics in chronological/logical order
        "Beginning of Time · The Pen & The Tablet",
        "Beginning of Time · The Throne & The Kursi",
        "Beginning of Time · Creation of the Earth",
        "Beginning of Time · Angels",
        "Beginning of Time · Jinn & Iblis",
        "Beginning of Time · Creation of Adam ﷺ",
        "Beginning of Time · Adam's Descent & Early Humanity",
    ],
    1: [  # The Prophets — one level per prophet in chronological order
        "The Prophets · Who Are the Prophets",
        "The Prophets · Faith in Prophets",
        "The Prophets · Adam ﷺ",
        "The Prophets · Idris ﷺ",
        "The Prophets · Nuh ﷺ",
        "The Prophets · Hud ﷺ",
        "The Prophets · Salih ﷺ",
        "The Prophets · Ibrahim ﷺ",
        "The Prophets · Isma'il ﷺ",
        "The Prophets · Ishaq ﷺ",
        "The Prophets · Lut ﷺ",
        "The Prophets · Yaqub ﷺ",
        "The Prophets · Yusuf ﷺ",
        "The Prophets · Ayyub ﷺ",
        "The Prophets · Shu'aib ﷺ",
        "The Prophets · Musa & Harun ﷺ",
        "The Prophets · Hizqael ﷺ",
        "The Prophets · Elisha ﷺ",
        "The Prophets · Samuel ﷺ",
        "The Prophets · Dawud ﷺ",
        "The Prophets · Sulaiman ﷺ",
        "The Prophets · Isaiah ﷺ",
        "The Prophets · Jeremiah ﷺ",
        "The Prophets · Daniel ﷺ",
        "The Prophets · Uzair ﷺ",
        "The Prophets · Dhul-Kifl ﷺ",
        "The Prophets · Yunus ﷺ",
        "The Prophets · Zakariyya ﷺ",
        "The Prophets · Yahya ﷺ",
        "The Prophets · Isa ﷺ",
        "The Prophets · Their Mission",
        "The Prophets · Their Qualities",
        "The Prophets · Our Duty",
        "The Prophets · Mixed Review",
    ],
    2: [  # Pre-Islam — topics as levels
        "Pre-Islam · Arabia · Lineage & Ancestry",
        "Pre-Islam · Arabia · Society & Tribes",
        "Pre-Islam · Arabia · The Ka'bah",
        "Pre-Islam · Arabia · Religions of Arabia",
        "Pre-Islam · Arabia · Seekers of Truth",
        "Pre-Islam · Arabia · Early Life of the Prophet ﷺ",
        "Pre-Islam · Arabia · Khadijah & Marriages",
        "Pre-Islam · Global · Rome",
        "Pre-Islam · Global · Persia",
        "Pre-Islam · Global · India",
        "Pre-Islam · Global · Christianity & Judaism",
        "Pre-Islam · Global · World Civilisations",
        "Pre-Islam · Mixed",
    ],
    3: [  # Seerah — chronological stages
        "Seerah · Early Life",
        "Seerah · The Revelation",
        "Seerah · Early Islam in Makkah",
        "Seerah · Persecution",
        "Seerah · Migration to Abyssinia",
        "Seerah · Year of Grief",
        "Seerah · At-Ta'if",
        "Seerah · Al-Isra wal-Mi'raj",
        "Seerah · Pledges of Aqabah",
        "Seerah · The Hijrah",
        "Seerah · Madinah",
        "Seerah · Battle of Badr",
        "Seerah · Battle of Uhud",
        "Seerah · Battle of the Trench",
        "Seerah · Hudaybiyyah & Later",
        "Seerah · Conquest of Makkah",
        "Seerah · Final Years",
    ],
    4: [  # Sahaabah
        "Sahaabah · The Companions",
        "Sahaabah · Stories of Conversion",
        "Sahaabah · Mixed",
    ],
    5: [  # Post-Islam
        "Post-Islam · Umayyad Era",
        "Post-Islam · Islamic Spain",
        "Post-Islam · Islamic History",
    ],
}

# Short display labels for timeline nodes
LEVEL_LABELS = {
    "The Prophets · Who Are the Prophets": "Who Are the Prophets",
    "The Prophets · Faith in Prophets": "Faith in Prophets",
    "The Prophets · Their Mission": "Their Mission",
    "The Prophets · Their Qualities": "Their Qualities",
    "The Prophets · Our Duty": "Our Duty",
    "The Prophets · Mixed Review": "Mixed Review",
    "The Prophets · Arabic Vocabulary": "Arabic Vocab",
    "The Prophets · Musa & Harun ﷺ": "Musa & Harun ﷺ",
    "Seerah · Early Life": "Early Life",
    "Seerah · The Revelation": "The Revelation",
    "Seerah · Early Islam in Makkah": "Early Makkah",
    "Seerah · Persecution": "Persecution",
    "Seerah · Migration to Abyssinia": "Abyssinia",
    "Seerah · Year of Grief": "Year of Grief",
    "Seerah · At-Ta'if": "At-Ta'if",
    "Seerah · Al-Isra wal-Mi'raj": "Al-Isra wal-Mi'raj",
    "Seerah · Pledges of Aqabah": "Pledges of Aqabah",
    "Seerah · The Hijrah": "The Hijrah",
    "Seerah · Madinah": "Madinah",
    "Seerah · Battle of Badr": "Battle of Badr",
    "Seerah · Battle of Uhud": "Battle of Uhud",
    "Seerah · Battle of the Trench": "The Trench",
    "Seerah · Hudaybiyyah & Later": "Hudaybiyyah",
    "Seerah · Conquest of Makkah": "Conquest",
    "Seerah · Final Years": "Final Years",
}

def get_label(topic):
    if topic in LEVEL_LABELS:
        return LEVEL_LABELS[topic]
    # Strip world prefix
    parts = topic.split(' · ')
    return parts[-1] if parts else topic

def esc_js(s):
    s = str(s)
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace("'", "\\'")
    s = s.replace('\n', ' ').replace('\r', '').replace('\xa0', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def build_levels_js(questions, world_id):
    """Build JS levels array with questions grouped by topic in chronological order."""
    # Group questions by topic
    by_topic = defaultdict(list)
    for q in questions:
        by_topic[q['topic']].append(q)

    # Get ordered topics for this world
    ordered = LEVEL_ORDER.get(world_id, [])
    # Add any topics not in ordered list at the end
    extra = [t for t in sorted(by_topic.keys()) if t not in ordered]
    all_topics = [t for t in ordered if t in by_topic] + [t for t in extra if t in by_topic]

    levels_js = []
    for i, topic in enumerate(all_topics):
        qs = by_topic[topic]
        label = get_label(topic)
        q_objs = []
        for q in qs:
            opts_js = "[" + ",".join(f'"{esc_js(o)}"' for o in q.get('opts', [])) + "]"
            explain = esc_js(q.get('explanation', q.get('explain', '')))
            q_objs.append(
                f'{{id:"{q["id"]}",q:"{esc_js(q["q"])}",opts:{opts_js},'
                f'correct:{q.get("correct",0)},difficulty:"{q.get("difficulty","medium")}"'
                + (f',explain:"{explain}"' if explain else '')
                + '}'
            )
        qs_str = "[\n    " + ",\n    ".join(q_objs) + "\n  ]"
        levels_js.append(
            f'  {{id:{i},topic:"{esc_js(topic)}",label:"{esc_js(label)}",questions:{qs_str}}}'
        )

    return "[\n" + ",\n".join(levels_js) + "\n]"

def build_html(meta, questions):
    world_id = meta['id']
    levels_js = build_levels_js(questions, world_id)
    ordered = LEVEL_ORDER.get(world_id, [])
    by_topic = defaultdict(list)
    for q in questions:
        by_topic[q['topic']].append(q)
    all_topics = [t for t in ordered if t in by_topic] + \
                 [t for t in sorted(by_topic.keys()) if t not in ordered and t in by_topic]
    total_levels = len(all_topics)
    total_q = len(questions)
    slug = meta['slug']
    name = meta['name']
    arabic = meta['arabic']
    emoji = meta['emoji']
    phase = meta['phase']
    desc = meta['desc']
    color = meta['color']
    accent = meta['accent']

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Seerah Quiz</title>
<link rel="stylesheet" href="assets/style.css">
<style>
  :root {{ --accent:{accent}; --bg:{color}; }}

  /* ── Timeline ── */
  .timeline-wrap {{
    overflow-x: auto;
    padding: 12px 0 20px;
    scrollbar-width: thin;
    scrollbar-color: var(--accent) transparent;
  }}
  .timeline {{
    display: flex;
    align-items: center;
    gap: 0;
    min-width: max-content;
    padding: 0 20px;
  }}
  .tl-node {{
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    position: relative;
  }}
  .tl-node.locked {{ cursor: not-allowed; opacity: 0.45; }}
  .tl-node.active .tl-dot {{ border-color: var(--accent); box-shadow: 0 0 0 4px rgba(255,255,255,0.15); }}
  .tl-dot {{
    width: 36px; height: 36px;
    border-radius: 50%;
    border: 3px solid #555;
    background: #1e1e2e;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    font-weight: 700;
    color: #ccc;
    transition: all 0.3s;
    z-index: 1;
  }}
  .tl-node.completed .tl-dot {{
    background: var(--accent);
    border-color: var(--accent);
    color: #000;
  }}
  .tl-node.active .tl-dot {{
    background: #2a2a3e;
    border-color: var(--accent);
    color: var(--accent);
  }}
  .tl-label {{
    font-size: 0.62rem;
    color: #888;
    margin-top: 6px;
    text-align: center;
    max-width: 70px;
    line-height: 1.2;
    white-space: normal;
  }}
  .tl-node.completed .tl-label {{ color: var(--accent); }}
  .tl-node.active .tl-label {{ color: #fff; font-weight: 600; }}
  .tl-line {{
    width: 30px; height: 3px;
    background: #333;
    flex-shrink: 0;
    margin-bottom: 22px;
  }}
  .tl-line.done {{ background: var(--accent); }}

  /* ── Level card (home screen) ── */
  .level-card {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .level-card:hover:not(.locked) {{ background: rgba(255,255,255,0.1); transform: translateX(4px); }}
  .level-card.locked {{ opacity: 0.4; cursor: not-allowed; }}
  .level-card.active {{ border-color: var(--accent); background: rgba(255,255,255,0.08); }}
  .level-card.completed {{ border-color: var(--accent); }}
  .level-num {{
    width: 44px; height: 44px;
    border-radius: 50%;
    border: 2px solid #555;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 1rem;
    flex-shrink: 0;
    color: #888;
  }}
  .level-card.completed .level-num {{ background: var(--accent); border-color: var(--accent); color: #000; }}
  .level-card.active .level-num {{ border-color: var(--accent); color: var(--accent); }}
  .level-info {{ flex: 1; }}
  .level-title {{ font-weight: 600; font-size: 0.95rem; color: #eee; }}
  .level-meta {{ font-size: 0.78rem; color: #888; margin-top: 2px; }}
  .level-badge {{ font-size: 0.75rem; padding: 3px 10px; border-radius: 20px; }}
  .badge-done {{ background: rgba(76,175,80,0.2); color: #4caf50; border: 1px solid #4caf50; }}
  .badge-locked {{ background: rgba(100,100,100,0.2); color: #888; border: 1px solid #555; }}
  .badge-active {{ background: rgba(255,255,255,0.1); color: var(--accent); border: 1px solid var(--accent); }}

  /* ── Quiz screen ── */
  .quiz-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0; margin-bottom: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }}
  .level-title-bar {{
    font-size: 0.8rem; color: #aaa;
    text-align: center; margin-bottom: 8px;
  }}
  .progress-bar {{ height: 4px; background: #2a2a3e; border-radius: 2px; margin-bottom: 20px; }}
  .progress-fill {{ height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.4s; }}
  .question-text {{ font-size: 1.1rem; line-height: 1.6; margin-bottom: 22px; color: #f0f0f0; }}
  .opt-btn {{
    display: flex; align-items: center; gap: 14px;
    width: 100%; padding: 14px 18px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px; margin-bottom: 10px;
    cursor: pointer; color: #ddd;
    font-size: 0.95rem; text-align: left;
    transition: all 0.15s;
  }}
  .opt-btn:hover:not(:disabled) {{ background: rgba(255,255,255,0.1); border-color: var(--accent); }}
  .opt-btn.correct {{ background: rgba(76,175,80,0.25); border-color: #4caf50; color: #fff; }}
  .opt-btn.wrong   {{ background: rgba(239,83,80,0.25);  border-color: #ef5350; color: #fff; }}
  .opt-letter {{
    width: 28px; height: 28px; border-radius: 50%;
    background: rgba(255,255,255,0.1);
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.8rem; flex-shrink: 0;
  }}
  .explain-box {{
    background: rgba(255,255,255,0.05);
    border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 0.88rem; color: #bbb;
    margin: 12px 0;
  }}
  .btn-next {{
    background: var(--accent); color: #000;
    border: none; border-radius: 10px;
    padding: 12px 32px; font-size: 1rem; font-weight: 700;
    cursor: pointer; margin-top: 8px;
    transition: opacity 0.2s;
  }}
  .btn-next:hover {{ opacity: 0.85; }}

  /* ── Results screen ── */
  .result-ring {{
    width: 120px; height: 120px;
    border-radius: 50%;
    border: 6px solid var(--accent);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    margin: 0 auto 20px;
  }}
  .result-pct {{ font-size: 2rem; font-weight: 800; color: var(--accent); }}
  .result-label {{ font-size: 0.7rem; color: #888; }}
  .result-msg {{ text-align: center; font-size: 1rem; color: #ddd; margin-bottom: 20px; }}
  .result-stats {{ display: flex; gap: 20px; justify-content: center; margin-bottom: 24px; }}
  .stat-box {{ text-align: center; }}
  .stat-num {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); }}
  .stat-lbl {{ font-size: 0.75rem; color: #888; }}
  .btn-row {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}
  .btn {{ padding: 12px 24px; border-radius: 10px; font-size: 0.95rem; font-weight: 600; cursor: pointer; border: none; transition: opacity 0.2s; }}
  .btn:hover {{ opacity: 0.85; }}
  .btn-primary {{ background: var(--accent); color: #000; }}
  .btn-outline {{ background: transparent; border: 2px solid var(--accent); color: var(--accent); }}
  .btn-grey {{ background: rgba(255,255,255,0.1); color: #ccc; border: 1px solid #444; }}
  .unlock-banner {{
    background: linear-gradient(135deg, rgba(76,175,80,0.2), rgba(76,175,80,0.05));
    border: 1px solid #4caf50;
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
    margin-bottom: 20px;
    display: none;
  }}
  .unlock-banner.show {{ display: block; }}
  .unlock-banner .unlock-title {{ color: #4caf50; font-weight: 700; font-size: 1rem; }}
  .unlock-banner .unlock-sub {{ color: #aaa; font-size: 0.85rem; margin-top: 4px; }}

  /* ── Certificate modal ── */
  .modal-overlay {{
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.85);
    display: none; align-items: center; justify-content: center;
    z-index: 1000; padding: 20px;
  }}
  .modal-overlay.show {{ display: flex; }}
  .modal-box {{
    background: #1a1a2e;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 28px;
    max-width: 480px; width: 100%;
    text-align: center;
  }}
  .modal-box h2 {{ color: var(--accent); margin-bottom: 8px; }}
  .modal-box p {{ color: #aaa; font-size: 0.9rem; margin-bottom: 20px; }}
  .name-input {{
    width: 100%; padding: 12px 16px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px; color: #fff;
    font-size: 1rem; margin-bottom: 16px;
    box-sizing: border-box;
  }}
  #cert-canvas {{ display: none; }}

  /* ── Nav bar ── */
  .nav {{ display: flex; align-items: center; justify-content: space-between; padding: 14px 0; margin-bottom: 8px; }}
  .nav-back {{ color: var(--accent); text-decoration: none; font-size: 0.9rem; }}
  .nav-title {{ font-size: 1rem; font-weight: 700; color: #fff; }}
  .nav-score {{ font-size: 0.85rem; color: #888; }}

  .screen {{ display: none; }}
  .screen.active {{ display: block; }}
  .fade-in {{ animation: fadeIn 0.3s ease; }}
  @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}

  .world-hero {{ text-align: center; padding: 30px 0 20px; }}
  .world-emoji {{ font-size: 3rem; margin-bottom: 8px; }}
  .world-phase {{ font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 2px; }}
  .world-name {{ font-size: 2rem; font-weight: 800; color: #fff; margin: 6px 0; }}
  .world-arabic {{ font-size: 1.3rem; color: var(--accent); font-family: serif; direction: rtl; }}
  .world-desc {{ color: #aaa; font-size: 0.9rem; margin-top: 10px; max-width: 500px; margin-left: auto; margin-right: auto; }}
  .world-stats {{ display: flex; gap: 20px; justify-content: center; margin: 16px 0; }}
  .wstat {{ text-align: center; }}
  .wstat-num {{ font-size: 1.4rem; font-weight: 700; color: var(--accent); }}
  .wstat-lbl {{ font-size: 0.72rem; color: #888; }}

  .section-title {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; color: #666; margin: 20px 0 10px; }}
</style>
</head>
<body>
<div class="container">

  <!-- HOME SCREEN -->
  <div id="screen-home" class="screen active fade-in">
    <nav class="nav">
      <a href="index.html" class="nav-back">← All Worlds</a>
      <span class="nav-title">🕌 Seerah Quiz</span>
      <span></span>
    </nav>

    <div class="world-hero">
      <div class="world-emoji">{emoji}</div>
      <div class="world-phase">{phase}</div>
      <div class="world-name">{name}</div>
      <div class="world-arabic">{arabic}</div>
      <div class="world-desc">{desc}</div>
      <div class="world-stats">
        <div class="wstat"><div class="wstat-num">{total_levels}</div><div class="wstat-lbl">Levels</div></div>
        <div class="wstat"><div class="wstat-num">{total_q}</div><div class="wstat-lbl">Questions</div></div>
        <div class="wstat"><div class="wstat-num">80%</div><div class="wstat-lbl">Pass Mark</div></div>
      </div>
    </div>

    <!-- Timeline -->
    <div class="timeline-wrap">
      <div class="timeline" id="timeline-nodes"></div>
    </div>

    <!-- Level list -->
    <div class="section-title">Choose a Level</div>
    <div id="level-list"></div>
  </div>

  <!-- QUIZ SCREEN -->
  <div id="screen-quiz" class="screen">
    <nav class="nav">
      <a href="#" class="nav-back" onclick="goHome(); return false;">← Back</a>
      <span class="nav-title">🕌 Seerah Quiz</span>
      <span class="nav-score" id="nav-score">0/0</span>
    </nav>
    <div class="level-title-bar" id="quiz-level-title"></div>
    <div class="progress-bar"><div class="progress-fill" id="q-progress-fill" style="width:0%"></div></div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <span id="q-counter" style="font-size:0.85rem;color:#888"></span>
      <span id="q-diff" class="badge" style="font-size:0.75rem"></span>
    </div>
    <div class="question-text" id="q-text"></div>
    <div id="q-options"></div>
    <div class="explain-box" id="q-explain" style="display:none"></div>
    <div style="text-align:right">
      <button class="btn-next" id="q-next-btn" style="display:none" onclick="nextQuestion()">Next →</button>
    </div>
  </div>

  <!-- RESULTS SCREEN -->
  <div id="screen-results" class="screen">
    <nav class="nav">
      <a href="#" class="nav-back" onclick="goHome(); return false;">← Back</a>
      <span class="nav-title">🕌 Seerah Quiz</span>
      <span></span>
    </nav>
    <div style="text-align:center;padding:20px 0">
      <div style="font-size:0.8rem;color:#888;margin-bottom:16px" id="res-level-name"></div>
      <div class="result-ring">
        <div class="result-pct" id="res-score">0%</div>
        <div class="result-label">Score</div>
      </div>
      <div class="result-stats">
        <div class="stat-box"><div class="stat-num" id="res-correct">0</div><div class="stat-lbl">Correct</div></div>
        <div class="stat-box"><div class="stat-num" id="res-total">0</div><div class="stat-lbl">Total</div></div>
        <div class="stat-box"><div class="stat-num" id="res-pass">—</div><div class="stat-lbl">Pass Mark</div></div>
      </div>
      <div class="result-msg" id="res-msg"></div>
      <div class="unlock-banner" id="unlock-banner">
        <div class="unlock-title">🔓 Level Unlocked!</div>
        <div class="unlock-sub" id="unlock-sub"></div>
      </div>
      <div class="btn-row">
        <button class="btn btn-outline" onclick="retryLevel()">↺ Retry</button>
        <button class="btn btn-primary" onclick="goHome()">← Back to Levels</button>
        <button class="btn btn-grey" id="cert-btn" style="display:none" onclick="showCertModal()">🏅 Certificate</button>
      </div>
    </div>
  </div>

</div>

<!-- Certificate Modal -->
<div class="modal-overlay" id="cert-modal">
  <div class="modal-box">
    <h2>🏅 Certificate of Completion</h2>
    <p>Enter your name to generate your certificate for completing <strong id="cert-world-name">{name}</strong>.</p>
    <input type="text" class="name-input" id="cert-name-input" placeholder="Your full name" maxlength="60">
    <div class="btn-row" style="justify-content:center">
      <button class="btn btn-primary" onclick="generateCert()">Generate Certificate</button>
      <button class="btn btn-grey" onclick="closeCertModal()">Cancel</button>
    </div>
    <canvas id="cert-canvas" width="900" height="640"></canvas>
  </div>
</div>

<script src="assets/certificate.js"></script>
<script>
// ── Data ──────────────────────────────────────────────────────────────────
const WORLD_ID   = {world_id};
const WORLD_NAME = "{esc_js(name)}";
const WORLD_EMOJI= "{emoji}";
const PASS_MARK  = 80;
const STORAGE_KEY = 'seerah_world_{world_id}';

const LEVELS = {levels_js};

// ── State ─────────────────────────────────────────────────────────────────
let CUR_LEVEL   = 0;
let SESSION     = [];
let CUR_Q       = 0;
let SCORE       = 0;
let ANSWERED    = false;

// ── Storage helpers ───────────────────────────────────────────────────────
function getProgress() {{
  try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {{}}; }} catch(e) {{ return {{}}; }}
}}
function saveProgress(data) {{
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }} catch(e) {{}}
}}
function isUnlocked(levelIdx) {{
  if (levelIdx === 0) return true;
  const prog = getProgress();
  return prog['level_' + (levelIdx-1) + '_passed'] === true;
}}
function isCompleted(levelIdx) {{
  const prog = getProgress();
  return prog['level_' + levelIdx + '_passed'] === true;
}}
function getBestScore(levelIdx) {{
  const prog = getProgress();
  return prog['level_' + levelIdx + '_best'] || 0;
}}
function markPassed(levelIdx, pct) {{
  const prog = getProgress();
  prog['level_' + levelIdx + '_passed'] = true;
  if (!prog['level_' + levelIdx + '_best'] || pct > prog['level_' + levelIdx + '_best']) {{
    prog['level_' + levelIdx + '_best'] = pct;
  }}
  saveProgress(prog);
}}
function allCompleted() {{
  return LEVELS.every((_, i) => isCompleted(i));
}}

// ── Shuffle ───────────────────────────────────────────────────────────────
function shuffle(arr) {{
  const a = arr.slice();
  for (let i = a.length-1; i > 0; i--) {{
    const j = Math.floor(Math.random() * (i+1));
    [a[i], a[j]] = [a[j], a[i]];
  }}
  return a;
}}

// ── Screens ───────────────────────────────────────────────────────────────
function showScreen(id) {{
  document.querySelectorAll('.screen').forEach(s => {{
    s.classList.remove('active');
    s.style.display = 'none';
  }});
  const el = document.getElementById('screen-' + id);
  if (el) {{
    el.style.display = 'block';
    el.classList.add('active', 'fade-in');
    setTimeout(() => el.classList.remove('fade-in'), 400);
  }}
}}

// ── Home screen ───────────────────────────────────────────────────────────
function renderHome() {{
  renderTimeline();
  renderLevelList();
}}

function renderTimeline() {{
  const wrap = document.getElementById('timeline-nodes');
  wrap.innerHTML = '';
  LEVELS.forEach((lv, i) => {{
    const unlocked  = isUnlocked(i);
    const completed = isCompleted(i);
    const active    = unlocked && !completed;

    // Connector line before node (except first)
    if (i > 0) {{
      const line = document.createElement('div');
      line.className = 'tl-line' + (isCompleted(i-1) ? ' done' : '');
      wrap.appendChild(line);
    }}

    const node = document.createElement('div');
    node.className = 'tl-node' + (completed ? ' completed' : active ? ' active' : ' locked');
    node.title = lv.label;
    node.innerHTML = `
      <div class="tl-dot">${{completed ? '✓' : (i+1)}}</div>
      <div class="tl-label">${{lv.label}}</div>
    `;
    if (unlocked) node.onclick = () => startLevel(i);
    wrap.appendChild(node);
  }});

  // Scroll to active node
  const activeNode = wrap.querySelector('.tl-node.active');
  if (activeNode) setTimeout(() => activeNode.scrollIntoView({{behavior:'smooth', block:'nearest', inline:'center'}}), 100);
}}

function renderLevelList() {{
  const list = document.getElementById('level-list');
  list.innerHTML = '';
  LEVELS.forEach((lv, i) => {{
    const unlocked  = isUnlocked(i);
    const completed = isCompleted(i);
    const best      = getBestScore(i);
    const active    = unlocked && !completed;

    const card = document.createElement('div');
    card.className = 'level-card' + (completed ? ' completed' : active ? ' active' : ' locked');

    let badge = '';
    if (completed) badge = `<span class="level-badge badge-done">✓ ${{best}}%</span>`;
    else if (unlocked) badge = `<span class="level-badge badge-active">▶ Start</span>`;
    else badge = `<span class="level-badge badge-locked">🔒 Locked</span>`;

    card.innerHTML = `
      <div class="level-num">${{completed ? '✓' : (i+1)}}</div>
      <div class="level-info">
        <div class="level-title">${{lv.label}}</div>
        <div class="level-meta">${{lv.questions.length}} questions</div>
      </div>
      ${{badge}}
    `;
    if (unlocked) card.onclick = () => startLevel(i);
    list.appendChild(card);
  }});
}}

// ── Quiz ──────────────────────────────────────────────────────────────────
function startLevel(levelIdx) {{
  CUR_LEVEL = levelIdx;
  SESSION   = shuffle(LEVELS[levelIdx].questions);
  CUR_Q     = 0;
  SCORE     = 0;
  ANSWERED  = false;
  document.getElementById('quiz-level-title').textContent =
    'Level ' + (levelIdx+1) + ' — ' + LEVELS[levelIdx].label;
  showScreen('quiz');
  renderQuestion();
}}

function renderQuestion() {{
  if (CUR_Q >= SESSION.length) {{ showResults(); return; }}
  ANSWERED = false;
  const q   = SESSION[CUR_Q];
  // Shuffle options if not already done for this question in this session
  if (q._shuffled === undefined) {{
    const correctText = q.opts[q.correct];
    const shuffled = [...q.opts].sort(() => Math.random() - 0.5);
    q._shuffled = shuffled;
    q._shuffledCorrect = shuffled.indexOf(correctText);
  }}
  const pct = Math.round((CUR_Q / SESSION.length) * 100);
  document.getElementById('q-progress-fill').style.width = pct + '%';
  document.getElementById('q-counter').textContent = (CUR_Q+1) + ' / ' + SESSION.length;
  document.getElementById('nav-score').textContent  = SCORE + '/' + CUR_Q + ' correct';
  const diffEl = document.getElementById('q-diff');
  diffEl.className = 'badge badge-' + (q.difficulty || 'medium');
  diffEl.textContent = (q.difficulty || 'medium').charAt(0).toUpperCase() + (q.difficulty || 'medium').slice(1);
  document.getElementById('q-text').textContent = q.q;
  document.getElementById('q-explain').style.display = 'none';
  document.getElementById('q-next-btn').style.display = 'none';
  const letters = ['A','B','C','D'];
  document.getElementById('q-options').innerHTML = q._shuffled.map((opt, i) =>
    `<button class="opt-btn" onclick="answer(${{i}})" id="opt-${{i}}">
      <span class="opt-letter">${{letters[i]}}</span>
      <span>${{opt.replace(/^[A-Da-d][.)\s]\s*/,'')}}</span>
    </button>`
  ).join('');
}}

function answer(idx) {{
  if (ANSWERED) return;
  ANSWERED = true;
  const q = SESSION[CUR_Q];
  const correctIdx = q._shuffledCorrect !== undefined ? q._shuffledCorrect : q.correct;
  document.querySelectorAll('.opt-btn').forEach((b,i) => {{
    b.disabled = true;
    if (i === correctIdx) b.classList.add('correct');
    else if (i === idx)   b.classList.add('wrong');
  }});
  if (idx === correctIdx) SCORE++;
  if (idx !== correctIdx && q.explain) {{
    const el = document.getElementById('q-explain');
    el.innerHTML = '<span style="color:#ffd700">💡 Did you know?</span> ' + q.explain;
    el.style.display = 'block';
  }}
  document.getElementById('q-next-btn').style.display = 'inline-block';
}}

function nextQuestion() {{
  CUR_Q++;
  renderQuestion();
}}

function goHome() {{
  showScreen('home');
  renderHome();
}}

// ── Results ───────────────────────────────────────────────────────────────
function showResults() {{
  showScreen('results');
  const pct = Math.round((SCORE / SESSION.length) * 100);
  const passed = pct >= PASS_MARK;

  document.getElementById('res-score').textContent   = pct + '%';
  document.getElementById('res-correct').textContent = SCORE;
  document.getElementById('res-total').textContent   = SESSION.length;
  document.getElementById('res-pass').textContent    = PASS_MARK + '%';
  document.getElementById('res-level-name').textContent =
    'Level ' + (CUR_LEVEL+1) + ' — ' + LEVELS[CUR_LEVEL].label;

  document.getElementById('res-msg').textContent =
    pct >= 90 ? "🌟 Excellent! Masha\\'Allah!" :
    pct >= 80 ? "✅ Well done! You passed!" :
    pct >= 60 ? "📖 Good effort — retry to unlock the next level." :
                "💪 Keep studying. You will get there!";

  if (passed) markPassed(CUR_LEVEL, pct);

  // Unlock banner
  const banner   = document.getElementById('unlock-banner');
  const nextIdx  = CUR_LEVEL + 1;
  if (passed && nextIdx < LEVELS.length) {{
    const nextLabel = LEVELS[nextIdx] ? LEVELS[nextIdx].label : null;
    if (nextLabel) {{
      banner.classList.add('show');
      document.getElementById('unlock-sub').textContent = 'Next: ' + nextLabel;
    }}
  }} else {{
    banner.classList.remove('show');
  }}

  // Certificate button — show only if ALL levels completed
  document.getElementById('cert-btn').style.display = allCompleted() ? 'inline-block' : 'none';
}}

function retryLevel() {{
  startLevel(CUR_LEVEL);
}}

// ── Certificate ───────────────────────────────────────────────────────────
function showCertModal() {{
  document.getElementById('cert-modal').classList.add('show');
}}
function closeCertModal() {{
  document.getElementById('cert-modal').classList.remove('show');
}}
function generateCert() {{
  const name = document.getElementById('cert-name-input').value.trim();
  if (!name) {{ alert('Please enter your name.'); return; }}
  if (typeof drawCertificate === 'function') {{
    drawCertificate({{
      name: name,
      world: WORLD_NAME,
      emoji: WORLD_EMOJI,
      date: new Date().toLocaleDateString('en-GB', {{day:'numeric',month:'long',year:'numeric'}}),
      canvasId: 'cert-canvas',
      accent: getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()
    }});
  }}
  closeCertModal();
}}

// ── Init ──────────────────────────────────────────────────────────────────
(function init() {{
  showScreen('home');
  renderHome();
}})();
</script>
</body>
</html>"""

def main():
    print("Building HTML files...")
    for meta in WORLDS_META:
        wid  = meta['id']
        slug = meta['slug']
        path = DATA_DIR / f'world{wid}.json'
        if not path.exists():
            print(f"  ⚠ Skipping world {wid} — no data file")
            continue
        with open(path, encoding='utf-8') as f:
            questions = json.load(f)
        html = build_html(meta, questions)
        out  = BASE_DIR / f'{slug}.html'
        with open(out, 'w', encoding='utf-8') as f:
            f.write(html)
        size_kb = out.stat().st_size // 1024
        print(f"  ✓ {slug}.html — {len(questions)} questions — {size_kb} KB")
    print("Done!")

if __name__ == '__main__':
    main()
