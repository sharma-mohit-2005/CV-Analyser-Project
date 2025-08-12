## Deployment

Two options are preconfigured: Render and Railway.

Environment variable required:
- `GEMINI_API_KEY`: Your Google Gemini Pro API key

### Render (recommended for simplicity)
1. Push to GitHub (already set up).
2. On Render, create a new Web Service from your repo.
3. When prompted, set:
   - Build Command: `pip install -r deploy-requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
4. Add environment variable `GEMINI_API_KEY`.
5. Deploy.

You can also use the `render.yaml` to auto-detect settings when importing the repo in Render.

### Railway
1. Create a new project and connect your repo.
2. Railway will read `railway.json` and use Nixpacks.
3. Ensure variable `GEMINI_API_KEY` is set.
4. Deploy.

### Notes
- Local `requirements.txt` includes extras; deployment uses `deploy-requirements.txt` to keep slug small.
- If WeasyPrint fails on the server (system libs), it’s optional; functionality will still work without PDF generation.
# CareerPathAI - AI-Powered Career Development Platform

## 🚀 Overview

CareerPathAI is an intelligent career development platform that analyzes CVs to provide personalized job recommendations, skill gap analysis, and learning pathways. Our AI-powered system helps job seekers discover their ideal career path and provides actionable insights to bridge skill gaps.

## ✨ Features

### 🔍 **CV Analysis**
- Upload CVs in multiple formats (PDF, DOCX, TXT)
- Advanced skill extraction using AI
- Comprehensive profile analysis

### 🎯 **Job Matching**
- Personalized job role recommendations
- Match percentage calculation
- Industry-specific suggestions

### 📈 **Skill Gap Analysis**
- Identify missing skills for target roles
- Prioritized skill development recommendations
- Career progression insights

### 📚 **Learning Recommendations**
- Curated course suggestions from top platforms
- Platform-specific learning paths
- Progress tracking capabilities

### 📊 **Analytics Dashboard**
- Track analyzed CVs
- User engagement metrics
- Success rate monitoring

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **AI/ML**: Custom skill extraction algorithms
- **Data Processing**: JSON-based storage
- **File Handling**: Multi-format CV parsing

## 📂 Project Structure

```
CareerPathAI/
├── app.py                 # Main Flask application
├── skills_extractor.py    # AI skill extraction module
├── job_match.py          # Job matching algorithm
├── course_recommender.py # Learning path recommendations
├── file_upload.py        # File handling utilities
├── templates/            # HTML templates
│   ├── index.html
│   └── about.html
├── uploads/              # CV upload directory
├── Scraping/            # Data collection scripts
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sharma-mohit-2005/CV-Analyser-Project.git
   cd CV-Analyser-Project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📈 Usage

1. **Upload Your CV**: Drag and drop or browse to upload your CV
2. **AI Analysis**: Our system extracts skills and analyzes your profile
3. **Get Recommendations**: Receive personalized job matches and skill gaps
4. **Learn & Grow**: Follow recommended learning paths to advance your career

## 🔮 Upcoming Features

- [ ] Advanced AI models for better skill extraction
- [ ] Real-time job market analysis
- [ ] Personalized learning dashboard
- [ ] Career progression tracking
- [ ] Interview preparation tools
- [ ] Salary prediction models
- [ ] Professional networking features

## 🤝 Contributing

We welcome contributions from team members and the community! 

### For Team Members:
- Contact repository owner for collaborator access
- Follow the branching workflow in [CONTRIBUTING.md](CONTRIBUTING.md)

### For External Contributors:
- Fork the project and submit Pull Requests
- Read our [Contributing Guidelines](CONTRIBUTING.md) for detailed instructions

### Quick Start:
1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Development Team**: Building the future of career development
- **AI Team**: Advancing skill extraction and job matching algorithms
- **UX Team**: Creating intuitive user experiences

## 📞 Contact

For questions, suggestions, or collaboration opportunities, please reach out to us.

---

**CareerPathAI** - Empowering careers through AI-driven insights 🚀
