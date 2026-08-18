import { useEffect, useMemo, useState } from "react";
import { apiGet } from "../services/api";

type TableInfo = { table_name: string; table_type: string };
type ColumnInfo = {
  column_name: string;
  data_type: string;
  is_nullable: string;
  ordinal_position: number;
};
type Row = Record<string, unknown>;

export function ExplorerPage() {
  const [schemas, setSchemas] = useState<string[]>([]);
  const [schema, setSchema] = useState<string>("");
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [table, setTable] = useState<string>("");
  const [columns, setColumns] = useState<ColumnInfo[]>([]);
  const [rows, setRows] = useState<Row[]>([]);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const selectedTable = useMemo(() => {
    if (!schema || !table) return null;
    return { schema, table };
  }, [schema, table]);

  useEffect(() => {
    let cancelled = false;
    setError("");
    setLoading(true);
    apiGet<string[]>("/api/explorer/schemas")
      .then((data) => {
        if (cancelled) return;
        setSchemas(data);
        if (data.length && !schema) setSchema(data[0]);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!schema) return;
    let cancelled = false;
    setError("");
    setLoading(true);
    setTables([]);
    setTable("");
    apiGet<TableInfo[]>(
      `/api/explorer/schemas/${encodeURIComponent(schema)}/tables`,
    )
      .then((data) => {
        if (cancelled) return;
        setTables(data);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [schema]);

  useEffect(() => {
    if (!selectedTable) return;
    let cancelled = false;
    setError("");
    setLoading(true);
    Promise.all([
      apiGet<ColumnInfo[]>(
        `/api/explorer/schemas/${encodeURIComponent(
          selectedTable.schema,
        )}/tables/${encodeURIComponent(selectedTable.table)}/describe`,
      ),
      apiGet<Row[]>(
        `/api/explorer/schemas/${encodeURIComponent(
          selectedTable.schema,
        )}/tables/${encodeURIComponent(selectedTable.table)}/preview?limit=20`,
      ),
    ])
      .then(([cols, preview]) => {
        if (cancelled) return;
        setColumns(cols);
        setRows(preview);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [selectedTable]);

  return (
    <section style={{ display: "grid", gap: 16 }}>
      {error ? (
        <div
          style={{ padding: 12, background: "#fee", border: "1px solid #f99" }}
        >
          {error}
        </div>
      ) : null}

      <div
        style={{
          display: "flex",
          gap: 12,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <span>Schema</span>
          <select
            value={schema}
            onChange={(e) => setSchema(e.target.value)}
            disabled={loading}
          >
            {schemas.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <span>Table</span>
          <select
            value={table}
            onChange={(e) => setTable(e.target.value)}
            disabled={loading}
          >
            <option value="">—</option>
            {tables.map((t) => (
              <option key={t.table_name} value={t.table_name}>
                {t.table_name} ({t.table_type})
              </option>
            ))}
          </select>
        </label>
      </div>

      {selectedTable ? (
        <div style={{ display: "grid", gap: 16 }}>
          <div>
            <h3 style={{ margin: "8px 0" }}>Columns</h3>
            <table style={{ borderCollapse: "collapse", width: "100%" }}>
              <thead>
                <tr>
                  {["name", "type", "nullable", "pos"].map((h) => (
                    <th
                      key={h}
                      style={{
                        textAlign: "left",
                        borderBottom: "1px solid #ddd",
                        padding: 8,
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {columns.map((c) => (
                  <tr key={c.column_name}>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>
                      {c.column_name}
                    </td>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>
                      {c.data_type}
                    </td>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>
                      {c.is_nullable}
                    </td>
                    <td style={{ borderBottom: "1px solid #eee", padding: 8 }}>
                      {c.ordinal_position}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div>
            <h3 style={{ margin: "8px 0" }}>Preview rows</h3>
            <pre
              style={{
                background: "#111",
                color: "#eee",
                padding: 12,
                overflow: "auto",
                maxHeight: 260,
              }}
            >
              {JSON.stringify(rows, null, 2)}
            </pre>
          </div>
        </div>
      ) : (
        <div style={{ color: "#555" }}>
          Selecciona una tabla para ver columnas y preview.
        </div>
      )}
    </section>
  );
}
