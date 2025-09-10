# HTML File Server

Tugas Sistem Terdistribusi - API untuk serve HTML files berbagai ukuran

## Apa ini?
Simple API pakai Flask buat serve file HTML dengan ukuran:
- 10 KB
- 100 KB  
- 1 MB
- 5 MB
- 10 MB

## File dalam project

```
├── app.py              # kode utama
├── requirements.txt    # dependencies
└── html_files/         # file HTML
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

Install dependencies dulu:
```bash
pip install -r requirements.txt
```

Jalankan server:
```bash
python app.py
```

Buka browser ke `http://localhost:5000`

## Testing

Bisa test pakai browser atau curl:

```bash
# Download file kecil
curl http://localhost:5000/api/html/small

# Info semua file
curl http://localhost:5000/api/info

# Cek status server
curl http://localhost:5000/api/status
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

## Notes

- Server jalan di port 5000
- Kalau salah parameter bakal kasih error JSON
- File besar mungkin agak lama downloadnya
- Threading enabled jadi bisa handle multiple request

Itu aja sih, simple API buat tugas kuliah.
