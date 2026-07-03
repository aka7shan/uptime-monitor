const BASE = "/api";

async function request(path, options) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

export function listMonitors() {
  return request("/monitors");
}

export function addMonitor(url, name) {
  return request("/monitors", {
    method: "POST",
    body: JSON.stringify({ url, name: name || null }),
  });
}

export function deleteMonitor(id) {
  return request(`/monitors/${id}`, { method: "DELETE" });
}
