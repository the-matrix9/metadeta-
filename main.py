from flask import Flask, request, jsonify
from PIL import Image, ExifTags
import requests
import time
from io import BytesIO

app = Flask(__name__)

# Extract EXIF metadata
def extract_metadata(image):
    metadata = {}
    try:
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tagname = ExifTags.TAGS.get(tag, tag)
                metadata[tagname] = value
    except Exception as e:
        metadata["error"] = str(e)
    return metadata

# Image info
def get_image_info(image):
    width, height = image.size
    info = {
        "format": image.format,
        "mode": image.mode,
        "width": width,
        "height": height
    }
    return info

@app.route('/')
def docs():
    return jsonify({
        "API": "Image Metadata Extractor",
        "routes": {
            "/": "Show API docs",
            "/url": "POST JSON { 'url': 'http://...jpg' } → metadata"
        },
        "developer": "t.me/AnshAPi",
        "version": "v2.0"
    })

@app.route('/url', methods=['POST'])
def from_url():
    start = time.time()

    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided", "developer": "t.me/AnshAPi"}), 400
    
    try:
        response = requests.get(data['url'])
        image = Image.open(BytesIO(response.content))
    except Exception as e:
        return jsonify({"error": f"Image fetch failed: {str(e)}", "developer": "t.me/AnshAPi"}), 400

    metadata = extract_metadata(image)
    info = get_image_info(image)

    return jsonify({
        "image_info": info,
        "metadata": metadata,
        "response_time_ms": round((time.time() - start) * 1000, 2),
        "developer": "t.me/AnshAPi"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
