#!/usr/bin/env python3
"""
Audit all world JSON files for misplaced questions and move them to the correct world.
"""
import json
import re
from pathlib import Path

DATA_DIR = Path('/home/ubuntu/seerah-quiz/data')

# World definitions
WORLDS = {
    0: "Beginning of Time",    # Pen, Tablet, Throne, Heavens, Earth, Angels, Jinn, Iblis, Creation of Adam
    1: "The Prophets",         # Adam ﷺ (as prophet) through Isa ﷺ
    2: "Pre-Islam",            # Arabia, Rome, Persia, India, world before Islam
    3: "Seerah",               # Life of Prophet Muhammad ﷺ
    4: "The Sahaabah",         # Companions
    5: "Post-Islam",           # After the Prophet's death — caliphs, empires
}

# Keywords that STRONGLY indicate a specific world
WORLD_KEYWORDS = {
    0: [
        # Creation topics only
        r'\bpen\b', r'\btablet\b', r'\bthrone\b', r'\bkursi\b', r'\barsh\b',
        r'\bseven heavens\b', r'\bfirmament\b', r'\bangel[s]?\b', r'\bjibril\b',
        r'\bjinn\b', r'\biblis\b', r'\bshaytan\b', r'\bsatan\b',
        r'\bcreation of (the )?earth\b', r'\bcreated (the )?earth\b',
        r'\bwater (was|existed)\b', r'\bsmoke\b.*\bcreation\b',
        r'\bpreserved tablet\b', r'\blawh\b', r'\bqalam\b',
    ],
    1: [
        # Prophets by name (excluding Muhammad ﷺ)
        r'\badam\b', r'\bidris\b', r'\bnuh\b', r'\bnoah\b',
        r'\bhud\b', r'\bpeople of.{0,20}ad\b', r"\'ad\b",
        r'\bsalih\b', r'\bthamud\b', r'\bshe-camel\b',
        r'\bibrahim\b', r'\babraham\b', r'\bismail\b', r'\bishmael\b',
        r'\bishaq\b', r'\bisaac\b', r'\byaqub\b', r'\bjacob\b',
        r'\byusuf\b', r'\bjoseph\b', r'\bayyub\b', r'\bjob\b',
        r'\bshuaib\b', r'\bjethro\b', r'\bmusa\b', r'\bmoises\b', r'\bmoses\b',
        r'\bharun\b', r'\baaron\b', r'\bdawud\b', r'\bdavid\b',
        r'\bsulaiman\b', r'\bsolomon\b', r'\byunus\b', r'\bjonah\b',
        r'\bzakariyya\b', r'\byahya\b', r'\bjohn\b.*\bbaptist\b',
        r'\bisa\b', r'\bjesus\b', r'\bchrist\b',
        r'\bpharaoh\b', r'\bfiraun\b', r'\bexodus\b',
        r'\bpeople of lut\b', r'\blut\b', r'\blot\b',
        r'\bpeople of.{0,20}madyan\b', r'\bmidian\b',
        r'\bpeople of.{0,20}thamud\b',
        r'\bpeople of.{0,20}ad\b',
        r'\bpeople of.{0,20}nuh\b',
        r'\bpeople of.{0,20}ibrahim\b',
        r'\bgoliath\b', r'\bjalut\b',
        r'\bsamuel\b', r'\bshammil\b',
        r'\belijah\b', r'\bilyas\b',
        r'\belisha\b', r'\bal-yasa\b',
        r'\bezekiel\b', r'\bhizqeel\b',
        r'\bdaniel\b', r'\buzair\b', r'\bezra\b',
        r'\bisaiah\b', r'\bjeremiah\b',
    ],
    2: [
        # Pre-Islamic Arabia and world context
        r'\bquraish\b', r'\bquraysh\b', r'\bjahiliyyah\b', r'\bpre.?islamic\b',
        r'\barabia\b', r'\barab tribe\b', r'\bbanu\b.*\btribe\b',
        r'\bkabah\b', r'\bkaba\b', r"\bka'bah\b", r"\bka'ba\b",
        r'\babrahah\b', r'\belephant\b.*\bkabah\b',
        r'\bkhadijah\b', r'\bwaraqah\b',
        r'\brome\b', r'\bbyzantine\b', r'\bpersia\b', r'\bsassan\b',
        r'\bindia\b.*\bcaste\b', r'\bbuddhism\b', r'\bhinduism\b',
        r'\bchristianity\b.*\barabia\b', r'\bjudaism\b.*\barabia\b',
        r'\bhilf al-fudul\b', r'\bbahira\b',
        r'\blineage\b.*\bprophet\b', r'\bancestry\b.*\bprophet\b',
        r'\bzamzam\b', r'\bhajj\b.*\bpre.?islam\b',
        r'\bseekers of truth\b', r'\bhanif\b',
    ],
    3: [
        # Seerah — life of Prophet Muhammad ﷺ
        r'\bprophet muhammad\b', r'\bprophet\s+\(pbuh\)\b', r'\bprophet\s+\(saw\)\b',
        r'\bmessenger of allah\b', r'\brasulullah\b',
        r'\bhira\b', r'\bcave of hira\b', r'\bfirst revelation\b',
        r'\bhijra\b', r'\bhijrah\b', r'\bmigration to madinah\b',
        r'\bbattle of badr\b', r'\bbattle of uhud\b', r'\bbattle of\b',
        r'\bghazwa\b', r'\bexpedition of\b',
        r'\bmadinah\b', r'\bmedina\b',
        r'\bpledge of aqabah\b', r'\baqabah\b',
        r'\bta.?if\b',
        r'\bisra wal miraj\b', r'\bisra\b.*\bmiraj\b', r'\bnight journey\b',
        r'\bconquest of makkah\b', r'\bfath makkah\b',
        r'\bfarewell sermon\b', r'\bhajjat al-wada\b',
        r'\bprophet.{0,20}death\b', r'\bprophet.{0,20}passed away\b',
        r'\bprophet.{0,20}born\b', r'\bbirth of.{0,20}prophet\b',
        r'\babyssinia\b', r'\bethiopia\b.*\bislam\b',
        r'\bbilal\b', r'\bhamza\b.*\bislam\b', r'\bumar\b.*\bembrac\b',
    ],
    4: [
        # Sahaabah
        r'\bsahabi\b', r'\bsahabah\b', r'\bcompanion[s]?\b.*\bprophet\b',
        r'\babu bakr\b', r'\bumar ibn\b', r'\buthman\b', r'\bali ibn\b',
        r'\bkhalid ibn walid\b', r'\bsaad ibn\b', r'\btalha\b', r'\bzubayr\b',
        r'\babdullah ibn\b', r'\banas ibn\b', r'\babu hurairah\b',
        r'\bmuadh ibn\b', r'\bsalman al-farisi\b', r'\bbilal ibn\b',
        r'\bkhadijah bint\b', r'\baisha\b', r'\bfatimah\b',
    ],
    5: [
        # Post-Islam
        r'\bumayyad\b', r'\babbasid\b', r'\bothoman\b', r'\bottoman\b',
        r'\bkhilafah\b', r'\bcaliphate\b', r'\bkhalifa\b', r'\bcaliph\b',
        r'\btariq ibn ziyad\b', r'\bislamic spain\b', r'\bal-andalus\b',
        r'\bkarbala\b', r'\bmuawiya\b', r'\byazid\b',
        r'\bislamic empire\b', r'\bislamic conquest\b',
    ],
}

def load_world(world_id):
    path = DATA_DIR / f'world{world_id}.json'
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_world(world_id, questions):
    path = DATA_DIR / f'world{world_id}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def detect_world(q):
    """Return the most likely world for a question based on keyword matching."""
    text = (q.get('q', '') + ' ' + ' '.join(q.get('opts', []))).lower()
    
    scores = {w: 0 for w in WORLDS}
    for world_id, patterns in WORLD_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores[world_id] += 1
    
    best_world = max(scores, key=scores.get)
    best_score = scores[best_world]
    
    return best_world, best_score, scores

# Load all worlds
all_worlds = {i: load_world(i) for i in range(6)}

# Count total
total = sum(len(v) for v in all_worlds.values())
print(f"Total questions across all worlds: {total}")
for i, qs in all_worlds.items():
    print(f"  World {i} ({WORLDS[i]}): {len(qs)} questions")

print("\n--- Auditing for misplaced questions ---\n")

# Find misplaced questions
misplaced = []
for world_id, questions in all_worlds.items():
    for q in questions:
        detected_world, score, scores = detect_world(q)
        if detected_world != world_id and score >= 1:
            misplaced.append({
                'q': q,
                'current_world': world_id,
                'detected_world': detected_world,
                'score': score,
                'text_preview': q.get('q', '')[:80]
            })

print(f"Found {len(misplaced)} potentially misplaced questions")
print("\nTop misplacements:")
# Group by current -> detected
from collections import defaultdict
groups = defaultdict(list)
for m in misplaced:
    key = f"World {m['current_world']} -> World {m['detected_world']}"
    groups[key].append(m)

for key, items in sorted(groups.items(), key=lambda x: -len(x[1])):
    print(f"\n  {key}: {len(items)} questions")
    for item in items[:5]:
        print(f"    - [{item['score']} match] {item['text_preview']}")
    if len(items) > 5:
        print(f"    ... and {len(items)-5} more")

# Save misplacement report
with open('/tmp/misplacement_report.json', 'w') as f:
    json.dump(misplaced, f, ensure_ascii=False, indent=2)
print(f"\nFull report saved to /tmp/misplacement_report.json")
