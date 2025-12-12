#!/usr/bin/env python3
"""
Instagram Video Downloader Website
نصب: pip install flask flask-cors yt-dlp requests
اجرا: python3 app.py
"""

from flask import Flask, render_template_string, request, send_file, jsonify, render_template
from flask_cors import CORS
import subprocess
import tempfile
import os
import io
import requests
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Downloader - دانلود ویدیو اینستاگرام</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .logo {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .subtitle {
            color: #666;
            font-size: 14px;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        
        input[type="url"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s;
            font-family: inherit;
        }
        
        input[type="url"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        button {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }
        
        .btn-download {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-download:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-download:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .btn-copy {
            background: #f0f0f0;
            color: #333;
            display: none;
        }
        
        .btn-copy:hover {
            background: #e0e0e0;
        }
        
        .btn-copy.show {
            display: flex;
        }
        
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .result {
            display: none;
            margin-top: 30px;
            padding-top: 30px;
            border-top: 2px solid #f0f0f0;
        }
        
        .result.show {
            display: block;
        }
        
        .video-preview {
            width: 100%;
            border-radius: 10px;
            margin-bottom: 15px;
            background: #f0f0f0;
        }
        
        .download-link {
            background: #f9f9f9;
            padding: 12px 15px;
            border-radius: 10px;
            word-break: break-all;
            font-size: 12px;
            color: #666;
            margin-bottom: 15px;
            font-family: monospace;
            border: 1px solid #e0e0e0;
        }
        
        .message {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
            font-size: 14px;
        }
        
        .message.show {
            display: block;
        }
        
        .error {
            background: #fee;
            color: #c33;
            border: 1px solid #fcc;
        }
        
        .success {
            background: #efe;
            color: #3c3;
            border: 1px solid #cfc;
        }
        
        .info {
            background: #eef;
            color: #33c;
            border: 1px solid #ccf;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            font-size: 12px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">📥</div>
            <h1>Instagram Downloader</h1>
            <p class="subtitle">دانلود رایگان ویدیو و عکس اینستاگرام</p>
        </div>
        
        <div class="message" id="message"></div>
        
        <form id="form">
            <div class="input-group">
                <label for="url">لینک پست یا ریلز</label>
                <input 
                    type="url" 
                    id="url" 
                    placeholder="https://www.instagram.com/reel/..." 
                    required
                >
            </div>
            
            <div class="button-group">
                <button type="submit" class="btn-download" id="downloadBtn">
                    <span id="btnText">دانلود</span>
                </button>
                <button type="button" class="btn-copy" id="copyBtn">
                    کپی لینک
                </button>
            </div>
        </form>
        
        <div class="result" id="result">
            <video class="video-preview" id="videoPreview" controls></video>
            <div class="download-link" id="linkDisplay"></div>
            <a href="#" id="directDownload" class="button-group" style="text-decoration: none; margin-bottom: 0;">
                <button type="button" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    ⬇️ دانلود مستقیم
                </button>
            </a>
        </div>
        
        <div class="footer">
            <p>🔒 امن و رایگان</p>
            <p>برای استفاده شخصی</p>
        </div>
    </div>

    <script>
        const form = document.getElementById('form');
        const urlInput = document.getElementById('url');
        const downloadBtn = document.getElementById('downloadBtn');
        const copyBtn = document.getElementById('copyBtn');
        const result = document.getElementById('result');
        const message = document.getElementById('message');
        const videoPreview = document.getElementById('videoPreview');
        const linkDisplay = document.getElementById('linkDisplay');
        const directDownload = document.getElementById('directDownload');
        const btnText = document.getElementById('btnText');

        function showMessage(text, type) {
            message.textContent = text;
            message.className = `message show ${type}`;
            setTimeout(() => message.classList.remove('show'), 5000);
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const url = urlInput.value.trim();
            
            if (!url.includes('instagram.com')) {
                showMessage('❌ لینک اینستاگرام معتبر نیست', 'error');
                return;
            }

            downloadBtn.disabled = true;
            btnText.innerHTML = '<span class="spinner"></span>درحال دانلود...';
            result.classList.remove('show');

            try {
                const response = await fetch(`/download?url=${encodeURIComponent(url)}`);
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'خطا در دانلود');
                }

                // ویدیو رو نشان بده
                const blob = await response.blob();
                const videoUrl = URL.createObjectURL(blob);
                
                videoPreview.src = videoUrl;
                linkDisplay.textContent = `فایل: ${(blob.size / 1024 / 1024).toFixed(2)} MB`;
                
                directDownload.href = videoUrl;
                directDownload.download = 'instagram_video.mp4';
                
                result.classList.add('show');
                showMessage('✅ ویدیو با موفقیت دانلود شد', 'success');
                
            } catch (error) {
                showMessage('❌ ' + error.message, 'error');
            } finally {
                downloadBtn.disabled = false;
                btnText.textContent = 'دانلود';
            }
        });

        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(linkDisplay.textContent);
            showMessage('✅ کپی شد', 'success');
        });
    </script>
</body>
</html>
'''

def download_video(url):
    """yt-dlp استفاده می‌کنه برای دانلود"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "video.mp4")
            
            cmd = [
                'yt-dlp',
                '-f', 'best[ext=mp4]/best',
                '-o', output_path,
                '--no-warnings',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    return f.read()
        
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download')
def download():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    if 'instagram.com' not in url:
        return jsonify({"error": "Invalid Instagram URL"}), 400
    
    print(f"[*] Downloading: {url}")
    
    video_data = download_video(url)
    
    if not video_data:
        return jsonify({"error": "نتونستم ویدیو رو دانلود کنم"}), 500
    
    return send_file(
        io.BytesIO(video_data),
        mimetype='video/mp4',
        as_attachment=False,
        download_name='instagram_video.mp4'
    )

@app.route('/api/instagram/instagram.php')
def api_instagram():
    """API compatible with mionapi.ir"""
    url = request.args.get('url')
    
    if not url or 'instagram.com' not in url:
        return jsonify({"error": "Invalid URL"}), 400
    
    video_data = download_video(url)
    
    if not video_data:
        return jsonify({"error": "Failed to download"}), 500
    
    return send_file(
        io.BytesIO(video_data),
        mimetype='video/mp4',
        as_attachment=False
    )

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Instagram Downloader Server")
    print("=" * 50)
    print("📍 http://localhost:8000")
    print("=" * 50)
    print("نصب ابزارهای مورد نیاز:")
    print("  pip install flask flask-cors yt-dlp")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=8000)