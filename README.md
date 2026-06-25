# Dragonic Source Explorer 🐉

Alat otomatis berbasis Cloud (GitHub Actions) untuk mengeksplorasi, mengunduh, dan menganalisis aset publik dari struktur kode sumber website secara aman dan legal.

## ✨ Fitur Utama
* **Tanpa Setup Server:** Berjalan sepenuhnya di server Github Actions (tidak perlu instalasi script lokal, Termux, atau perintah Linux manual).
* **Automated Parsing:** Mendeteksi berkas CSS, JavaScript, Gambar, Fonta, Manifest, dan Publik Aset lainnya.
* **Struktur Folder Rapi:** Memisahkan hasil unduhan berdasarkan jenis formatnya.
* **Laporan Premium:** Desain laporan HTML mengadopsi tema gelap futuristik eksklusif Dragonic King V5.
* **Keamanan Ketat:** Mematuhi aturan `robots.txt`, hanya mengakses berkas publik, dan tidak menerobos sistem proteksi/CORS.

## 🚀 Cara Menggunakan
1. Masuk ke tab **Actions** di bagian atas repositori GitHub Anda.
2. Di panel sebelah kiri, pilih workflow **Dragonic Source Explorer**.
3. Klik menu dropdown **Run workflow**.
4. Masukkan URL website target (contoh: `https://example.com`) pada kolom input.
5. Klik tombol hijau **Run workflow**.
6. Tunggu proses selesai. Hasil akhir berupa file `.zip` dan laporan komprehensif dapat langsung Anda unduh pada bagian **Artifacts** di bawah halaman detail run.
