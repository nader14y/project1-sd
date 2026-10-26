import json
import logging

import pytest

from app_log import AppLog
from storage import QuestionBank, ScoreBoard


@pytest.mark.parametrize("question", [None, [], {}, {"text": "", "options": ["a"] * 4, "correct": "A"},
                                      {"text": "q", "options": "abcd", "correct": "A"},
                                      {"text": "q", "options": [1, 2, 3, 4], "correct": "A"},
                                      {"text": "q", "options": ["a"] * 4, "correct": "A", "power_up": "unknown"}])
def test_invalid_question_schema(tmp_path, question):
    path = tmp_path / "questions.json"
    path.write_text(json.dumps([question]))
    with pytest.raises(ValueError):
        QuestionBank(path)


@pytest.mark.parametrize("content", ["{", "[]", "null", '{"a": {"wins": "1", "points": 3}}',
                                     '{"a": {"wins": -1, "points": 3}}', '{"a": []}'])
def test_invalid_leaderboard_recovers_with_warning(tmp_path, content, caplog):
    path = tmp_path / "leaderboard.json"
    path.write_text(content)
    with caplog.at_level(logging.WARNING):
        board = ScoreBoard(path)
    assert board.is_empty()
    assert "Could not read leaderboard" in caplog.text


def test_failed_atomic_replace_preserves_previous_file_and_memory(tmp_path, monkeypatch):
    path = tmp_path / "leaderboard.json"
    board = ScoreBoard(path)
    board.record("a", "a", 13, "b", 0)
    previous = path.read_bytes()
    def fail(*args):
        raise OSError("read only")
    monkeypatch.setattr("storage.os.replace", fail)
    with pytest.raises(OSError):
        board.record("a", "a", 13, "b", 0)
    assert path.read_bytes() == previous
    assert dict(board.top())["a"]["points"] == 13
    assert not list(tmp_path.glob(".leaderboard-*.tmp"))


def test_web_log_is_rotated_and_setup_is_idempotent(tmp_path):
    path = tmp_path / "web.log"
    logger = logging.getLogger("quiz.web")
    original = list(logger.handlers)
    try:
        AppLog.setup_web(path)
        AppLog.setup_web(path)
        handlers = [handler for handler in logger.handlers if getattr(handler, "baseFilename", None) == str(path)]
        assert len(handlers) == 1
        assert handlers[0].maxBytes == 1_000_000 and handlers[0].backupCount == 3
        logger.info("Persian log: شروع بازی")
        assert "شروع بازی" in path.read_text(encoding="utf-8")
    finally:
        for handler in list(logger.handlers):
            if handler not in original:
                logger.removeHandler(handler)
                handler.close()


def test_log_file_failure_falls_back_to_stderr(tmp_path, capsys):
    logger = logging.getLogger("quiz.web")
    original = list(logger.handlers)
    try:
        AppLog.setup_web(tmp_path / "missing" / "web.log")
        assert "writing logs to stderr" in capsys.readouterr().err
    finally:
        for handler in list(logger.handlers):
            if handler not in original:
                logger.removeHandler(handler)
                handler.close()
