import { useMsal } from "@azure/msal-react";
import { AuthButtons } from "./components/AuthButtons";
import { ExplorerPage } from "./pages/ExplorerPage";

export default function App() {
  const { accounts } = useMsal();
  const signedIn = accounts.length > 0;

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "24px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <h1 style={{ margin: 0 }}>Lakebase Entra ID Explorer</h1>
        <AuthButtons />
      </div>

      <hr style={{ margin: "16px 0" }} />

      {signedIn ? (
        <ExplorerPage />
      ) : (
        <p style={{ color: "#555" }}>
          Inicia sesión para explorar schemas y tablas.
        </p>
      )}
    </main>
  );
}
