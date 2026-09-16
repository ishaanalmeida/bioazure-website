"""
BioAzure content generation via GPT-6 Astra.
Split into smaller calls to avoid server timeouts.
"""
import json, os, sys
from openai import OpenAI

def load_key():
    with open(os.path.join(os.path.dirname(__file__), '..', '.env')) as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise RuntimeError('.env missing OPENAI_API_KEY')

CONTEXT = """You are a senior B2B copywriter for BioAzure Technologies Pvt. Ltd., an Indian distributor of global biotech and IVD products. Founded 2009, Mumbai, by Dr. Adrian Almeida and Dr. Asha Kulkarni Almeida (both PhDs).

PRINCIPALS: Liofilchem (Italy, culture media + AST), Sacace (Italy, PCR kits), ViennaLab (Austria, StripAssay genotyping), Micreos (Netherlands, PhageGuard food safety), Medix Biochemica (Finland, IVD raw materials), Candor Bioscience (Germany/Medix group, immunoassay optimization).

CUSTOMERS: Referral labs, hospitals, govt orgs, food companies, IVD manufacturers, research institutions. Pan-India cold-chain distribution.

Tone: professional, warm, specific. B2B audience of lab managers, procurement heads, R&D directors. No fluff. Return ONLY valid JSON."""

CALLS = [
    {
        "key": "hero_and_why",
        "prompt": CONTEXT + """

Generate JSON:
{
  "hero": {"title": "main headline 6-10 words", "subtitle": "1-2 sentences"},
  "whyBioazure": {"headline": "short headline", "body": "2-3 sentences on PhD founders, technical depth, regulatory knowledge, pan-India cold-chain"}
}""",
        "tokens": 500
    },
    {
        "key": "about",
        "prompt": CONTEXT + """

Write the BioAzure founding story. Two scientists dreamed of bridging global biotech to India. Started Mumbai 2009, built partnerships across Europe, focused on making cutting-edge diagnostics accessible and affordable.

Generate JSON:
{
  "aboutStory": ["paragraph 1 founding moment", "paragraph 2 mission beyond importing", "paragraph 3 building global partnerships", "paragraph 4 BioAzure today"]
}""",
        "tokens": 800
    },
    {
        "key": "partners",
        "prompt": CONTEXT + """

Write 2-3 sentence descriptions for each principal emphasizing their clinical/commercial value to Indian customers.

Generate JSON:
{
  "partners": {
    "liofilchem": "description",
    "sacace": "description",
    "viennalab": "description",
    "micreos": "description",
    "medix": "description",
    "candor": "description"
  }
}""",
        "tokens": 800
    },
    {
        "key": "products",
        "prompt": CONTEXT + """

Write 2-3 sentence descriptions for each product family.

Generate JSON:
{
  "products": {
    "Culture Media": "description of Liofilchem's ready-to-use plates, tubes, selective/chromogenic media",
    "Antimicrobial Susceptibility Testing": "description of Liofilchem's AST discs, MIC strips, EUCAST/CLSI",
    "PCR Diagnostic Kits": "description of Sacace's real-time PCR for hepatitis, HIV, HPV, respiratory, STI",
    "StripAssay Kits": "description of ViennaLab's reverse-hybridization for pharmacogenetics, thrombophilia, HLA",
    "PhageGuard Solutions": "description of Micreos bacteriophage biocontrol for Listeria and Salmonella",
    "Immunodiagnostic Raw Materials": "description of Medix antibodies, antigens, enzymes for IVD manufacturing",
    "Immunoassay Optimization": "description of Candor's LowCross-Buffer, Assay Defender, HAMA blockers"
  }
}""",
        "tokens": 800
    },
    {
        "key": "applications_and_seo",
        "prompt": CONTEXT + """

Generate JSON with application area descriptions and SEO meta descriptions (max 155 chars each):
{
  "applications": {
    "clinical-microbiology": "2-3 sentence description",
    "molecular-diagnostics": "2-3 sentence description",
    "food-safety": "2-3 sentence description",
    "ivd-raw-materials": "2-3 sentence description"
  },
  "seoDescriptions": {
    "home": "155 char max",
    "about": "155 char max",
    "products": "155 char max",
    "partners": "155 char max",
    "contact": "155 char max",
    "applications": "155 char max",
    "clinical-microbiology": "155 char max",
    "molecular-diagnostics": "155 char max",
    "food-safety": "155 char max",
    "ivd-raw-materials": "155 char max"
  }
}""",
        "tokens": 1000
    }
]

def main():
    api_key = load_key()
    client = OpenAI(api_key=api_key, timeout=120)
    merged = {}
    total_in = total_out = 0

    for i, call in enumerate(CALLS):
        print(f"[{i+1}/{len(CALLS)}] Generating {call['key']}...", flush=True)
        try:
            r = client.chat.completions.create(
                model="gpt-6-astra",
                messages=[{"role": "user", "content": call["prompt"]}],
                max_completion_tokens=call["tokens"],
            )
            raw = r.choices[0].message.content
            # Strip markdown code fences if present
            if raw.strip().startswith("```"):
                raw = raw.strip().split("\n", 1)[1].rsplit("```", 1)[0]
            chunk = json.loads(raw)
            merged.update(chunk)
            total_in += r.usage.prompt_tokens
            total_out += r.usage.completion_tokens
            print(f"  OK ({r.usage.prompt_tokens}+{r.usage.completion_tokens} tokens)")
        except Exception as e:
            print(f"  FAILED: {e}")
            sys.exit(1)

    out_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'astra-copy.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Total: {total_in} in + {total_out} out = {total_in+total_out} tokens")
    print(f"Saved to {out_path}")

if __name__ == '__main__':
    main()
