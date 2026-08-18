import { useMsal } from "@azure/msal-react";
import { getApiScopes } from "../auth/msalConfig";

export function AuthButtons() {
  const { instance, accounts } = useMsal();
  const signedIn = accounts.length > 0;

  const scopes = getApiScopes();

  if (!signedIn) {
    return (
      <button
        onClick={() =>
          instance.loginRedirect({
            scopes,
          })
        }
      >
        Sign in
      </button>
    );
  }

  return (
    <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
      <span style={{ fontSize: 14 }}>{accounts[0]?.username}</span>
      <button onClick={() => instance.logoutRedirect()}>Sign out</button>
    </div>
  );
}
