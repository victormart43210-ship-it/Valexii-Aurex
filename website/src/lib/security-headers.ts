/**
 * Baseline security headers applied to every server response.
 * frame-ancestors allows Lovable's editor preview; script-src is not restricted
 * because SSR hydration and JSON-LD use inline scripts (documented in docs/aurex-threat-model.md).
 */
export const SECURITY_HEADERS: Readonly<Record<string, string>> = {
  "Content-Security-Policy":
    "base-uri 'self'; object-src 'none'; form-action 'self'; frame-ancestors 'self' https://*.lovable.app https://*.lovable.dev https://lovable.dev",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
  "Cross-Origin-Resource-Policy": "same-site",
};

export function withSecurityHeaders(res: Response): Response {
  let out = res;
  try {
    for (const [k, v] of Object.entries(SECURITY_HEADERS))
      if (!out.headers.has(k)) out.headers.set(k, v);
  } catch {
    // Immutable headers: copy into a new response.
    const h = new Headers(res.headers);
    for (const [k, v] of Object.entries(SECURITY_HEADERS)) if (!h.has(k)) h.set(k, v);
    out = new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
  }
  return out;
}
