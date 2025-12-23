#!/usr/bin/env python3
"""LLM Annotation using Groq (Llama 3.3 70B - free tier)"""
import csv
import os
import requests
import time

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not set")
    exit(1)

ROLE_TAXONOMY = """
Choose ONE of these roles:
Query, Command, Entity, Repository, Service, Factory, Builder, Validator,
Transformer, Adapter, Controller, Presenter, View, Configuration, Constant,
Utility, Test, ImpureFunction, EventHandler
"""

def annotate(name, file_path, repo):
    prompt = f"""Classify this code element's SEMANTIC ROLE.

Element: {name}
Path: ...{file_path[-50:]}
Repo: {repo}

{ROLE_TAXONOMY}

1. Name suggests: 
2. Path suggests:
3. Role:

Just the role name on last line."""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 100
        },
        timeout=30
    )
    
    if response.status_code == 200:
        text = response.json()['choices'][0]['message']['content'].strip()
        role = text.split('\n')[-1].strip()
        # Clean role (remove prefixes like "3. Role: ")
        if ':' in role:
            role = role.split(':')[-1].strip()
        return role
    else:
        raise Exception(f"API error: {response.status_code}")

def main():
    with open('data/benchmark/tier1_annotation.csv', 'r') as f:
        samples = list(csv.DictReader(f))

    print(f"🤖 GROQ ANNOTATION (Llama 3.3 70B) - {len(samples)} samples")
    print("=" * 60)

    results = []
    matches = 0
    for i, s in enumerate(samples[:30], 1):
        try:
            llm_role = annotate(s['name'], s['file'], s['repo'])
            is_match = llm_role.lower() == s['predicted'].lower()
            if is_match:
                matches += 1
            match = "✅" if is_match else "❌"
            print(f"[{i:2}] {s['name']:25} | Pred: {s['predicted']:15} | LLM: {llm_role:15} {match}")
            
            results.append({**s, 'llm_annotated': llm_role, 'match': is_match})
            time.sleep(0.3)
        except Exception as e:
            print(f"[{i:2}] ERROR: {s['name']}: {e}")

    print(f"\n{'='*60}")
    if results:
        print(f"🎯 ACCURACY: {matches}/{len(results)} = {matches/len(results)*100:.1f}%")
        with open('data/benchmark/tier1_llm_annotated.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"📄 Saved: data/benchmark/tier1_llm_annotated.csv")

if __name__ == "__main__":
    main()
