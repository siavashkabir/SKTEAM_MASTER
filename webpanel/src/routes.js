import {
  IDENTIFIER_PATTERN,
  authorized,
  json,
  missingConfig,
  parseLimit,
} from "./http.js";
import * as supabase from "./supabase.js";
import * as turso from "./turso.js";

function requireConfig(env, names) {
  const missing = missingConfig(env, names);
  return missing.length
    ? json({ error: "missing config", missing }, 500)
    : null;
}

function readIdentifier(value) {
  try {
    const identifier = decodeURIComponent(value);
    return IDENTIFIER_PATTERN.test(identifier) ? identifier : null;
  } catch {
    return null;
  }
}

async function healthRoute(env) {
  const result = {
    ok: true,
    turso: "unconfigured",
    supabase: "unconfigured",
  };

  if (!missingConfig(env, ["TURSO_DATABASE_URL", "TURSO_AUTH_TOKEN"]).length) {
    try {
      await turso.turso(env, "SELECT 1 AS ok");
      result.turso = "ok";
    } catch (error) {
      console.error("Turso health check failed:", error);
      result.turso = "error";
      result.ok = false;
    }
  }

  if (!missingConfig(env, ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]).length) {
    try {
      result.supabase = (await supabase.health(env)) ? "ok" : "error";
    } catch (error) {
      console.error("Supabase health check failed:", error);
      result.supabase = "error";
    }
    if (result.supabase !== "ok") result.ok = false;
  }

  return json(result, result.ok ? 200 : 503);
}

export async function handleApi(request, env, url) {
  if (url.pathname === "/api/health") return healthRoute(env);
  if (!authorized(request, env)) return json({ error: "unauthorized" }, 401);

  if (url.pathname === "/api/turso/tables") {
    const configError = requireConfig(env, [
      "TURSO_DATABASE_URL",
      "TURSO_AUTH_TOKEN",
    ]);
    if (configError) return configError;
    return json({ tables: await turso.listTables(env) });
  }

  const tableMatch = url.pathname.match(
    /^\/api\/(turso\/table|supabase)\/([^/]+)$/,
  );
  if (!tableMatch) return json({ error: "not found" }, 404);

  const name = readIdentifier(tableMatch[2]);
  if (!name) return json({ error: "bad table name" }, 400);
  const limit = parseLimit(url.searchParams);

  if (tableMatch[1] === "turso/table") {
    const configError = requireConfig(env, [
      "TURSO_DATABASE_URL",
      "TURSO_AUTH_TOKEN",
    ]);
    if (configError) return configError;
    return json(await turso.readTable(env, name, limit));
  }

  const configError = requireConfig(env, ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]);
  if (configError) return configError;
  return json(await supabase.readTable(env, name, limit));
}
