from flask import Flask, request, jsonify, render_template, make_response, send_file
from file_upload import save_uploaded_file, extract_text_from_file
from skills_extractor import extract_skills_from_text
from job_match import match_skills_to_jobs
from course_recommender import enhance_job_recommendations_with_courses
from ats_analyzer import analyze_cv_for_ats
import os
from flask_cors import CORS
import json
from datetime import datetime
import tempfile
import io

app = Flask(__name__)
CORS(app)
    
WEASYPRINT_AVAILABLE = False
REPORTLAB_AVAILABLE = False

# Check for PDF generation libraries availability
def check_pdf_libraries():
    global REPORTLAB_AVAILABLE
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        REPORTLAB_AVAILABLE = True
        print("ReportLab available for PDF generation")
        return True
    except ImportError as e:
        print(f"ReportLab not available: {e}")
        REPORTLAB_AVAILABLE = False
        return False

# Initialize PDF libraries on startup
check_pdf_libraries()

if not REPORTLAB_AVAILABLE and not WEASYPRINT_AVAILABLE:
    print("No PDF generation libraries available. Will use HTML fallback.")



# Gemini Pro API integration
import requests

# You may want to store your Gemini Pro API key securely (e.g., environment variable)
GEMINI_API_KEY = os.getenv('AIzaSyBWk5dpBGhSIJVK4PGwBbAJt8YULhSNgvQ',)
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

def generate_roadmap_with_gemini(job_role, current_skills):
    prompt = f"""
You are an expert career coach and instructional designer. 
Your task is to generate a structured career roadmap for a student who wants to become a {job_role}.
The roadmap must be actionable, beginner-friendly, and personalized to the user's current skills: {current_skills}.

Instructions:
1. Break the roadmap into sequential stages (Stage 1, Stage 2, etc.).
2. For each stage, include:
   - Stage Name
   - Description (2-3 sentences)
   - Skills to learn (list)
   - Recommended projects (list)
   - Certifications/courses (list)
   - Estimated duration in months
3. Suggest learning order so skills build progressively.
4. Highlight any skill gaps based on {current_skills}.
5. Output the result ONLY in the following JSON format:

{
  "job_role": "...",
  "total_duration_months": ...,
  "stages": [
    {
      "stage_number": 1,
      "stage_name": "...",
      "description": "...",
      "skills": ["...", "..."],
      "projects": ["...", "..."],
      "certifications": ["...", "..."],
      "duration_months": ...
    }
  ],
  "skill_gaps": ["...", "..."]
}
"""
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }
    params = {"key": GEMINI_API_KEY}
    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
    if response.status_code == 200:
        try:
            result = response.json()
            # Extract the model's text output
            text = result['candidates'][0]['content']['parts'][0]['text']
            # Try to parse as JSON
            roadmap_json = json.loads(text)
            return roadmap_json, None
        except Exception as e:
            return None, f"Error parsing Gemini response: {e}"
    else:
        return None, f"Gemini API error: {response.status_code} {response.text}"

# Roadmap generation endpoint
@app.route('/generate_roadmap', methods=['POST'])
def generate_roadmap():
    data = request.get_json()
    job_role = data.get('job_role', '').strip()
    current_skills = data.get('current_skills', [])
    if not job_role:
        return jsonify({'error': 'Job role required'}), 400
    if not isinstance(current_skills, list):
        return jsonify({'error': 'Current skills must be a list'}), 400
    roadmap, error = generate_roadmap_with_gemini(job_role, current_skills)
    if error:
        return jsonify({'error': error}), 500
    return jsonify(roadmap)

@app.route('/')
def health_check():
    return jsonify({'message': 'API is running'}), 200

# Serve roadmap page
@app.route('/roadmap')
def roadmap_page():
    return render_template('roadmap.html')

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

        # Analyze CV for ATS compatibility
        ats_analysis = analyze_cv_for_ats(cv_text)
        print(f"ATS analysis completed: Score {ats_analysis.get('analysis', {}).get('overall_score', 'N/A')}")

        return jsonify({
            'extracted_skills': extracted_skills,
            'job_recommendations': enhanced_job_recommendations,
            'ats_analysis': ats_analysis
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

@app.route('/cv-count')
def count_cvs():
    upload_folder = os.path.join(app.root_path, 'uploads')
    try:
        num_files = len([
            f for f in os.listdir(upload_folder)
            if os.path.isfile(os.path.join(upload_folder, f))
        ])
        return jsonify({"cv_count": num_files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cv-builder')
def cv_builder():
    """CV Builder page"""
    return render_template('cv-builder.html')

@app.route('/ats-analyzer')
def ats_analyzer():
    """ATS Score Analyzer page"""
    return render_template('ats_analyzer.html')

@app.route('/api/generate-cv', methods=['POST'])
def generate_cv():
    """Generate CV from form data"""
    try:
        cv_data = request.json
        print(f"Received CV data: {cv_data}")  # Debug log
        
        if not cv_data:
            return jsonify({"error": "No data provided"}), 400
            
        output_format = cv_data.get('output_format', 'pdf')  # default to PDF
        print(f"Output format requested: {output_format}")  # Debug log
        
        if output_format == 'pdf' and REPORTLAB_AVAILABLE:
            try:
                print("Attempting PDF generation with ReportLab...")  # Debug log
                # Generate PDF using ReportLab
                pdf_buffer = io.BytesIO()
                generate_cv_pdf_reportlab(cv_data, pdf_buffer)
                pdf_buffer.seek(0)
                
                print("PDF generated successfully")  # Debug log
                
                # Create response with PDF
                response = make_response(pdf_buffer.getvalue())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename="{cv_data.get("personal", {}).get("fullName", "CV").replace(" ", "_")}.pdf"'
                
                return response
                
            except Exception as pdf_error:
                print(f"ReportLab PDF generation error: {pdf_error}")
                import traceback
                traceback.print_exc()  # Print full traceback
                # Fallback to HTML since WeasyPrint is not available
                output_format = 'html'
        
        print("Falling back to HTML generation...")  # Debug log
        # Return HTML content (either requested or as fallback)
        html_content = generate_cv_html(cv_data)
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename="{cv_data.get("personal", {}).get("fullName", "CV").replace(" ", "_")}.html"'
        
        return response
        
    except Exception as e:
        print(f"CV generation error: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full traceback
        return jsonify({"error": f"Failed to generate CV: {str(e)}"}), 500

def generate_cv_html(cv_data):
    """Generate HTML content for CV"""
    # Helper function to safely get nested data
    def safe_get(data, key, default=''):
        if data and isinstance(data, dict):
            return data.get(key, default)
        return default
    
    # Validate required data
    if not cv_data or not isinstance(cv_data, dict):
        raise ValueError("Invalid CV data provided")
    
    personal = cv_data.get('personal', {})
    full_name = safe_get(personal, 'fullName', 'Your Name')
    
    # Generate sections dynamically
    sections_html = ""
    
    # Professional Summary/Objective
    summary = cv_data.get('summary', '').strip()
    if summary:
        sections_html += f"""
        <div class="section">
            <h2>Professional Summary</h2>
            <p>{summary}</p>
        </div>
        """
    
    # Experience Section
    experience = cv_data.get('experience', [])
    if experience and isinstance(experience, list) and len(experience) > 0:
        sections_html += """
        <div class="section">
            <h2>Professional Experience</h2>
        """
        for exp in experience:
            if isinstance(exp, dict):
                position = safe_get(exp, 'position', 'Position')
                company = safe_get(exp, 'company', 'Company')
                start_date = safe_get(exp, 'startDate', '')
                end_date = safe_get(exp, 'endDate', 'Present')
                description = safe_get(exp, 'description', '')
                
                sections_html += f"""
                <div class="item">
                    <div class="item-header">
                        <span class="position">{position}</span>
                        <span class="dates">{start_date} - {end_date}</span>
                    </div>
                    <div class="company">{company}</div>
                    {f'<p class="description">{description}</p>' if description else ''}
                </div>
                """
        sections_html += "</div>"
    
    # Education Section
    education = cv_data.get('education', [])
    if education and isinstance(education, list) and len(education) > 0:
        sections_html += """
        <div class="section">
            <h2>Education</h2>
        """
        for edu in education:
            if isinstance(edu, dict):
                degree = safe_get(edu, 'degree', 'Degree')
                school = safe_get(edu, 'school', 'Institution')
                graduation_date = safe_get(edu, 'graduationDate', '')
                gpa = safe_get(edu, 'gpa', '')
                
                sections_html += f"""
                <div class="item">
                    <div class="item-header">
                        <span class="position">{degree}</span>
                        <span class="dates">{graduation_date}</span>
                    </div>
                    <div class="company">{school}</div>
                    {f'<p class="gpa">GPA: {gpa}</p>' if gpa else ''}
                </div>
                """
        sections_html += "</div>"
    
    # Skills Section
    skills = cv_data.get('skills', [])
    if skills and isinstance(skills, list) and len(skills) > 0:
        sections_html += """
        <div class="section">
            <h2>Skills</h2>
            <div class="skills">
        """
        for skill in skills:
            if skill and isinstance(skill, str):
                sections_html += f'<span class="skill">{skill.strip()}</span>'
        sections_html += """
            </div>
        </div>
        """
    
    # Projects Section
    projects = cv_data.get('projects', [])
    if projects and isinstance(projects, list) and len(projects) > 0:
        sections_html += """
        <div class="section">
            <h2>Projects</h2>
        """
        for project in projects:
            if isinstance(project, dict):
                name = safe_get(project, 'name', 'Project')
                description = safe_get(project, 'description', '')
                technologies = safe_get(project, 'technologies', '')
                
                sections_html += f"""
                <div class="item">
                    <div class="position">{name}</div>
                    {f'<p class="description">{description}</p>' if description else ''}
                    {f'<p class="technologies"><strong>Technologies:</strong> {technologies}</p>' if technologies else ''}
                </div>
                """
        sections_html += "</div>"
    
    # Certifications Section
    certifications = cv_data.get('certifications', [])
    if certifications and isinstance(certifications, list) and len(certifications) > 0:
        sections_html += """
        <div class="section">
            <h2>Certifications</h2>
        """
        for cert in certifications:
            if isinstance(cert, dict):
                name = safe_get(cert, 'name', 'Certification')
                issuer = safe_get(cert, 'issuer', '')
                date = safe_get(cert, 'date', '')
                
                sections_html += f"""
                <div class="item">
                    <div class="item-header">
                        <span class="position">{name}</span>
                        <span class="dates">{date}</span>
                    </div>
                    {f'<div class="company">{issuer}</div>' if issuer else ''}
                </div>
                """
        sections_html += "</div>"
    
    # Languages Section
    languages = cv_data.get('languages', [])
    if languages and isinstance(languages, list) and len(languages) > 0:
        sections_html += """
        <div class="section">
            <h2>Languages</h2>
        """
        for lang in languages:
            if isinstance(lang, dict):
                language = safe_get(lang, 'language', 'Language')
                proficiency = safe_get(lang, 'proficiency', '')
                
                sections_html += f"""
                <div class="language-item">
                    <span class="language-name">{language}</span>
                    {f'<span class="proficiency">({proficiency})</span>' if proficiency else ''}
                </div>
                """
            elif isinstance(lang, str):
                sections_html += f'<div class="language-item"><span class="language-name">{lang}</span></div>'
        sections_html += "</div>"
    
    # Get contact information
    email = safe_get(personal, 'email', '')
    phone = safe_get(personal, 'phone', '')
    location = safe_get(personal, 'location', '')
    linkedin = safe_get(personal, 'linkedin', '')
    website = safe_get(personal, 'website', '')
    
    # Build contact string
    contact_parts = []
    if email:
        contact_parts.append(f'<a href="mailto:{email}">{email}</a>')
    if phone:
        contact_parts.append(phone)
    if location:
        contact_parts.append(location)
    if linkedin:
        contact_parts.append(f'<a href="{linkedin}" target="_blank">LinkedIn</a>')
    if website:
        contact_parts.append(f'<a href="{website}" target="_blank">Website</a>')
    
    contact_info = ' | '.join(contact_parts) if contact_parts else ''
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{full_name} - CV</title>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm;
            }}
            
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 0;
                line-height: 1.6; 
                color: #333; 
                font-size: 11pt;
            }}
            
            .header {{ 
                text-align: center; 
                border-bottom: 3px solid #2c3e50; 
                padding-bottom: 15px; 
                margin-bottom: 25px; 
            }}
            
            .name {{ 
                font-size: 24pt; 
                font-weight: bold; 
                margin-bottom: 8px; 
                color: #2c3e50; 
                letter-spacing: 1px;
            }}
            
            .contact {{ 
                color: #666; 
                font-size: 10pt; 
                line-height: 1.4;
            }}
            
            .contact a {{
                color: #2c3e50;
                text-decoration: none;
            }}
            
            .section {{ 
                margin-bottom: 20px; 
                page-break-inside: avoid;
            }}
            
            .section h2 {{ 
                color: #2c3e50; 
                border-bottom: 2px solid #3498db; 
                padding-bottom: 5px; 
                margin-bottom: 12px; 
                font-size: 14pt;
                font-weight: 600;
            }}
            
            .item {{ 
                margin-bottom: 12px; 
                page-break-inside: avoid;
            }}
            
            .item-header {{ 
                display: flex; 
                justify-content: space-between; 
                margin-bottom: 4px; 
                align-items: baseline;
            }}
            
            .position {{ 
                font-weight: bold; 
                font-size: 12pt; 
                color: #2c3e50;
            }}
            
            .company {{ 
                color: #666; 
                font-style: italic; 
                margin-bottom: 4px; 
                font-size: 10pt;
            }}
            
            .dates {{ 
                color: #888; 
                font-size: 9pt; 
                font-weight: normal;
            }}
            
            .description, .gpa, .technologies {{
                margin: 4px 0; 
                font-size: 10pt;
                text-align: justify;
            }}
            
            .skills {{ 
                display: flex; 
                flex-wrap: wrap; 
                gap: 6px; 
            }}
            
            .skill {{ 
                background: #ecf0f1; 
                padding: 4px 8px; 
                border-radius: 3px; 
                font-size: 9pt; 
                border: 1px solid #bdc3c7;
                color: #2c3e50;
            }}
            
            .language-item {{
                margin-bottom: 4px;
                font-size: 10pt;
            }}
            
            .language-name {{
                font-weight: 500;
            }}
            
            .proficiency {{
                color: #666;
                font-style: italic;
            }}
            
            /* Print optimizations */
            @media print {{
                body {{ 
                    -webkit-print-color-adjust: exact; 
                    color-adjust: exact;
                }}
                .section {{ 
                    page-break-inside: avoid; 
                }}
                .item {{ 
                    page-break-inside: avoid; 
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="name">{full_name}</div>
            <div class="contact">{contact_info}</div>
        </div>
        
        {sections_html}
        
    </body>
    </html>
    """
    
    return html

def generate_cv_pdf_reportlab(cv_data, buffer):
    """Generate PDF using ReportLab"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    except ImportError as e:
        raise ImportError(f"ReportLab library not available: {e}")
    
    # Helper function to safely get nested data
    def safe_get(data, key, default=''):
        if data and isinstance(data, dict):
            return data.get(key, default)
        return default
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
    story = []
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    )
    
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#666666')
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=16,
        textColor=colors.HexColor('#2c3e50'),
        borderWidth=1,
        borderColor=colors.HexColor('#3498db'),
        borderPadding=4
    )
    
    item_title_style = ParagraphStyle(
        'ItemTitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceBefore=8,
        spaceAfter=4,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )
    
    item_company_style = ParagraphStyle(
        'ItemCompanyStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        textColor=colors.HexColor('#666666'),
        fontName='Helvetica-Oblique'
    )
    
    # Personal information
    personal = cv_data.get('personal', {})
    full_name = safe_get(personal, 'fullName', 'Your Name')
    
    # Add name
    story.append(Paragraph(full_name, title_style))
    
    # Add contact information
    contact_parts = []
    if safe_get(personal, 'email'):
        contact_parts.append(safe_get(personal, 'email'))
    if safe_get(personal, 'phone'):
        contact_parts.append(safe_get(personal, 'phone'))
    if safe_get(personal, 'location'):
        contact_parts.append(safe_get(personal, 'location'))
    
    if contact_parts:
        contact_info = ' | '.join(contact_parts)
        story.append(Paragraph(contact_info, contact_style))
    
    # Professional Summary
    summary = cv_data.get('summary', '').strip()
    if summary:
        story.append(Paragraph('Professional Summary', section_style))
        story.append(Paragraph(summary, styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Experience Section
    experience = cv_data.get('experience', [])
    if experience and isinstance(experience, list) and len(experience) > 0:
        story.append(Paragraph('Professional Experience', section_style))
        for exp in experience:
            if isinstance(exp, dict):
                position = safe_get(exp, 'position', 'Position')
                company = safe_get(exp, 'company', 'Company')
                start_date = safe_get(exp, 'startDate', '')
                end_date = safe_get(exp, 'endDate', 'Present')
                description = safe_get(exp, 'description', '')
                
                # Position and dates
                position_text = f"{position}"
                if start_date or end_date:
                    position_text += f" ({start_date} - {end_date})"
                
                story.append(Paragraph(position_text, item_title_style))
                story.append(Paragraph(company, item_company_style))
                
                if description:
                    story.append(Paragraph(description, styles['Normal']))
                story.append(Spacer(1, 8))
    
    # Education Section
    education = cv_data.get('education', [])
    if education and isinstance(education, list) and len(education) > 0:
        story.append(Paragraph('Education', section_style))
        for edu in education:
            if isinstance(edu, dict):
                degree = safe_get(edu, 'degree', 'Degree')
                school = safe_get(edu, 'school', 'Institution')
                graduation_date = safe_get(edu, 'graduationDate', '')
                gpa = safe_get(edu, 'gpa', '')
                
                degree_text = degree
                if graduation_date:
                    degree_text += f" ({graduation_date})"
                
                story.append(Paragraph(degree_text, item_title_style))
                story.append(Paragraph(school, item_company_style))
                
                if gpa:
                    story.append(Paragraph(f"GPA: {gpa}", styles['Normal']))
                story.append(Spacer(1, 8))
    
    # Skills Section
    skills = cv_data.get('skills', [])
    if skills and isinstance(skills, list) and len(skills) > 0:
        story.append(Paragraph('Skills', section_style))
        skills_text = ' • '.join([skill.strip() for skill in skills if skill and isinstance(skill, str)])
        story.append(Paragraph(skills_text, styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Projects Section
    projects = cv_data.get('projects', [])
    if projects and isinstance(projects, list) and len(projects) > 0:
        story.append(Paragraph('Projects', section_style))
        for project in projects:
            if isinstance(project, dict):
                name = safe_get(project, 'name', 'Project')
                description = safe_get(project, 'description', '')
                technologies = safe_get(project, 'technologies', '')
                
                story.append(Paragraph(name, item_title_style))
                if description:
                    story.append(Paragraph(description, styles['Normal']))
                if technologies:
                    story.append(Paragraph(f"<b>Technologies:</b> {technologies}", styles['Normal']))
                story.append(Spacer(1, 8))
    
    # Certifications Section
    certifications = cv_data.get('certifications', [])
    if certifications and isinstance(certifications, list) and len(certifications) > 0:
        story.append(Paragraph('Certifications', section_style))
        for cert in certifications:
            if isinstance(cert, dict):
                name = safe_get(cert, 'name', 'Certification')
                issuer = safe_get(cert, 'issuer', '')
                date = safe_get(cert, 'date', '')
                
                cert_text = name
                if date:
                    cert_text += f" ({date})"
                
                story.append(Paragraph(cert_text, item_title_style))
                if issuer:
                    story.append(Paragraph(issuer, item_company_style))
                story.append(Spacer(1, 8))
    
    # Languages Section
    languages = cv_data.get('languages', [])
    if languages and isinstance(languages, list) and len(languages) > 0:
        story.append(Paragraph('Languages', section_style))
        lang_texts = []
        for lang in languages:
            if isinstance(lang, dict):
                language = safe_get(lang, 'language', 'Language')
                proficiency = safe_get(lang, 'proficiency', '')
                if proficiency:
                    lang_texts.append(f"{language} ({proficiency})")
                else:
                    lang_texts.append(language)
            elif isinstance(lang, str):
                lang_texts.append(lang)
        
        if lang_texts:
            lang_text = ' • '.join(lang_texts)
            story.append(Paragraph(lang_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)

@app.route('/api/pdf-status')
def pdf_status():
    """Check if PDF generation is available"""
    return jsonify({
        'pdf_available': REPORTLAB_AVAILABLE or WEASYPRINT_AVAILABLE,
        'reportlab_available': REPORTLAB_AVAILABLE,
        'weasyprint_available': WEASYPRINT_AVAILABLE,
        'message': 'PDF generation ready' if (REPORTLAB_AVAILABLE or WEASYPRINT_AVAILABLE) else 'PDF generation unavailable - will fallback to HTML'
    })

@app.route('/api/ats-analysis', methods=['POST'])
def ats_analysis():
    """Analyze CV for ATS compatibility and provide improvement suggestions"""
    try:
        print("ATS Analysis endpoint hit")
        
        # Check if file is uploaded
        if 'file' not in request.files:
            print("No file uploaded")
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        target_job_title = request.form.get('job_title', '')
        
        if file.filename == '':
            print("No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        # Save the uploaded file
        print(f"Processing file: {file.filename}")
        file_path = save_uploaded_file(file)
        print(f"File saved to: {file_path}")
        
        # Extract text from the uploaded file
        cv_text = extract_text_from_file(file_path)
        print(f"Extracted text length: {len(cv_text)} characters")
        
        if not cv_text or len(cv_text.strip()) < 50:
            return jsonify({
                'error': 'Could not extract sufficient text from the file. Please ensure the file is readable and contains text.',
                'success': False
            }), 400
        
        # Perform ATS analysis
        print("Starting ATS analysis...")
        ats_results = analyze_cv_for_ats(cv_text, target_job_title)
        print(f"ATS analysis completed. Overall score: {ats_results['analysis']['overall_score']}")
        
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up file: {file_path}")
        
        return jsonify({
            'success': True,
            'ats_analysis': ats_results,
            'message': 'ATS analysis completed successfully'
        })
        
    except Exception as e:
        print(f"Error in ATS analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Failed to analyze CV: {str(e)}',
            'success': False
        }), 500

@app.route('/api/test', methods=['GET', 'POST'])
def test_api():
    """Test endpoint to verify API is working"""
    if request.method == 'POST':
        return jsonify({
            'status': 'success',
            'message': 'POST request received',
            'data': request.json
        })
    else:
        return jsonify({
            'status': 'success',
            'message': 'API is working',
            'method': 'GET'
        })

# ...existing code...

if __name__ == '__main__':
    app.run(debug=True)