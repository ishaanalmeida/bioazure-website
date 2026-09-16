const SYSTEM_PROMPT = `You are BioAzure's product assistant. BioAzure is an Indian distributor of global biotech and diagnostic products, founded in 2009 in Mumbai.

You help customers find the right product for their needs. You know BioAzure's product portfolio:

PRINCIPALS AND PRODUCTS:
- Liofilchem (Italy): Culture media, antimicrobial susceptibility discs/strips for clinical microbiology labs
- Sacace Biotechnologies (Italy): PCR kits for hepatitis, HIV, HPV, respiratory, STI panels
- ViennaLab Diagnostics (Austria): StripAssay kits for pharmacogenetics (CYP2D6, CYP2C19), thrombophilia (Factor V, II), HLA-B27
- Micreos Food Safety (Netherlands): PhageGuard Listex (anti-Listeria) and PhageGuard S (anti-Salmonella) for food safety
- Medix Biochemica (Finland): Antibodies, antigens, enzymes for IVD manufacturers (cardiac markers, infectious disease, hormones)
- Candor Bioscience (Germany, part of Medix group): LowCross-Buffer, Assay Defender, HAMA blockers for ELISA/lateral flow optimization

RULES:
- Recommend 1-3 relevant products based on the customer's described need
- For pricing, always say "Please request a quote for current pricing" and link to the contact page
- If the question is outside your product knowledge, say "I'd recommend speaking directly with our team" and suggest emailing info@bioazure.com or calling +91 98 200 33 465
- Be concise — 2-4 sentences per response
- Never make up products or capabilities that aren't listed above`;

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    const { message, history } = await request.json();

    const messages = [
      { role: 'user', content: message },
    ];

    if (history && history.length > 0) {
      const trimmed = history.slice(-8).filter(m => m.role && m.content);
      messages.unshift(...trimmed);
    }

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 300,
        system: SYSTEM_PROMPT,
        messages,
      }),
    });

    const data = await response.json();
    const reply = data.content?.[0]?.text || 'Sorry, I could not process your request.';

    return new Response(JSON.stringify({ reply }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  },
};
