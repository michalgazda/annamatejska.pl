// Decap CMS GitHub OAuth bridge for Cloudflare Workers.
// Endpoints (per Decap's proxy contract):
//   GET /auth?provider=github&site_id=<site>  -> redirect to GitHub authorize
//   GET /callback?code=...&state=...          -> exchange code, postMessage token
// Secrets (wrangler secret put): GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
// Optional var ALLOWED_REPO: "user/repo" — token exchange still succeeds for
// any GitHub user, so repo access control stays on GitHub's side (collaborators only).

const ALLOWED_ORIGINS = (globalThis.ALLOWED_ORIGINS || '')
  .split(',').map(s => s.trim()).filter(Boolean);

function html(body) {
  return new Response(body, { headers: { 'content-type': 'text/html; charset=utf-8' } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/auth') {
      const redirectUri = `${url.origin}/callback`;
      const state = crypto.randomUUID();
      const params = new URLSearchParams({
        client_id: env.GITHUB_CLIENT_ID,
        redirect_uri: redirectUri,
        scope: 'repo,user',
        state,
        allow_signup: 'true',
      });
      return Response.redirect(`https://github.com/login/oauth/authorize?${params}`, 302);
    }

    if (url.pathname === '/callback') {
      const code = url.searchParams.get('code');
      if (!code) return html('<h1>Missing code</h1>', { status: 400 });

      const res = await fetch('https://github.com/login/oauth/access_token', {
        method: 'POST',
        headers: { 'content-type': 'application/json', accept: 'application/json' },
        body: JSON.stringify({
          client_id: env.GITHUB_CLIENT_ID,
          client_secret: env.GITHUB_CLIENT_SECRET,
          code,
        }),
      });
      const data = await res.json();
      if (data.error) {
        return html(`<h1>Auth failed</h1><pre>${data.error}: ${data.error_description || ''}</pre>`, { status: 400 });
      }
      const token = data.access_token;
      const provider = 'github';
      const script = ALLOWED_ORIGINS.length
        ? `(${postMessageScript.toString()})(${JSON.stringify(token)}, ${JSON.stringify(provider)}, ${JSON.stringify(ALLOWED_ORIGINS)});`
        : `(${postMessageScript.toString()})(${JSON.stringify(token)}, ${JSON.stringify(provider)}, null);`;
      return html(`<!DOCTYPE html><html><body><p>Logging you in…</p><script>${script}</script></body></html>`);
    }

    return new Response('Decap OAuth bridge. Use /auth from the CMS panel.', { status: 404 });
  },
};

// Runs in the popup: sends the token to the opener (Decap CMS) and closes.
function postMessageScript(token, provider, allowedOrigins) {
  var opener = window.opener;
  if (!opener) { document.body.textContent = 'No opener window.'; return; }
  var targets = allowedOrigins || ['' + opener.location.origin];
  targets.forEach(function (o) {
    opener.postMessage(
      { authorization: { token: token, provider: provider } },
      o || '*'
    );
  });
  window.close();
}
