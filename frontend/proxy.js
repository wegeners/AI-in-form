// Save as proxy.js and run with: node proxy.js
const express = require("express");
const cors = require("cors");
const app = express();
app.use(cors());
app.use(express.json());

const OPENROUTER_API_KEY =
  "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";

app.post("/chat", async (req, res) => {
  try {
    const resp = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req.body),
    });
    const data = await resp.json();
    if (!resp.ok) {
      console.error("OpenRouter API error:", data);
      return res.status(resp.status).json({ error: data });
    }
    res.json(data);
  } catch (err) {
    console.error("Proxy error:", err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(3001, () => console.log("Proxy running on http://localhost:3001"));
