# Simpel APi serve html

from flask import Flask, send_file, jsonify, render_template_string
import os
import time
from datetime import datetime

# Inisialisasi Flask app
app = Flask(__name__)

# Konfigurasi folder untuk HTML files
HTML_FOLDER = 'html_files'

# Homepage
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>HTML File Server</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            line-height: 1.6; 
        }
        h1 { color: #333; }
        h3 { color: #666; margin-top: 25px; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .files { margin: 15px 0; }
        .files a { 
            display: inline-block; 
            margin: 5px 10px 5px 0; 
            padding: 8px 12px; 
            background: #f0f0f0; 
            border-radius: 4px; 
        }
        .info { 
            background: #f9f9f9; 
            padding: 15px; 
            border-radius: 4px; 
            margin: 20px 0; 
        }
        code { 
            background: #eee; 
            padding: 2px 4px; 
            border-radius: 2px; 
        }
    </style>
</head>
<body>
    <h1>HTML File Server</h1>
    <p>Simple API untuk serve HTML files dengan ukuran berbeda.</p>
    
    <h3>Available Files:</h3>
    <div class="files">
        <a href="/api/html/small">Small (10KB)</a>
        <a href="/api/html/medium">Medium (100KB)</a>
        <a href="/api/html/large">Large (1MB)</a>
        <a href="/api/html/xlarge">XLarge (5MB)</a>
        <a href="/api/html/xxlarge">XXLarge (10MB)</a>
    </div>
    
    <h3>API Info:</h3>
    <div class="files">
        <a href="/api/info">File Info</a>
        <a href="/api/status">Server Status</a>
    </div>
    
    <div class="info">
        <h3>Usage:</h3>
        <p>Browser: Klik link di atas</p>
        <p>Command line: <code>curl http://localhost:5000/api/html/small</code></p>
        
        <h3>Endpoints:</h3>
        <p><code>GET /api/html/&lt;size&gt;</code> - Download HTML file</p>
        <p><code>GET /api/info</code> - File information</p>
        <p><code>GET /api/status</code> - Server status</p>
    </div>
    
    <p><small>Server time: {{ current_time }}</small></p>
</body>
</html>
'''

# Route 1: Home page - menampilkan dokumentasi dan daftar endpoints
@app.route('/')
def home():
    """
    Endpoint utama yang menampilkan halaman dokumentasi
    
    Returns:
        HTML: Halaman dengan daftar endpoints dan dokumentasi
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template_string(HOME_TEMPLATE, current_time=current_time)

# Route 2: API endpoint untuk serve HTML files berdasarkan ukuran
@app.route('/api/html/<size>')
def serve_html(size):
    """
    Serve HTML file berdasarkan ukuran yang diminta
    
    Args:
        size (str): Ukuran file (small, medium, large, xlarge, xxlarge)
    
    Returns:
        File: HTML file yang diminta
        JSON: Error message jika file tidak ditemukan
    """
    # Mapping ukuran ke nama file
    size_mapping = {
        'small': 'small_10kb.html',
        'medium': 'medium_100kb.html', 
        'large': 'large_1mb.html',
        'xlarge': 'xlarge_5mb.html',
        'xxlarge': 'xxlarge_10mb.html'
    }
    
    # Cek apakah ukuran yang diminta valid
    if size not in size_mapping:
        return jsonify({
            'error': 'Invalid size',
            'valid_sizes': list(size_mapping.keys())
        }), 400
    
    filename = size_mapping[size]
    file_path = os.path.join(HTML_FOLDER, filename)
    
    # Cek apakah file ada
    if not os.path.exists(file_path):
        return jsonify({
            'error': 'File not found',
            'requested_file': filename
        }), 404
    
    # Log request
    print(f"Serving {filename} ({size})")
    
    # Serve file dengan proper headers
    return send_file(
        file_path,
        mimetype='text/html',
        as_attachment=False,  # Display di browser, bukan download
        download_name=filename
    )

# Route 3: API untuk mendapatkan informasi tentang files
@app.route('/api/info')
def file_info():
    """
    Endpoint untuk mendapatkan informasi tentang semua HTML files
    
    Returns:
        JSON: Informasi ukuran dan status semua files
    """
    size_mapping = {
        'small': 'small_10kb.html',
        'medium': 'medium_100kb.html', 
        'large': 'large_1mb.html',
        'xlarge': 'xlarge_5mb.html',
        'xxlarge': 'xxlarge_10mb.html'
    }
    
    files_info = {}
    total_size = 0
    
    for size_key, filename in size_mapping.items():
        file_path = os.path.join(HTML_FOLDER, filename)
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            files_info[size_key] = {
                'filename': filename,
                'size_bytes': file_size,
                'size_kb': round(file_size / 1024, 2),
                'size_mb': round(file_size / (1024 * 1024), 2),
                'exists': True,
                'endpoint': f'/api/html/{size_key}'
            }
        else:
            files_info[size_key] = {
                'filename': filename,
                'exists': False,
                'endpoint': f'/api/html/{size_key}'
            }
    
    return jsonify({
        'files': files_info,
        'total_files': len([f for f in files_info.values() if f.get('exists')]),
        'total_size_bytes': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'server_time': datetime.now().isoformat()
    })

# Route 4: API status endpoint
@app.route('/api/status')
def server_status():
    """
    Endpoint untuk cek status server
    
    Returns:
        JSON: Status server dan informasi sistem
    """
    return jsonify({
        'status': 'ok',
        'server': 'HTML File Server',
        'timestamp': datetime.now().isoformat(),
        'endpoints': ['/', '/api/html/<size>', '/api/info', '/api/status'],
        'sizes': ['small', 'medium', 'large', 'xlarge', 'xxlarge']
    })

# Error handler untuk 404
@app.errorhandler(404)
def not_found(error):
    """
    Handler untuk error 404 (Not Found)
    """
    return jsonify({
        'error': 'Not found',
        'available_endpoints': ['/', '/api/html/<size>', '/api/info', '/api/status']
    }), 404

# Error handler untuk 500
@app.errorhandler(500)
def internal_error(error):
    """
    Handler untuk error 500 (Internal Server Error)
    """
    return jsonify({
        'error': 'Server error'
    }), 500

# Main function untuk menjalankan server
if __name__ == '__main__':
    """
    Fungsi utama untuk menjalankan Flask server
    """
    # Buat folder html_files jika belum ada
    if not os.path.exists(HTML_FOLDER):
        os.makedirs(HTML_FOLDER)
        print(f"Created folder: {HTML_FOLDER}")
    
    # Info startup
    print("HTML File Server Starting...")
    print(f"Files folder: {HTML_FOLDER}")
    print("Available endpoints:")
    print("  /                     - Homepage")
    print("  /api/html/<size>      - Get HTML file")
    print("  /api/info             - File info")
    print("  /api/status           - Server status")
    
    # Jalankan Flask server
    # Debug=True untuk development, ubah ke False untuk production
    app.run(
        debug=True,          # Enable debug mode
        host='0.0.0.0',      # Allow external connections
        port=5000,           # Port 5000 (default Flask)
        threaded=True        # Enable threading
    )

