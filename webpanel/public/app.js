const element = (id) => document.getElementById(id);
const status = element("status");
const token = element("token");
const output = element("out");
const table = element("table");

token.value = sessionStorage.getItem("admin-token") || "";

async function api(path) {
  const response = await fetch(path, {
    headers: { authorization: `Bearer ${token.value}` },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.missing ? ` (${body.missing.join(", ")})` : "";
    throw new Error(`${body.error || `HTTP ${response.status}`}${detail}`);
  }
  return body;
}

function render(rows) {
  output.replaceChildren();
  if (!rows.length) {
    output.textContent = "(empty)";
    return;
  }

  const columns = Object.keys(rows[0]);
  const heading = output.createTHead().insertRow();
  for (const column of columns) {
    const cell = document.createElement("th");
    cell.textContent = column;
    heading.appendChild(cell);
  }

  const body = output.createTBody();
  for (const row of rows) {
    const tableRow = body.insertRow();
    for (const column of columns) tableRow.insertCell().textContent = row[column] ?? "";
  }
}

async function refreshHealth() {
  try {
    const data = await api("/api/health");
    status.textContent = `Turso: ${data.turso} | Supabase: ${data.supabase}`;
  } catch (error) {
    status.textContent = `health error: ${error.message}`;
  }
}

element("save").addEventListener("click", () => {
  sessionStorage.setItem("admin-token", token.value);
  status.textContent = "رمز وارد شد؛ اکنون داده‌ها را بارگذاری کنید.";
});

element("list").addEventListener("click", async () => {
  try {
    const data = await api("/api/turso/tables");
    render(data.tables.map((name) => ({ table: name })));
  } catch (error) {
    window.alert(error.message);
  }
});

element("load").addEventListener("click", async () => {
  const name = table.value.trim();
  if (!name) return window.alert("نام جدول را وارد کنید.");

  try {
    const source = element("src").value;
    const path =
      source === "turso"
        ? `/api/turso/table/${encodeURIComponent(name)}`
        : `/api/supabase/${encodeURIComponent(name)}`;
    const data = await api(path);
    render(Array.isArray(data) ? data : data.rows);
  } catch (error) {
    window.alert(error.message);
  }
});

refreshHealth();
