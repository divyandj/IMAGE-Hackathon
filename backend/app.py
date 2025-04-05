from flask import Flask, Blueprint, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from config import Config
from models.image import Image
from utils.image_generator import ImageGenerator
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)

@app.route('/generated/<path:filename>')
def serve_generated_image(filename):
    return send_from_directory(os.getcwd(), filename)

# Image blueprint
image_bp = Blueprint('image', __name__)

@image_bp.route('/generate', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    try:
        image_path, generated_prompt = ImageGenerator.generate_image(prompt)
        if not image_path:
            return jsonify({'error': 'Image generation failed'}), 500
        image_url = f"/generated/{image_path}"
        return jsonify({'image': image_url, 'prompt': generated_prompt}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@image_bp.route('/modify', methods=['POST'])
def modify_image():
    data = request.get_json()
    original_prompt = data.get('original_prompt')
    modification_prompt = data.get('modification_prompt')
    if not all([original_prompt, modification_prompt]):
        return jsonify({'error': 'Original and modification prompt required'}), 400
    try:
        modified_path, modified_prompt = ImageGenerator.modify_image(
            original_prompt=original_prompt,
            modification_prompt=modification_prompt
        )
        if not modified_path:
            return jsonify({'error': 'Image modification failed'}), 500
        modified_url = f"/generated/{modified_path}"
        return jsonify({'image': modified_url, 'prompt': modified_prompt}), 200
    except Exception as e:
        return jsonify({'error': f'Image modification failed: {str(e)}'}), 500

@image_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    return jsonify({'url': f"/uploads/{filename}"}), 200

@image_bp.route('/save', methods=['POST'])
def save_image():
    data = request.get_json()
    title = data.get('title')
    category = data.get('category')
    url = data.get('url')
    prompt = data.get('prompt')
    if not all([title, category, url, prompt]):
        return jsonify({'error': 'Missing required fields'}), 400
    image_id = Image.create("anonymous_user", title, category, url, prompt)
    return jsonify({'image_id': str(image_id), 'message': 'Image saved successfully'}), 201

@image_bp.route('/story', methods=['POST'])
def generate_story():
    data = request.get_json()
    story_prompt = data.get('story_prompt')
    num_images = data.get('num_images', 3)
    if not story_prompt or not isinstance(num_images, int) or not (1 <= num_images <= 10):
        return jsonify({'error': 'Story prompt and valid number of images (1-10) are required'}), 400
    try:
        story_result = ImageGenerator.generate_story(story_prompt, num_images)
        if not story_result or any(scene['path'] is None for scene in story_result['scenes']):
            return jsonify({'error': 'Story generation failed'}), 500
        formatted_scenes = [{
            'text': scene['text'],
            'image': f"/generated/{scene['path']}",
            'prompt': scene['prompt'],
            'timestamp': datetime.now().strftime('%B %d, %Y - %I:%M%p')
        } for scene in story_result['scenes']]
        return jsonify({'introduction': story_result['introduction'], 'scenes': formatted_scenes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Gallery blueprint
gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route('/all', methods=['GET'])
def get_all_images():
    images = Image.get_all()
    return jsonify([{
        'id': str(img['_id']),
        'title': img['title'],
        'category': img['category'],
        'url': img['url'],
        'likes': img['likes'],
        'prompt': img.get('prompt', '')
    } for img in images]), 200

@gallery_bp.route('/user', methods=['GET'])
def get_user_images():
    images = Image.find_by_user("anonymous_user")
    return jsonify([{
        'id': str(img['_id']),
        'title': img['title'],
        'category': img['category'],
        'url': img['url'],
        'likes': img['likes'],
        'prompt': img.get('prompt', '')
    } for img in images]), 200

@gallery_bp.route('/like/<image_id>', methods=['POST'])
def like_image(image_id):
    image = Image.find_by_id(image_id)
    if not image:
        return jsonify({'error': 'Image not found'}), 404
    Image.collection.update_one(
        {'_id': image['_id']},
        {'$set': {'likes': image['likes'] + 1 if image['likes'] == 0 else image['likes'] - 1}}
    )
    return jsonify({'message': 'Like toggled'}), 200

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'Invalid file name'}), 400
    filename = secure_filename(image.filename)
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    image.save(file_path)
    analysis_result = ImageGenerator.analyze_image(file_path)
    return jsonify(analysis_result), 200

# Register blueprints
app.register_blueprint(image_bp, url_prefix='/image')
app.register_blueprint(gallery_bp, url_prefix='/gallery')

@app.route('/')
def health_check():
    return 'ImageTales Backend is running without authentication', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6001)
