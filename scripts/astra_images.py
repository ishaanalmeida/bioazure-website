"""
Generate website images via GPT Image 2.5 Flare.
Hero image, OG image, and 4 application area icons.
"""
import json, os, sys, base64, time
from openai import OpenAI

def load_key():
    with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise RuntimeError('.env missing OPENAI_API_KEY')

IMAGES = [
    {
        "name": "hero-biotech",
        "prompt": "Professional photograph of a modern clinical laboratory in India. Clean white lab bench with PCR equipment and culture media plates in foreground, slightly blurred. A scientist in a white lab coat examining a test tube, warm overhead lighting. Blue and green color accent tones. Corporate website hero image style, wide aspect ratio, high quality, no text overlays.",
        "size": "1536x1024",
        "output": "public/images/hero-biotech.webp"
    },
    {
        "name": "icon-clinical-micro",
        "prompt": "Minimal flat icon for clinical microbiology. A petri dish with bacterial colonies and a magnifying glass, on a light blue circular background. Simple clean vector style, suitable for website use. Blue (#1e3a5f) and green (#2d8a4e) accent colors. No text.",
        "size": "1024x1024",
        "output": "public/images/icon-clinical-micro.png"
    },
    {
        "name": "icon-molecular-dx",
        "prompt": "Minimal flat icon for molecular diagnostics. A DNA double helix with a small PCR tube beside it, on a light blue circular background. Simple clean vector style, suitable for website use. Blue (#1e3a5f) and green (#2d8a4e) accent colors. No text.",
        "size": "1024x1024",
        "output": "public/images/icon-molecular-dx.png"
    },
    {
        "name": "icon-food-safety",
        "prompt": "Minimal flat icon for food safety testing. A shield with a checkmark overlaid on a stylized food item (apple or leaf), on a light blue circular background. Simple clean vector style, suitable for website use. Blue (#1e3a5f) and green (#2d8a4e) accent colors. No text.",
        "size": "1024x1024",
        "output": "public/images/icon-food-safety.png"
    },
    {
        "name": "icon-ivd-raw",
        "prompt": "Minimal flat icon for IVD raw materials and antibodies. A test tube with an antibody Y-shape symbol, on a light blue circular background. Simple clean vector style, suitable for website use. Blue (#1e3a5f) and green (#2d8a4e) accent colors. No text.",
        "size": "1024x1024",
        "output": "public/images/icon-ivd-raw.png"
    }
]

def main():
    api_key = load_key()
    client = OpenAI(api_key=api_key, timeout=120)
    base_dir = os.path.join(os.path.dirname(__file__), '..')

    for i, img in enumerate(IMAGES):
        out_path = os.path.join(base_dir, img["output"])
        # ponytail: skip files already generated (>10KB = not a placeholder)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10240:
            print(f"[{i+1}/{len(IMAGES)}] Skipping {img['name']} (already exists)", flush=True)
            continue

        print(f"[{i+1}/{len(IMAGES)}] Generating {img['name']} ({img['size']})...", flush=True)

        try:
            result = client.images.generate(
                model="gpt-image-2.5-flare",
                prompt=img["prompt"],
                n=1,
                size=img["size"],
            )

            image_data = result.data[0]

            if hasattr(image_data, 'b64_json') and image_data.b64_json:
                img_bytes = base64.b64decode(image_data.b64_json)
                with open(out_path, 'wb') as f:
                    f.write(img_bytes)
                print(f"  Saved ({len(img_bytes)} bytes)")
            elif hasattr(image_data, 'url') and image_data.url:
                import urllib.request
                urllib.request.urlretrieve(image_data.url, out_path)
                size = os.path.getsize(out_path)
                print(f"  Saved ({size} bytes)")
            else:
                print(f"  WARNING: No image data returned")

        except Exception as e:
            print(f"  FAILED: {e}")

    print("\nDone.")

if __name__ == '__main__':
    main()
