#!/usr/bin/env python3
"""
Flask wrapper for the Cover Letter Generation System
This allows deployment using Flask while keeping the FastAPI functionality
"""

from flask import Flask, request, jsonify, render_template_string, send_file, redirect
import requests
import threading
import time
import os
import subprocess
import sys

# Flask app
app = Flask(__name__)

# FastAPI server details
FASTAPI_HOST = "127.0.0.1"
FASTAPI_PORT = 8001
FASTAPI_URL = f"http://{FASTAPI_HOST}:{FASTAPI_PORT}"

# Global variable to track FastAPI process
fastapi_process = None

def start_fastapi_server():
    """Start the FastAPI server in a separate process"""
    global fastapi_process
    
    try:
        # Change to the project directory
        os.chdir('/home/ubuntu/cover-letter-agent')
        
        # Start FastAPI with uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", FASTAPI_HOST,
            "--port", str(FASTAPI_PORT),
            "--reload"
        ]
        
        fastapi_process = subprocess.Popen(cmd)
        
        # Wait for server to start
        for _ in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"{FASTAPI_URL}/health", timeout=1)
                if response.status_code == 200:
                    print(f"FastAPI server started successfully on {FASTAPI_URL}")
                    return True
            except:
                time.sleep(1)
        
        print("Failed to start FastAPI server")
        return False
        
    except Exception as e:
        print(f"Error starting FastAPI server: {e}")
        return False

def proxy_request(path, method='GET', **kwargs):
    """Proxy requests to FastAPI server"""
    try:
        url = f"{FASTAPI_URL}{path}"
        
        if method == 'GET':
            response = requests.get(url, **kwargs)
        elif method == 'POST':
            response = requests.post(url, **kwargs)
        elif method == 'PUT':
            response = requests.put(url, **kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, **kwargs)
        else:
            return jsonify({"error": "Unsupported method"}), 405
        
        return response
        
    except Exception as e:
        return jsonify({"error": f"Proxy error: {str(e)}"}), 500

@app.route('/')
def home():
    """Home page - proxy to FastAPI"""
    try:
        response = proxy_request('/')
        return response.content, response.status_code, response.headers.items()
    except:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cover Letter Generation System</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error { color: #dc3545; }
                .loading { color: #007bff; }
            </style>
        </head>
        <body>
            <h1>Cover Letter Generation System</h1>
            <p class="loading">Starting up... Please refresh in a moment.</p>
            <script>
                setTimeout(function() {
                    window.location.reload();
                }, 3000);
            </script>
        </body>
        </html>
        """)

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        response = proxy_request('/health')
        if response.status_code == 200:
            return jsonify({"status": "healthy", "fastapi": "running"})
        else:
            return jsonify({"status": "degraded", "fastapi": "error"}), 503
    except:
        return jsonify({"status": "unhealthy", "fastapi": "down"}), 503

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    try:
        response = proxy_request(f'/static/{filename}')
        return response.content, response.status_code, response.headers.items()
    except:
        return "File not found", 404

@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """Generate cover letter endpoint"""
    try:
        # Forward the form data to FastAPI
        response = proxy_request('/generate-cover-letter', method='POST', data=request.form)
        
        if response.headers.get('content-type', '').startswith('application/json'):
            return response.json(), response.status_code
        else:
            return response.content, response.status_code, response.headers.items()
            
    except Exception as e:
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    """Upload resume endpoint"""
    try:
        files = {}
        if 'file' in request.files:
            files['file'] = request.files['file']
        
        response = proxy_request('/upload-resume', method='POST', files=files)
        return response.json(), response.status_code
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        response = proxy_request(f'/download/{filename}')
        return response.content, response.status_code, response.headers.items()
    except:
        return "File not found", 404

@app.route('/api/company-info/<company_name>')
def company_info(company_name):
    """Get company information"""
    try:
        response = proxy_request(f'/api/company-info/{company_name}')
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.before_first_request
def startup():
    """Initialize the application"""
    print("Starting Cover Letter Generation System...")
    
    # Start FastAPI server in background
    threading.Thread(target=start_fastapi_server, daemon=True).start()

if __name__ == '__main__':
    # Start FastAPI server
    start_fastapi_server()
    
    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False
    )

