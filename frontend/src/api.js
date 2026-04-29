const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const fetchResults = async () => {
  const response = await fetch(`${API_BASE_URL}/reconcile?regenerate=true`);
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }
  return response.json();
};
