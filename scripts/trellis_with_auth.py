#!/usr/bin/env python3
"""
TRELLIS.2 with HuggingFace Authentication
Bypasses free tier GPU quota limits
"""

from gradio_client import Client, handle_file
import sys
import os
import shutil
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python trellis_with_auth.py <image_path> [output_dir]")
        sys.exit(1)

    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    # Get HF token from environment (Doppler injects this)
    hf_token = os.getenv('HUGGINGFACE_API_KEY')

    if not hf_token:
        print("❌ ERROR: HUGGINGFACE_API_KEY not found in environment")
        print("\nSet it up:")
        print("  1. Get token: open https://huggingface.co/settings/tokens")
        print("  2. Add to Doppler: doppler secrets set HUGGINGFACE_API_KEY 'hf_...'")
        print("  3. Run with Doppler: doppler run -- python scripts/trellis_with_auth.py <image>")
        sys.exit(1)

    print("=" * 80)
    print("TRELLIS.2 - Authenticated Session")
    print("=" * 80)
    print(f"Input: {image_path}")
    print(f"Output: {output_dir}")
    print(f"Token: {hf_token[:10]}...{hf_token[-4:]}")
    print("-" * 80)

    print("\nConnecting with authentication...")
    client = Client("microsoft/TRELLIS.2", hf_token=hf_token)

    print("Generating 3D model (HIGH DETAIL)...")
    print("  Resolution: 1536 (maximum)")
    print("  Decimation: 500k polygons")
    print("  Texture: 4096x4096")

    try:
        # Direct conversion with max detail settings
        client.predict(
            image=handle_file(image_path),
            seed=42,
            resolution="1536",  # MAXIMUM
            ss_guidance_strength=7.5,
            ss_guidance_rescale=0.7,
            ss_sampling_steps=12,
            ss_rescale_t=5,
            shape_slat_guidance_strength=7.5,
            shape_slat_guidance_rescale=0.5,
            shape_slat_sampling_steps=12,
            shape_slat_rescale_t=3,
            tex_slat_guidance_strength=2.0,  # Enhanced texture
            tex_slat_guidance_rescale=0.3,
            tex_slat_sampling_steps=12,
            tex_slat_rescale_t=3,
            api_name="/image_to_3d"
        )

        print("\n✓ Model generated! Extracting GLB...")

        glb_file, _ = client.predict(
            decimation_target=500000,  # High poly count
            texture_size=4096,         # Max texture
            api_name="/extract_glb"
        )

        # Save output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"ancient_city_3d_{timestamp}.glb"
        output_path = os.path.join(output_dir, output_filename)

        os.makedirs(output_dir, exist_ok=True)
        shutil.copy(glb_file, output_path)

        print("\n" + "=" * 80)
        print("✓ SUCCESS!")
        print("=" * 80)
        print(f"File: {output_path}")
        print(f"Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
        print("\nView at: https://gltf-viewer.donmccurdy.com/")
        print("Or open in Blender, SketchFab, etc.")
        print("=" * 80)

        return output_path

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if "quota" in str(e).lower():
            print("\nEven with authentication, you've hit quota limits.")
            print("Try again in a few hours or upgrade HuggingFace plan.")
        sys.exit(1)

if __name__ == "__main__":
    main()
