"""
Generate a professional India distribution network map via GPT Image 2.5 Flare.
Properly structured prompt based on OpenAI's image prompting guide.
"""
import os, base64
from openai import OpenAI

def load_key():
    with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise RuntimeError('.env missing OPENAI_API_KEY')

PROMPT = """Create a professional infographic-style map of India showing a distribution network.

Background: Clean white background with very subtle light gray grid pattern.

Map: A detailed, accurate outline of India filled with a soft gradient from light blue (#E0F0FF) to white. The map should be geographically accurate with correct coastline shape, including the southern peninsula, western coast indent at Goa, eastern coast curve, and northern border shape.

City markers:
- "MUMBAI (HQ)" marked with a large green (#2D8A4E) filled circle with a white ring around it, positioned on the west coast. Add a small label box with white background.
- 12 smaller navy blue (#1E3A5F) filled circles at these cities: "Delhi" (north), "Kolkata" (east), "Chennai" (southeast coast), "Bangalore" (south interior), "Hyderabad" (central-south), "Pune" (near Mumbai), "Ahmedabad" (northwest), "Cochin" (southwest coast), "Goa" (west coast), "Bhubaneswar" (east), "Nagpur" (central), "Mangalore" (southwest coast).
- Each city has its name in small, clean, dark gray sans-serif text next to the marker.

Network lines: Thin, subtle dashed lines in light blue connecting Mumbai to each other city, suggesting a hub-and-spoke distribution network.

Style: Clean, modern, corporate infographic. Flat design, no 3D effects, no decorative elements. Professional and minimal like a consulting firm's slide.

Constraints: No watermarks, no extra decorative elements, no country names, no neighboring countries, no ocean labels. Only India and the distribution markers. Highly readable text labels. Use sans-serif typography throughout."""

def main():
    api_key = load_key()
    client = OpenAI(api_key=api_key, timeout=180)
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    out_path = os.path.join(base_dir, 'public', 'images', 'india-distribution-map.png')

    print("Generating India distribution map (1024x1024, high quality)...", flush=True)
    try:
        result = client.images.generate(
            model="gpt-image-2.5-flare",
            prompt=PROMPT,
            n=1,
            size="1024x1024",
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
