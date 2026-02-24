#!/usr/bin/env python3
"""
Fix misplaced questions by moving them to the correct world based on topic content.
Uses a comprehensive keyword matching system with confidence scoring.
"""
import json
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path('/home/ubuntu/seerah-quiz/data')

# ── World topic definitions ──────────────────────────────────────────────────
# World 0: Beginning of Time — ONLY creation topics
# World 1: The Prophets — Adam ﷺ through Isa ﷺ (stories, miracles, peoples)
# World 2: Pre-Islam — Arabia, Rome, Persia, India, world before Islam
# World 3: Seerah — Life of Prophet Muhammad ﷺ
# World 4: The Sahaabah — Companions of the Prophet ﷺ
# World 5: Post-Islam — Caliphs, empires, Islamic history after the Prophet

# High-confidence patterns (weight 3) — very specific to one world
HIGH_CONF = {
    0: [
        r'\bpreserved tablet\b', r'\blawh al-mahfuz\b', r'\bthe pen\b.*\bcreated\b',
        r'\bqalam\b.*\bfirst\b', r'\bfirst thing.*created\b', r'\bcreated.*first\b',
        r'\bthrone of allah\b', r'\barsh\b', r'\bkursi\b',
        r'\bseven heavens\b', r'\bseven skies\b', r'\bfirmaments\b',
        r'\bcreation of (the )?earth\b', r'\bearth was created\b',
        r'\bwater existed\b', r'\bbefore creation\b',
        r'\bangels (were|are) created\b', r'\bcreated.*angels\b',
        r'\biblis refused\b', r'\biblis.*prostrate\b', r'\brefused to prostrate\b',
    ],
    1: [
        r'\bpeople of.{0,15}ad\b', r"people of 'ad\b", r'\bpeople of.{0,15}thamud\b',
        r'\bpeople of.{0,15}nuh\b', r'\bpeople of.{0,15}lut\b',
        r'\bpeople of.{0,15}madyan\b', r'\bpeople of.{0,15}ibrahim\b',
        r'\bnuh.{0,20}flood\b', r'\bflood.{0,20}nuh\b', r'\bnoah.{0,20}ark\b',
        r'\bibrahim.{0,20}fire\b', r'\bfire.{0,20}ibrahim\b',
        r'\byusuf.{0,20}egypt\b', r'\byusuf.{0,20}prison\b',
        r'\bmusa.{0,20}pharaoh\b', r'\bpharaoh.{0,20}musa\b',
        r'\bten plagues\b', r'\bparting of the sea\b', r'\bred sea\b.*\bmusa\b',
        r'\bsulaiman.{0,20}jinn\b', r'\bdawud.{0,20}goliath\b',
        r'\bisa.{0,20}miracles\b', r'\bisa.{0,20}born\b',
        r'\bshe.?camel.{0,20}salih\b', r'\bsalih.{0,20}she.?camel\b',
        r'\bthe ark\b.*\bnuh\b', r'\bnuh\b.*\bthe ark\b',
    ],
    3: [
        r'\bcave of hira\b', r'\bhira\b.*\brevelation\b', r'\bfirst revelation\b',
        r'\bprophet.{0,20}born in makkah\b', r'\bbirth of the prophet\b',
        r'\bhijra to madinah\b', r'\bmigration to madinah\b',
        r'\bbattle of badr\b', r'\bbattle of uhud\b', r'\bbattle of khandaq\b',
        r'\bbattle of the trench\b', r'\btrench\b.*\bbattle\b',
        r'\bconquest of makkah\b', r'\bfath makkah\b',
        r'\bfarewell sermon\b', r'\bhajjat al-wada\b',
        r'\bisra wal miraj\b', r'\bnight journey\b.*\bprophet\b',
        r'\bpledge of aqabah\b',
        r'\bprophet.{0,30}passed away\b', r'\bdeath of the prophet\b',
    ],
    4: [
        r'\babu bakr al-siddiq\b', r'\bumar ibn al-khattab\b',
        r'\buthman ibn affan\b', r'\bali ibn abi talib\b',
        r'\bkhalid ibn walid\b', r'\bsaad ibn abi waqqas\b',
        r'\btalha ibn\b', r'\bzubayr ibn\b',
        r'\bsalman al-farisi\b', r'\bbilal ibn rabah\b',
        r'\babu hurairah\b', r'\banas ibn malik\b',
        r'\baisha bint\b', r'\bfatimah bint\b',
        r'\bcompanions of the prophet\b', r'\bsahabah\b',
    ],
    5: [
        r'\bumayyad caliphate\b', r'\babbasid caliphate\b',
        r'\bothoman empire\b', r'\bottoman empire\b',
        r'\btariq ibn ziyad\b', r'\bal-andalus\b', r'\bislamic spain\b',
        r'\bbattle of karbala\b', r'\bkarbala\b.*\bhusayn\b',
        r'\bmuawiya.{0,20}caliph\b', r'\bcaliph muawiya\b',
        r'\byazid ibn muawiya\b',
        r'\babdur rahman.{0,20}spain\b',
        r'\bsalahuddin\b', r'\bsaladin\b',
        r'\bmongol\b.*\binvasion\b', r'\bbaghdad.{0,20}destroyed\b',
    ],
}

# Medium-confidence patterns (weight 2)
MED_CONF = {
    0: [
        r'\bpen\b.*\bwrote\b', r'\bpen\b.*\bdestinies\b',
        r'\bthrone\b.*\bwater\b', r'\bwater\b.*\bthrone\b',
        r'\bangels\b.*\bprostrate\b', r'\bprostrate\b.*\badam\b',
        r'\biblis\b', r'\bshaytan\b.*\brefused\b',
        r'\bjinn\b.*\bcreated\b', r'\bcreated.*\bjinn\b',
        r'\bsmoke\b.*\bheavens\b', r'\bheavens\b.*\bsmoke\b',
    ],
    1: [
        r'\badam\b.*\bparadise\b', r'\badam\b.*\beve\b', r'\badam\b.*\bhawa\b',
        r'\bcain\b', r'\babel\b', r'\bqabil\b', r'\bhabil\b',
        r'\bidris\b', r'\bnuh\b', r'\bhud\b', r'\bsalih\b',
        r'\bibrahim\b', r'\bismail\b', r'\bishaq\b', r'\byaqub\b',
        r'\byusuf\b', r'\bayyub\b', r'\bshuaib\b',
        r'\bmusa\b', r'\bharun\b', r'\bdawud\b', r'\bsulaiman\b',
        r'\byunus\b', r'\bzakariyya\b', r'\byahya\b', r'\bisa\b',
        r'\bpharaoh\b', r'\bfiraun\b',
        r'\blut\b', r'\bsodom\b',
        r'\bgoliath\b', r'\bjalut\b',
        r'\bsamuel\b', r'\bilyas\b', r'\bal-yasa\b',
        r'\bezekiel\b', r'\bdaniel\b', r'\buzair\b',
        r'\bwind\b.*\bpeople\b.*\bad\b', r'\bpeople\b.*\bad\b.*\bwind\b',
        r'\bpeople of.{0,20}hud\b',
    ],
    2: [
        r'\bquraish\b', r'\bquraysh\b', r'\bjahiliyyah\b',
        r'\barabia\b', r'\barab\b.*\btribe\b',
        r'\bkabah\b', r"\bka'bah\b", r'\babrahah\b',
        r'\bkhadijah\b', r'\bwaraqah\b', r'\bbahira\b',
        r'\brome\b', r'\bbyzantine\b', r'\bpersia\b',
        r'\bhanif\b', r'\bseekers of truth\b',
        r'\bzamzam\b', r'\bhilf al-fudul\b',
    ],
    3: [
        r'\bprophet\b.*\bmakkah\b', r'\bprophet\b.*\bmadinah\b',
        r'\bprophet\b.*\bhijra\b', r'\bprophet\b.*\bbattle\b',
        r'\bprophet\b.*\bcompanions\b',
        r'\brasulullah\b', r'\bmessenger of allah\b',
        r'\babyssinia\b', r'\bnegus\b',
        r'\bta.?if\b.*\bprophet\b', r'\bprophet\b.*\bta.?if\b',
        r'\byear of grief\b', r'\bam al-huzn\b',
        r'\bprophet\b.*\bpersecution\b', r'\bpersecution\b.*\bprophet\b',
        r'\bprophet\b.*\bbilal\b', r'\bprophet\b.*\bhamza\b',
    ],
    4: [
        r'\bsahabi\b', r'\bcompanion\b.*\bislam\b',
        r'\babu bakr\b', r'\bumar\b.*\bcompanion\b',
        r'\buthman\b.*\bcaliph\b', r'\bali\b.*\bcaliph\b',
        r'\bkhalid\b.*\bwalid\b', r'\bsaad\b.*\bwaqqas\b',
        r'\btalha\b.*\bzubayr\b',
        r'\bmen around the prophet\b',
    ],
    5: [
        r'\bumayyad\b', r'\babbasid\b', r'\bothoman\b', r'\bottoman\b',
        r'\bcaliphate\b', r'\bcaliph\b.*\bafter\b',
        r'\bmuawiya\b', r'\byazid\b',
        r'\bislamic empire\b', r'\bislamic conquest\b',
        r'\bkarbala\b', r'\btariq\b.*\bziyad\b',
    ],
}

# Low-confidence patterns (weight 1)
LOW_CONF = {
    0: [
        r'\bpen\b', r'\btablet\b', r'\bthrone\b', r'\bangel\b',
        r'\bjinn\b', r'\biblis\b', r'\bcreation\b.*\bday\b',
    ],
    1: [
        r'\bprophet\b.*\bstory\b', r'\bstory of\b.*\bprophet\b',
        r'\bpeople of\b', r'\bmiracle\b.*\bprophet\b',
        r'\bpunishment\b.*\bpeople\b', r'\bdivine punishment\b',
    ],
    2: [
        r'\barabia\b', r'\barab\b', r'\btribe\b.*\barab\b',
        r'\bpre.?islam\b', r'\bbefore islam\b',
    ],
    3: [
        r'\bprophet\b', r'\bprophet muhammad\b', r'\bpbuh\b', r'\bsaw\b',
        r'\bislam\b.*\bspread\b', r'\bislam\b.*\bmakkah\b',
    ],
    4: [
        r'\bcompanion\b', r'\bsahabi\b', r'\bsahabah\b',
    ],
    5: [
        r'\bcaliph\b', r'\bkhilafah\b', r'\bislamic history\b',
        r'\bempire\b.*\bislam\b',
    ],
}

def score_question(q, world_id):
    text = (q.get('q', '') + ' ' + ' '.join(q.get('opts', []))).lower()
    score = 0
    for pattern in HIGH_CONF.get(world_id, []):
        if re.search(pattern, text, re.IGNORECASE):
            score += 3
    for pattern in MED_CONF.get(world_id, []):
        if re.search(pattern, text, re.IGNORECASE):
            score += 2
    for pattern in LOW_CONF.get(world_id, []):
        if re.search(pattern, text, re.IGNORECASE):
            score += 1
    return score

def best_world(q):
    scores = {w: score_question(q, w) for w in range(6)}
    best = max(scores, key=scores.get)
    return best, scores[best], scores

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

# Load all worlds
print("Loading all worlds...")
all_worlds = {i: load_world(i) for i in range(6)}
for i, qs in all_worlds.items():
    print(f"  World {i}: {len(qs)} questions")

# Reclassify
print("\nReclassifying questions...")
new_worlds = {i: [] for i in range(6)}
moved = defaultdict(int)
stayed = 0

for world_id, questions in all_worlds.items():
    for q in questions:
        target, score, scores = best_world(q)
        
        # Only move if we have a strong signal (score >= 2) AND it's different from current
        # AND the target world scores significantly higher than current world
        current_score = scores[world_id]
        
        if target != world_id and score >= 2 and score > current_score:
            new_worlds[target].append(q)
            moved[(world_id, target)] += 1
        else:
            new_worlds[world_id].append(q)
            stayed += 1

print(f"\nResults:")
print(f"  Questions that stayed: {stayed}")
print(f"  Questions moved:")
for (src, dst), count in sorted(moved.items()):
    print(f"    World {src} -> World {dst}: {count}")

print(f"\nNew world sizes:")
for i, qs in new_worlds.items():
    print(f"  World {i}: {len(qs)} questions")

# Save
print("\nSaving updated worlds...")
for i, qs in new_worlds.items():
    save_world(i, qs)
    print(f"  Saved world{i}.json ({len(qs)} questions)")

print("\nDone! All worlds updated.")
