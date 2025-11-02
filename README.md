<div align="center">

# 🎯 Competitive Programming Test Case Generator

**Transform coding problem ideas into ready-to-test bundles with a single click**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Contributing](#-contributing) • [License](#-license)

</div>

---

## 🚀 What is This?

A powerful FastAPI web application that scrapes coding problems from top competitive programming platforms, generates test cases with `.in`/`.out` files, and packages everything into downloadable bundles. Perfect for educators, competitive programmers, and coding interview preparation.

## ✨ Features

- **🌐 Multi-Platform Support**: Scrapes from Codeforces, LeetCode, CodeChef, GeeksforGeeks, and AtCoder
- **🎨 Modern Web UI**: Clean, single-page interface with real-time progress tracking
- **📊 Live Updates**: Watch your scraping job progress with streaming logs
- **🎯 Smart Filtering**: Select specific platforms and difficulty levels
- **✅ Problem Curation**: Review, accept, or reject problems before downloading
- **📦 Instant Downloads**: Get filtered ZIP bundles with organized test cases
- **⚡ Placeholder Mode**: Generate synthetic problems instantly for testing
- **🔄 Job Queue**: Background processing with concurrent job support

## 📸 Demo

> **Note**: Screenshots and demo video coming soon! In the meantime, try the app yourself following the setup below.

### 💡 Example Workflow

1. Enter: *"Give me 5 medium difficulty sorting problems"*
2. Select platforms: Codeforces, LeetCode
3. Watch real-time scraping progress
4. Review and curate problems
5. Download filtered bundle with organized test cases

---

## 🏃 Quick Start

### Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AVPthegreat/codebase-problem-scrapper.git
cd codebase-problem-scrapper

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 4. Install dependencies
pip install -e '.[dev]'

# 5. Launch the app
python scripts/run_web.py
```

### First Run

Open your browser and navigate to **http://127.0.0.1:8000**

Try this example:
- **Prompt**: "Give me 3 easy array problems"
- **Platforms**: Select Codeforces
- **Difficulty**: Easy
- **Click**: "Generate Problems"

---

## 📖 Usage

### Basic Workflow

1. **Enter Your Prompt**
   - Describe what problems you want (e.g., "5 dynamic programming problems")
   - Be specific about topics, difficulty, or quantity

2. **Configure Options**
   - **Platforms**: Choose one or more (Codeforces, LeetCode, etc.)
   - **Difficulty**: Easy, Medium, Hard, or Mixed
   - **Placeholder Mode**: Enable for instant synthetic test problems

3. **Monitor Progress**
   - Real-time progress bar and live logs
   - See which platforms are being scraped
   - Track problem discovery in real-time

4. **Curate Results**
   - Review all discovered problems
   - Accept ✅ or reject ❌ individual problems
   - See problem descriptions and metadata

5. **Download Bundle**
   - Click "Download Selected Problems"
   - Get a ZIP file with organized folders
   - Each problem includes `.in` and `.out` test files

### Advanced Features

**Placeholder Mode** 🎭
- Instant synthetic problems for UI testing
- No network requests or rate limiting
- Perfect for demos and development

**Platform Filtering** 🔍
- Select specific platforms for targeted scraping
- Combine multiple sources in one bundle
- Leave all unchecked to search everywhere

**Job Queue** 📋
- Multiple jobs can be queued
- Background processing doesn't block UI
- Check `/recent` for job history

---

## 🏗️ Project Structure

```
codebase-problem-scrapper/
├── src/
│   ├── app/
│   │   └── services/
│   │       ├── orchestrator.py      # Core bundle generation logic
│   │       └── scrapers/            # Platform-specific scrapers
│   │           ├── codeforces.py
│   │           ├── leetcode.py
│   │           ├── codechef.py
│   │           ├── geeksforgeeks.py
│   │           └── atcoder.py
│   └── webapp/
│       ├── main.py                   # FastAPI application
│       └── templates/                # Jinja2 HTML templates
│           ├── index.html            # Main UI
│           ├── job.html              # Job details
│           └── recent.html           # Job history
├── scripts/
│   └── run_web.py                    # Server launcher
├── tests/
│   └── test_orchestrator.py         # Unit tests
├── .github/
│   ├── ISSUE_TEMPLATE/               # Bug & feature templates
│   └── pull_request_template.md     # PR template
├── pyproject.toml                    # Dependencies & config
├── LICENSE                           # MIT License
├── CODE_OF_CONDUCT.md               # Community guidelines
├── SECURITY.md                       # Security policy
└── README.md                         # You are here!
```

---

## ⚙️ Configuration

### Environment Variables

Currently, the app runs without external API keys. Future enhancements may include:
- OpenAI integration for intelligent test case generation
- OAuth for platform authentication
- Custom scraping rate limits

### Custom Settings

Edit `scripts/run_web.py` to customize:
- **Port**: Change from default `8000`
- **Host**: Bind to `0.0.0.0` for network access (add auth first!)
- **Workers**: Adjust concurrent scraping jobs

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py -v

# Check code style
ruff check src/ tests/
```

---

## 🛡️ Security & Best Practices

- ✅ **Never commit** `.env` files or virtual environments
- ✅ **Respect rate limits** when scraping live platforms
- ✅ **Use placeholder mode** for demos and testing
- ✅ **Add authentication** before exposing beyond localhost
- ✅ **Review** the [Security Policy](SECURITY.md) before reporting vulnerabilities

---

## 🐛 Troubleshooting

<details>
<summary><b>Port 8000 already in use</b></summary>

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or run on different port
# Edit scripts/run_web.py and change port number
```
</details>

<details>
<summary><b>Missing dependencies error</b></summary>

```bash
# Reinstall all dependencies
pip install -e '.[dev]'

# Or install specific package
pip install <package-name>
```
</details>

<details>
<summary><b>Virtual environment not activating</b></summary>

```bash
# On macOS/Linux
source .venv/bin/activate

# On Windows
.venv\Scripts\activate

# On Windows PowerShell
.venv\Scripts\Activate.ps1
```
</details>

<details>
<summary><b>Tests failing</b></summary>

```bash
# Ensure you're in virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate

# Reinstall dependencies
pip install -e '.[dev]'

# Run tests with verbose output
pytest tests/ -v
```
</details>

<details>
<summary><b>Scraping returns no results</b></summary>

- Check your internet connection
- Some platforms may have rate limits or anti-scraping measures
- Try placeholder mode for testing
- Check platform availability (some may be down temporarily)
</details>

---

## 🤝 Contributing

We love contributions! Whether it's bug fixes, new features, or documentation improvements.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'feat: add amazing feature'`)
4. **Push** to your branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

See [CONTRIBUTING.md](contributing.md) for detailed guidelines.

### Contribution Ideas

- 🎨 Add more platform scrapers
- 🚀 Improve scraping accuracy and speed
- 📱 Create mobile-responsive UI
- 🤖 Integrate AI for test case generation
- 🌐 Add internationalization support
- 📊 Add analytics and statistics

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **Uvicorn** - Lightning-fast ASGI server
- **Jinja2** - Powerful templating engine
- All the competitive programming platforms for providing great problems

---

## 📬 Contact & Support

- **Author**: Anant Vardhan Pandey
- **GitHub**: [@AVPthegreat](https://github.com/AVPthegreat)
- **Issues**: [Report a bug or request a feature](https://github.com/AVPthegreat/codebase-problem-scrapper/issues)

---

<div align="center">

**Built with ❤️ by [AVPTHEGREAT](https://github.com/AVPthegreat)**

⭐ Star this repo if you find it helpful!

[Report Bug](https://github.com/AVPthegreat/codebase-problem-scrapper/issues/new?template=bug_report.md) • [Request Feature](https://github.com/AVPthegreat/codebase-problem-scrapper/issues/new?template=feature_request.md)

</div>
