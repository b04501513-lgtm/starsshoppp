const https = require("https");

const JB_BIN_ID = process.env.JB_BIN_ID;
const JB_KEY    = process.env.JB_API_KEY;
const SS_SECRET = process.env.SS_API_KEY || "stars_store_secret_2024";

function jsonbinReq(method, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const options = {
      hostname: "api.jsonbin.io",
      path: "/v3/b/" + JB_BIN_ID,
      method: method,
      headers: {
        "Content-Type": "application/json",
        "X-Master-Key": JB_KEY,
        "X-Bin-Meta": "false",
        ...(data ? { "Content-Length": Buffer.byteLength(data) } : {})
      }
    };
    const req = https.request(options, (res) => {
      let raw = "";
      res.on("data", c => raw += c);
      res.on("end", () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(raw) }); }
        catch(e) { reject(new Error("Parse xato: " + raw.slice(0, 200))); }
      });
    });
    req.on("error", reject);
    if (data) req.write(data);
    req.end();
  });
}

exports.handler = async (event) => {
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, x-api-key",
    "Content-Type": "application/json"
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers: cors, body: "" };
  }

  const key = (event.headers || {})["x-api-key"] || "";
  if (key !== SS_SECRET) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: "Unauthorized" }) };
  }

  try {
    if (event.httpMethod === "GET") {
      const r = await jsonbinReq("GET");
      const record = r.body.record !== undefined ? r.body.record : r.body;
      return { statusCode: 200, headers: cors, body: JSON.stringify({ ok: true, record }) };
    }

    if (event.httpMethod === "POST") {
      const body = JSON.parse(event.body || "{}");
      await jsonbinReq("PUT", body);
      return { statusCode: 200, headers: cors, body: JSON.stringify({ ok: true }) };
    }

    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: "Method not allowed" }) };

  } catch (err) {
    return { statusCode: 500, headers: cors, body: JSON.stringify({ error: err.message }) };
  }
};
