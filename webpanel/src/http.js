export const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
};

export function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: JSON_HEADERS,
  });
}

function safeEqual(left, right) {
  if (
    typeof left !== "string" ||
    typeof right !== "string" ||
    left.length !== right.length
  ) {
    return false;
  }

  let difference = 0;
  for (let index = 0; index < left.length; index += 1) {
    difference |= left.charCodeAt(index) ^ right.charCodeAt(index);
  }
  return difference === 0;
}

export function authorized(request, env) {
  if (!env.ADMIN_TOKEN) return false;
  const authorization = request.headers.get("authorization") || "";
  const match = authorization.match(/^Bearer\s+(.+)$/i);
  return Boolean(match && safeEqual(match[1], env.ADMIN_TOKEN));
}

export function missingConfig(env, names) {
  return names.filter((name) => !env[name]);
}

export function parseLimit(searchParams, defaultValue = 100, maximum = 500) {
  const requested = Number.parseInt(
    searchParams.get("limit") ?? String(defaultValue),
    10,
  );
  if (!Number.isFinite(requested)) return defaultValue;
  return Math.min(Math.max(requested, 1), maximum);
}

export const IDENTIFIER_PATTERN = /^[A-Za-z_][A-Za-z0-9_]{0,63}$/;
