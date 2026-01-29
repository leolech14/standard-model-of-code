#!/usr/bin/env python3
"""
TRELLIS.2 Image to 3D Converter
Registered as T052 in .agent/intelligence/TOOLS_REGISTRY.yaml
"""

import os
import sys
from gradio_client import Client, handle_file
from datetime import datetime

def convert_to_3d(
    image_path: str,
    output_dir: str = None,
    resolution: str = "1536",  # Maximum resolution
    seed: int = 42,
    # Structure sampling (high detail)
    ss_guidance_strength: float = 7.5,
    ss_guidance_rescale: float = 0.7,
    ss_sampling_steps: int = 12,
    ss_rescale_t: int = 5,
    # Shape SLAT (high detail)
    shape_slat_guidance_strength: float = 7.5,
    shape_slat_guidance_rescale: float = 0.5,
    shape_slat_sampling_steps: int = 12,
    shape_slat_rescale_t: int = 3,
    # Texture SLAT (enhanced for detail)
    tex_slat_guidance_strength: float = 2.0,  # Increased from default 1.0
    tex_slat_guidance_rescale: float = 0.3,   # Increased from default 0.0
    tex_slat_sampling_steps: int = 12,
    tex_slat_rescale_t: int = 3,
    # Extraction settings (high quality)
    decimation_target: int = 500000,  # Higher poly count (default 300k)
    texture_size: int = 4096,         # Maximum texture resolution (default 2048)
):
    """
    Convert 2D image to 3D GLB model using Microsoft TRELLIS.2

    Args:
        image_path: Path to input image
        output_dir: Directory to save outputs (default: current directory)
        resolution: Output resolution (512, 1024, or 1536)
        seed: Random seed for reproducibility
        decimation_target: Target polygon count for GLB export
        texture_size: Texture resolution in pixels
    """
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)

    if output_dir is None:
        output_dir = os.getcwd()

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 80)
    print("TRELLIS.2 - Image to 3D Converter (T052)")
    print("=" * 80)
    print(f"Input: {image_path}")
    print(f"Output: {output_dir}")
    print(f"Resolution: {resolution}")
    print(f"Seed: {seed}")
    print(f"Decimation Target: {decimation_target:,} polygons")
    print(f"Texture Size: {texture_size}x{texture_size}")
    print("-" * 80)

    # Initialize client
    print("Connecting to microsoft/TRELLIS.2...")
    client = Client("microsoft/TRELLIS.2")

    # Start session
    print("Starting session...")
    session = client.predict(api_name="/start_session")

    # Preprocess image
    print("Preprocessing image...")
    preprocessed = client.predict(
        input=handle_file(image_path),
        api_name="/preprocess_image"
    )

    # Generate 3D model
    print("Generating 3D model (this may take several minutes)...")
    print("  Structure sampling settings:")
    print(f"    - Guidance strength: {ss_guidance_strength}")
    print(f"    - Sampling steps: {ss_sampling_steps}")
    print("  Shape SLAT settings:")
    print(f"    - Guidance strength: {shape_slat_guidance_strength}")
    print(f"    - Sampling steps: {shape_slat_sampling_steps}")
    print("  Texture SLAT settings:")
    print(f"    - Guidance strength: {tex_slat_guidance_strength}")
    print(f"    - Sampling steps: {tex_slat_sampling_steps}")

    model_3d = client.predict(
        image=preprocessed,
        seed=seed,
        resolution=resolution,
        ss_guidance_strength=ss_guidance_strength,
        ss_guidance_rescale=ss_guidance_rescale,
        ss_sampling_steps=ss_sampling_steps,
        ss_rescale_t=ss_rescale_t,
        shape_slat_guidance_strength=shape_slat_guidance_strength,
        shape_slat_guidance_rescale=shape_slat_guidance_rescale,
        shape_slat_sampling_steps=shape_slat_sampling_steps,
        shape_slat_rescale_t=shape_slat_rescale_t,
        tex_slat_guidance_strength=tex_slat_guidance_strength,
        tex_slat_guidance_rescale=tex_slat_guidance_rescale,
        tex_slat_sampling_steps=tex_slat_sampling_steps,
        tex_slat_rescale_t=tex_slat_rescale_t,
        api_name="/image_to_3d"
    )

    print("3D model generated!")

    # Extract GLB file
    print(f"Extracting GLB file (decimation: {decimation_target:,}, texture: {texture_size}x{texture_size})...")
    glb_file, download_link = client.predict(
        decimation_target=decimation_target,
        texture_size=texture_size,
        api_name="/extract_glb"
    )

    # Copy GLB to output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"trellis_output_{timestamp}.glb"
    output_path = os.path.join(output_dir, output_filename)

    import shutil
    shutil.copy(glb_file, output_path)

    print("=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    print(f"3D Model saved to: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
    print()
    print("View your 3D model:")
    print(f"  - Open in Blender, Sketchfab, or any GLB viewer")
    print(f"  - Drag and drop into https://gltf-viewer.donmccurdy.com/")
    print("=" * 80)

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trellis_convert.py <image_path> [output_dir]")
        print("Example: python trellis_convert.py city.png ./output")
        sys.exit(1)

    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    convert_to_3d(image_path, output_dir)
