const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem("access_token");
  const orgId = localStorage.getItem("organisation_id"); // Used for organisation isolation

  const headers = new Headers(options.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (orgId) {
    headers.set("X-Organisation-ID", orgId);
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
      // Only 401 means the token is invalid/expired. 403 means forbidden but authenticated.
      if (window.location.pathname !== '/login') {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
      }
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `API Request failed with status ${response.status}`);
  }

  return response.json();
}
