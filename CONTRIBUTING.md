# Contributing to evi.run

Thank you for your interest in contributing to **evi.run**! We welcome contributions from the community.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/pipedude/evi-run.git
   cd evi-run
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and test them
5. **Commit your changes**:
   ```bash
   git commit -m "feat: add your feature description"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request** on GitHub

## 🛠️ Development Setup

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Local Development
```bash
# Clone and setup
git clone https://github.com/pipedude/evi-run.git
cd evi-run

# Configure environment
cp .env.example .env
nano .env  # Add your API keys
nano config.py  # Set your Telegram ID

# Start development environment
docker compose up --build
```

## 📋 Types of Contributions

- **🐛 Bug Reports**: Create detailed issue reports
- **✨ Features**: Propose and implement new features
- **📚 Documentation**: Improve README or code comments
- **🧪 Tests**: Add or improve test coverage
- **🌐 Localization**: Add translations in `I18N/`
- **🤖 Custom Agents**: Add new AI agents in `bot/agents_tools/`

## 🎯 Guidelines

### Code Style
- Follow **PEP 8** for Python
- Use meaningful variable names
- Add docstrings for functions
- Keep functions focused and small

### Commit Messages
Use conventional commit format:
```
feat(agents): add new trading agent
fix(database): resolve connection issue
docs(readme): update installation guide
style: format code according to PEP 8
```

### Testing
```bash
# Run tests
python -m pytest

# Run with coverage
python -m pytest --cov=bot
```

## 🔒 Security

- **Never commit API keys or secrets**
- Use environment variables for sensitive data
- Report security issues privately to project maintainers

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/pipedude/evi-run/issues)
- **Telegram**: [@playa3000](https://t.me/playa3000)
- **Community**: [Telegram Support Group](https://t.me/evi_run)

---

**Thank you for contributing to evi.run! 🚀**
