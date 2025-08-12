# Contributing to CareerPathAI

Thank you for your interest in contributing to CareerPathAI! This guide will help you get started.

## 🚀 Getting Started

### Prerequisites
- Git installed on your machine
- Python 3.8+ 
- GitHub account
- Basic knowledge of Flask and Python

## 🔄 Contribution Workflow

### For Team Members with Direct Access:

1. **Clone the repository**
   ```bash
   git clone https://github.com/sharma-mohit-2005/CV-Analyser-Project.git
   cd CV-Analyser-Project
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, well-documented code
   - Follow the existing code style
   - Test your changes locally

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: descriptive commit message"
   ```

5. **Push to GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub repository
   - Click "Compare & pull request"
   - Add description of your changes
   - Request review from team members

### For External Contributors:

1. **Fork the repository** on GitHub
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/CV-Analyser-Project.git
   ```
3. **Follow steps 2-6** from above
4. **Submit Pull Request** from your fork to main repository

## 📝 Commit Message Guidelines

Use clear, descriptive commit messages:

- `Add: new feature or functionality`
- `Fix: bug fixes`
- `Update: improvements to existing features`
- `Docs: documentation changes`
- `Style: formatting, missing semicolons, etc.`
- `Refactor: code restructuring without functional changes`
- `Test: adding or modifying tests`

### Examples:
```
Add: user authentication system
Fix: CV upload validation error
Update: improve skill extraction algorithm
Docs: add API documentation
```

## 🧪 Testing

Before submitting your changes:

1. **Test locally**
   ```bash
   python app.py
   ```

2. **Check for errors**
   - Upload test CVs
   - Verify all features work
   - Check browser console for errors

3. **Validate code quality**
   - Ensure proper indentation
   - Remove debug print statements
   - Add comments for complex logic

## 📋 Pull Request Guidelines

### Before Creating PR:
- ✅ Test your changes thoroughly
- ✅ Update documentation if needed
- ✅ Ensure code follows project style
- ✅ Rebase with latest main branch

### PR Description Should Include:
- **What**: Brief description of changes
- **Why**: Reason for the changes
- **How**: How you implemented it
- **Testing**: How you tested the changes
- **Screenshots**: If UI changes are involved

### Example PR Template:
```markdown
## What
Added user authentication system with login/signup functionality

## Why
Users need to save their analysis history and track progress

## How
- Implemented Flask-Login for session management
- Added SQLite database for user storage
- Created login/signup forms with validation

## Testing
- Tested login/signup flow
- Verified session persistence
- Tested with multiple user accounts

## Screenshots
[Add screenshots of new UI elements]
```

## 🎯 Areas for Contribution

### High Priority:
- [ ] User authentication system
- [ ] Resume builder functionality
- [ ] Mobile responsive design improvements
- [ ] API documentation

### Medium Priority:
- [ ] Interview preparation module
- [ ] Salary prediction feature
- [ ] Advanced skill extraction algorithms
- [ ] Database optimization

### Low Priority:
- [ ] Dark mode theme
- [ ] Email notifications
- [ ] Social media integration
- [ ] Analytics dashboard enhancements

## 🚫 Code of Conduct

- Be respectful and constructive
- Help others learn and grow
- Focus on the problem, not the person
- Collaborate effectively with team members

## ❓ Questions?

If you have questions or need help:
- Create an issue on GitHub
- Contact team lead: [Your contact info]
- Join our development discussions

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

---

Happy coding! 🚀 Let's build something amazing together!
