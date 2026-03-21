"""
models.py - Database Models
============================
SQLAlchemy ORM models for Users and Summaries.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Represents an application user (regular or admin)."""

    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True,  nullable=False)
    email      = db.Column(db.String(120), unique=True,  nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    is_admin   = db.Column(db.Boolean,     default=False, nullable=False)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    is_active  = db.Column(db.Boolean,     default=True, nullable=False)

    # Relationship: one user → many summaries
    summaries  = db.relationship("Summary", backref="user", lazy=True,
                                 cascade="all, delete-orphan")

    # ── Password helpers ──────────────────────────────────────────────────────
    def set_password(self, raw_password: str) -> None:
        """Hash and store the user's password."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password, raw_password)

    def __repr__(self) -> str:
        return f"<User {self.username} ({'admin' if self.is_admin else 'user'})>"


class Summary(db.Model):
    """Stores a document summary created by a user."""

    __tablename__ = "summaries"

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename       = db.Column(db.String(256), nullable=False)
    file_type      = db.Column(db.String(20),  nullable=False)   # pdf, docx, image …
    extracted_text = db.Column(db.Text,        nullable=True)    # raw OCR / parsed text
    summary        = db.Column(db.Text,        nullable=False)
    word_count     = db.Column(db.Integer,     default=0)
    created_at     = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Summary #{self.id} – {self.filename}>"
