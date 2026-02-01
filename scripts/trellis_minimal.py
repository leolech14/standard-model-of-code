#!/usr/bin/env python3
"""
TRELLIS.2 - Minimal working version
"""

from gradio_client import Client, handle_file
import sys
import os
import shutil
from datetime import datetime

image_path = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

print("Connecting to TRELLIS.2...")
client = Client("microsoft/TRELLIS.2")

print("Uploading image directly (skipping preprocessing)...")

try:
    # Try direct conversion without preprocessing
    result = client.predict(
        image=handle_file(image_path),
        seed=42,
        resolution="1024",
        ss_guidance_strength=7.5,
        ss_guidance_rescale=0.7,
        ss_sampling_steps=12,
        ss_rescale_t=5,
        shape_slat_guidance_strength=7.5,
        shape_slat_guidance_rescale=0.5,
        shape_slat_sampling_steps=12,
        shape_slat_rescale_t=3,
        tex_slat_guidance_strength=1,
        tex_slat_guidance_rescale=0,
        tex_slat_sampling_steps=12,
        tex_slat_rescale_t=3,
        api_name="/image_to_3d"
    )

    print("Success! Extracting GLB...")

    glb_file, _ = client.predict(
        decimation_target=300000,
        texture_size=2048,
        api_name="/extract_glb"
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"ancient_city_{timestamp}.glb")
    shutil.copy(glb_file, output_path)

    print(f"\n✓ SUCCESS: {output_path}")
    print(f"Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nThe space might be:")
    print("  1. Out of GPU resources (it's on serverless 'Zero')")
    print("  2. Temporarily down")
    print("  3. Unable to process this specific image")
    print("\nTry:")
    print(f"  - Visit directly: open https://microsoft-trellis-2.hf.space")
    print(f"  - Or wait a few minutes and retry")
    sys.exit(1)
