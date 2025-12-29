import { Hono } from "@hono/hono";
import { serveStatic } from "@hono/hono/deno";

const app = new Hono();

app.all("/_proxy/R4", async (c) => {
  const query = new URL(c.req.url).searchParams.toString();
  const targetURL = "https://ci.line-apps.com/R4" +
    (query === "" ? "" : "?" + query);

  const response = await fetch(targetURL, {
    method: c.req.method,
    headers: c.req.raw.headers,
    body: c.req.method === "GET" || c.req.method === "HEAD"
      ? undefined
      : c.req.raw.body,
  });

  return new Response(response.body, {
    status: response.status,
    headers: Object.fromEntries(
      [
        ...response.headers.entries(),
        ["Access-Control-Allow-Origin", "*"],
      ],
    ),
    statusText: response.statusText,
  });
});

app.all("/_proxy/CHROME_GW/*", async (c) => {
  const query = new URL(c.req.url).searchParams.toString();
  const targetURL = "https://line-chrome-gw.line-apps.com" +
    c.req.path.replace("/_proxy/CHROME_GW", "") +
    (query === "" ? "" : "?" + query);

  const response = await fetch(targetURL, {
    method: c.req.method,
    headers: c.req.raw.headers,
    body: c.req.method === "GET" || c.req.method === "HEAD"
      ? undefined
      : c.req.raw.body,
  });

  return new Response(response.body, {
    status: response.status,
    headers: Object.fromEntries(
      [
        ...response.headers.entries(),
        ["Access-Control-Allow-Origin", "*"],
      ],
    ),
    statusText: response.statusText,
  });
});

app.use(
  "*",
  serveStatic({
    root: "./www",
  }),
);

app.notFound((c) =>
  c.redirect("/?fallbackBy=" + encodeURIComponent(c.req.path))
);

// 🔧 修正：環境に応じた起動設定
if (Deno.env.get("DENO_DEPLOYMENT_ID")) {
  // Deno Deploy環境
  Deno.serve(app.fetch);
} else if (Deno.args[0] === "localhost") {
  // ローカル開発環境（HTTPS）
  Deno.serve({
    port: 443,
    cert: await Deno.readTextFile("./secret/cert.pem"),
    key: await Deno.readTextFile("./secret/key.pem"),
  }, app.fetch);
} else {
  // その他の環境
  Deno.serve({ port: 8000 }, app.fetch);
}
