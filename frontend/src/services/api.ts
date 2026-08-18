import { InteractionRequiredAuthError } from "@azure/msal-browser";
import { msalInstance } from "../auth/authProvider";
import { getApiScopes } from "../auth/msalConfig";

function apiBaseUrl(): string {
  return (import.meta.env.VITE_API_BASE_URL as string).replace(/\/+$/, "");
}

async function getAccessToken(): Promise<string> {
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length === 0) {
    throw new Error("Not signed in");
  }

  const scopes = getApiScopes();
  if (scopes.length === 0) {
    throw new Error("VITE_API_SCOPES is empty");
  }

  try {
    const result = await msalInstance.acquireTokenSilent({
      account: accounts[0],
      scopes,
    });
    return result.accessToken;
  } catch (e) {
    if (e instanceof InteractionRequiredAuthError) {
      // triggers redirect (simple MVP)
      await msalInstance.acquireTokenRedirect({
        account: accounts[0],
        scopes,
      });
    }
    throw e;
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const token = await getAccessToken();
  const res = await fetch(`${apiBaseUrl()}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }

  return (await res.json()) as T;
}
