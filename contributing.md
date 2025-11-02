# Contributing to Coding Problem Scraper

Thank you for considering contributing to this project! 🎉

We welcome contributions of all kinds: bug reports, feature requests, documentation improvements, and code contributions.

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Git
- A GitHub account

### Setting Up Your Development Environment

1. **Fork the repository**
   - Click the "Fork" button at the top right of the repository page
   - This creates your own copy of the repository

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/codebase-problem-scrapper.git
   cd codebase-problem-scrapper
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/AVPthegreat/codebase-problem-scrapper.git
   ```

4. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -e '.[dev]'
   ```

## Making Changes

### 1. Create a feature branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

### 2. Make your changes
- Write clean, readable code
- Follow existing code style and conventions
- Add comments where necessary
- Update documentation if needed

### 3. Test your changes

**Run tests:**
```bash
pytest tests/
```

**Run the web app locally:**
```bash
python scripts/run_web.py
```
Then test at http://127.0.0.1:8000

**Check code style:**
```bash
ruff check src/ tests/
```

### 4. Commit your changes

Use clear, descriptive commit messages:
```bash
git add .
git commit -m "feat: add support for HackerRank scraper"
# or
git commit -m "fix: resolve timeout issue in Codeforces scraper"
# or
git commit -m "docs: update README with deployment instructions"
```

**Commit message prefixes:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 5. Push to your fork
```bash
git push origin feature/your-feature-name
```

### 6. Create a Pull Request
1. Go to your fork on GitHub
2. Click "Pull Request" button
3. Select your feature branch
4. Provide a clear title and description:
   - What changes did you make?
   - Why are these changes needed?
   - How did you test them?
5. Submit the Pull Request

## Code Guidelines

### Python Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions small and focused
- Write docstrings for classes and functions

### Testing
- Add tests for new features
- Ensure existing tests pass
- Aim for good test coverage

### Documentation
- Update README.md if adding new features
- Add docstrings to new functions/classes
- Comment complex logic

## What to Contribute

### Good First Issues
- Fix typos or improve documentation
- Add tests for existing code
- Improve error messages
- Add type hints

### Feature Ideas
- Support for additional coding platforms
- Improved problem filtering
- Better test case generation
- UI/UX improvements
- Export formats (PDF, Markdown, etc.)

### Bug Reports
If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error messages or logs

## Code Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited in the repository

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion in the repository
- Reach out to maintainers

## Thank You! 🙏

Every contribution, no matter how small, helps make this project better!