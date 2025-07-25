from flask import Flask, request, jsonify
from file_upload import save_uploaded_file, extract_text_from_file
from skills_extractor import extract_skills_from_text
from job_match import match_skills_to_jobs
from course_recommender import enhance_job_recommendations_with_courses
import os
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/')
def health_check():
    return jsonify({'message': 'API is running'}), 200

@app.route('/upload', methods=['POST'])
def upload_cv():
    try:
        print("Request received")

        if 'cv' not in request.files:
            print("No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['cv']
        print(f"Received file: {file.filename}")

        if file.filename == '':
            print("Empty filename")
            return jsonify({'error': 'No selected file'}), 400
        
        # Save the uploaded file
        file_path = save_uploaded_file(file)
        print(f"File saved at: {file_path}")

        if not file_path:
            print("Invalid file format")
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Extract text from the uploaded CV
        cv_text = extract_text_from_file(file_path)
        print("Text extracted")

        # Extract skills from the CV text
        extracted_skills = extract_skills_from_text(cv_text)
        print(f"Extracted skills: {extracted_skills}")

        # Match the extracted skills with relevant jobs
        job_recommendations = match_skills_to_jobs(extracted_skills)
        print(f"Matched jobs: {job_recommendations}")
        
        # Enhance job recommendations with course recommendations
        enhanced_job_recommendations = enhance_job_recommendations_with_courses(job_recommendations)
        print("Added course recommendations")

        return jsonify({
            'extracted_skills': extracted_skills,
            'job_recommendations': enhanced_job_recommendations
        })
    
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json

    # Add a timestamp to the data
    data['timestamp'] = datetime.now().isoformat()

    # Append to a JSON file
    try:
        with open('contact_data.json', 'a') as f:
            json.dump(data, f)
            f.write('\n')  # Add newline for each entry
        return jsonify({"message": "Data saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

UPLOAD_FOLDER = 'uploads'

@app.route('/cv-count')
def count_cvs():
    UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
    try:
        num_files = len([
            f for f in os.listdir(UPLOAD_FOLDER)
            if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))
        ])
        return jsonify({"cv_count": num_files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)