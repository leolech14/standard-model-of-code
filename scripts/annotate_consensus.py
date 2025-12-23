#!/usr/bin/env python3
"""
Multi-LLM Consensus Annotator

Uses 3 LLMs (GPT-4, Claude, Llama) to annotate samples.
Takes majority vote for high-confidence ground truth.
Flags conflicts for human review.
"""

import csv
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter
import time

# Try imports
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

import requests

ROLE_TAXONOMY = """
Available Roles (choose ONE):
Query, Command, Entity, Repository, Service, Factory, Builder, Validator,
Transformer, Adapter, Controller, Presenter, View, Configuration, Constant,
Utility, Test, Mock, Fixture, Migration, EventHandler, Observer, Strategy,
Decorator, Singleton, Guard, Middleware
"""

def annotate_with_gpt4(sample: Dict, api_key: str) -> str:
    """GPT-4 annotation."""
    client = OpenAI(api_key=api_key)
    
    prompt = f"""Classify this code element's SEMANTIC ROLE.

Element: {sample['name']} ({sample['kind']})
Signature: {sample['signature'][:150]}
Doc: {sample['docstring'][:150]}

{ROLE_TAXONOMY}

Respond with ONLY the role name. No explanation."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=10
    )
    
    return response.choices[0].message.content.strip()

def annotate_with_claude(sample: Dict, api_key: str) -> str:
    """Claude annotation."""
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""Classify this code element's SEMANTIC ROLE.

Element: {sample['name']} ({sample['kind']})
Signature: {sample['signature'][:150]}
Doc: {sample['docstring'][:150]}

{ROLE_TAXONOMY}

Respond with ONLY the role name. No explanation."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text.strip()

def annotate_with_ollama(sample: Dict, model: str = "llama3.2") -> str:
    """Ollama annotation."""
    prompt = f"""Classify this code element's SEMANTIC ROLE.

Element: {sample['name']} ({sample['kind']})
Signature: {sample['signature'][:150]}
Doc: {sample['docstring'][:150]}

{ROLE_TAXONOMY}

Respond with ONLY the role name. No explanation."""

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {'temperature': 0}
        }
    )
    
    if response.status_code == 200:
        return response.json()['response'].strip()
    else:
        raise Exception(f"Ollama failed: {response.status_code}")

def compute_consensus(annotations: Dict[str, str]) -> Tuple[str, str, int]:
    """
    Compute consensus from multiple annotations.
    
    Returns: (consensus_role, confidence_level, agreement_count)
    - consensus_role: The majority vote
    - confidence_level: HIGH/MEDIUM/LOW/CONFLICT
    - agreement_count: How many LLMs agreed
    """
    votes = list(annotations.values())
    vote_counts = Counter(votes)
    most_common = vote_counts.most_common(1)[0]
    consensus_role = most_common[0]
    agreement_count = most_common[1]
    total_voters = len(votes)
    
    # Determine confidence
    if agreement_count == total_voters:
        confidence = "HIGH"  # All agree
    elif agreement_count >= total_voters - 1:
        confidence = "MEDIUM"  # Majority (2/3)
    elif agreement_count == 1:
        confidence = "CONFLICT"  # All disagree
    else:
        confidence = "LOW"
    
    return consensus_role, confidence, agreement_count

def annotate_with_consensus(
    input_csv: Path,
    output_csv: Path,
    openai_key: Optional[str] = None,
    anthropic_key: Optional[str] = None,
    use_ollama: bool = True,
    limit: Optional[int] = None
) -> None:
    """Annotate with multi-LLM consensus."""
    
    # Check available LLMs
    llms = []
    if openai_key and HAS_OPENAI:
        llms.append("gpt4")
    if anthropic_key and HAS_ANTHROPIC:
        llms.append("claude")
    if use_ollama:
        llms.append("ollama")
    
    if len(llms) < 2:
        print("⚠️  Need at least 2 LLMs for consensus")
        print("   Available:", llms)
        return
    
    print(f"Using {len(llms)} LLMs: {', '.join(llms)}")
    
    # Load samples
    with open(input_csv, encoding='utf-8') as f:
        samples = list(csv.DictReader(f))
    
    if limit:
        samples = samples[:limit]
    
    print(f"\nAnnotating {len(samples)} samples...")
    
    results = []
    conflicts = []
    
    for i, sample in enumerate(samples, 1):
        annotations = {}
        
        try:
            # Get annotations from each LLM
            if "gpt4" in llms:
                annotations['gpt4'] = annotate_with_gpt4(sample, openai_key)
                time.sleep(0.5)
            
            if "claude" in llms:
                annotations['claude'] = annotate_with_claude(sample, anthropic_key)
                time.sleep(0.5)
            
            if "ollama" in llms:
                try:
                    annotations['ollama'] = annotate_with_ollama(sample)
                except Exception as e:
                    print(f"  Ollama failed for {sample['name']}: {e}")
            
            # Compute consensus
            if len(annotations) >= 2:
                consensus, confidence, agreement = compute_consensus(annotations)
                
                # Build result
                result = sample.copy()
                result['consensus_role'] = consensus
                result['confidence'] = confidence
                result['agreement_count'] = agreement
                result['total_llms'] = len(annotations)
                
                # Add individual votes
                for llm, vote in annotations.items():
                    result[f'{llm}_vote'] = vote
                
                results.append(result)
                
                # Display
                status = "✅" if confidence == "HIGH" else "⚠️" if confidence == "MEDIUM" else "❌"
                print(f"[{i}/{len(samples)}] {status} {sample['name']}: {consensus} ({confidence})")
                print(f"           Votes: {annotations}")
                
                # Track conflicts
                if confidence in ["CONFLICT", "LOW"]:
                    conflicts.append((i, sample['name'], annotations, consensus))
                    
        except Exception as e:
            print(f"Error on {sample['name']}: {e}")
            result = sample.copy()
            result['consensus_role'] = 'ERROR'
            result['confidence'] = 'ERROR'
            result['error'] = str(e)
            results.append(result)
    
    # Save results
    if results:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Consensus Annotation Complete")
    print(f"{'='*60}")
    
    high = sum(1 for r in results if r.get('confidence') == 'HIGH')
    medium = sum(1 for r in results if r.get('confidence') == 'MEDIUM')
    conflict = sum(1 for r in results if r.get('confidence') in ['CONFLICT', 'LOW'])
    
    print(f"\nQuality Breakdown:")
    print(f"  HIGH confidence (all agree):     {high} ({high/len(results)*100:.1f}%)")
    print(f"  MEDIUM confidence (majority):    {medium} ({medium/len(results)*100:.1f}%)")
    print(f"  CONFLICT (need review):          {conflict} ({conflict/len(results)*100:.1f}%)")
    
    print(f"\n📄 Output: {output_csv}")
    
    # Save conflicts for review
    if conflicts:
        conflict_file = output_csv.parent / 'conflicts_for_review.txt'
        with open(conflict_file, 'w') as f:
            f.write("CONFLICTS REQUIRING HUMAN REVIEW\n")
            f.write("="*60 + "\n\n")
            for idx, name, votes, consensus in conflicts:
                f.write(f"#{idx}: {name}\n")
                f.write(f"  Votes: {votes}\n")
                f.write(f"  Consensus: {consensus}\n")
                f.write(f"  → Manual review needed\n\n")
        
        print(f"⚠️  {len(conflicts)} conflicts saved to: {conflict_file}")
        print(f"   Review these manually for best quality")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-LLM consensus annotation')
    parser.add_argument('--input', type=Path,
                       default=Path('data/mini_validation_samples.csv'))
    parser.add_argument('--output', type=Path,
                       default=Path('data/mini_validation_consensus.csv'))
    parser.add_argument('--openai-key', help='OpenAI API key')
    parser.add_argument('--anthropic-key', help='Anthropic API key')
    parser.add_argument('--no-ollama', action='store_true',
                       help='Disable Ollama')
    parser.add_argument('--limit', type=int, help='Limit samples (testing)')
    
    args = parser.parse_args()
    
    # Get API keys from env if not provided
    openai_key = args.openai_key or os.getenv('OPENAI_API_KEY')
    anthropic_key = args.anthropic_key or os.getenv('ANTHROPIC_API_KEY')
    
    annotate_with_consensus(
        args.input,
        args.output,
        openai_key,
        anthropic_key,
        not args.no_ollama,
        args.limit
    )

if __name__ == '__main__':
    main()
