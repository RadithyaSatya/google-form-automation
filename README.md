# Google Form Filler Universal

Alat untuk mengotomatisasi pengisian Google Form dengan deteksi otomatis struktur formulir dan simulasi perilaku manusia.

## Fitur

- **Deteksi Otomatis:** Mendeteksi jenis pertanyaan dan opsi jawaban secara otomatis
- **Multi-bahasa:** Mendukung berbagai bahasa (Indonesia, Inggris, Spanyol, Prancis, Jerman)
- **Anti-deteksi:** Simulasi perilaku manusia yang realistis (jeda ketik, gerakan mouse, dll)
- **Dukungan Proxy:** Rotasi IP untuk menghindari pemblokiran
- **Mode Headless:** Dapat dijalankan tanpa tampilan browser (lebih cepat)
- **Deteksi Captcha:** Mendeteksi dan memberi tahu jika ada captcha
- **Mode Pengujian:** Isi form tanpa submit untuk menguji konfigurasi
- **GUI:** Antarmuka grafis untuk penggunaan yang lebih mudah

## Requirements

- Python `3.8+`
- Disarankan Python `3.10+`
- Teruji di environment ini dengan Python `3.14.2`
- `playwright>=1.49,<2`
- `faker==18.9.0`
- Browser Playwright Chromium harus diinstal dengan `playwright install`
- `tkinter` diperlukan jika ingin memakai GUI

## Setup

### 1. Buat virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependency Python

```bash
pip install -r requirements.txt
```

### 3. Install browser Playwright

```bash
playwright install
```

## Distribusi ke Pengguna Lain

Ada 2 cara yang realistis untuk dibagikan.

### Opsi 1: Portable Windows dengan `venv-win`

Jika folder `venv-win` sudah lengkap, pengguna Windows bisa langsung memakai launcher:

- `run_gui_portable_windows.bat`
- `run_cli_portable_windows.bat`

Keunggulan:

- Tidak perlu install Python manual
- Cocok untuk pemakaian internal
- Paling dekat dengan setup Anda sekarang

Catatan:

- Paket ini tetap bergantung pada dependency di dalam `venv-win`
- Browser Playwright tetap harus sudah tersedia di environment target

### Opsi 2: Executable Windows

Repo ini sekarang menyediakan builder:

```bat
build_windows_exe.bat
```

File itu akan:

- install dependency build dari `requirements-build.txt`
- membuat `playwright_form_filler.exe`
- membuat bundle GUI `formfiller_gui.exe`
- menyalin CLI exe ke dalam folder GUI bundle

Hasil akhir ada di:

- `dist\formfiller_gui\formfiller_gui.exe`

Catatan:

- Build `exe` sebaiknya dijalankan di Windows
- Untuk Playwright, lebih aman memakai mode `--onedir` seperti konfigurasi saat ini dibanding memaksa `--onefile`

## Penggunaan

### Menggunakan GUI

1. Pastikan semua dependensi terinstal
2. Instal browser Playwright
3. Jalankan aplikasi GUI: `python formfiller_gui.py`
4. Masukkan URL Google Form dan konfigurasi lainnya
5. Klik "Uji Form" untuk mode pengujian atau "Mulai Pengisian" untuk mulai mengisi

### Menggunakan Command Line

```bash
source .venv/bin/activate
```

```bash
python playwright_form_filler.py
```

```bash
python playwright_form_filler.py [URL] [TOTAL_RESPONSES] [MAX_PER_SESSION] [--headless] [--proxy-file PROXY_FILE] [--language LANGUAGE] [--test]
```
Contoh:

```bash
python playwright_form_filler.py https://forms.gle/example 100 20 --language id_ID
```

## Peringatan

Gunakan alat ini hanya untuk tujuan pendidikan dan dengan izin pemilik formulir. Penggunaan untuk spam atau tujuan yang melanggar Syarat Layanan Google dapat mengakibatkan pemblokiran akun.

## Dependensi

- Python `3.8+`
- `playwright>=1.49,<2`
- `faker==18.9.0`
- `tkinter` untuk GUI

## Pengembangan

Proyek ini dikembangkan dengan tujuan pendidikan dan demonstrasi otomatisasi web. Silakan berkontribusi dengan mengirimkan pull request atau melaporkan masalah.
