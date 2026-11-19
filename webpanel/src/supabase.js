export async function readTable(env, table, limit) {
  const baseUrl = env.SUPABASE_URL.replace(/\/$/, "");
  const response = await fetch(
    `${baseUrl}/rest/v1/${encodeURIComponent(table)}?select=*&limit=${limit}`,
    {
      headers: {
        apikey: env.SUPABASE_SERVICE_KEY,
        authorization: `Bearer ${env.SUPABASE_SERVICE_KEY}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Supabase request failed with HTTP ${response.status}`);
  }

  const body = await response.json().catch(() => null);
  if (!Array.isArray(body)) throw new Error("Supabase returned an invalid response");
  return body;
}

export async function health(env) {
  const response = await fetch(
    `${env.SUPABASE_URL.replace(/\/$/, "")}/rest/v1/`,
    {
      headers: { apikey: env.SUPABASE_SERVICE_KEY },
    },
  );
  return response.ok;
}
