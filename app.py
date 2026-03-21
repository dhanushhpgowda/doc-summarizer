"""
app.py - Application Entry Point
==================================
Initialises Flask, registers blueprints, sets up the database,
and defines the main (user-facing) routes.
"""

import os
import uuid
import logging
from flask import (
    Flask, render_template, redirect, url_for,
    flash, request, current_app
)
from flask_login import LoginManager, login_required, current_user
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Summary
from auth import auth_bp
from admin import admin_bp
from text_extractor import extract_text
from summarizer import summarize

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)


# ── App factory ───────────────────────────────────────────────────────────────

def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view      = "auth.login"
    login_manager.login_message   = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # ── DB + seed ─────────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_admin(app)

    # ── Routes ────────────────────────────────────────────────────────────────
    _register_main_routes(app)
    _register_error_handlers(app)

    return app


# ── Admin seeding ─────────────────────────────────────────────────────────────

def _seed_admin(app: Flask) -> None:
    """Create default admin account on first run."""
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            username=app.config["ADMIN_USERNAME"],
            email=app.config["ADMIN_EMAIL"],
            is_admin=True,
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()
        logger.info("Default admin account created: %s", app.config["ADMIN_EMAIL"])


# ── Utility helpers ───────────────────────────────────────────────────────────

def _allowed_file(filename: str) -> bool:
    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def _unique_filename(original: str) -> str:
    """Prefix filename with a UUID to avoid collisions."""
    ext = original.rsplit(".", 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"


# ── Main routes ───────────────────────────────────────────────────────────────

def _register_main_routes(app: Flask) -> None:

    # Landing page
    @app.route("/")
    def index():
        return render_template("index.html")

    # User dashboard
    @app.route("/dashboard")
    @login_required
    def dashboard():
        summaries = (
            Summary.query
            .filter_by(user_id=current_user.id)
            .order_by(Summary.created_at.desc())
            .all()
        )
        return render_template("dashboard.html", summaries=summaries)

    # Upload + summarise
    @app.route("/upload", methods=["POST"])
    @login_required
    def upload():
        if "document" not in request.files:
            flash("No file selected.", "danger")
            return redirect(url_for("dashboard"))

        file = request.files["document"]

        if file.filename == "":
            flash("No file selected.", "danger")
            return redirect(url_for("dashboard"))

        if not _allowed_file(file.filename):
            flash(
                "Unsupported file type. Allowed: PDF, DOCX, PPTX, PNG, JPG, JPEG.",
                "danger",
            )
            return redirect(url_for("dashboard"))

        # Save file securely
        safe_name   = secure_filename(file.filename)
        unique_name = _unique_filename(safe_name)
        filepath    = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
        file.save(filepath)

        extension = safe_name.rsplit(".", 1)[1].lower()

        try:
            # 1. Extract text
            extracted = extract_text(filepath, extension)

            # 2. Summarise with Groq
            summary_text = summarize(
                text    = extracted,
                api_key = current_app.config["GROQ_API_KEY"],
                model   = current_app.config["GROQ_MODEL"],
            )

            # 3. Persist to DB
            record = Summary(
                user_id        = current_user.id,
                filename       = safe_name,
                file_type      = extension,
                extracted_text = extracted[:20_000], # Store first 5000 chars
                summary        = summary_text,
                word_count     = len(extracted.split()),
            )
            db.session.add(record)
            db.session.commit()

            logger.info(
                "Summary created for user %s – file: %s",
                current_user.username, safe_name,
            )

            flash("Document summarized successfully!", "success")
            return redirect(url_for("result", summary_id=record.id))

        except Exception as exc:
            logger.error("Processing error for %s: %s", safe_name, exc)
            flash(f"Error processing document: {exc}", "danger")
            return redirect(url_for("dashboard"))

        finally:
            # Always clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)

    # Result page
    @app.route("/result/<int:summary_id>")
    @login_required
    def result(summary_id: int):
        summary = Summary.query.get_or_404(summary_id)
        # Ensure the summary belongs to the current user (or they're admin)
        if summary.user_id != current_user.id and not current_user.is_admin:
            flash("Access denied.", "danger")
            return redirect(url_for("dashboard"))
        return render_template("result.html", summary=summary)

    # Delete own summary
    @app.route("/summary/<int:summary_id>/delete", methods=["POST"])
    @login_required
    def delete_summary(summary_id: int):
        summary = Summary.query.get_or_404(summary_id)
        if summary.user_id != current_user.id and not current_user.is_admin:
            flash("Access denied.", "danger")
            return redirect(url_for("dashboard"))
        db.session.delete(summary)
        db.session.commit()
        flash("Summary deleted.", "success")
        return redirect(url_for("dashboard"))


# ── Error handlers ────────────────────────────────────────────────────────────

def _register_error_handlers(app: Flask) -> None:

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403,
                               message="Access Denied – Admins only."), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404,
                               message="Page not found."), 404

    @app.errorhandler(413)
    def too_large(e):
        flash("File is too large. Maximum upload size is 16 MB.", "danger")
        return redirect(url_for("dashboard"))

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500,
                               message="Internal server error."), 500


# ── Run ───────────────────────────────────────────────────────────────────────

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
