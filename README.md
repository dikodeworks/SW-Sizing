# SolarWinds Sizing

Kalkulator sizing lisensi & hardware SolarWinds untuk SWO SaaS, OSH Essentials & Advanced, OSH Premier, DPA, dan Service Desk.

## Deploy

- `index.html` adalah sumber utama halaman (responsif untuk mobile/tablet/desktop, dan dapat dipasang sebagai PWA).
- `worker.js` adalah versi Cloudflare Worker yang menyajikan `index.html` beserta aset PWA (`manifest.webmanifest`, `sw.js`, ikon, favicon).
- Setiap kali mengubah `index.html`, `manifest.webmanifest`, `sw.js`, `favicon.svg`, atau file ikon PNG, jalankan:

```bash
python3 build-worker.py
```

lalu deploy `worker.js` ke Cloudflare Workers. Melewati langkah ini akan membuat deploy masih menyajikan halaman lama.

Untuk pengujian lokal:

```bash
python3 -m http.server 8765
```

lalu buka `http://localhost:8765`. Service worker dan install prompt hanya aktif lewat HTTP/HTTPS (bukan `file://`).

## PWA

- `manifest.webmanifest` mendefinisikan nama, warna tema, dan ikon 192/512 px.
- `sw.js` menyimpan app shell dan memberi fallback offline untuk navigasi.
- Ikon: `icon-192.png`, `icon-512.png` (juga dipakai sebagai ikon maskable), `apple-touch-icon.png`, dan `favicon.svg` — semuanya memakai mark Westcon.
- Tombol **Install app** muncul di browser yang mendukung `beforeinstallprompt`. Di iOS, gunakan **Share → Add to Home Screen**.
- Bila aset ikon diubah, naikkan versi cache `sw-sizing-v2` di `sw.js` agar klien mengambil versi baru.
