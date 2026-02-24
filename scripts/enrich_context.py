#!/usr/bin/env python3
"""
Enrich context-less questions with AI-generated preamble text.
For hadith references: adds the actual hadith text + narrator.
For context-less narrative questions: adds a brief context sentence.
"""
import json, re, os, time
from pathlib import Path
from openai import OpenAI

DATA_DIR = Path('/home/ubuntu/seerah-quiz/data')
client = OpenAI()

SYSTEM_PROMPT = """You are an Islamic scholar assistant helping to enrich quiz questions.
A quiz question is missing its context — it references "this hadith", "this verse", "this incident" 
or asks about something without explaining what it is.

Your job is to:
1. Identify what the question is referring to based on the question text, answer options, and topic.
2. Generate a SHORT context preamble (1-3 sentences max) to show ABOVE the question.
3. For hadith references: quote the actual hadith text in English with narrator and source.
4. For Quranic verse references: quote the ayah with Surah name and ayah number.
5. For narrative questions ("When did the punishment come?"): write a brief context like 
   "Regarding the punishment of the people of Thamud after they slaughtered the she-camel of Salih ﷺ..."

Rules:
- Keep preambles SHORT (1-3 sentences maximum)
- Be accurate — only quote hadith/ayah if you are confident
- For hadith: format as: "The Prophet ﷺ said: '[hadith text]' (Narrated by [narrator] — [collection, hadith no.])"
- For ayah: format as: "Allah says in the Quran: '[translation]' (Surah [name], [number]:[number])"
- For narrative context: start with "Context:" and give 1-2 sentences of background
- If you cannot identify the specific reference with confidence, write a general context sentence instead

Return ONLY the preamble text, nothing else."""

def generate_context(q_data):
    question = q_data['q']
    topic = q_data['topic']
    opts = q_data['opts']
    correct_idx = q_data['correct']
    correct_ans = opts[correct_idx] if correct_idx < len(opts) else ''
    
    user_msg = f"""Topic: {topic}
Question: {question}
Options: {' | '.join(opts)}
Correct answer: {correct_ans}

Generate a short context preamble for this question."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=200,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  Error: {e}")
        return None

# Load the context-less questions
with open('/tmp/contextless_questions.json') as f:
    contextless = json.load(f)

print(f"Processing {len(contextless)} context-less questions...")

# Generate context for each
results = []
for i, q_data in enumerate(contextless):
    print(f"  [{i+1}/{len(contextless)}] {q_data['topic'][:50]} | {q_data['q'][:60]}...")
    context = generate_context(q_data)
    if context:
        results.append({
            'world': q_data['world'],
            'idx': q_data['idx'],
            'context': context,
            'q': q_data['q']
        })
        print(f"    → {context[:80]}...")
    else:
        print(f"    → FAILED")
    time.sleep(0.3)

print(f"\nGenerated context for {len(results)}/{len(contextless)} questions")

# Save results
with open('/tmp/context_results.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Saved to /tmp/context_results.json")

# Now apply to world JSON files
print("\nApplying context to world JSON files...")
for world_id in range(6):
    path = DATA_DIR / f'world{world_id}.json'
    if not path.exists():
        continue
    with open(path) as f:
        qs = json.load(f)
    
    updated = 0
    for result in results:
        if result['world'] == world_id:
            idx = result['idx']
            if idx < len(qs) and qs[idx]['q'] == result['q']:
                qs[idx]['context'] = result['context']
                updated += 1
    
    if updated > 0:
        with open(path, 'w') as f:
            json.dump(qs, f, ensure_ascii=False, indent=2)
        print(f"  World {world_id}: updated {updated} questions")

print("\nDone!")
