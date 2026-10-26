const API_BASE = "";
export function token() { return localStorage.getItem("supplyguard_token"); }
export function saveSession(session) { localStorage.setItem("supplyguard_token", session.access_token); localStorage.setItem("supplyguard_user", JSON.stringify(session.user)); }
export function clearSession() { localStorage.removeItem("supplyguard_token"); localStorage.removeItem("supplyguard_user"); }
export async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (token()) headers.set("Authorization", `Bearer ${token()}`);
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    if (response.status === 401) clearSession();
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}
