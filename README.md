# HTML File Server dengan Locust Load Testing

Tugas Sistem Terdistribusi - API untuk serve HTML files berbagai ukuran + Load Testing dengan Locust Web UI

## Apa ini?
Simple API pakai Flask buat serve file HTML dengan ukuran:
- 10 KB
- 100 KB  
- 1 MB
- 5 MB
- 10 MB

## File dalam project

```
├── app.py                    # Flask server utama
├── requirements.txt          # Python dependencies
├── locustfile.py            # Locust test scenarios
├── monitor_system.py        # System monitoring
└── html_files/              # HTML files berbagai ukuran
    ├── small_10kb.html
    ├── medium_100kb.html
    ├── large_1mb.html
    ├── xlarge_5mb.html
    └── xxlarge_10mb.html
```

## Penjelasan kode

`app.py` isinya:
- Import Flask dan library lain
- Setup routes untuk API
- Homepage buat dokumentasi
- Error handling kalau ada yang salah

## Endpoints yang ada

**Homepage (`/`)**
Halaman utama dengan dokumentasi dan link ke semua file

**Get HTML file (`/api/html/<size>`)**
Download file HTML sesuai ukuran:
- `/api/html/small` - file 10KB
- `/api/html/medium` - file 100KB  
- `/api/html/large` - file 1MB
- `/api/html/xlarge` - file 5MB
- `/api/html/xxlarge` - file 10MB

**Info (`/api/info`)**
JSON info tentang semua file (ukuran, dll)

**Status (`/api/status`)**  
Cek server masih jalan atau ngga

## Cara kerja

1. User request ke endpoint (misal `/api/html/small`)
2. Server cek parameter valid atau ngga
3. Cari file yang diminta
4. Kalau ada, kirim file. Kalau ngga ada, kasih error
5. Done

Sederhana aja, Flask handle routing dan file serving.

## Cara jalanin

### 1. Install Dependencies (include Locust)
```bash
pip install -r requirements.txt
```

### 2. Jalankan Flask Server
```bash
python app.py
```

### 3. Akses Server
Buka browser ke `http://localhost:5000`

### 4. Jalankan Load Testing
```bash
# Locust Web UI (recommended)
locust -f locustfile.py --host=http://localhost:5000

# Buka browser ke: http://localhost:8089
# Input users, spawn rate, dan duration
```

## Testing

### Manual Testing
```bash
# Download file kecil
curl http://localhost:5000/api/html/small

# Info semua file
curl http://localhost:5000/api/info

# Cek status server
curl http://localhost:5000/api/status
```

### Load Testing dengan Locust
```bash
# Web UI Mode (recommended untuk demo cantik)
locust -f locustfile.py --host=http://localhost:5000
# Buka http://localhost:8089

# Command Line Mode (untuk exact request count)
locust -f locustfile.py --host=http://localhost:5000 -u 10 -r 2 -t 60s --headless

# Different user types:
# LightLoadUser    - File kecil, response time cepat
# MediumLoadUser   - Mix file size, beban sedang  
# HeavyLoadUser    - File besar, test bandwidth
# StressTestUser   - Maksimal beban, test breaking point
```

### System Monitoring
```bash
# Monitor resource usage selama testing
python monitor_system.py
```

## Contoh response

File HTML langsung di-download kalau request berhasil.

Info endpoint kasih JSON kayak gini:
```json
{
  "files": {
    "small": {
      "filename": "small_10kb.html",
      "size_kb": 10.0,
      "exists": true
    }
  },
  "total_files": 5
}
```
