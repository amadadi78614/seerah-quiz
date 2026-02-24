#!/usr/bin/env python3
"""
Fix world assignments strictly by the topic field prefix.
Each question's topic field starts with the world name it belongs to.
"""
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path('/home/ubuntu/seerah-quiz/data')

# Map topic prefixes to world IDs
TOPIC_TO_WORLD = {
    'Beginning of Time': 0,
    'The Prophets': 1,
    'Pre-Islam': 2,
    'Seerah': 3,
    'The Sahaabah': 4,
    'Post-Islam': 5,
    # Also handle old-style topic names
    'Arabia': 2,
    'Global': 2,
    'Knowing the Prophets': 1,
    'Early Islam': 3,
    'Revelation': 3,
    'Prophets': 1,
}

def get_target_world(q):
    topic = q.get('topic', '')
    for prefix, world_id in TOPIC_TO_WORLD.items():
        if topic.startswith(prefix):
            return world_id
    return None  # Unknown — keep in current world

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

# Reclassify by topic prefix
print("\nReclassifying by topic prefix...")
new_worlds = {i: [] for i in range(6)}
moved = defaultdict(int)
stayed = 0
unknown = 0

for world_id, questions in all_worlds.items():
    for q in questions:
        target = get_target_world(q)
        if target is None:
            # No clear topic prefix — keep in current world
            new_worlds[world_id].append(q)
            unknown += 1
        elif target != world_id:
            new_worlds[target].append(q)
            moved[(world_id, target)] += 1
        else:
            new_worlds[world_id].append(q)
            stayed += 1

print(f"\nResults:")
print(f"  Questions that stayed: {stayed}")
print(f"  Questions with unknown topic (kept in place): {unknown}")
print(f"  Questions moved:")
for (src, dst), count in sorted(moved.items()):
    print(f"    World {src} -> World {dst}: {count}")

print(f"\nNew world sizes:")
for i, qs in new_worlds.items():
    print(f"  World {i}: {len(qs)} questions")

# Verify World 0 topics
print(f"\nWorld 0 topics after fix:")
from collections import Counter
topics = Counter(q.get('topic','') for q in new_worlds[0])
for t, c in sorted(topics.items(), key=lambda x: -x[1]):
    print(f"  {c:3d}  {t}")

# Save
print("\nSaving updated worlds...")
for i, qs in new_worlds.items():
    save_world(i, qs)
    print(f"  Saved world{i}.json ({len(qs)} questions)")

print("\nDone!")
