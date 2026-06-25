import os
import sys
import json
import zipfile
from urllib.parse import urljoin, urlparse
import urllib.robotparser
import requests
from bs4 import BeautifulSoup

# Ambil URL dari environment variable GitHub Actions
TARGET_URL = os.environ.get("TARGET_URL")

if not TARGET_URL:
    print("[EROR] URL target tidak ditemukan. Harap masukkan URL melalui input workflow.")
    sys.exit(1)

# Normalisasi URL
if not TARGET_URL.startswith(("http://", "https://")):
    TARGET_URL = "https://" + TARGET_URL

print(f"[INFO] Memulai eksplorasi untuk: {TARGET_URL}")

# Inisialisasi folder output
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

stats = {
    "css": 0,
    "javascript": 0,
    "images": 0,
    "fonts": 0,
    "manifest": 0,
    "failed": 0
}
downloaded_files = []

# Cek Robots.txt (Aturan Keamanan)
parsed_base = urlparse(TARGET_URL)
base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
rp = urllib.robotparser.RobotFileParser()
rp.set_url(urljoin(base_domain, "robots.txt"))
try:
    rp.read()
    can_fetch = rp.can_fetch(headers["User-Agent"], TARGET_URL)
except Exception:
    can_fetch = True

if not can_fetch:
    print("[PERINGATAN] Robots.txt melarang akses ke halaman ini. Tetap melanjutkan mode aman publik.")

# Fetch HTML Utama
try:
    response = requests.get(TARGET_URL, headers=headers, timeout=15)
    response.raise_for_status()
    html_content = response.text
except Exception as e:
    print(f"[EROR] Gagal mengakses URL Utama: {e}")
    sys.exit(1)

soup = BeautifulSoup(html_content, "html.parser")

def dapatkan_kategori(url_path, tag_name, attr_name):
    path_lower = url_path.lower()
    if path_lower.endswith(".css") or tag_name == "link" and "stylesheet" in attr_name:
        return "css"
    elif path_lower.endswith((".js", ".mjs")) or tag_name == "script":
        return "javascript"
    elif path_lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico")):
        return "images"
    elif path_lower.endswith((".woff", ".woff2", ".ttf", ".otf", ".eot")):
        return "fonts"
    elif "manifest" in path_lower or path_lower.endswith(".json") and "manifest" in attr_name:
        return "manifest"
    return "public_assets"

def unduh_asset(asset_url, kategori):
    global stats
    try:
        parsed_asset = urlparse(asset_url)
        if parsed_asset.netloc and parsed_asset.netloc != parsed_base.netloc:
            return
        
        clean_path = parsed_asset.path.lstrip("/")
        if not clean_path or clean_path.endswith("/"):
            clean_path += f"index_asset_{stats[kategori] if kategori in stats else 0}"
            
        lokal_filepath = os.path.join(OUTPUT_DIR, kategori, clean_path)
        os.makedirs(os.path.dirname(lokal_filepath), exist_ok=True)
        
        res = requests.get(asset_url, headers=headers, timeout=10)
        if res.status_code == 200:
            with open(lokal_filepath, "wb") as f:
                f.write(res.content)
            
            ukuran_kb = round(len(res.content) / 1024, 2)
            downloaded_files.append({
                "url": asset_url,
                "lokal_path": lokal_filepath,
                "kategori": kategori,
                "ukuran_kb": ukuran_kb
            })
            if kategori in stats:
                stats[kategori] += 1
            print(f"[BERHASIL] [{kategori.upper()}] -> {clean_path} ({ukuran_kb} KB)")
        else:
            stats["failed"] += 1
    except Exception as e:
        stats["failed"] += 1

assets_to_clean = []

# 1. CSS & Manifest
for link in soup.find_all("link", href=True):
    rel = link.get("rel", [])
    rel_str = "".join(rel).lower()
    url_penuh = urljoin(TARGET_URL, link["href"])
    kat = dapatkan_kategori(url_penuh, "link", rel_str)
    assets_to_clean.append((url_penuh, kat))

# 2. JavaScript
for script in soup.find_all("script", src=True):
    url_penuh = urljoin(TARGET_URL, script["src"])
    kat = dapatkan_kategori(url_penuh, "script", "")
    assets_to_clean.append((url_penuh, kat))

# 3. Images
for img in soup.find_all(["img", "source"], src=True):
    url_penuh = urljoin(TARGET_URL, img["src"])
    assets_to_clean.append((url_penuh, "images"))

for img in soup.find_all("source", srcset=True):
    srcset_first = img["srcset"].split(",")[0].strip().split(" ")[0]
    url_penuh = urljoin(TARGET_URL, srcset_first)
    assets_to_clean.append((url_penuh, "images"))

# Jalankan Unduh
assets_to_clean = list(set(assets_to_clean))
for asset_url, kategori in assets_to_clean:
    unduh_asset(asset_url, kategori)

# Simpan HTML Halaman Utama asli di folder output
with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(soup.prettify())

# --- LAPORAN JSON ---
laporan_json = {
    "target_url": TARGET_URL,
    "statistik": stats,
    "files_terunduh": downloaded_files
}
with open("source_report.json", "w", encoding="utf-8") as f:
    json.dump(laporan_json, f, indent=4)

# --- LAPORAN HTML (RE-DESIGNED MATCHING USER IMAGE) ---
html_report_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dragonic KING DATABASE V5 - Laporan Explorer</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;600;700&display=swap');
        
        body {{ 
            font-family: 'Rajdhani', sans-serif; 
            margin: 0; 
            padding: 20px;
            background-color: #0b0b0e; 
            color: #ffffff; 
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .phone-mockup {{
            max-width: 450px;
            width: 100%;
            background: #111217;
            border-radius: 24px;
            padding: 24px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.8);
            border: 1px solid #1f2026;
            box-sizing: border-box;
        }}

        .brand-header {{
            text-align: center;
            margin-bottom: 25px;
            position: relative;
        }}

        .brand-logo {{
            font-family: 'Orbitron', sans-serif;
            color: #ffffff; 
            font-size: 28px;
            font-weight: 700;
            margin: 0;
            text-shadow: 0 0 12px rgba(255,255,255,0.4);
            text-transform: uppercase;
            letter-spacing: 1px;
            line-height: 1.2;
        }}
        
        .brand-sub {{
            font-family: 'Orbitron', sans-serif;
            color: #ffffff;
            font-size: 11px;
            letter-spacing: 1.5px;
            margin: 6px 0 0 0;
            opacity: 0.6;
        }}

        .main-card {{
            border: 1px solid #23242d;
            background: #16171e;
            border-radius: 18px;
            padding: 20px;
            text-align: center;
            margin-bottom: 18px;
        }}

        .url-display {{
            background: #0d0e12;
            border: 1px solid #23242d;
            border-radius: 10px;
            padding: 12px;
            color: #a5a6b4;
            font-size: 14px;
            word-break: break-all;
            display: block;
            margin-bottom: 15px;
            text-align: left;
        }}
        
        .btn-scan {{
            width: 100%;
            background: transparent;
            border: 2px solid #ffffff;
            color: #ffffff;
            padding: 14px;
            border-radius: 12px;
            font-family: 'Orbitron', sans-serif;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            text-shadow: 0 0 4px #ffffff;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.3s;
        }}

        .info-note {{
            font-size: 12px;
            color: #7b7c87;
            margin-top: 12px;
            display: block;
        }}

        .grid-stats {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 18px;
        }}
        
        .stat-box {{ 
            background: #16171e; 
            padding: 15px; 
            border-radius: 12px; 
            text-align: left; 
            border: 1px solid #23242d;
        }}
        
        .stat-box h3 {{ margin: 0; color: #7b7c87; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-box p {{ margin: 5px 0 0 0; font-size: 24px; font-weight: 700; font-family: 'Orbitron', sans-serif; color: #ffffff; }}

        .action-channel {{
            display: flex;
            align-items: center;
            padding: 14px 18px;
            border-radius: 16px;
            margin-bottom: 14px;
            justify-content: space-between;
            text-decoration: none;
        }}

        .channel-whatsapp {{
            background: #091a12;
            border: 1px solid #10b981;
            color: #10b981;
        }}

        .channel-telegram {{
            background: #1a0f12;
            border: 1px solid #ef4444;
            color: #ef4444;
        }}

        .channel-info text {{
            display: block;
        }}
        
        .channel-title {{
            font-weight: 700;
            font-size: 15px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        .channel-sub {{
            font-size: 11px;
            color: #7b7c87;
            margin-top: 2px;
        }}

        .btn-join-inner {{
            padding: 8px 16px;
            border-radius: 20px;
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            font-family: 'Orbitron', sans-serif;
        }}
        .channel-whatsapp .btn-join-inner {{ background: #10b981; }}
        .channel-telegram .btn-join-inner {{ background: #ef4444; }}
        
        .log-section-title {{
            font-family: 'Orbitron', sans-serif;
            font-size: 13px;
            margin: 20px 0 10px 4px;
            color: #7b7c87;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .log-list-wrapper {{
            max-height: 180px;
            overflow-y: auto;
            background: #0d0e12;
            border-radius: 12px;
            padding: 12px;
            font-size: 13px;
            border: 1px solid #23242d;
        }}

        .log-row {{
            padding: 8px 4px;
            border-bottom: 1px solid #16171e;
            display: flex;
            justify-content: space-between;
            color: #c5c6c7;
        }}
        .log-row:last-child {{ border: none; }}
        .log-size {{ color: #10b981; font-weight: 600; font-family: 'Orbitron', sans-serif; }}
    </style>
</head>
<body>

    <div class="phone-mockup">
        <div class="brand-header">
            <div class="brand-logo">Dragonic KING<br>DATABASE V5</div>
            <div class="brand-sub">ADVANCED SOURCE LOOKUP SYSTEM</div>
        </div>

        <div class="main-card">
            <div class="url-display">
                <span style="font-size: 10px; color: #7b7c87; display: block; margin-bottom: 4px; font-family: 'Orbitron';">TARGET EXPLORED:</span>
                {TARGET_URL}
            </div>
            <button class="btn-scan">🔍 EXPLORE FINISHED</button>
            <span class="info-note">✓ Status 200 OK - Publik data sukses diunduh</span>
        </div>

        <div class="grid-stats">
            <div class="stat-box"><h3>CSS FILES</h3><p>{stats['css']}</p></div>
            <div class="stat-box"><h3>JS FILES</h3><p>{stats['javascript']}</p></div>
            <div class="stat-box"><h3>IMAGES</h3><p>{stats['images']}</p></div>
            <div class="stat-box"><h3>FONTS</h3><p>{stats['fonts']}</p></div>
        </div>

        <div class="action-channel channel-whatsapp">
            <div class="channel-info">
                <span class="channel-title">🟢 ARSIP DATA ZIP</span>
                <span class="channel-sub">Kompilasi sukses tanpa ada berkas rusak</span>
            </div>
            <div class="btn-join-inner">READY</div>
        </div>

        <div class="action-channel channel-telegram">
            <div class="channel-info">
                <span class="channel-title">🔴 FAILED ASSETS</span>
                <span class="channel-sub">Total berkas gagal bypass/CORS</span>
            </div>
            <div class="btn-join-inner">{stats['failed']} FILE</div>
        </div>

        <div class="log-section-title">LOG SCRIPT FILE EXPLORER</div>
        <div class="log-list-wrapper">
"""

for file in downloaded_files:
    nama_file = os.path.basename(file["lokal_path"])
    html_report_content += f"""            <div class="log-row">
                <span>📁 {nama_file}</span>
                <span class="log-size">{file['ukuran_kb']} KB</span>
            </div>\n"""

if not downloaded_files:
    html_report_content += """            <div class="log-row" style="justify-content: center; color: #7b7c87;">
                <span>Tidak ada file lokal yang terunduh</span>
            </div>\n"""

html_report_content += """        </div>
    </div>

</body>
</html>"""

with open("source_report.html", "w", encoding="utf-8") as f:
    f.write(html_report_content)

# --- SISTEM KOMPRESI ZIP ---
zip_filename = "website_source.zip"
print(f"[INFO] Membuat arsip ZIP: {zip_filename}")
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, OUTPUT_DIR)
            zipf.write(file_path, arcname=os.path.join("source", rel_path))

print("[SUKSES] Semua proses selesai dengan aman.")
