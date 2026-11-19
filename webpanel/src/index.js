// SK.TEAM panel API — Cloudflare Worker.
// Secrets: ADMIN_TOKEN, TURSO_AUTH_TOKEN, SUPABASE_SERVICE_KEY
// Vars: TURSO_DATABASE_URL, SUPABASE_URL

const JSON_HEADERS = { "content-type": "application/json; charset=utf-8" };

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: JSON_HEADERS });

function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

function authorized(request, env) {
  if (!env.ADMIN_TOKEN) return false;
  const h = request.headers.get("authorization") || "";
  return safeEqual(h.replace(/^Bearer\s+/i, ""), env.ADMIN_TOKEN);
}

function missing(env, names) {
  return names.filter((n) => !env[n]);
}

function tursoHttpUrl(env) {
  return env.TURSO_DATABASE_URL.replace(/^libsql:\/\//, "https://").replace(/\/$/, "");
}

function cell(v) {
  if (v && typeof v === "object" && "type" in v) {
    if (v.type === "null") return null;
    if (v.type === "integer") return Number(v.value);
    if (v.type === "float") return v.value;
    return v.value;
  }
  return v;
}

async function turso(env, sql, args = []) {
  const res = await fetch(`${tursoHttpUrl(env)}/v2/pipeline`, {
    method: "POST",
    headers: { authorization: `Bearer ${env.TURSO_AUTH_TOKEN}`, "content-type": "application/json" },
    body: JSON.stringify({
      requests: [
        { type: "execute", stmt: { sql, args: args.map((v) => ({ type: "text", value: String(v) })) } },
        { type: "close" },
      ],
    }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`Turso HTTP ${res.status}: ${JSON.stringify(body).slice(0, 300)}`);
  const first = body.results && body.results[0];
  if (!first || first.type === "error") {
    throw new Error(first && first.error ? first.error.message : "Turso error");
  }
  const r = first.response.result;
  const cols = r.cols.map((c) => c.name);
  const rows = r.rows.map((row) => Object.fromEntries(row.map((v, i) => [cols[i], cell(v)])));
  return { columns: cols, rows };
}

async function supabase(env, table, query) {
  const res = await fetch(`${env.SUPABASE_URL.replace(/\/$/, "")}/rest/v1/${encodeURIComponent(table)}?${query}`, {
    headers: {
      apikey: env.SUPABASE_SERVICE_KEY,
      authorization: `Bearer ${env.SUPABASE_SERVICE_KEY}`,
    },
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`Supabase HTTP ${res.status}: ${text.slice(0, 300)}`);
  return JSON.parse(text);
}

const IDENT = /^[A-Za-z_][A-Za-z0-9_]{0,63}$/;

async function handleApi(request, env, url) {
  const path = url.pathname;

  if (path === "/api/health") {
    const out = { ok: true, turso: "unconfigured", supabase: "unconfigured" };
    if (!missing(env, ["TURSO_DATABASE_URL", "TURSO_AUTH_TOKEN"]).length) {
      try { await turso(env, "SELECT 1 AS ok"); out.turso = "ok"; }
      catch (e) { out.turso = "error"; out.ok = false; }
    }
    if (!missing(env, ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]).length) {
      try {
        const r = await fetch(`${env.SUPABASE_URL.replace(/\/$/, "")}/rest/v1/`, {
          headers: { apikey: env.SUPABASE_SERVICE_KEY },
        });
        out.supabase = r.ok ? "ok" : "error";
        if (!r.ok) out.ok = false;
      } catch (e) { out.supabase = "error"; out.ok = false; }
    }
    return json(out, out.ok ? 200 : 503);
  }

  if (!authorized(request, env)) return json({ error: "unauthorized" }, 401);

  if (path === "/api/turso/tables") {
    const m = missing(env, ["TURSO_DATABASE_URL", "TURSO_AUTH_TOKEN"]);
    if (m.length) return json({ error: "missing config", missing: m }, 500);
    const r = await turso(env, "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name");
    return json({ tables: r.rows.map((x) => x.name) });
  }

  const t = path.match(/^\/api\/turso\/table\/([^/]+)$/);
  if (t) {
    const m = missing(env, ["TURSO_DATABASE_URL", "TURSO_AUTH_TOKEN"]);
    if (m.length) return json({ error: "missing config", missing: m }, 500);
    const name = decodeURIComponent(t[1]);
    if (!IDENT.test(name)) return json({ error: "bad table name" }, 400);
    const limit = Math.min(Math.max(parseInt(url.searchParams.get("limit") || "100", 10) || 100, 1), 500);
    const r = await turso(env, `SELECT * FROM "${name}" LIMIT ${limit}`);
    return json(r);
  }

  const s = path.match(/^\/api\/supabase\/([^/]+)$/);
  if (s) {
    const m = missing(env, ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]);
    if (m.length) return json({ error: "missing config", missing: m }, 500);
    const name = decodeURIComponent(s[1]);
    if (!IDENT.test(name)) return json({ error: "bad table name" }, 400);
    const limit = Math.min(Math.max(parseInt(url.searchParams.get("limit") || "100", 10) || 100, 1), 500);
    return json(await supabase(env, name, `select=*&limit=${limit}`));
  }

  return json({ error: "not found" }, 404);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith("/api/")) {
      return env.ASSETS ? env.ASSETS.fetch(request) : new Response("Not found", { status: 404 });
    }
    if (request.method !== "GET") return json({ error: "method not allowed" }, 405);
    try {
      return await handleApi(request, env, url);
    } catch (e) {
      console.error(e && e.stack ? e.stack : e);
      return json({ error: "upstream error", detail: String(e && e.message ? e.message : e) }, 502);
    }
  },
};
