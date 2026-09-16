"""
Generate a professional founder scene using real photos as reference input.
Uses GPT Image 2.5 Flare edit endpoint with founder photos.
"""
import os, base64
from openai import OpenAI
from pathlib import Path

def load_key():
    with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise RuntimeError('.env missing OPENAI_API_KEY')

def main():
    api_key = load_key()
    client = OpenAI(api_key=api_key, timeout=180)
    base_dir = Path(__file__).parent.parent

    adrian_path = base_dir / 'public' / 'images' / 'founder-adrian.jpg'
    asha_path = base_dir / 'public' / 'images' / 'founder-asha.jpg'
    out_path = base_dir / 'public' / 'images' / 'about-founders.webp'

    print("Generating founders scene with real photos as reference...", flush=True)
    print(f"  Input 1: {adrian_path} ({adrian_path.stat().st_size} bytes)", flush=True)
    print(f"  Input 2: {asha_path} ({asha_path.stat().st_size} bytes)", flush=True)

    prompt = """Create a professional corporate portrait photograph of these two people standing together in a modern biotech office.

Scene: They are standing side by side in a well-lit modern office. Behind them, shelves display biotech product boxes and laboratory equipment. The lighting is warm and professional, similar to a corporate annual report photograph.

Composition: Medium shot from the waist up. The man (Image 1) on the left, the woman (Image 2) on the right. Both looking at the camera with confident, approachable expressions.

Style: High-quality corporate photography. Shallow depth of field with the background slightly blurred. Clean, professional, warm color tones with blue and white accents in the background. No text overlays, no watermarks.

Constraints: Preserve the exact facial features, skin tone, hair, and glasses of both people from the reference photos. Do not alter their appearance. Professional business attire."""

    try:
        result = client.images.edit(
            model="gpt-image-2.5-flare",
            image=[
                open(adrian_path, "rb"),
                open(asha_path, "rb"),
            ],
            prompt=prompt,
            size="1536x1024",
            quality="high",
        )

        image_data = result.data[0]
        if hasattr(image_data, 'b64_json') and image_data.b64_json:
            img_bytes = base64.b64decode(image_data.b64_json)
            with open(out_path, 'wb') as f:
                f.write(img_bytes)
            print(f"Saved ({len(img_bytes)} bytes)")
        elif hasattr(image_data, 'url') and image_data.url:
            import urllib.request
            urllib.request.urlretrieve(image_data.url, out_path)
            print(f"Saved ({os.path.getsize(out_path)} bytes)")
        else:
            print("WARNING: No image data returned")

    except Exception as e:
        print(f"FAILED: {e}")
        print("Trying alternative approach with single combined prompt...", flush=True)
        try:
            # Fallback: try with just one image at a time or different params
            result = client.images.edit(
                model="gpt-image-2.5-flare",
                image=[
                    open(adrian_path, "rb"),
                    open(asha_path, "rb"),
                ],
                prompt=prompt,
                size="1024x1024",
            )
            image_data = result.data[0]
            if hasattr(image_data, 'b64_json') and image_data.b64_json:
                img_bytes = base64.b64decode(image_data.b64_json)
                with open(out_path, 'wb') as f:
                    f.write(img_bytes)
                print(f"Saved fallback ({len(img_bytes)} bytes)")
            elif hasattr(image_data, 'url') and image_data.url:
                import urllib.request
                urllib.request.urlretrieve(image_data.url, out_path)
                print(f"Saved fallback ({os.path.getsize(out_path)} bytes)")
        except Exception as e2:
            print(f"Fallback also FAILED: {e2}")

if __name__ == '__main__':
    main()
