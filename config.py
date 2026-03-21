"""
config.py - Application Configuration
======================================
Central configuration for the Universal AI Document Summarizer.
All sensitive values should be overridden via environment variables in production.
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production-please")

    # ── Database ──────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'docusumm.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── File Uploads ──────────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB hard limit
    ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "png", "jpg", "jpeg"}

    # ── Groq AI ───────────────────────────────────────────────────────────────
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ── Admin seed credentials (used only on first-run seeding) ───────────────
    ADMIN_EMAIL    = os.environ.get("ADMIN_EMAIL",    "admin@docusumm.ai")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@1234")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "Admin")
