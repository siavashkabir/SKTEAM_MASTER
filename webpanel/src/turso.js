function databaseUrl(env) {
  return env.TURSO_DATABASE_URL.replace(/^libsql:\/\//, "https://").replace(
    /\/$/,
    "",
  );
}

function argument(value) {
  if (value === null || value === undefined) return { type: "null" };
  if (typeof value === "number") {
    return {
      type: Number.isInteger(value) ? "integer" : "float",
      value: String(value),
    };
  }
  if (typeof value === "bigint") return { type: "integer", value: String(value) };
  return { type: "text", value: String(value) };
}

function cell(value) {
  if (!value || typeof value !== "object" || !("type" in value)) return value;
  if (value.type === "null") return null;
  if (value.type === "integer") return Number(value.value);
  if (value.type === "float") return Number(value.value);
  if (value.type === "blob") return value.value;
  return value.value;
}

export async function turso(env, sql, args = []) {
  const response = await fetch(`${databaseUrl(env)}/v2/pipeline`, {
    method: "POST",
    headers: {
      authorization: `Bearer ${env.TURSO_AUTH_TOKEN}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      requests: [
        {
          type: "execute",
          stmt: { sql, args: args.map(argument) },
        },
        { type: "close" },
      ],
    }),
  });

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(`Turso request failed with HTTP ${response.status}`);
  }

  const result = body?.results?.[0];
  if (!result || result.type === "error") {
    throw new Error(result?.error?.message || "Turso query failed");
  }

  const queryResult = result.response?.result;
  if (!queryResult) throw new Error("Turso returned an invalid response");

  const columns = queryResult.cols.map((column) => column.name);
  const rows = queryResult.rows.map((row) =>
    Object.fromEntries(row.map((value, index) => [columns[index], cell(value)])),
  );
  return { columns, rows };
}

export async function listTables(env) {
  const result = await turso(
    env,
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
  );
  return result.rows.map((row) => row.name);
}

export async function readTable(env, name, limit) {
  return turso(env, `SELECT * FROM "${name}" LIMIT ${limit}`);
}
