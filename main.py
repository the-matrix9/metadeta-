from flask import Flask, request, jsonify
from PIL import Image, ExifTags
import pytesseract
import requests
from io import BytesIO
import time
import base64

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

# Extract text using OCR
def extract_text(image):
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        return str(e)

# Image info
def get_image_info(image, file=None):
    width, height = image.size
    info = {
        "format": image.format,
        "mode": image.mode,
        "width": width,
        "height": height
    }
    if file:
        info["filename"] = file.filename
        info["size_kb"] = round(len(file.read()) / 1024, 2)
        file.seek(0)
    return info

@app.route('/')
def docs():
    return jsonify({
        "API": "Image Metadata & Text Extractor",
        "routes": {
            "/": "Show API docs",
            "/image": "POST image file (form-data) → metadata + OCR text + info",
            "/url": "POST JSON { 'url': 'http://...jpg' } → same",
            "/base64": "POST JSON { 'base64': '...' } → same"
        },
        "developer": "t.me/AnshAPi",
        "version": "v2.0"
    })

@app.route('/image', methods=['POST'])
def from_image():
    start = time.time()

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded", "developer": "t.me/AnshAPi"}), 400
    
    file = request.files['image']
    image = Image.open(file.stream)

    metadata = extract_metadata(image)
    text = extract_text(image)
    info = get_image_info(image, file)

    return jsonify({
        "image_info": info,
        "metadata": metadata,
        "text_extracted": text.strip(),
        "response_time_ms": round((time.time() - start) * 1000, 2),
        "developer": "t.me/AnshAPi"
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
    text = extract_text(image)
    info = get_image_info(image)

    return jsonify({
        "image_info": info,
        "metadata": metadata,
        "text_extracted": text.strip(),
        "response_time_ms": round((time.time() - start) * 1000, 2),
        "developer": "t.me/AnshAPi"
    })

@app.route('/base64', methods=['POST'])
def from_base64():
    start = time.time()

    data = request.get_json()
    if not data or 'base64' not in data:
        return jsonify({"error": "No base64 data provided", "developer": "t.me/AnshAPi"}), 400
    
    try:
        image_data = base64.b64decode(data['base64'])
        image = Image.open(BytesIO(image_data))
    except Exception as e:
        return jsonify({"error": f"Base64 decode failed: {str(e)}", "developer": "t.me/AnshAPi"}), 400

    metadata = extract_metadata(image)
    text = extract_text(image)
    info = get_image_info(image)

    return jsonify({
        "image_info": info,
        "metadata": metadata,
        "text_extracted": text.strip(),
        "response_time_ms": round((time.time() - start) * 1000, 2),
        "developer": "t.me/AnshAPi"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
