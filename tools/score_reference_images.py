#!/usr/bin/env python3
"""
Score reference images for quality/usefulness.

Criteria:
1. Size score: Tiny files are garbage
2. Aspect ratio: Extreme ratios (thin lines) are garbage
3. Entropy: Low entropy = blank/simple, high = detailed figure
4. Color variance: Diagrams often have distinct colors vs B&W text
5. Edge density: Figures have structured edges, text has uniform density

Usage:
    python score_reference_images.py                    # Score all, show summary
    python score_reference_images.py --sample 100      # Score random sample
    python score_reference_images.py --threshold 0.5   # List files to delete
    python score_reference_images.py --delete 0.3      # Actually delete low-scoring
"""

import os
import sys
import random
import csv
from pathlib import Path
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

# Try to import PIL for image analysis
try:
    from PIL import Image
    import math
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARNING: PIL not installed. Install with: pip install Pillow")
    print("         Running in size-only mode.\n")

PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / "wave/archive/references/images"


def calculate_entropy(img):
    """Calculate image entropy (information density)."""
    histogram = img.histogram()
    total = sum(histogram)
    if total == 0:
        return 0
    entropy = 0
    for count in histogram:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def calculate_pixel_variance(img):
    """Calculate pixel value variance (blank detection)."""
    if img.mode != 'L':
        img = img.convert('L')
    pixels = list(img.getdata())
    if not pixels:
        return 0
    mean = sum(pixels) / len(pixels)
    variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
    return variance


def estimate_text_density(img):
    """Estimate if image is mostly text (horizontal line patterns).

    Optimized: samples every 50th row, every 4th pixel for speed.
    """
    if img.mode != 'L':
        img = img.convert('L')

    width, height = img.size
    if width < 50 or height < 50:
        return 0

    pixels = list(img.getdata())

    # Sample horizontal lines and count transitions
    # Text has many small transitions (letter edges)
    transitions = 0
    samples = 0

    # Sample every 50th row (fast), every 4th pixel
    step_y = max(50, height // 20)  # At most 20 rows
    step_x = 4

    for y in range(5, height - 5, step_y):
        row_transitions = 0
        sampled_pixels = 0
        for x in range(1, width - 1, step_x):
            idx = y * width + x
            # Count edge transitions
            diff = abs(pixels[idx] - pixels[idx - step_x]) if x >= step_x else 0
            if diff > 20:  # Edge threshold
                row_transitions += 1
            sampled_pixels += 1
        # Text pages have MANY transitions per row (letter edges)
        if sampled_pixels > 0 and row_transitions > sampled_pixels * 0.15:
            transitions += 1
        samples += 1

    return transitions / samples if samples > 0 else 0


def calculate_edge_density(img):
    """Estimate edge density using simple gradient."""
    if img.mode != 'L':
        img = img.convert('L')

    width, height = img.size
    if width < 3 or height < 3:
        return 0

    pixels = list(img.getdata())
    edges = 0

    # Sample for speed (every 4th pixel)
    for y in range(1, height - 1, 2):
        for x in range(1, width - 1, 2):
            idx = y * width + x
            # Simple gradient magnitude
            dx = abs(pixels[idx + 1] - pixels[idx - 1])
            dy = abs(pixels[idx + width] - pixels[idx - width])
            if dx + dy > 30:  # Edge threshold
                edges += 1

    sampled_pixels = ((height - 2) // 2) * ((width - 2) // 2)
    return edges / sampled_pixels if sampled_pixels > 0 else 0


def score_image(filepath: Path) -> dict:
    """Score a single image for quality/usefulness."""
    result = {
        'path': str(filepath.relative_to(PROJECT_ROOT)),
        'size_bytes': 0,
        'width': 0,
        'height': 0,
        'aspect_ratio': 0,
        'entropy': 0,
        'edge_density': 0,
        'color_variance': 0,
        'score': 0,
        'verdict': 'unknown',
        'reason': ''
    }

    try:
        stat = filepath.stat()
        result['size_bytes'] = stat.st_size

        # Size score (0-1): penalize tiny files heavily
        if result['size_bytes'] < 1000:
            size_score = 0
        elif result['size_bytes'] < 5000:
            size_score = 0.1
        elif result['size_bytes'] < 10000:
            size_score = 0.2
        elif result['size_bytes'] < 50000:
            size_score = 0.4
        elif result['size_bytes'] < 100000:
            size_score = 0.6
        elif result['size_bytes'] < 300000:
            size_score = 0.8
        else:
            size_score = 1.0

        if not HAS_PIL:
            result['score'] = size_score
            result['verdict'] = 'keep' if size_score >= 0.4 else 'delete'
            result['reason'] = 'size-only mode'
            return result

        # Open image for detailed analysis
        with Image.open(filepath) as img:
            result['width'] = img.width
            result['height'] = img.height

            # HARD FAIL: Tiny images (less than 50px in any dimension)
            if img.width < 50 or img.height < 50:
                result['score'] = 0.08
                result['verdict'] = 'delete'
                result['reason'] = 'tiny image fragment'
                return result

            # Aspect ratio score: penalize extreme ratios
            if img.width == 0 or img.height == 0:
                aspect_score = 0
            else:
                ratio = max(img.width, img.height) / min(img.width, img.height)
                result['aspect_ratio'] = round(ratio, 2)
                if ratio > 20:  # Very thin = line fragment
                    result['score'] = 0.05
                    result['verdict'] = 'delete'
                    result['reason'] = 'extreme aspect ratio (line fragment)'
                    return result
                elif ratio > 10:
                    aspect_score = 0.2
                elif ratio > 5:
                    aspect_score = 0.5
                else:
                    aspect_score = 1.0

            # Skip detailed analysis for tiny images
            if result['size_bytes'] < 5000:
                result['score'] = (size_score * 0.7 + aspect_score * 0.3)
                result['verdict'] = 'delete'
                result['reason'] = 'tiny file'
                return result

            # Entropy score (information density)
            gray = img.convert('L')
            entropy = calculate_entropy(gray)
            result['entropy'] = round(entropy, 2)

            # Pixel variance (blank detection) - NEW
            pixel_var = calculate_pixel_variance(gray)

            # HARD FAIL: Near-blank images (very low entropy AND low variance)
            # Only trigger for truly blank pages, not simple diagrams
            if entropy < 1.0 and pixel_var < 200:
                result['score'] = 0.05
                result['verdict'] = 'delete'
                result['reason'] = 'blank or near-blank page'
                return result

            # Normalize entropy: typical range 4-8
            entropy_score = min(1.0, max(0, (entropy - 3) / 5))

            # Edge density score (structured content)
            edge_density = calculate_edge_density(gray)
            result['edge_density'] = round(edge_density, 3)

            # HARD FAIL: Text pages (very high edge density = dense text)
            # Skip expensive text_density calculation, use edge density alone
            if edge_density > 0.45:
                result['score'] = 0.15
                result['verdict'] = 'delete'
                result['reason'] = 'text page (not a figure)'
                return result

            # Refined edge scoring
            # Good figures: 0.05-0.25, text pages: 0.30+, blank: <0.01
            if edge_density < 0.01:
                edge_score = 0.1  # Mostly blank
            elif edge_density < 0.05:
                edge_score = 0.6  # Simple diagram (not bad)
            elif edge_density < 0.20:
                edge_score = 1.0  # Good figure (optimal range)
            elif edge_density < 0.30:
                edge_score = 0.7  # Detailed diagram
            elif edge_density < 0.40:
                edge_score = 0.3  # Probably text-heavy
            else:
                edge_score = 0.1  # Dense text page

            # Color variance (diagrams often colorful)
            if img.mode in ('RGB', 'RGBA'):
                # Sample colors
                small = img.resize((50, 50))
                colors = small.getcolors(2500) or []
                unique_colors = len(colors)
                result['color_variance'] = unique_colors
                color_score = min(1.0, unique_colors / 500)
            else:
                color_score = 0.5  # Grayscale, neutral

            # Page shape penalty: Full page scans (portrait, book-like) are suspect
            if img.height > img.width * 1.3 and img.height > 800:
                # Portrait orientation, tall = probably full page scan
                page_penalty = 0.15
            else:
                page_penalty = 0

            # Combined score (weighted)
            raw_score = (
                size_score * 0.20 +
                aspect_score * 0.15 +
                entropy_score * 0.15 +
                edge_score * 0.35 +  # Edge density most important
                color_score * 0.15
            ) - page_penalty

            result['score'] = round(max(0, min(1.0, raw_score)), 3)

            # Verdict (stricter thresholds)
            if result['score'] >= 0.65:
                result['verdict'] = 'keep'
                result['reason'] = 'high quality figure'
            elif result['score'] >= 0.45:
                result['verdict'] = 'review'
                result['reason'] = 'medium quality, manual review'
            else:
                result['verdict'] = 'delete'
                if aspect_score < 0.3:
                    result['reason'] = 'extreme aspect ratio (fragment)'
                elif entropy_score < 0.2:
                    result['reason'] = 'low entropy (blank/simple)'
                elif edge_score < 0.3:
                    result['reason'] = 'text page or low detail'
                elif page_penalty > 0:
                    result['reason'] = 'full page scan (not cropped figure)'
                else:
                    result['reason'] = 'low overall quality'

    except Exception as e:
        result['verdict'] = 'error'
        result['reason'] = str(e)[:50]

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Score reference images')
    parser.add_argument('--sample', type=int, help='Score random sample of N images')
    parser.add_argument('--threshold', type=float, help='Show files below this score')
    parser.add_argument('--delete', type=float, help='DELETE files below this score (DANGEROUS)')
    parser.add_argument('--output', type=str, help='Write full results to CSV')
    parser.add_argument('--source', type=str, help='Specific source folder (e.g., SIMON)')
    args = parser.parse_args()

    # Collect image files
    search_dir = IMAGES_DIR
    if args.source:
        search_dir = IMAGES_DIR / args.source

    print(f"Scanning {search_dir}...")
    all_images = list(search_dir.rglob("*.png"))
    print(f"Found {len(all_images)} PNG files")

    if args.sample and args.sample < len(all_images):
        images = random.sample(all_images, args.sample)
        print(f"Sampling {args.sample} random images")
    else:
        images = all_images

    # Score images (with progress)
    print("\nScoring images...")
    results = []

    for i, img_path in enumerate(images):
        if i % 500 == 0:
            print(f"  Progress: {i}/{len(images)}")
        results.append(score_image(img_path))

    # Summary statistics
    verdicts = Counter(r['verdict'] for r in results)
    scores = [r['score'] for r in results if r['score'] > 0]

    print("\n" + "=" * 60)
    print("SCORING SUMMARY")
    print("=" * 60)
    print(f"Total scored: {len(results)}")
    print(f"\nVerdict distribution:")
    for verdict, count in verdicts.most_common():
        pct = count / len(results) * 100
        print(f"  {verdict:10} {count:>6} ({pct:.1f}%)")

    if scores:
        print(f"\nScore statistics:")
        print(f"  Min:    {min(scores):.3f}")
        print(f"  Max:    {max(scores):.3f}")
        print(f"  Mean:   {sum(scores)/len(scores):.3f}")
        print(f"  Median: {sorted(scores)[len(scores)//2]:.3f}")

    # Score buckets
    buckets = {'0.0-0.2': 0, '0.2-0.4': 0, '0.4-0.6': 0, '0.6-0.8': 0, '0.8-1.0': 0}
    for s in scores:
        if s < 0.2: buckets['0.0-0.2'] += 1
        elif s < 0.4: buckets['0.2-0.4'] += 1
        elif s < 0.6: buckets['0.4-0.6'] += 1
        elif s < 0.8: buckets['0.6-0.8'] += 1
        else: buckets['0.8-1.0'] += 1

    print(f"\nScore distribution:")
    for bucket, count in buckets.items():
        bar = '#' * (count * 40 // max(buckets.values())) if buckets.values() else ''
        print(f"  {bucket}: {count:>5} {bar}")

    # Estimate space savings
    delete_candidates = [r for r in results if r['verdict'] == 'delete']
    delete_size = sum(r['size_bytes'] for r in delete_candidates)
    print(f"\nPotential cleanup:")
    print(f"  Files to delete: {len(delete_candidates)}")
    print(f"  Space to recover: {delete_size / (1024*1024):.1f} MB")

    # Show threshold results
    if args.threshold:
        below = [r for r in results if r['score'] < args.threshold]
        print(f"\n{len(below)} files below threshold {args.threshold}:")
        for r in sorted(below, key=lambda x: x['score'])[:20]:
            print(f"  {r['score']:.3f} | {r['reason']:30} | {r['path'][:50]}")

    # Write CSV output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(sorted(results, key=lambda x: x['score']))
        print(f"\nFull results written to: {output_path}")

    # DANGEROUS: Actually delete files
    if args.delete:
        to_delete = [r for r in results if r['score'] < args.delete]
        print(f"\n{'='*60}")
        print(f"WARNING: About to DELETE {len(to_delete)} files!")
        print(f"{'='*60}")
        confirm = input("Type 'DELETE' to confirm: ")
        if confirm == 'DELETE':
            deleted = 0
            for r in to_delete:
                try:
                    (PROJECT_ROOT / r['path']).unlink()
                    deleted += 1
                except Exception as e:
                    print(f"  Failed: {r['path']}: {e}")
            print(f"Deleted {deleted} files")
        else:
            print("Aborted.")


if __name__ == '__main__':
    main()
