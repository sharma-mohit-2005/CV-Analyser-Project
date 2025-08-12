"""
ATS (Applicant Tracking System) Score Analyzer
Analyzes CVs for ATS compatibility and provides improvement suggestions
"""

import re
import json
from datetime import datetime
from collections import Counter
import os

class ATSAnalyzer:
    def __init__(self):
        # Load common ATS keywords and patterns
        self.load_ats_patterns()
        
    def load_ats_patterns(self):
        """Load ATS-friendly patterns and keywords"""
        # Technical skills keywords
        self.technical_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'html', 'css',
            'machine learning', 'data science', 'artificial intelligence', 'aws', 'azure',
            'docker', 'kubernetes', 'git', 'agile', 'scrum', 'devops', 'ci/cd',
            'tensorflow', 'pytorch', 'pandas', 'numpy', 'api', 'rest', 'microservices',
            'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'spring boot',
            'angular', 'vue.js', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go',
            'kotlin', 'swift', 'flutter', 'django', 'flask', 'express.js'
        ]
        
        # Soft skills keywords
        self.soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'creative', 'adaptable', 'collaborative', 'organized', 'detail-oriented',
            'time management', 'project management', 'critical thinking', 'innovative',
            'strategic planning', 'decision making', 'interpersonal', 'multitasking',
            'negotiation', 'presentation', 'mentoring', 'coaching', 'conflict resolution'
        ]
        
        # Action verbs preferred by ATS
        self.action_verbs = [
            'achieved', 'administered', 'analyzed', 'built', 'created', 'developed',
            'designed', 'enhanced', 'established', 'executed', 'generated', 'implemented',
            'improved', 'increased', 'led', 'managed', 'optimized', 'organized',
            'planned', 'reduced', 'resolved', 'streamlined', 'supervised', 'transformed',
            'delivered', 'collaborated', 'coordinated', 'facilitated', 'initiated',
            'launched', 'maintained', 'monitored', 'negotiated', 'operated', 'performed'
        ]
        
        # Industry-specific keywords
        self.industry_keywords = {
            'software': ['programming', 'coding', 'development', 'software', 'algorithms', 'debugging', 'testing', 'deployment'],
            'data': ['analytics', 'statistics', 'visualization', 'modeling', 'database', 'big data', 'reporting', 'insights'],
            'marketing': ['campaigns', 'branding', 'seo', 'social media', 'content', 'roi', 'advertising', 'digital marketing'],
            'finance': ['financial', 'accounting', 'budget', 'forecasting', 'analysis', 'investment', 'audit', 'compliance'],
            'hr': ['recruitment', 'talent', 'employee', 'performance', 'training', 'benefits', 'onboarding', 'culture'],
            'sales': ['revenue', 'targets', 'conversion', 'pipeline', 'prospecting', 'closing', 'customer relationship'],
            'healthcare': ['patient care', 'medical', 'clinical', 'diagnosis', 'treatment', 'healthcare', 'medical records'],
            'engineering': ['design', 'manufacturing', 'quality', 'testing', 'CAD', 'specifications', 'technical documentation']
        }

        # Common sections that should be present
        self.required_sections = {
            'contact': ['contact', 'phone', 'email', 'address', 'linkedin'],
            'experience': ['experience', 'work', 'employment', 'career', 'professional', 'history'],
            'education': ['education', 'degree', 'university', 'college', 'school', 'qualification'],
            'skills': ['skills', 'competencies', 'technologies', 'technical', 'expertise']
        }

    def analyze_cv(self, cv_text, target_job_title=""):
        """
        Comprehensive ATS analysis of CV text
        Returns ATS score and detailed suggestions
        """
        analysis_results = {
            'overall_score': 0,
            'category_scores': {},
            'suggestions': [],
            'keyword_analysis': {},
            'formatting_issues': [],
            'strengths': [],
            'improvement_areas': [],
            'detailed_feedback': {}
        }
        
        # Perform various ATS checks
        analysis_results['category_scores']['format'] = self.analyze_format(cv_text, analysis_results)
        analysis_results['category_scores']['keywords'] = self.analyze_keywords(cv_text, target_job_title, analysis_results)
        analysis_results['category_scores']['structure'] = self.analyze_structure(cv_text, analysis_results)
        analysis_results['category_scores']['content'] = self.analyze_content_quality(cv_text, analysis_results)
        analysis_results['category_scores']['length'] = self.analyze_length(cv_text, analysis_results)
        analysis_results['category_scores']['readability'] = self.analyze_readability(cv_text, analysis_results)
        
        # Calculate overall score with weighted categories
        category_weights = {
            'format': 0.20,
            'keywords': 0.30,
            'structure': 0.20,
            'content': 0.15,
            'length': 0.10,
            'readability': 0.05
        }
        
        overall_score = sum(
            analysis_results['category_scores'][category] * weight 
            for category, weight in category_weights.items()
        )
        
        analysis_results['overall_score'] = round(overall_score, 1)
        analysis_results['score_interpretation'] = self.get_score_interpretation(overall_score)
        
        return analysis_results

    def analyze_format(self, cv_text, results):
        """Analyze CV format for ATS compatibility"""
        score = 100
        issues = []
        
        # Check for excessive special characters
        special_chars = re.findall(r'[•●▪▫◦‣⁃★☆♦♥♠♣]', cv_text)
        if len(special_chars) > 15:
            score -= 15
            issues.append("Too many special bullet characters detected")
            results['suggestions'].append("Use simple hyphens (-) or asterisks (*) for bullet points instead of special symbols")
        elif len(special_chars) > 0:
            results['strengths'].append("Moderate use of formatting symbols")
        
        # Check for proper email format
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, cv_text)
        if not emails:
            score -= 20
            issues.append("No email address found")
            results['suggestions'].append("Add a clear, professional email address in a standard format")
        elif len(emails) == 1:
            results['strengths'].append("Professional email format detected")
        else:
            score -= 5
            issues.append("Multiple email addresses found")
            results['suggestions'].append("Use only one professional email address")
            
        # Check for phone number
        phone_patterns = [
            r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+\d{1,3}[-.\s]?\d{8,12}',
            r'\d{10,12}'
        ]
        
        phone_found = False
        for pattern in phone_patterns:
            if re.search(pattern, cv_text):
                phone_found = True
                break
                
        if not phone_found:
            score -= 15
            issues.append("No phone number found")
            results['suggestions'].append("Add a clear phone number in standard format")
        else:
            results['strengths'].append("Contact phone number is present")
        
        # Check for excessive formatting (tabs, multiple spaces)
        excessive_tabs = len(re.findall(r'\t{2,}', cv_text))
        excessive_spaces = len(re.findall(r' {4,}', cv_text))
        
        if excessive_tabs > 5 or excessive_spaces > 10:
            score -= 10
            issues.append("Excessive use of tabs or spaces for formatting")
            results['suggestions'].append("Use consistent, simple formatting without excessive tabs or spaces")
        
        # Check for tables/columns indicators
        table_indicators = ['|', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼']
        if any(indicator in cv_text for indicator in table_indicators):
            score -= 20
            issues.append("Table formatting detected")
            results['suggestions'].append("Avoid tables and complex formatting - use simple text layout")
        
        results['formatting_issues'] = issues
        return max(0, score)

    def analyze_keywords(self, cv_text, target_job_title, results):
        """Analyze keyword density and relevance"""
        cv_lower = cv_text.lower()
        score = 0
        
        # Count technical skills
        tech_skills_found = [skill for skill in self.technical_skills if skill.lower() in cv_lower]
        tech_score = min(len(tech_skills_found) * 6, 35)  # Max 35 points for tech skills
        
        # Count soft skills
        soft_skills_found = [skill for skill in self.soft_skills if skill.lower() in cv_lower]
        soft_score = min(len(soft_skills_found) * 4, 25)  # Max 25 points for soft skills
        
        # Count action verbs
        action_verbs_found = [verb for verb in self.action_verbs if verb.lower() in cv_lower]
        action_score = min(len(action_verbs_found) * 2, 25)  # Max 25 points for action verbs
        
        # Industry-specific keywords bonus
        industry_score = 0
        industry_terms_found = []
        for industry, terms in self.industry_keywords.items():
            for term in terms:
                if term.lower() in cv_lower:
                    industry_terms_found.append(term)
                    industry_score += 1
        
        industry_score = min(industry_score * 1.5, 15)  # Max 15 points for industry terms
        
        score = tech_score + soft_score + action_score + industry_score
        
        # Store keyword analysis
        results['keyword_analysis'] = {
            'technical_skills': tech_skills_found,
            'soft_skills': soft_skills_found,
            'action_verbs': action_verbs_found,
            'industry_terms': industry_terms_found,
            'technical_skills_count': len(tech_skills_found),
            'soft_skills_count': len(soft_skills_found),
            'action_verbs_count': len(action_verbs_found),
            'industry_terms_count': len(industry_terms_found)
        }
        
        # Provide suggestions based on keyword analysis
        if len(tech_skills_found) < 3:
            results['suggestions'].append("Add more technical skills relevant to your field (programming languages, tools, technologies)")
            results['improvement_areas'].append("Technical Skills")
        elif len(tech_skills_found) >= 8:
            results['strengths'].append(f"Excellent technical skills coverage ({len(tech_skills_found)} skills found)")
        else:
            results['strengths'].append(f"Good technical skills representation ({len(tech_skills_found)} skills found)")
            
        if len(soft_skills_found) < 2:
            results['suggestions'].append("Include more soft skills like 'leadership', 'communication', 'teamwork', 'problem solving'")
            results['improvement_areas'].append("Soft Skills")
        else:
            results['strengths'].append(f"Good soft skills representation ({len(soft_skills_found)} skills found)")
            
        if len(action_verbs_found) < 5:
            results['suggestions'].append("Use more strong action verbs to describe your accomplishments (achieved, developed, led, improved)")
            results['improvement_areas'].append("Action Verbs")
        else:
            results['strengths'].append(f"Strong use of action verbs ({len(action_verbs_found)} found)")
        
        if len(industry_terms_found) < 3:
            results['suggestions'].append("Include more industry-specific keywords and terminology relevant to your field")
            results['improvement_areas'].append("Industry Keywords")
        else:
            results['strengths'].append(f"Good use of industry-specific terminology ({len(industry_terms_found)} terms)")
        
        return min(score, 100)

    def analyze_structure(self, cv_text, results):
        """Analyze CV structure and organization"""
        score = 100
        cv_lower = cv_text.lower()
        missing_sections = []
        
        # Check for essential sections
        for section, keywords in self.required_sections.items():
            section_found = any(keyword in cv_lower for keyword in keywords)
            if not section_found:
                missing_sections.append(section.title())
                score -= 20
        
        if missing_sections:
            results['suggestions'].append(f"Add missing essential sections: {', '.join(missing_sections)}")
            results['improvement_areas'].extend(missing_sections)
        else:
            results['strengths'].append("All essential CV sections are present")
        
        # Check for clear section headers
        section_headers = re.findall(r'^[A-Z][A-Z\s&]{2,}$', cv_text, re.MULTILINE)
        professional_headers = ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'CONTACT', 'SUMMARY', 'OBJECTIVE', 'PROJECTS', 'CERTIFICATIONS']
        
        found_headers = []
        for header in section_headers:
            if any(prof_header in header.upper() for prof_header in professional_headers):
                found_headers.append(header)
        
        if len(found_headers) < 3:
            score -= 15
            results['suggestions'].append("Use clear, consistent section headers (e.g., EXPERIENCE, EDUCATION, SKILLS)")
        else:
            results['strengths'].append(f"Clear section organization with {len(found_headers)} professional headers")
        
        # Check for logical order (contact info should be at top)
        lines = cv_text.split('\n')[:10]  # Check first 10 lines
        early_contact = False
        for line in lines:
            if re.search(r'@|phone|\+\d|email', line.lower()):
                early_contact = True
                break
        
        if not early_contact:
            score -= 10
            results['suggestions'].append("Place contact information at the top of your CV")
        else:
            results['strengths'].append("Contact information is properly positioned")
        
        return max(0, score)

    def analyze_content_quality(self, cv_text, results):
        """Analyze content quality and relevance"""
        score = 100
        
        # Check for quantifiable achievements
        numbers_pattern = r'\b\d+(?:\.\d+)?%?\b'
        numbers_found = re.findall(numbers_pattern, cv_text)
        quantifiable_words = ['increased', 'decreased', 'improved', 'reduced', 'grew', 'achieved', 'exceeded']
        
        quantifiable_achievements = 0
        for word in quantifiable_words:
            if word.lower() in cv_text.lower():
                quantifiable_achievements += len(re.findall(rf'{word}.*?\d+', cv_text, re.IGNORECASE))
        
        if len(numbers_found) < 3:
            score -= 25
            results['suggestions'].append("Include more quantifiable achievements with specific numbers, percentages, or metrics")
            results['improvement_areas'].append("Quantifiable Results")
        elif quantifiable_achievements >= 3:
            results['strengths'].append(f"Excellent use of quantifiable achievements ({quantifiable_achievements} found)")
        else:
            results['strengths'].append(f"Good use of metrics and numbers ({len(numbers_found)} found)")
        
        # Check for dates and timeframes
        date_patterns = [
            r'\b\d{4}\b',  # Years
            r'\b\d{1,2}/\d{4}\b',  # MM/YYYY
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',  # Month Year
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
        ]
        
        dates_found = 0
        for pattern in date_patterns:
            dates_found += len(re.findall(pattern, cv_text, re.IGNORECASE))
        
        if dates_found < 2:
            score -= 15
            results['suggestions'].append("Include clear dates for education and work experience (MM/YYYY format)")
            results['improvement_areas'].append("Date Formatting")
        else:
            results['strengths'].append("Clear timeline with proper date formatting")
        
        # Check for professional summary/objective
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        has_summary = any(keyword in cv_text.lower() for keyword in summary_keywords)
        
        if not has_summary:
            score -= 10
            results['suggestions'].append("Add a professional summary or objective statement at the beginning")
        else:
            results['strengths'].append("Professional summary or objective present")
        
        # Check for consistency in formatting
        bullet_points = len(re.findall(r'^[\s]*[-•*]\s', cv_text, re.MULTILINE))
        if bullet_points > 0:
            results['strengths'].append("Good use of bullet points for readability")
        else:
            score -= 5
            results['suggestions'].append("Use bullet points to make your experience more readable")
        
        return max(0, score)

    def analyze_length(self, cv_text, results):
        """Analyze CV length appropriateness"""
        word_count = len(cv_text.split())
        char_count = len(cv_text.replace(' ', '').replace('\n', ''))
        
        score = 100
        
        if word_count < 150:
            score -= 40
            results['suggestions'].append("CV is too short. Add more details about your experience, skills, and achievements")
            results['improvement_areas'].append("Content Length")
        elif word_count > 1200:
            score -= 25
            results['suggestions'].append("CV might be too long. Consider condensing to 1-2 pages for better readability")
            results['improvement_areas'].append("Content Length")
        elif word_count > 800:
            score -= 10
            results['suggestions'].append("Consider condensing some sections to ensure your CV stays concise")
        else:
            results['strengths'].append(f"Appropriate length ({word_count} words)")
        
        return max(0, score)

    def analyze_readability(self, cv_text, results):
        """Analyze CV readability and clarity"""
        score = 100
        
        # Check for overly long sentences
        sentences = re.split(r'[.!?]+', cv_text)
        long_sentences = [s for s in sentences if len(s.split()) > 25]
        
        if len(long_sentences) > 5:
            score -= 20
            results['suggestions'].append("Break down long sentences for better readability")
        
        # Check for paragraph structure
        paragraphs = cv_text.split('\n\n')
        very_long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]
        
        if len(very_long_paragraphs) > 2:
            score -= 15
            results['suggestions'].append("Break down large text blocks into smaller, more digestible sections")
        
        # Check for consistency in capitalization
        inconsistent_caps = len(re.findall(r'\b[a-z]+[A-Z][a-z]*\b', cv_text))
        if inconsistent_caps > 5:
            score -= 10
            results['suggestions'].append("Ensure consistent capitalization throughout your CV")
        
        return max(0, score)

    def get_score_interpretation(self, score):
        """Provide interpretation of ATS score"""
        if score >= 85:
            return {
                'level': 'Excellent',
                'description': 'Your CV is highly ATS-friendly and likely to pass automated screening systems',
                'color': '#22c55e',
                'icon': 'fas fa-check-circle'
            }
        elif score >= 70:
            return {
                'level': 'Good',
                'description': 'Your CV has good ATS compatibility with room for minor improvements',
                'color': '#3b82f6',
                'icon': 'fas fa-thumbs-up'
            }
        elif score >= 55:
            return {
                'level': 'Fair',
                'description': 'Your CV needs some improvements to be more ATS-friendly',
                'color': '#f59e0b',
                'icon': 'fas fa-exclamation-triangle'
            }
        else:
            return {
                'level': 'Poor',
                'description': 'Your CV needs significant improvements for ATS compatibility',
                'color': '#ef4444',
                'icon': 'fas fa-times-circle'
            }

    def generate_improvement_plan(self, analysis_results):
        """Generate a detailed improvement plan"""
        improvement_plan = {
            'priority_actions': [],
            'quick_fixes': [],
            'long_term_improvements': [],
            'keyword_suggestions': [],
            'ats_optimization_tips': []
        }
        
        score = analysis_results['overall_score']
        
        # Priority actions based on score
        if score < 55:
            improvement_plan['priority_actions'] = [
                "Restructure CV with clear section headers (EXPERIENCE, EDUCATION, SKILLS)",
                "Add contact information in standard format (email, phone)",
                "Include more relevant keywords from your industry",
                "Add quantifiable achievements with specific numbers and metrics",
                "Ensure proper CV length (300-800 words)"
            ]
        elif score < 70:
            improvement_plan['priority_actions'] = [
                "Enhance keyword density with more technical and soft skills",
                "Add more action verbs to describe your accomplishments",
                "Include industry-specific terminology",
                "Improve quantifiable achievements"
            ]
        else:
            improvement_plan['priority_actions'] = [
                "Fine-tune keyword placement for specific job applications",
                "Optimize content for target roles",
                "Add industry certifications if applicable"
            ]
        
        # Quick fixes (can be done immediately)
        improvement_plan['quick_fixes'] = [
            "Replace special bullet symbols with simple hyphens (-) or asterisks (*)",
            "Ensure consistent date formatting (MM/YYYY)",
            "Add missing contact information (email, phone, LinkedIn)",
            "Use standard section headers in ALL CAPS",
            "Remove tables, graphics, or complex formatting",
            "Spell-check and proofread for errors"
        ]
        
        # Long-term improvements
        improvement_plan['long_term_improvements'] = [
            "Develop and highlight more technical skills relevant to your field",
            "Gain quantifiable achievements in your current or future roles",
            "Obtain industry certifications and add them to your CV",
            "Build a portfolio of projects to showcase your skills",
            "Keep your CV updated with latest achievements and skills"
        ]
        
        # Keyword suggestions based on analysis
        keyword_analysis = analysis_results['keyword_analysis']
        if keyword_analysis['technical_skills_count'] < 5:
            improvement_plan['keyword_suggestions'].extend([
                "Add programming languages you know (Python, Java, JavaScript, etc.)",
                "Include software tools and platforms you've used",
                "Mention relevant technologies and frameworks"
            ])
        
        if keyword_analysis['soft_skills_count'] < 3:
            improvement_plan['keyword_suggestions'].extend([
                "Highlight leadership and management experience",
                "Emphasize communication and presentation skills",
                "Mention teamwork and collaboration achievements"
            ])
        
        # ATS optimization tips
        improvement_plan['ats_optimization_tips'] = [
            "Use keywords from the job description in your CV",
            "Save your CV as both PDF and Word format",
            "Use standard fonts like Arial, Times New Roman, or Calibri",
            "Avoid headers, footers, and text boxes",
            "Use simple formatting with clear section breaks",
            "Include both acronyms and full forms (e.g., 'AI' and 'Artificial Intelligence')",
            "Tailor your CV for each job application"
        ]
        
        return improvement_plan

def analyze_cv_for_ats(cv_text, target_job_title=""):
    """
    Main function to analyze CV for ATS compatibility
    """
    analyzer = ATSAnalyzer()
    analysis_results = analyzer.analyze_cv(cv_text, target_job_title)
    improvement_plan = analyzer.generate_improvement_plan(analysis_results)
    
    return {
        'analysis': analysis_results,
        'improvement_plan': improvement_plan,
        'timestamp': datetime.now().isoformat(),
        'target_job': target_job_title if target_job_title else "General Analysis"
    }
