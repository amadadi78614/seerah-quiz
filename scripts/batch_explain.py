"""
batch_explain.py
================
Generates explanations for all questions across all world JSON files.
Saves progress every 50 questions so it can be resumed if interrupted.
"""
import json, time, re, sys
from pathlib import Path
from openai import OpenAI

client = OpenAI()
DATA = Path('/home/ubuntu/seerah-quiz/data')

def generate_explanation(q_text, opts, correct_idx, topic, source):
    correct_answer = opts[correct_idx] if correct_idx < len(opts) else opts[0]
    correct_clean = re.sub(r'^[A-Da-d][\.\)]\s*', '', correct_answer).strip()
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": (
                "You are a knowledgeable Islamic studies teacher. "
                "When a student answers a quiz question incorrectly, provide a brief, clear, "
                "accurate explanation (1-2 sentences) of why the correct answer is correct. "
                "Be factual and educational. Do not start with 'The correct answer is'. Keep under 60 words."
            )},
            {"role": "user", "content": (
                f"Topic: {topic}\nSource: {source}\n"
                f"Question: {q_text}\nCorrect answer: {correct_clean}\n\n"
                "Write a brief educational explanation (1-2 sentences, max 60 words)."
            )}
        ],
        max_tokens=120,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

worlds = [0, 1, 2, 3, 4, 5]
if len(sys.argv) > 1:
    worlds = [int(x) for x in sys.argv[1:]]

for world_id in worlds:
    filepath = DATA / f'world{world_id}.json'
    with open(filepath, encoding='utf-8') as f:
        questions = json.load(f)

    needs = [(i, q) for i, q in enumerate(questions) if not q.get('explanation')]
    print(f"\nWorld {world_id}: {len(needs)}/{len(questions)} need explanations")

    errors = 0
    for count, (i, q) in enumerate(needs):
        try:
            exp = generate_explanation(
                q['q'], q['opts'], q['correct'],
                q.get('topic', ''), q.get('source', 'Islamic Studies')
            )
            questions[i]['explanation'] = exp
            errors = 0
            time.sleep(0.12)
        except Exception as e:
            print(f"  Error [{i}]: {e}")
            questions[i]['explanation'] = ""
            errors += 1
            time.sleep(3)
            if errors > 5:
                print("  Too many errors, saving and moving on.")
                break

        if (count + 1) % 50 == 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            done = sum(1 for q in questions if q.get('explanation'))
            print(f"  [{count+1}/{len(needs)}] saved — {done}/{len(questions)} total done")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    done = sum(1 for q in questions if q.get('explanation'))
    print(f"  World {world_id} complete: {done}/{len(questions)} have explanations")

print("\nAll done!")
