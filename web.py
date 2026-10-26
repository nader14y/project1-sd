"""Persian Quiz Battle web entry point. Run: python web.py."""

import logging
import os
import secrets
import time
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request, session
from werkzeug.exceptions import HTTPException

from app_log import AppLog
from storage import LEADERBOARD_PATH, QUESTIONS_PATH
from web_game import GameError, GameStore, RULES


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("QUIZ_SECRET_KEY") or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=os.environ.get("QUIZ_HTTPS") == "1",
        MAX_CONTENT_LENGTH=4096,
        QUESTIONS_PATH=QUESTIONS_PATH,
        LEADERBOARD_PATH=LEADERBOARD_PATH,
        LOG_PATH=Path(__file__).parent / "quiz_web.log",
        MATCH_TTL=7200,
        MAX_MATCHES=512,
        CLOCK=time.monotonic,
    )
    if config:
        app.config.update(config)
    AppLog.setup_web(app.config["LOG_PATH"])
    app.json.ensure_ascii = False
    store = GameStore(app.config["QUESTIONS_PATH"], app.config["LEADERBOARD_PATH"],
                      clock=app.config["CLOCK"], ttl=app.config["MATCH_TTL"],
                      max_matches=app.config["MAX_MATCHES"])
    app.extensions["quiz_store"] = store
    logger = logging.getLogger("quiz.web")

    @app.before_request
    def prepare_request():
        g.request_id = secrets.token_hex(6)
        g.started_at = time.monotonic()
        if request.path.startswith("/api/") and request.method == "POST":
            expected = session.get("csrf_token")
            received = request.headers.get("X-CSRF-Token", "")
            if not expected or not secrets.compare_digest(expected.encode(), received.encode()):
                raise GameError("نشست معتبر نیست؛ صفحه را تازه کنید.", 403, "csrf")
            if not request.is_json:
                raise GameError("بدنهٔ درخواست باید JSON باشد.", 415, "invalid_json")

    @app.after_request
    def complete_request(response):
        response.headers["X-Request-ID"] = g.request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; font-src 'self'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        if request.path.startswith("/api/") or request.path == "/":
            response.headers["Cache-Control"] = "no-store"
        logger.info("request=%s method=%s path=%s status=%s duration_ms=%.1f",
                    g.request_id, request.method, request.path, response.status_code,
                    (time.monotonic() - g.started_at) * 1000)
        return response

    @app.errorhandler(GameError)
    def game_error(error):
        logger.warning("request=%s rejected code=%s", g.request_id, error.code)
        return jsonify(error={"code": error.code, "message": str(error),
                              "request_id": g.request_id}), error.status

    @app.errorhandler(HTTPException)
    def http_error(error):
        messages = {400: "درخواست نامعتبر است.", 404: "صفحه یا مسیر پیدا نشد.",
                    405: "روش درخواست مجاز نیست.", 413: "حجم درخواست بیش از حد مجاز است."}
        return jsonify(error={"code": "http_error", "message": messages.get(error.code, "درخواست قابل پردازش نیست."),
                              "request_id": g.request_id}), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        logger.exception("Unexpected error request=%s", g.request_id)
        return jsonify(error={"code": "internal_error", "message": "خطایی رخ داد؛ دوباره تلاش کنید.",
                              "request_id": g.request_id}), 500

    def payload():
        data = request.get_json()
        if not isinstance(data, dict):
            raise GameError("درخواست باید یک شیء JSON باشد.")
        return data

    def current_id():
        return session.get("match_id")

    def envelope(match):
        return jsonify(match=match, leaderboard=store.leaderboard(), rules=RULES)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/state")
    def state():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        match = None
        expired = False
        if current_id():
            try:
                match = store.state(current_id())
            except GameError as error:
                if error.code != "match_expired":
                    raise
                session.pop("match_id", None)
                expired = True
        return jsonify(match=match, rules=RULES, leaderboard=store.leaderboard(),
                       csrf_token=session["csrf_token"], expired=expired)

    @app.post("/api/matches")
    def create_match():
        match_id, match = store.create(payload().get("players"), current_id())
        session["match_id"] = match_id
        return envelope(match), 201

    @app.post("/api/match/start")
    def start():
        return envelope(store.start(current_id(), payload().get("turn")))

    @app.post("/api/match/answer")
    def answer():
        data = payload()
        if "choice" not in data:
            raise GameError("گزینهٔ پاسخ ارسال نشده است.")
        return envelope(store.answer(current_id(), data.get("turn"), data["choice"]))

    @app.post("/api/match/next")
    def next_round():
        return envelope(store.next_round(current_id(), payload().get("turn")))

    return app


if __name__ == "__main__":
    from waitress import serve

    app = create_app()
    host = os.environ.get("QUIZ_HOST", "127.0.0.1")
    port = int(os.environ.get("QUIZ_PORT", "8000"))
    print(f"Quiz Battle: http://{host}:{port}", flush=True)
    serve(app, host=host, port=port, threads=8)
