from flask import Flask, request, jsonify
import os
import tempfile
import docx2txt
import pdfplumber

app = Flask(__name__)

@app.route('/parse', methods=['POST'])
def parse_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    filename = file.filename.lower()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        filepath = tmp.name

    try:
        if filename.endswith('.docx'):
            text = docx2txt.process(filepath)
        elif filename.endswith('.pdf'):
            with pdfplumber.open(filepath) as pdf:
                text = "\n".join(page.extract_text() or '' for page in pdf.pages)
        elif filename.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        else:
            return jsonify({"error": "Unsupported file format"}), 400
    finally:
        os.remove(filepath)

    return jsonify({"text": text.strip()})
