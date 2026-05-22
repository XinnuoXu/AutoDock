from flask import Flask, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__, static_folder='static')

PROTEIN_DIR = 'protein_squences'

if not os.path.exists(PROTEIN_DIR):
    os.makedirs(PROTEIN_DIR)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/save_protein', methods=['POST'])
def save_protein():
    try:
        data = request.json
        protein_name = data.get('protein_name')
        original_protein = data.get('original_protein')
        replace_pos = data.get('replace_pos', [])

        if not protein_name or not original_protein:
            return jsonify({'error': 'Missing protein name or sequence'}), 400

        # Create JSON structure
        protein_data = {
            'original_protein': original_protein,
            'replace_pos': replace_pos
        }

        # Save to file
        filename = os.path.join(PROTEIN_DIR, f"{protein_name}.json")
        with open(filename, 'w') as f:
            json.dump(protein_data, f, indent=2)

        return jsonify({'success': True, 'filename': f"{protein_name}.json"})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list_proteins', methods=['GET'])
def list_proteins():
    try:
        files = [f for f in os.listdir(PROTEIN_DIR) if f.endswith('.json')]
        return jsonify({'proteins': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load_protein/<filename>', methods=['GET'])
def load_protein(filename):
    try:
        filepath = os.path.join(PROTEIN_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404

        with open(filepath, 'r') as f:
            data = json.load(f)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
