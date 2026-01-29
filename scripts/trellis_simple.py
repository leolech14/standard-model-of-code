#!/usr/bin/env python3
"""
TRELLIS.2 Simple Converter - Conservative settings that work
"""

import os
import sys
from gradio_client import Client, handle_file
from datetime import datetime
import shutil

def convert_to_3d(image_path: str, output_dir: str = "."):
    """Convert 2D image to 3D using TRELLIS.2 with balanced settings"""

    print("=" * 80)
    print("TRELLIS.2 - Image to 3D Converter")
    print("=" * 80)
    print(f"Input: {image_path}")
    print(f"Output: {output_dir}")

    os.makedirs(output_dir, exist_ok=True)

    # Initialize client
    print("\nConnecting to microsoft/TRELLIS.2...")
    client = Client("microsoft/TRELLIS.2")

    # Start session
    print("Starting session...")
    client.predict(api_name="/start_session")

    # Preprocess image
    print("Preprocessing image...")
    preprocessed = client.predict(
        input=handle_file(image_path),
        api_name="/preprocess_image"
    )

    # Generate 3D model with optimized settings
    print("\nGenerating 3D model...")
    print("Settings: Resolution=1024, Enhanced texture guidance")

    client.predict(
        image=preprocessed,
        seed=42,
        resolution="1024",  # Good balance (not max 1536 which might fail)
        # Structure sampling - defaults
        ss_guidance_strength=7.5,
        ss_guidance_rescale=0.7,
        ss_sampling_steps=12,
        ss_rescale_t=5,
        # Shape SLAT - defaults
        shape_slat_guidance_strength=7.5,
        shape_slat_guidance_rescale=0.5,
        shape_slat_sampling_steps=12,
        shape_slat_rescale_t=3,
        # Texture SLAT - slightly enhanced
        tex_slat_guidance_strength=1.5,  # Moderate increase for detail
        tex_slat_guidance_rescale=0.2,
        tex_slat_sampling_steps=12,
        tex_slat_rescale_t=3,
        api_name="/image_to_3d"
    )

    print("3D model generated!")

    # Extract GLB file with reasonable settings
    print("\nExtracting GLB file...")
    glb_file, download_link = client.predict(
        decimation_target=300000,  # Default, proven to work
        texture_size=2048,         # Default, proven to work
        api_name="/extract_glb"
    )

    # Copy to output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"trellis_{timestamp}.glb"
    output_path = os.path.join(output_dir, output_filename)

    shutil.copy(glb_file, output_path)

    print("\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    print(f"3D Model: {output_path}")
    print(f"Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
    print("\nView at: https://gltf-viewer.donmccurdy.com/")
    print("=" * 80)

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trellis_simple.py <image_path> [output_dir]")
        sys.exit(1)

    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    convert_to_3d(image_path, output_dir)
