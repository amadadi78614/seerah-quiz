"""
generate_explanations.py
========================
Generates 1-2 sentence explanations for quiz questions using OpenAI API.
Usage: python3 generate_explanations.py <world_json_file>
Adds 'explanation' field to each question that doesn't already have one.
"""

import json, os, sys, time, re
from pathlib import Path
from openai import OpenAI

client = OpenAI()  # uses OPENAI_API_KEY from environment

def generate_explanation(q_text, opts, correct_idx, topic, source):
    correct_answer = opts[correct_idx] if correct_idx < len(opts) else opts[0]
    
    # Strip option letters if present
    correct_clean = re.sub(r'^[A-Da-d][\.\)]\s*', '', correct_answer).strip()
    
    system_prompt = (
        "You are a knowledgeable Islamic studies teacher. "
        "When a student answers a quiz question incorrectly, you provide a brief, clear, "
        "accurate explanation (1-2 sentences) of why the correct answer is correct. "
        "Be factual, educational, and reference the Islamic source when relevant. "
        "Do not start with 'The correct answer is' — instead explain the concept or fact directly. "
        "Keep it under 60 words."
    )
    
    user_prompt = (
        f"Topic: {topic}\n"
        f"Source: {source}\n"
        f"Question: {q_text}\n"
        f"Correct answer: {correct_clean}\n\n"
        "Write a brief educational explanation (1-2 sentences, max 60 words) "
        "that helps the student understand why this is correct."
    )
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=120,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def process_world_file(json_path):
    json_path = Path(json_path)
    print(f"\nProcessing {json_path.name}...")
    
    with open(json_path, encoding='utf-8') as f:
        questions = json.load(f)
    
    total = len(questions)
    needs_explanation = [q for q in questions if not q.get('explanation')]
    print(f"  Total: {total} | Need explanations: {len(needs_explanation)}")
    
    if not needs_explanation:
        print("  All questions already have explanations. Skipping.")
        return
    
    errors = 0
    for i, q in enumerate(needs_explanation):
        try:
            explanation = generate_explanation(
                q['q'], q['opts'], q['correct'],
                q.get('topic', ''), q.get('source', 'Islamic Studies')
            )
            q['explanation'] = explanation
            
            if (i + 1) % 50 == 0:
                # Save progress checkpoint
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, ensure_ascii=False, indent=2)
                print(f"  [{i+1}/{len(needs_explanation)}] checkpoint saved...")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  Error on question {i+1}: {e}")
            q['explanation'] = ""
            errors += 1
            if errors > 10:
                print("  Too many errors, saving progress and stopping.")
                break
            time.sleep(2)
    
    # Final save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    
    done = sum(1 for q in questions if q.get('explanation'))
    print(f"  Done. {done}/{total} questions now have explanations.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 generate_explanations.py <world_json_file>")
        sys.exit(1)
    process_world_file(sys.argv[1])
