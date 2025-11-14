# 🔐 Keystone Redactor Framework

> **Privacy-first AI pipeline**: Detect, redact, process with LLMs, restore PII safely—without ever exposing sensitive data to third parties.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Gemini API](https://img.shields.io/badge/Powered%20by-Gemini%20AI-orange.svg)](https://ai.google.dev/)

---

## 🚀 What Is This?

A **production-ready privacy framework** for using Large Language Models (LLMs) like Google Gemini on sensitive data—**without ever sending Personal Identifiable Information (PII) to external APIs**.

### Core Features:
- 🔍 **Automated PII Detection** — Names, emails, dates, locations, phone numbers, and more
- 🛡️ **Secure Redaction** — Replaces PII with unique placeholders before LLM processing
- 🤖 **LLM Integration** — Google Gemini API with full logging and error handling
- 🔄 **Smart Restoration** — Restores original PII in LLM outputs for human-readable results
- 📊 **Full Audit Trail** — Every stage logged for compliance and transparency

**Built for GDPR compliance, enterprise security, and privacy-conscious AI development.**

---

## 🎯 Why Does This Matter?

LLMs are powerful—but sending raw user data to cloud APIs is a **privacy and compliance risk**. Keystone Redactor ensures:
- ✅ **Zero PII exposure** to third-party services
- ✅ **GDPR/CCPA compliant** workflows
- ✅ **Full auditability** for enterprise and research use
- ✅ **Production-ready** modular architecture

---

## 📂 Project Structure

Keystone-Redactor_Framework/
├── redactor/
│ ├── detector.py # PII detection (spaCy + regex)
│ ├── redactor.py # Redaction with placeholder mapping
│ ├── llm_client.py # Gemini API client
│ ├── restorer.py # De-redaction and PII restoration
│ └── init.py
├── demo.py # End-to-end demonstration
├── requirements.txt # Python dependencies
├── .env.example # API key template
├── .gitignore
└── README.md

text

---

## ⚡ Quick Start

### 1. Clone and Install
git clone https://github.com/karantomar11/Keystone-Redactor_Framework.git
cd Keystone-Redactor_Framework
pip install -r requirements.txt
python -m spacy download en_core_web_sm

text

### 2. Configure API Key
Create a `.env` file in the project root:
GEMINI_API_KEY=your-api-key-here

text

### 3. Run the Demo
python demo.py

text

---

## 🛠️ How It Works

### Pipeline Overview

Input Text (with PII)
↓
PIIDetector → Detects entities (names, emails, dates, etc.)
↓
Redactor → Replaces PII with placeholders: [PERSON_A], [EMAIL_A]
↓
LLM Client → Sends ONLY redacted text to Gemini API
↓
Restorer → Maps placeholders back to original PII
↓
Final Output (fully restored, human-readable)

text

### Example Workflow

**Input:**
"Schedule a call with Dr. Evelyn Reed for May 20, 2024.
Email: e.reed@science-corp.net. Budget: $750."

text

**Redacted (sent to LLM):**
"Schedule a call with Dr. [PERSON_A] for [DATE_A].
Email: [EMAIL_A]. Budget: $[MONEY_A]."

text

**LLM Response:**
"Here are the key points:

Call scheduled with Dr. [PERSON_A] on [DATE_A]

Contact: [EMAIL_A]

Budget: $[MONEY_A]"

text

**Restored Output:**
"Here are the key points:

Call scheduled with Dr. Evelyn Reed on May 20, 2024

Contact: e.reed@science-corp.net

Budget: $750"

text

✅ **No PII ever sent to external APIs**

---

## 🧪 Use Cases

- **Enterprise AI**: Use LLMs on customer data without compliance risk
- **Healthcare & Legal**: Process sensitive documents with AI assistance
- **Research**: Privacy-preserving NLP workflows
- **Startups**: Build AI features with privacy by design

---

## 🔧 Extending the Framework

- Swap LLM providers (OpenAI, Anthropic, etc.)
- Add custom entity types (credit cards, SSNs, etc.)
- Build a REST API or web interface
- Integrate with data pipelines (batch processing, streaming)

---

## 📝 Requirements

- Python 3.9+
- Google Gemini API key ([Get one here](https://ai.google.dev/))
- Dependencies: `spacy`, `google-generativeai`, `python-dotenv`

---

## 🤝 Contributing

Contributions welcome! Please open issues or pull requests for:
- New PII detection patterns
- LLM provider integrations
- Performance optimizations
- Documentation improvements

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Karan Tomar**  
📍 Berlin, Germany  
🔗 [GitHub](https://github.com/karantomar11) | [LinkedIn](https://linkedin.com/in/yourprofile)

---

## ⭐ Show Your Support

If this project helped you, give it a ⭐️ on GitHub!

---

**Built with privacy in mind. Powered by AI.**