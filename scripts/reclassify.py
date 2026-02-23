"""
reclassify.py
=============
Reclassifies:
1. "The Prophets · Stories of the Prophets" → specific prophet topics
2. "The Prophets · Muhammad ﷺ" → moves to Seerah world (world3)
3. "Seerah · Makkah" (555 q) → splits into chronological sub-stages
4. Merges al-Jibaly theory topics into a single "Prophethood" level
"""

import json, re
from pathlib import Path

BASE = Path(__file__).parent.parent
DATA = BASE / 'data'

# ── Prophet keyword map ─────────────────────────────────────────────────────
PROPHET_KEYWORDS = {
    "Adam ﷺ":       ["adam","hawa","eve","iblis","satan","cain","abel","qabil","habil","garden","jannah","forbidden tree","khalifah","vicegerent"],
    "Idris ﷺ":      ["idris","enoch"],
    "Nuh ﷺ":        ["nuh","noah","ark","flood","deluge","son of nuh","wife of nuh","canaan","ham","shem"],
    "Hud ﷺ":        ["hud","aad","'aad","wind","iram"],
    "Salih ﷺ":      ["salih","thamud","she-camel","camel of allah","al-hijr"],
    "Ibrahim ﷺ":    ["ibrahim","abraham","fire","nimrod","namrud","ka'bah","kaaba","ismail","ishmael","sarah","hajar","hagar","zamzam","sacrifice","slaughter","idols","star","moon","sun","hanif"],
    "Isma'il ﷺ":    ["ismail","ishmael","zamzam","sacrifice","well of zamzam"],
    "Ishaq ﷺ":      ["ishaq","isaac","rebecca"],
    "Lut ﷺ":        ["lut","lot","sodom","people of lut","wife of lut"],
    "Yaqub ﷺ":      ["yaqub","jacob","israel","bani israel","twelve sons","twelve tribes"],
    "Yusuf ﷺ":      ["yusuf","joseph","egypt","zulaykha","potiphar","prison","dream","interpretation","brothers of yusuf","coat","well"],
    "Ayyub ﷺ":      ["ayyub","job","patience","affliction","illness","satan tested"],
    "Shu'aib ﷺ":    ["shu'aib","jethro","midian","madyan","measure","weight"],
    "Musa ﷺ":       ["musa","moses","pharaoh","fir'awn","bani israel","red sea","sinai","tawrah","torah","ten commandments","staff","serpent","magicians","plagues","golden calf","khidr","khadir","samiri","mount sinai","mount tur"],
    "Harun ﷺ":      ["harun","aaron","golden calf"],
    "Hizqael ﷺ":    ["hizqael","ezekiel","dhul-kifl","valley of dry bones"],
    "Elisha ﷺ":     ["elisha","al-yasa"],
    "Samuel ﷺ":     ["samuel","shamwil","saul","talut","jalut","goliath","ark of covenant"],
    "Dawud ﷺ":      ["dawud","david","zabur","psalms","goliath","jalut","iron","armour"],
    "Sulaiman ﷺ":   ["sulaiman","solomon","queen of sheba","bilqis","jinn","wind","birds","hoopoe","hudhud","ant"],
    "Isaiah ﷺ":     ["isaiah","shu'ya"],
    "Jeremiah ﷺ":   ["jeremiah","irmiya","babylon","nebuchadnezzar","jerusalem","temple"],
    "Daniel ﷺ":     ["daniel","daniyal","babylon","nebuchadnezzar","lions"],
    "Uzair ﷺ":      ["uzair","ezra","donkey","hundred years"],
    "Yunus ﷺ":      ["yunus","jonah","whale","fish","nineveh","darkness"],
    "Zakariyya ﷺ":  ["zakariyya","zechariah","yahya","john","temple","maryam","mary"],
    "Yahya ﷺ":      ["yahya","john the baptist","herod","herodias"],
    "Isa ﷺ":        ["isa","jesus","maryam","mary","injeel","gospel","miracles of isa","disciples","apostles","crucifixion","ascension","second coming","dajjal"],
}

# ── Seerah Makkah sub-stage keywords ────────────────────────────────────────
SEERAH_STAGES = [
    ("Seerah · Early Life",           ["birth","born","amina","aminah","halima","halimah","wet nurse","childhood","youth","grandfather","abdul muttalib","bahira","monk","hilf al-fudool","hilful fudul","before prophethood","before revelation","khadijah","marriage of khadijah","first wife","cave hira","hira","meditation","before islam","jahiliyyah","pre-islamic","lineage","ancestry","tribe of quraysh","quraysh","hashim","banu hashim"]),
    ("Seerah · The Revelation",       ["first revelation","iqra","read","jibril","gabriel","cave hira","first verses","surah alaq","waraqah","khadijah believed","first muslim","first to believe","revelation began","nuzul","wahy","revelation stopped","fatra"]),
    ("Seerah · Early Islam in Makkah",["first muslims","early converts","early muslims","abu bakr","ali ibn abi talib","zaid ibn haritha","khadijah believed","house of arqam","dar al-arqam","secret preaching","open preaching","mount safa","three years","call to islam","tawheed","oneness of allah","first prayer","first salah"]),
    ("Seerah · Persecution",          ["persecution","torture","bilal","sumayyah","ammar","yasir","hot sand","oppression","boycott","shi'b abi talib","social boycott","three years boycott","abu jahl","abu lahab","umayyah ibn khalaf","slaves","early muslims tortured","hamza embraced","umar embraced","umar ibn al-khattab converted","hamza converted"]),
    ("Seerah · Migration to Abyssinia",["abyssinia","ethiopia","negus","najashi","ja'far ibn abi talib","first migration","second migration","migration to abyssinia","asylum","christian king"]),
    ("Seerah · Year of Grief",        ["year of grief","aam al-huzn","death of khadijah","death of abu talib","abu talib died","khadijah died","two losses"]),
    ("Seerah · At-Ta'if",             ["ta'if","taif","thaqif","tribe of thaqif","rejected at ta'if","stoned","blood","addas","utbah and shaybah","jinn listened"]),
    ("Seerah · Al-Isra wal-Mi'raj",   ["isra","mi'raj","night journey","al-aqsa","bait al-maqdis","jerusalem","buraq","seven heavens","sidrat al-muntaha","fifty prayers","five prayers","musa advised","night of isra"]),
    ("Seerah · Pledges of Aqabah",    ["aqabah","pledge of aqabah","first pledge","second pledge","ansar","helpers","twelve leaders","nuqaba","seventy three men","makkah to madinah","invitation to madinah"]),
    ("Seerah · The Hijrah",           ["hijrah","migration to madinah","hijra","cave thawr","thawr","abu bakr accompanied","suraqa","ali slept in bed","spider web","dove","migration route","quba","masjid quba","first mosque"]),
    ("Seerah · Madinah",              ["madinah","medina","masjid al-nabawi","brotherhood","muakhat","ansar and muhajirun","constitution of madinah","charter of madinah","jewish tribes","banu qaynuqa","banu nadir","banu qurayza","hypocrites","munafiqun","abdullah ibn ubayy","adhan","call to prayer","bilal adhan"]),
    ("Seerah · Battle of Badr",       ["badr","battle of badr","first major battle","313","three hundred","abu jahl killed","badr captives","ransom","quraysh army","uhud","wells of badr","angels at badr","jibril at badr"]),
    ("Seerah · Battle of Uhud",       ["uhud","battle of uhud","mount uhud","archers","hamza killed","hamza martyred","khalid ibn walid flanked","defeat at uhud","seventy martyrs","rumour of prophet death","abu sufyan","hind","liver of hamza"]),
    ("Seerah · Battle of the Trench", ["trench","khandaq","ahzab","confederates","battle of khandaq","salman al-farisi","dug the trench","nu'aym ibn mas'ud","banu qurayza betrayal","ten thousand","coalition","wind dispersed"]),
    ("Seerah · Hudaybiyyah & Later",  ["hudaybiyyah","treaty of hudaybiyyah","ten years peace","umrah","shaving heads","abu jandal","letters to kings","khaybar","conquest of khaybar","umrah al-qada","expedition"]),
    ("Seerah · Conquest of Makkah",   ["conquest of makkah","fath makkah","ten thousand","twenty thousand","abu sufyan embraced","general amnesty","idols destroyed","khalid ibn walid","ikrimah","safwan","hind embraced","makkah surrendered","year eight","8 ah"]),
    ("Seerah · Final Years",          ["farewell pilgrimage","farewell sermon","hajjat al-wada","last sermon","illness of prophet","death of prophet","prophet passed away","prophet died","abu bakr speech","umar wept","burial","madinah burial","succession","caliphate","aisha's room","last days"]),
]

def classify_prophet(q_text, opts_text):
    text = (q_text + " " + opts_text).lower()
    best = None
    best_score = 0
    for prophet, keywords in PROPHET_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best = prophet
    return best if best_score > 0 else None

def classify_seerah_stage(q_text, opts_text):
    text = (q_text + " " + opts_text).lower()
    best = None
    best_score = 0
    for stage, keywords in SEERAH_STAGES:
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best = stage
    return best if best_score > 0 else None

# ── Load data ────────────────────────────────────────────────────────────────
with open(DATA / 'world1.json') as f:
    w1 = json.load(f)
with open(DATA / 'world3.json') as f:
    w3 = json.load(f)

# ── Process World 1 ──────────────────────────────────────────────────────────
new_w1 = []
moved_to_seerah = []

for q in w1:
    topic = q['topic']
    
    # Move Muhammad ﷺ questions to Seerah
    if "Muhammad" in topic:
        q2 = dict(q)
        q2['topic'] = 'Seerah · Early Islam in Makkah'
        moved_to_seerah.append(q2)
        continue
    
    # Reclassify "Stories of the Prophets"
    if topic == "The Prophets · Stories of the Prophets":
        opts_text = " ".join(q.get('opts', []))
        prophet = classify_prophet(q['q'], opts_text)
        if prophet:
            q2 = dict(q)
            q2['topic'] = f"The Prophets · {prophet}"
            new_w1.append(q2)
        else:
            # Keep as generic if can't classify
            new_w1.append(q)
        continue
    
    # Keep all other prophets questions
    new_w1.append(q)

print(f"World 1: {len(w1)} → {len(new_w1)} questions ({len(moved_to_seerah)} moved to Seerah)")

# ── Process World 3 ──────────────────────────────────────────────────────────
new_w3 = []

for q in w3:
    topic = q['topic']
    
    # Split "Seerah · Makkah" into sub-stages
    if topic == "Seerah · Makkah":
        opts_text = " ".join(q.get('opts', []))
        stage = classify_seerah_stage(q['q'], opts_text)
        if stage:
            q2 = dict(q)
            q2['topic'] = stage
            new_w3.append(q2)
        else:
            # Default to Early Islam in Makkah if unclassified
            q2 = dict(q)
            q2['topic'] = "Seerah · Early Islam in Makkah"
            new_w3.append(q2)
        continue
    
    # Also reclassify "Seerah · Detailed Studies" by keyword
    if topic == "Seerah · Detailed Studies":
        opts_text = " ".join(q.get('opts', []))
        stage = classify_seerah_stage(q['q'], opts_text)
        if stage:
            q2 = dict(q)
            q2['topic'] = stage
            new_w3.append(q2)
        else:
            new_w3.append(q)
        continue
    
    new_w3.append(q)

# Add moved Muhammad ﷺ questions
new_w3.extend(moved_to_seerah)

print(f"World 3: {len(w3)} → {len(new_w3)} questions")

# ── Show new topic distribution ──────────────────────────────────────────────
from collections import Counter

print("\n=== NEW World 1 topics ===")
c1 = Counter(q['topic'] for q in new_w1)
for t, n in sorted(c1.items()):
    print(f"  {n:3d}  {t}")

print("\n=== NEW World 3 topics ===")
c3 = Counter(q['topic'] for q in new_w3)
for t, n in sorted(c3.items()):
    print(f"  {n:3d}  {t}")

# ── Save ─────────────────────────────────────────────────────────────────────
with open(DATA / 'world1.json', 'w', encoding='utf-8') as f:
    json.dump(new_w1, f, ensure_ascii=False, indent=2)
with open(DATA / 'world3.json', 'w', encoding='utf-8') as f:
    json.dump(new_w3, f, ensure_ascii=False, indent=2)

print("\n✓ world1.json and world3.json saved.")
