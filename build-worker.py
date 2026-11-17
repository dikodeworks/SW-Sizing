#!/usr/bin/env python3
"""Regenerate worker.js from index.html and the PWA assets.

Run this after every change to index.html, manifest.webmanifest, sw.js,
favicon.svg or the PNG icons, then deploy worker.js to Cloudflare Workers.
"""

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

ASSETS = {
    "/icon-192.png": "icon-192.png",
    "/icon-512.png": "icon-512.png",
    "/apple-touch-icon.png": "apple-touch-icon.png",
}


def js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def main() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    manifest = (ROOT / "manifest.webmanifest").read_text(encoding="utf-8")
    service_worker = (ROOT / "sw.js").read_text(encoding="utf-8")
    favicon = (ROOT / "favicon.svg").read_text(encoding="utf-8")
    icons = {
        route: base64.b64encode((ROOT / filename).read_bytes()).decode("ascii")
        for route, filename in ASSETS.items()
    }

    parts = [
        "// Cloudflare Worker — serves the SolarWinds Sizing calculator and its PWA assets",
        "const HTML = " + js_string(html) + ";",
        "const MANIFEST = " + js_string(manifest) + ";",
        "const SERVICE_WORKER = " + js_string(service_worker) + ";",
        "const FAVICON = " + js_string(favicon) + ";",
        "const ICON_192_B64 = " + js_string(icons["/icon-192.png"]) + ";",
        "const ICON_512_B64 = " + js_string(icons["/icon-512.png"]) + ";",
        "const APPLE_TOUCH_B64 = " + js_string(icons["/apple-touch-icon.png"]) + ";",
        WORKER_TEMPLATE,
    ]
    (ROOT / "worker.js").write_text("\n".join(parts), encoding="utf-8")
    print("worker.js regenerated from index.html and PWA assets")


WORKER_TEMPLATE = r"""
function b64ToBytes(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

const PNG_HEADERS = {
  "cache-control": "public, max-age=86400",
  "x-content-type-options": "nosniff"
};

const ASSETS = {
  "/manifest.webmanifest": {
    body: MANIFEST,
    headers: { "content-type": "application/manifest+json;charset=UTF-8", "cache-control": "public, max-age=3600" }
  },
  "/favicon.svg": {
    body: FAVICON,
    headers: { "content-type": "image/svg+xml;charset=UTF-8", "cache-control": "public, max-age=86400" }
  },
  "/icon-192.png": {
    body: b64ToBytes(ICON_192_B64),
    headers: Object.assign({ "content-type": "image/png" }, PNG_HEADERS)
  },
  "/icon-512.png": {
    body: b64ToBytes(ICON_512_B64),
    headers: Object.assign({ "content-type": "image/png" }, PNG_HEADERS)
  },
  "/apple-touch-icon.png": {
    body: b64ToBytes(APPLE_TOUCH_B64),
    headers: Object.assign({ "content-type": "image/png" }, PNG_HEADERS)
  }
};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const method = request.method;

    if (method !== "GET" && method !== "HEAD") {
      return new Response("Method Not Allowed", { status: 405, headers: { "allow": "GET, HEAD" } });
    }

    if (url.pathname === "/sw.js") {
      return new Response(method === "HEAD" ? null : SERVICE_WORKER, {
        headers: {
          "content-type": "application/javascript;charset=UTF-8",
          "cache-control": "no-cache",
          "service-worker-allowed": "/",
          "x-content-type-options": "nosniff"
        }
      });
    }

    const asset = ASSETS[url.pathname];
    if (asset) {
      return new Response(method === "HEAD" ? null : asset.body, { headers: asset.headers });
    }

    if (url.pathname === "/favicon.ico") {
      return new Response(method === "HEAD" ? null : b64ToBytes(ICON_192_B64), { headers: Object.assign({ "content-type": "image/png" }, PNG_HEADERS) });
    }

    return new Response(method === "HEAD" ? null : HTML, {
      headers: {
        "content-type": "text/html;charset=UTF-8",
        "cache-control": "no-cache",
        "x-content-type-options": "nosniff"
      }
    });
  }
};
"""


if __name__ == "__main__":
    main()
