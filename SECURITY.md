# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please do the following:

1. **DO NOT** open a public issue
2. Email the maintainer directly at: dkpandeycan1@gmail.com
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and provide a timeline for addressing the issue.

## Security Best Practices

When using this project:

- Never commit `.env` files or virtual environments
- Keep dependencies up to date
- Use the latest Python version (3.11+)
- Don't expose the web server beyond localhost without authentication
- Be mindful of rate limits when scraping external platforms
