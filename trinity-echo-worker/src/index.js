// Trinity Echo Worker — DEPRECATED
// Worker submission is deprecated. Use the static Echo submission page instead.
// See: /echoes/submit for the current submission path.
// See: /docs/claim-gate for claim gate documentation.

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    // All submissions are redirected to the static page.
    const current_submission_path = '/echoes/submit';
    const claim_gate_required_for_technical_claims = true;
    const claim_gate_docs = '/docs/claim-gate';

    const body = JSON.stringify({
      status: 'deprecated',
      message: 'Worker submission is deprecated. Use the static Echo submission page.',
      current_submission_path,
      claim_gate_required_for_technical_claims,
      claim_gate_docs,
      redirect: current_submission_path,
    });

    return new Response(body, {
      status: 410,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  },
};
