
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from datetime import datetime
import os
import glob

app = Flask(__name__)

# Store alerts
alerts_history = []

# Directory to save received images
IMAGES_DIR = "received_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

@app.route('/alert', methods=['POST'])
def receive_alert():
    """Receive alert from detection system with optional image"""
    # Handle both JSON and form-data
    if request.is_json:
        data = request.json
        image_file = None
    else:
        data = request.form.to_dict()
        # Convert confidence to float if present
        if 'confidence' in data:
            data['confidence'] = float(data['confidence'])
        image_file = request.files.get('image')
    
    # Save image if provided
    image_path = None
    image_filename = None
    if image_file:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"human_detection_{timestamp_str}.jpg"
        image_path = os.path.join(IMAGES_DIR, image_filename)
        image_file.save(image_path)
        data['image_path'] = image_path
        data['image_url'] = f"/images/{image_filename}"
        print(f"📸 Image saved: {image_path}")
    
    # Store alert
    alerts_history.append(data)
    
    # Print alert
    print("\n" + "=" * 60)
    print("🚨 ALERT RECEIVED!")
    print("=" * 60)
    print(f"Sound: {data.get('sound')}")
    print(f"Confidence: {data.get('confidence')}")
    print(f"Risk Level: {data.get('risk')}")
    print(f"Message: {data.get('message')}")
    print(f"Timestamp: {data.get('timestamp')}")
    print(f"Sensor ID: {data.get('sensor_id')}")
    print(f"Zone ID: {data.get('zone_id')}")
    if image_path:
        print(f"Image: {image_path}")
    print("=" * 60 + "\n")
    
    return jsonify({"status": "received", "message": "Alert processed", "image_saved": image_path is not None}), 200

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts history"""
    return jsonify({"alerts": alerts_history, "count": len(alerts_history)}), 200

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve image files"""
    return send_from_directory(IMAGES_DIR, filename)

@app.route('/view_images')
def view_images():
    """View all received images in a web page"""
    # Get all image files
    image_files = sorted(glob.glob(os.path.join(IMAGES_DIR, "*.jpg")), reverse=True)
    image_filenames = [os.path.basename(f) for f in image_files]
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Human Detection Images</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
            }
            .image-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .image-card {
                background: white;
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .image-card img {
                width: 100%;
                height: auto;
                border-radius: 4px;
            }
            .image-card p {
                margin: 10px 0 0 0;
                color: #666;
                font-size: 14px;
            }
            .no-images {
                text-align: center;
                color: #999;
                margin-top: 40px;
                font-size: 18px;
            }
            .back-link {
                display: inline-block;
                margin-bottom: 20px;
                color: #007bff;
                text-decoration: none;
            }
            .back-link:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <a href="/" class="back-link">← Back to Home</a>
        <h1>📸 Human Detection Images</h1>
        {% if images %}
        <p>Total images: {{ images|length }}</p>
        <div class="image-grid">
            {% for image in images %}
            <div class="image-card">
                <img src="/images/{{ image }}" alt="{{ image }}">
                <p>{{ image }}</p>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="no-images">
            No images received yet. Images will appear here when alerts are sent with human detection.
        </div>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_template, images=image_filenames)

@app.route('/')
def index():
    """Home page with links to view alerts and images"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Alert System Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            .link-card {
                display: block;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 20px;
                margin: 15px 0;
                text-decoration: none;
                color: #333;
                transition: background-color 0.2s;
            }
            .link-card:hover {
                background: #e9ecef;
            }
            .link-card h2 {
                margin: 0 0 10px 0;
                color: #007bff;
            }
            .link-card p {
                margin: 0;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚨 Alert System Dashboard</h1>
            <a href="/view_images" class="link-card">
                <h2>📸 View Detection Images</h2>
                <p>View all captured human detection images</p>
            </a>
            <a href="/alerts" class="link-card">
                <h2>📋 View Alert History</h2>
                <p>View all alerts in JSON format</p>
            </a>
            <a href="/health" class="link-card">
                <h2>💚 Health Check</h2>
                <p>Check if the server is running</p>
            </a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "running"}), 200

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 Alert Backend Server Starting...")
    print("=" * 60)
    print("📍 Server running on: http://localhost:8000")
    print("📍 Alert endpoint: http://localhost:8000/alert")
    print("📍 View images: http://localhost:8000/view_images")
    print("📍 View alerts: http://localhost:8000/alerts")
    print("📍 Dashboard: http://localhost:8000/")
    print("📍 Health check: http://localhost:8000/health")
    print("=" * 60)
    print("\n⚠️  Keep this running while using live_detection.py")
    print("📸 Images are saved to: received_images/")
    print("🌐 Open http://localhost:8000/view_images in your browser to see images")
    print("Press Ctrl+C to stop the server\n")
    
    app.run(host='localhost', port=8000, debug=True)
