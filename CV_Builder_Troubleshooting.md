# CV Builder Troubleshooting Guide

## ✅ Current Status
- Flask backend is running on `http://127.0.0.1:5000`
- ReportLab PDF generation is available
- API endpoints are working
- CORS is properly configured

## 🔧 How to Test

### 1. Test API Connection
1. Open CV Builder: `http://127.0.0.1:5000/cv-builder`
2. Navigate to Step 6 (Review & Generate)
3. Click "Test API Connection" button
4. Should see green "API connection successful!" notification

### 2. Test CV Generation
1. Click "Test CV Generation" button
2. Should download a test PDF file automatically
3. Check browser's download folder for `test_cv.pdf`

### 3. Test Full CV Generation
1. Fill in your information through all steps
2. At Step 6, click "Generate & Download CV"
3. Should download your personalized CV as PDF

## 🐛 If You're Still Getting Errors

### Check Browser Console
1. Press F12 to open Developer Tools
2. Go to Console tab
3. Try generating CV and check for any error messages
4. Look for network errors in the Network tab

### Common Issues & Solutions

#### Issue: "Failed to fetch" or network error
**Solution**: 
- Make sure Flask is running (`python app.py`)
- Check that you're accessing `http://127.0.0.1:5000/cv-builder` (not localhost)
- Try refreshing the page

#### Issue: CV doesn't download
**Solution**:
- Check browser's download settings
- Allow pop-ups for the site
- Try using a different browser
- Check if the file is blocked by antivirus

#### Issue: PDF generation fails
**Solution**:
- The system will automatically fallback to HTML
- HTML files can be printed as PDF using browser
- Check Flask logs for detailed error messages

### Manual Testing via Command Line
Test the API directly:
```bash
# Test basic API
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/test" -Method GET

# Test CV generation (create test.json with CV data first)
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/generate-cv" -Method POST -Body (Get-Content test.json) -ContentType "application/json"
```

## 📝 Sample Test Data
If you want to test with specific data, use this JSON structure:

```json
{
    "personal": {
        "fullName": "John Doe",
        "email": "john@example.com",
        "phone": "123-456-7890",
        "location": "New York, NY"
    },
    "summary": "Experienced software developer",
    "experience": [
        {
            "position": "Software Developer",
            "company": "Tech Corp",
            "startDate": "Jan 2020",
            "endDate": "Present",
            "description": "Developed web applications"
        }
    ],
    "education": [
        {
            "degree": "Computer Science",
            "school": "University",
            "graduationDate": "2019",
            "gpa": "3.8"
        }
    ],
    "skills": ["JavaScript", "Python", "React"],
    "projects": [
        {
            "name": "Web App",
            "description": "A cool web application",
            "technologies": "React, Node.js"
        }
    ],
    "template": "modern",
    "output_format": "pdf"
}
```

## 🎯 Expected Behavior
1. **API Test**: Should show success notification in 1-2 seconds
2. **CV Generation**: Should start download within 3-5 seconds
3. **File Download**: PDF should be 50-200KB depending on content
4. **Error Handling**: Clear error messages if something fails

## 📞 Next Steps
1. Try the "Test API Connection" button first
2. If that works, try "Test CV Generation"
3. If both work, fill out the form and generate your CV
4. Check browser console if any step fails
5. Check Flask terminal logs for backend errors

The CV Builder is now properly configured and should work correctly!
