const BASE_URL = "http://localhost:8000/api";

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem("access_token");

  const headers = new Headers(options.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (response.status === 401 || response.status === 403) {
      if (window.location.pathname !== '/login') {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
      }
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "API Request failed");
  }

  return response.json();
}
