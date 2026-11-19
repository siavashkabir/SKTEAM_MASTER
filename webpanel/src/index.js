import { json } from "./http.js";
import { handleApi } from "./routes.js";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith("/api/")) {
      return env.ASSETS
        ? env.ASSETS.fetch(request)
        : new Response("Not found", { status: 404 });
    }
    if (request.method !== "GET") return json({ error: "method not allowed" }, 405);
    try {
      return await handleApi(request, env, url);
    } catch (error) {
      console.error("Panel API request failed:", error);
      return json({ error: "upstream error" }, 502);
    }
  },
};
