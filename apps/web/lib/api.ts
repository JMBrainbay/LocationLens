import type { CompareResponse } from "@nl-location-lens/contracts/src/compare";
import type { LocationProfile } from "@nl-location-lens/contracts/src/profile";
import type { SuggestResponse } from "@nl-location-lens/contracts/src/place";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";

type ApiError = {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
};

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store"
  });

  if (!response.ok) {
    let payload: ApiError | null = null;
    try {
      payload = (await response.json()) as ApiError;
    } catch {
      payload = null;
    }
    throw new Error(payload?.error.message ?? `Request failed (${response.status})`);
  }

  return (await response.json()) as T;
}

export function suggestPlaces(query: string): Promise<SuggestResponse> {
  return apiGet(`/api/places/suggest?q=${encodeURIComponent(query)}`);
}

export function resolveProfile(id: string): Promise<LocationProfile> {
  return apiGet(`/api/places/profile?id=${encodeURIComponent(id)}`);
}

export function comparePlaces(left: string, right: string): Promise<CompareResponse> {
  return apiGet(`/api/compare?left=${encodeURIComponent(left)}&right=${encodeURIComponent(right)}`);
}
