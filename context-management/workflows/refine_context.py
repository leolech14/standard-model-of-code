#!/usr/bin/env python3
"""
Context Refinement Engine (Semantic Mapper)
===========================================
A "Tier 3" workflow tool that uses the "Verification-Driven Loop" pattern
to validate the codebase against semantic models (The Map).

Mechanism:
1. Hypothesis: "All X must be Y" (from semantic_models.yaml)
2. Verification:
   - Search: Find candidate files.
   - Reason: Use Tier 1 analysis to prove/disprove the hypothesis.
3. Refinement: Output validated knowledge.

Usage:
  python refine_context.py --domain pipeline
  python refine_context.py --domain theory --output validated_theory.md
"""

import sys
import os
import yaml
import argparse
import time
from pathlib import Path

# Reuse infrastructure from local_analyze
# We add the parent directory to sys.path to import local_analyze as a module if needed
# But since local_analyze is a script, we might import specific functions if possible
# or just reuse the logic pattern.

# Determine Project Root (context-management/workflows -> context-management -> PROJECT_elements)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Add Project Root to path for imports
sys.path.append(str(PROJECT_ROOT))

# Add tools/ai to path for local_analyze import
ai_tools_path = PROJECT_ROOT / "context-management/tools/ai"
if not ai_tools_path.exists():
    print(f"Warning: AI tools path not found at {ai_tools_path}")
sys.path.append(str(ai_tools_path))

try:
    import local_analyze
    from local_analyze import (
        create_client, 
        create_developer_client,
        list_file_search_stores,
        search_with_file_search,
        get_or_create_store,
        index_files_to_store,
        list_local_files,
        retry_with_backoff,
        FILE_SEARCH_MODEL
    )
    # Configure local_analyze constants if needed
    local_analyze.PROJECT_ROOT = PROJECT_ROOT
except ImportError as e:
    print(f"Error: Could not import local_analyze.py functions: {e}")
    sys.exit(1)

from google.genai.types import Part, Content

# Configuration
SEMANTIC_MODELS_PATH = PROJECT_ROOT / "context-management/config/semantic_models.yaml"

def load_semantic_models():
    if not SEMANTIC_MODELS_PATH.exists():
        print(f"Error: Semantic models not found at {SEMANTIC_MODELS_PATH}")
        sys.exit(1)
    with open(SEMANTIC_MODELS_PATH) as f:
        return yaml.safe_load(f)

def generate_hypotheses(domain_config):
    """
    Convert domain definitions into testable hypotheses.
    Returns a list of dicts: {'claim': str, 'invariants': list, 'context': str}
    """
    hypotheses = []
    definitions = domain_config.get('definitions', {})
    
    for concept, details in definitions.items():
        desc = details.get('description', 'No description')
        invariants = details.get('invariants', [])
        
        # Formulate the "claim"
        claim = f"Hypothesis: The concept '{concept}' is implemented according to strict invariants."
        
        hypotheses.append({
            'concept': concept,
            'claim': claim,
            'description': desc,
            'invariants': invariants
        })
    
    return hypotheses

def verify_hypothesis(dev_client, vertex_client, hypothesis, store_name):
    """
    Execute the Verification Loop:
    1. Search (Tier 2) for candidates
    2. Analyze (Tier 1) for compliance
    """
    concept = hypothesis['concept']
    invariants = hypothesis['invariants']
    
    print(f"\nTargeting Concept: {concept}")
    print(f"  Invariants: {len(invariants)}")
    
    # Phase A: Discovery (Tier 2)
    # "Find files that represent [Concept]"
    discovery_query = f"Find code that implements or represents the concept '{concept}'. List relevant classes or modules."
    print(f"  Phase A: Discovering candidates (File Search)...")
    
    search_result = search_with_file_search(dev_client, store_name, discovery_query)
    
    # Extract file candidates from citations
    candidate_files = set()
    if search_result.get('citations'):
        for cite in search_result['citations']:
            if 'file' in cite:
                # Need to convert URI to local path if possible, or just treat as hint
                # local_analyze uses URIs that might be relative or full. 
                # Assuming relative to project root or absolute.
                fpath = cite['file']
                if fpath.startswith('file://'):
                    fpath = fpath[7:]
                candidate_files.add(fpath)
    
    if not candidate_files:
        print("    No candidates found via File Search.")
        return {'verified': False, 'reason': 'No candidates found'}
    
    print(f"    Found {len(candidate_files)} candidates: {', '.join([Path(f).name for f in list(candidate_files)[:3]])}...")
    
    # Phase B: Deep Verification (Tier 1)
    # We construct a prompt for the "Surgeon"
    
    files_context = ""
    valid_files = []
    
    # Read first N files to build verification context
    for fpath in list(candidate_files)[:5]: # Limit to 5 files for analysis
        full_path = Path(fpath)
        if not full_path.is_absolute():
            full_path = PROJECT_ROOT / fpath
        
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
                files_context += f"\n--- FILE: {fpath} ---\n{content}\n"
                valid_files.append(fpath)
            except Exception as e:
                print(f"    Warning: Could not read candidate file {fpath}: {e}")
                pass

    if not files_context:
        return {'verified': False, 'reason': 'Could not read candidate files'}

    print(f"  Phase B: Verifying Invariants (Long Context)...")
    
    prompt = f"""
    You are a Semantic Auditor. Your job is to verify if the code matches the Semantic Definition.
    
    CONCEPT: {concept}
    DESCRIPTION: {hypothesis['description']}
    
    INVARIANTS (MUST BE TRUE):
    {chr(10).join([f'- {i}' for i in invariants])}
    
    CODEBASE CONTEXT:
    {files_context}
    
    TASK:
    1. Identify which classes/functions in the context correspond to '{concept}'.
    2. Check each against the invariants.
    3. Output a structured report.
    
    FORMAT:
    ### Findings
    - **Entity**: [Name]
    - **Status**: [Compliant / Non-Compliant]
    - **Evidence**: [Quote or reasoning]
    - **Deviation**: [If non-compliant, explain why]
    """
    
    # Use Vertex client (from local_analyze)
    # We call generate_content
    response = vertex_client.models.generate_content(
        model=local_analyze.DEFAULT_MODEL,
        contents=[Part.from_text(text=prompt)]
    )
    
    return {
        'verified': True,
        'candidates': list(candidate_files),
        'analysis': response.text
    }

def main():
    parser = argparse.ArgumentParser(description="Context Refinement Engine")
    parser.add_argument("--domain", required=True, help="Domain to refine (from semantic_models.yaml)")
    parser.add_argument("--store-name", help="File Search store to use (defaults to collider-[domain])")
    parser.add_argument("--output", help="Output file for the refinement log")
    parser.add_argument("--index", action="store_true", help="Force re-indexing of the store before analysis")
    
    args = parser.parse_args()
    
    # Load Models (The Map)
    models = load_semantic_models()
    if args.domain not in models:
        print(f"Error: Domain '{args.domain}' not found in semantic_models.yaml")
        print(f"Available: {list(models.keys())}")
        sys.exit(1)
    
    domain_config = models[args.domain]
    store_name = args.store_name or f"collider-{args.domain}"
    
    # Initialize Clients
    print("Initializing clients...")
    dev_client = create_developer_client()
    if not dev_client:
        sys.exit(1)
        
    vertex_client, _ = create_client()
    
    # Indexing (Optional)
    if args.index:
        print(f"Indexing domain '{args.domain}' to store '{store_name}'...")
        # Basic heuristic: map domain to folders. This is manual for now.
        # Ideally this map is also in config.
        # For 'pipeline', we assume 'src/core' or similar.
        # Using a simple default: search whole repo? No, too big.
        # Let's search for "src/core" for pipeline, "docs" for theory.
        
        target_dir = None
        if args.domain == 'pipeline':
            target_dir = PROJECT_ROOT / "standard-model-of-code/src/core"
        elif args.domain == 'theory':
            target_dir = PROJECT_ROOT / "standard-model-of-code/docs/theory"
        
        if not target_dir:
            print(f"Error: No indexing target directory defined for domain '{args.domain}'.")
            print("Please update refine_context.py to map this domain to a folder.")
            sys.exit(1)
        
        store_res = get_or_create_store(dev_client, store_name)
        files = list_local_files(target_dir) # Should pass patterns
        index_files_to_store(dev_client, store_res, files, PROJECT_ROOT)

    # Resolve Store Name (Display Name -> Resource Name)
    print(f"Resolving store '{store_name}'...")
    stores = list_file_search_stores(dev_client)
    target_store = next((s for s in stores if s.display_name == store_name), None)
    
    if not target_store:
        print(f"Error: Store '{store_name}' not found.")
        print("Please run with --index first to create it.")
        sys.exit(1)
        
    store_resource_name = target_store.name
    print(f"  Found store: {store_resource_name}")

    # 1. Hypothesize
    hypotheses = generate_hypotheses(domain_config)
    print(f"\nLoaded {len(hypotheses)} hypotheses for domain '{args.domain}'")
    
    results = []
    
    # 2. Verify Loop
    for h in hypotheses:
        print("-" * 60)
        res = verify_hypothesis(dev_client, vertex_client, h, store_resource_name)
        results.append({
            'hypothesis': h,
            'result': res
        })
        time.sleep(2) # Rate limit politeness
    
    # 3. Validated Output
    output_content = f"# Validated Semantic Map: {args.domain.upper()}\n\n"
    output_content += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for item in results:
        h = item['hypothesis']
        res = item['result']
        
        output_content += f"## Concept: {h['concept']}\n"
        output_content += f"> {h['description']}\n\n"
        
        if res['verified']:
            output_content += res['analysis'] + "\n\n"
        else:
            output_content += f"**Verification Failed**: {res.get('reason')}\n\n"
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_content)
        print(f"\nRefinement log saved to: {args.output}")
    else:
        print("\n" + "="*60)
        print(output_content)

if __name__ == "__main__":
    main()
