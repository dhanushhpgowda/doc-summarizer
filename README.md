# ⚡ DocuSumm AI — Universal Document Summarizer

> A production-ready, full-stack AI web application that turns any document into a clean, structured summary in seconds.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python\&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000?logo=flask)
![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA%203-F97316)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-10b981)

---

## ✨ Features

| Feature                     | Details                                          |
| --------------------------- | ------------------------------------------------ |
| 📄 **Multi-format support** | PDF, DOCX, PPTX, PNG, JPG, JPEG                  |
| 🧠 **LLM Summarization**    | Groq API · LLaMA 3 (8B)                          |
| 👁️ **OCR**                 | Tesseract — extracts text from images & scans    |
| 🔐 **Auth system**          | Registration, login, hashed passwords, sessions  |
| 📊 **User dashboard**       | Upload, view summaries, full history             |
| 🛡️ **Admin panel**         | User management, summary oversight, system stats |
| 🎨 **Modern UI**            | Dark editorial design, drag-and-drop, responsive |

---

## 🖥️ Screenshots

| Landing                 | Dashboard                           | Result                       | Admin                       |
| ----------------------- | ----------------------------------- | ---------------------------- | --------------------------- |
| Hero + feature sections | Drag-and-drop upload + history grid | Markdown-rendered AI summary | Stats + user/summary tables |

---

## 🏗️ Project Structure

```
docusumm/
│
├── app.py
├── config.py
├── models.py
├── auth.py
├── admin.py
├── summarizer.py
├── text_extractor.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── result.html
│   ├── admin_dashboard.html
│   └── error.html
│
├── static/
│   ├── css/style.css
│   └── js/script.js
│
├── uploads/
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

* Backend: Python · Flask · Flask-Login · Flask-SQLAlchemy
* Database: SQLite
* AI: Groq API — LLaMA 3
* OCR: Tesseract OCR
* File Parsing: PyMuPDF · python-docx · python-pptx · Pillow
* Security: Werkzeug hashing · sessions · validation
* Frontend: Jinja2 · Font Awesome · marked.js

---

## 🚀 Quick Start

### Clone

```
git clone https://github.com/yourusername/docusumm-ai.git
cd docusumm-ai
```

### Virtual Env

```
python -m venv venv
venv\Scripts\activate
```

### Install

```
pip install -r requirements.txt
```

### Run

```
python app.py
```

Visit → http://localhost:5000

---

## 🔑 Default Admin

Email → [admin@docusumm.ai](mailto:admin@docusumm.ai)
Password → Admin@1234

---

## 📋 Supported Files

PDF · DOCX · PPTX · PNG · JPG · JPEG

---

## 🤖 AI Flow

Upload → Extract → Summarize → Store → Display

---

## 🛡️ Security

Password hashing · file validation · admin protection

---

## 🌐 Deployment

Use gunicorn · strong secret key · PostgreSQL in prod

---

## 📄 License

MIT

---

## 🙏 Credits

Groq · Tesseract · PyMuPDF

---

## 👨‍💻 Developed By

**Done by Dhanush — BE Student | AI & Full-Stack Developer**
