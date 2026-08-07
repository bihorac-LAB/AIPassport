/**
 * Embed mode.
 *
 * Canvas will eventually load these pages in an iframe. `?embed=1` (or simply being framed) collapses
 * global chrome to a compact context bar while keeping deep links and the AI tutor working.
 *
 * Note what this does NOT do: it carries no identity. Any future Canvas identity arrives from a
 * verified LTI 1.3 launch validated on the server, never from a URL parameter.
 */

export function isEmbedded(): boolean {
  if (typeof window === 'undefined') return false;
  const params = new URLSearchParams(window.location.search);
  if (params.get('embed') === '1' || params.get('embed') === 'true') return true;
  try {
    return window.self !== window.top;
  } catch {
    // Cross-origin framing throws on access — which itself means we are framed.
    return true;
  }
}

export function referrerKind(): 'direct' | 'canvas' | 'other' {
  if (typeof document === 'undefined' || !document.referrer) return 'direct';
  return /instructure\.com|canvas/i.test(document.referrer) ? 'canvas' : 'other';
}

/** Preserves ?embed=1 across in-app navigation so an embedded session stays embedded. */
export function withEmbed(path: string): string {
  if (!isEmbedded()) return path;
  const separator = path.includes('?') ? '&' : '?';
  return `${path}${separator}embed=1`;
}
