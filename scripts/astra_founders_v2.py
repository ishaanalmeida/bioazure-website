"""
Generate a polished founder portrait using real photos as loose reference.
Uses features/likeness as inspiration, not literal compositing.
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

    print("Generating polished founders portrait...", flush=True)

    prompt = """Using these two reference photographs, create a cinematic, editorially polished portrait of these two people for a corporate website.

Setting: A sleek, modern biotech company headquarters lobby. Floor-to-ceiling glass windows with soft natural daylight streaming in from the left. Behind them, a blurred wall with a subtle illuminated company logo silhouette and a living green plant wall. The environment suggests innovation and science.

Composition: Wide 3:2 landscape format. The two people are positioned slightly off-center, standing naturally with relaxed confident body language. Shot from chest level up. Use a 85mm portrait lens look with f/2.0 bokeh — the background is beautifully blurred while they are tack-sharp.

The man (from Image 1): Preserve his exact facial features, hair color and style, skin tone, and facial structure. He wears a tailored navy suit jacket over a crisp light blue dress shirt, no tie. Natural, warm expression — approachable but authoritative.

The woman (from Image 2): Preserve her exact facial features, glasses style, hair color and texture, skin tone, earrings, and necklace. She wears a professional teal blazer over a burgundy turtleneck, consistent with her actual style. Confident, warm smile.

Lighting: Soft, directional key light from left (window light), subtle fill from right. Warm color temperature. Slight rim light separating them from the background. Magazine-quality lighting.

Quality: This should look like a photograph from Forbes or a biotech annual report. Ultra-high detail on faces. Natural skin texture, no over-smoothing. Photorealistic, not illustrated.

Constraints: No text, no watermarks, no logos. No artificial posing. The image should feel candid yet composed, like a great editorial photographer caught them in a natural moment."""

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

if __name__ == '__main__':
    main()
