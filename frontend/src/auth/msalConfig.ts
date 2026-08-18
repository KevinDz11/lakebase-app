import { Configuration, LogLevel } from "@azure/msal-browser";

function requireEnv(name: string): string {
  const v = import.meta.env[name] as string | undefined;
  if (!v) {
    throw new Error(`Missing env var ${name}. Check frontend/.env`);
  }
  return v;
}

export const msalConfig: Configuration = {
  auth: {
    clientId: requireEnv("VITE_ENTRA_CLIENT_ID"),
    authority: requireEnv("VITE_ENTRA_AUTHORITY"),
    redirectUri: requireEnv("VITE_ENTRA_REDIRECT_URI"),
  },
  cache: {
    cacheLocation: "sessionStorage",
  },
  system: {
    loggerOptions: {
      loggerCallback: (_level, message) => {
        // No tokens
        if (message.toLowerCase().includes("token")) return;
        // eslint-disable-next-line no-console
        console.debug(message);
      },
      logLevel: LogLevel.Warning,
      piiLoggingEnabled: false,
    },
  },
};

export function getApiScopes(): string[] {
  const raw = (import.meta.env.VITE_API_SCOPES as string | undefined) ?? "";
  return raw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}
