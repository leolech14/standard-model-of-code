#!/usr/bin/env python3
"""
LLM Annotation Script for Tier 1 Repos
Uses Claude API with proper environment handling
"""
import csv
import os
import json
import requests
import time

# Get API key from environment
API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
if not API_KEY:
    print("❌ ANTHROPIC_API_KEY not set")
    exit(1)

ROLE_TAXONOMY = """
Choose ONE of these roles:
Query, Command, Entity, Repository, Service, Factory, Builder, Validator,
Transformer, Adapter, Controller, Presenter, View, Configuration, Constant,
Utility, Test, Mock, Fixture, Migration, EventHandler, Observer, Strategy,
Decorator, Singleton, Guard, Middleware, ImpureFunction
"""

def annotate(name, file_path, repo):
    """High-reasoning annotation with Claude via HTTP."""
    prompt = f"""Classify this code element's SEMANTIC ROLE.

Element name: {name}
File path: ...{file_path[-60:]}
Repository: {repo}

{ROLE_TAXONOMY}

Think step-by-step:
1. What does the name suggest?
2. What does the file path suggest (e.g., /tests/ = Test)?
3. What is the most likely role?

Respond with ONLY the role name on the last line."""

    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 100,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        text = response.json()['content'][0]['text'].strip()
        role = text.split('\n')[-1].strip()
        return role
    else:
        raise Exception(f"API error: {response.status_code} - {response.text[:100]}")

def main():
    # Load samples  
    with open('data/benchmark/tier1_annotation.csv', 'r') as f:
        samples = list(csv.DictReader(f))

    print(f"🤖 LLM ANNOTATION (Claude Sonnet 4) - {len(samples)} samples")
    print("=" * 60)

    results = []
    matches = 0
    for i, s in enumerate(samples[:30], 1):  # First 30 for speed
        try:
            llm_role = annotate(s['name'], s['file'], s['repo'])
            is_match = llm_role.lower() == s['predicted'].lower()
            match = "✅" if is_match else "❌"
            if is_match:
                matches += 1
            print(f"[{i:2}] {s['name']:25} | Pred: {s['predicted']:15} | LLM: {llm_role:15} {match}")
            
            results.append({
                **s,
                'llm_annotated': llm_role,
                'match': is_match
            })
            time.sleep(0.5)  # Rate limit
        except Exception as e:
            print(f"[{i:2}] ERROR: {s['name']}: {e}")

    print(f"\n{'='*60}")
    if results:
        print(f"🎯 ACCURACY: {matches}/{len(results)} = {matches/len(results)*100:.1f}%")

        # Save results
        with open('data/benchmark/tier1_llm_annotated.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"📄 Saved to data/benchmark/tier1_llm_annotated.csv")

if __name__ == "__main__":
    main()
