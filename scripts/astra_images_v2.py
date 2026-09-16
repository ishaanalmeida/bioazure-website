"""
Generate additional website images via GPT Image 2.5 Flare.
About page, cold-chain logistics, laboratory scenes.
"""
import os, base64
from openai import OpenAI

def load_key():
    with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise RuntimeError('.env missing OPENAI_API_KEY')

IMAGES = [
    {
        "name": "about-founders",
        "prompt": "Professional photograph of two Indian scientists in their 50s, a man and a woman, standing together in a modern office with biotech product displays behind them. They wear business casual clothing. Warm natural lighting, shallow depth of field. Corporate headshot style, high quality. No text overlays. Blue and white color tones.",
        "size": "1024x1024",
        "output": "public/images/about-founders.webp"
    },
    {
        "name": "cold-chain",
        "prompt": "Professional photograph of temperature-controlled shipping boxes and cold chain logistics for biotech products. Insulated boxes with temperature monitoring labels, dry ice visible, in a clean warehouse setting. Blue-tinted corporate photography style. No text, no brand logos.",
        "size": "1536x1024",
        "output": "public/images/cold-chain.webp"
    },
    {
        "name": "lab-scene",
        "prompt": "Professional photograph of a modern Indian diagnostic laboratory interior. Scientists working at clean benches with PCR machines and diagnostic equipment. Bright overhead lighting, blue and white tones. Wide angle, shallow depth of field. Corporate website photography style. No text overlays.",
        "size": "1536x1024",
        "output": "public/images/lab-scene.webp"
    },
    {
        "name": "partners-banner",
        "prompt": "Abstract professional banner image showing a world map with connection lines between Europe and India, suggesting global partnerships. Dark blue background with glowing green connection points on Italy, Austria, Netherlands, Finland, Germany, and India. Minimal, corporate, futuristic style. No text.",
        "size": "1536x1024",
        "output": "public/images/partners-banner.webp"
    },
]

def main():
    api_key = load_key()
    client = OpenAI(api_key=api_key, timeout=120)
    base_dir = os.path.join(os.path.dirname(__file__), '..')

    for i, img in enumerate(IMAGES):
        out_path = os.path.join(base_dir, img["output"])
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
                print(f"  Saved ({os.path.getsize(out_path)} bytes)")
            else:
                print(f"  WARNING: No image data returned")
        except Exception as e:
            print(f"  FAILED: {e}")

    print("\nDone.")

if __name__ == '__main__':
    main()
