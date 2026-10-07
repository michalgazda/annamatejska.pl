// Decap CMS GitHub OAuth bridge for Cloudflare Workers.
// Secrets: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
// Var: ALLOWED_ORIGINS (comma-separated exact CMS origins).

function allowedOrigins(env) {
  return (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
}

function html(body, status = 200, headers = {}) {
  return new Response(body, {
    status,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'x-content-type-options': 'nosniff',
      'cache-control': 'no-store',
      ...headers,
    },
  });
}

function cookieValue(request, name) {
  const entry = (request.headers.get('Cookie') || '').split(';')
    .map(value => value.trim()).find(value => value.startsWith(`${name}=`));
  return entry ? decodeURIComponent(entry.slice(name.length + 1)) : null;
}

function popupPage({ token, error, origins }) {
  const message = error
    ? `authorization:github:error:${JSON.stringify({ message: error })}`
    : `authorization:github:success:${JSON.stringify({ token, provider: 'github' })}`;
  const safeMessage = JSON.stringify(message).replace(/</g, '\\u003c');
  const safeOrigins = JSON.stringify(origins);
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>GitHub sign-in</title></head><body><p>Completing sign-in…</p><script>
(() => {
  const allowed = ${safeOrigins};
  const result = ${safeMessage};
  const opener = window.opener;
  if (!opener) { document.body.textContent = 'Sign-in window unavailable. Close this tab and retry from the CMS.'; return; }
  let completed = false;
  const onHandshake = event => {
    if (completed || event.source !== opener || !allowed.includes(event.origin) || event.data !== 'authorizing:github') return;
    completed = true;
    window.removeEventListener('message', onHandshake);
    opener.postMessage(result, event.origin);
    setTimeout(() => window.close(), 250);
  };
  window.addEventListener('message', onHandshake);
  for (const origin of allowed) opener.postMessage('authorizing:github', origin);
  setTimeout(() => {
    if (!completed) document.body.textContent = 'Sign-in could not be completed. Close this window and retry from the CMS.';
  }, 60000);
})();
</script></body></html>`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origins = allowedOrigins(env);
    if (request.method !== 'GET') {
      return new Response('Method not allowed', { status: 405, headers: { Allow: 'GET' } });
    }

    if (url.pathname === '/auth') {
      if (!env.GITHUB_CLIENT_ID) return new Response('OAuth client is not configured', { status: 503 });
      const provider = url.searchParams.get('provider') || 'github';
      if (provider !== 'github') return new Response('Unsupported OAuth provider', { status: 400 });
      const state = crypto.randomUUID();
      const params = new URLSearchParams({
        client_id: env.GITHUB_CLIENT_ID,
        redirect_uri: `${url.origin}/callback`,
        scope: 'repo,user',
        state,
        allow_signup: 'true',
      });
      return new Response(null, {
        status: 302,
        headers: {
          Location: `https://github.com/login/oauth/authorize?${params}`,
          'Set-Cookie': `decap_oauth_state=${encodeURIComponent(state)}; Path=/callback; HttpOnly; Secure; SameSite=Lax; Max-Age=600`,
          'Cache-Control': 'no-store',
        },
      });
    }

    if (url.pathname === '/callback') {
      const clearCookie = 'decap_oauth_state=; Path=/callback; HttpOnly; Secure; SameSite=Lax; Max-Age=0';
      const state = url.searchParams.get('state');
      if (!state || !cookieValue(request, 'decap_oauth_state') || state !== cookieValue(request, 'decap_oauth_state')) {
        return html(popupPage({ error: 'OAuth state check failed. Restart sign-in from the CMS.', origins }), 400, { 'Set-Cookie': clearCookie });
      }
      if (url.searchParams.has('error')) {
        const message = url.searchParams.get('error_description') || url.searchParams.get('error');
        return html(popupPage({ error: message, origins }), 400, { 'Set-Cookie': clearCookie });
      }
      const code = url.searchParams.get('code');
      if (!code || !env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET || origins.length === 0) {
        return html(popupPage({ error: 'OAuth Worker is missing required configuration.', origins }), 503, { 'Set-Cookie': clearCookie });
      }
      const exchange = await fetch('https://github.com/login/oauth/access_token', {
        method: 'POST',
        headers: { 'content-type': 'application/json', accept: 'application/json', 'user-agent': 'annamatejska-decap-oauth' },
        body: JSON.stringify({ client_id: env.GITHUB_CLIENT_ID, client_secret: env.GITHUB_CLIENT_SECRET, code }),
      });
      const result = await exchange.json();
      if (!exchange.ok || result.error || !result.access_token) {
        return html(popupPage({ error: result.error_description || result.error || `GitHub token exchange failed (${exchange.status})`, origins }), 502, { 'Set-Cookie': clearCookie });
      }
      return html(popupPage({ token: result.access_token, origins }), 200, {
        'Set-Cookie': clearCookie,
        'Referrer-Policy': 'no-referrer',
        'Content-Security-Policy': "default-src 'none'; script-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'",
      });
    }

    return new Response('Decap OAuth bridge. Use /auth from the CMS panel.', { status: 404 });
  },
};
