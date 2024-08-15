from flask import Flask, request, jsonify
from flask_cors import CORS
from app.utils.pdf_extractor import extract_pdf_sections
from app.utils.table_extractor import extract_pdf_tables
import os
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/")
def index():
    return jsonify({'name': 'Minhazul Hasan', 'email': 'minhazul.hasan.sohan@gmail.com', 'phone': '01723183898'})



@app.route("/get_pdf_content/", methods=["POST"])
def get_pdf_content():
    if 'file' not in request.files:
        return jsonify({'detail': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.content_type != 'application/pdf':
        return jsonify({'detail': 'Only PDF files are allowed.'}), 400

    try:
        contents = file.read()
        extracted_sections_dict = extract_pdf_sections(contents)
        extracted_tables_dict = extract_pdf_tables(contents, file.filename)
        # Merge the two dictionaries
        merged_dict = {**extracted_sections_dict, **extracted_tables_dict}
        # Save CSV
        df = pd.DataFrame(list(merged_dict.items()), columns=['Section', 'Content'])
        os.makedirs('output', exist_ok=True)
        csv_path = os.path.join('output', f"{file.filename.replace('.pdf', '.csv')}")
        df.to_csv(csv_path, index=False)
        return jsonify(merged_dict)
    except Exception as e:
        return jsonify({'detail': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
