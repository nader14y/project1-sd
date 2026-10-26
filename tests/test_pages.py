import json
import pytest

from engine import ROUNDS, TIME_LIMIT
from pages_runtime import BrowserRuntime
from scripts.build_pages import ROOT, build


@pytest.fixture
def browser(tmp_path):
    question_path = tmp_path / "questions.json"
    question_path.write_text(json.dumps([
        {"text": f"سؤال {index}", "options": ["درست", "دو", "سه", "چهار"], "correct": "A"}
        for index in range(ROUNDS)
    ]), encoding="utf-8")
    now = [100.0]
    runtime = BrowserRuntime(question_path, tmp_path / "data", clock=lambda: now[0])
    saved = [None]

    def request(path="/api/state", body=None):
        response = json.loads(runtime.dispatch_json(json.dumps({"path": path, "body": body, "saved": saved[0]})))
        saved[0] = response["saved"]
        return response

    return runtime, request, now, saved


def create(browser):
    response = browser[1]("/api/matches", {"players": ["سارا", "علی"]})
    assert response["status"] == 201
    return response["data"]["match"]


def action(browser, match, name, **extra):
    response = browser[1](f"/api/match/{name}", {"turn": match["turn"], **extra})
    assert response["status"] == 200, response
    return response["data"]["match"]


def finish(browser, double=False):
    if double:
        path = browser[0].question_path
        data = json.loads(path.read_text())
        for question in data:
            question["power_up"] = "double"
        path.write_text(json.dumps(data))
    match = create(browser)
    for index in range(ROUNDS):
        for choice in ("A", "B"):
            match = action(browser, match, "start")
            browser[2][0] += 2
            match = action(browser, match, "answer", choice=choice)
        if index < ROUNDS - 1:
            match = action(browser, match, "next")
    return match


def test_pages_build_uses_project_relative_paths_and_identical_engine(tmp_path):
    destination = build(tmp_path / "site")
    html = (destination / "index.html").read_text()
    assert "url_for" not in html
    assert 'href="/"' not in html
    assert 'href="./"' in html
    assert html.index("pages-bridge.js") < html.index("app.js")
    assert "امتیازها فقط در همین مرورگر ذخیره می‌شوند" in html
    assert (destination / "engine.py").read_bytes() == (ROOT / "engine.py").read_bytes()
    for name in ("storage.py", "web_game.py", "pages_runtime.py", "questions.json", ".nojekyll"):
        assert (destination / name).exists()
    assert not (destination / "web.py").exists()
    assert not (destination / "quiz_web.log").exists()
    assert not (destination / ".git").exists()


def test_build_refuses_to_overwrite_checkout():
    with pytest.raises(ValueError):
        build(ROOT)
    with pytest.raises(ValueError):
        build(ROOT / "static")


def test_initial_browser_state(browser):
    response = browser[1]()
    assert response["status"] == 200
    assert response["data"]["match"] is None
    assert response["data"]["rules"]["rounds"] == ROUNDS


def test_ready_and_answering_survive_checkpoint_reload(browser):
    match = create(browser)
    restored = browser[1]()["data"]["match"]
    assert restored == match
    match = action(browser, match, "start")
    browser[2][0] += 12
    restored = browser[1]()["data"]["match"]
    assert restored["turn"] == match["turn"]
    assert restored["question"] == match["question"]
    assert restored["remaining_seconds"] == TIME_LIMIT - 12
    assert "correct" not in restored["question"]


def test_first_answer_stays_hidden_after_reload(browser):
    match = action(browser, create(browser), "start")
    match = action(browser, match, "answer", choice="A")
    restored = browser[1]()["data"]["match"]
    assert match == restored
    assert restored["player_index"] == 1
    assert "correct" not in restored and "results" not in restored


@pytest.mark.parametrize("double", [False, True])
def test_complete_browser_game_records_exactly_once_across_reloads(browser, double):
    match = finish(browser, double)
    expected = ROUNDS * 13 * (2 if double else 1)
    assert match["phase"] == "finished" and match["recorded"]
    assert match["scores"]["سارا"] == expected
    for _ in range(3):
        response = browser[1]()["data"]
        assert response["match"] == match
        assert response["leaderboard"][0] == {"name": "سارا", "wins": 1, "points": expected}
    match = create(browser)
    assert match["scores"]["سارا"] == 0
    assert browser[1]()["data"]["leaderboard"][0]["points"] == expected


def test_expired_answer_restores_as_timeout(browser):
    match = action(browser, create(browser), "start")
    browser[2][0] += TIME_LIMIT + 10
    match = browser[1]()["data"]["match"]
    assert match["phase"] == "ready" and match["player_index"] == 1
    match = action(browser, match, "start")
    match = action(browser, match, "answer", choice="B")
    assert match["results"]["سارا"]["status"] == "too_late"
    assert match["scores"]["سارا"] == 0


def test_expired_game_keeps_leaderboard(browser):
    finish(browser)
    browser[2][0] += 7200
    response = browser[1]()["data"]
    assert response["match"] is None and response["expired"]
    assert response["leaderboard"][0]["wins"] == 1


def test_duplicate_answer_after_reload_never_changes_choice(browser):
    previous = action(browser, create(browser), "start")
    match = action(browser, previous, "answer", choice="A")
    assert action(browser, previous, "answer", choice="B") == match


def test_duplicate_next_after_reload_never_skips_round(browser):
    match = create(browser)
    for choice in ("A", "B"):
        match = action(browser, match, "start")
        match = action(browser, match, "answer", choice=choice)
    previous = match
    match = action(browser, match, "next")
    assert action(browser, previous, "next") == match
    assert match["round"] == 2


@pytest.mark.parametrize("saved", ["{", "null", "[]", "{}", '{"version":999}', '{"version":1,"board":[]}'])
def test_corrupt_browser_data_recovers_with_message(browser, saved):
    browser[3][0] = saved
    response = browser[1]()
    assert response["status"] == 200
    assert response["data"]["match"] is None
    assert response["data"]["storage_warning"]


@pytest.mark.parametrize("field,value", [("phase", "invalid"), ("round", 99), ("scores", {}),
                                          ("answers", {"stranger": ["A", 0]}),
                                          ("completed_turns", [[]]), ("started", "invalid"),
                                          ("touched", 10 ** 1000)])
def test_corrupt_match_keeps_previous_leaderboard(browser, field, value):
    finish(browser)
    create(browser)
    if field == "started":
        match = browser[1]()["data"]["match"]
        action(browser, match, "start")
    checkpoint = json.loads(browser[3][0])
    checkpoint["game"][field] = value
    browser[3][0] = json.dumps(checkpoint)
    response = browser[1]()["data"]
    assert response["match"] is None
    assert response["storage_warning"]
    assert response["leaderboard"][0]["wins"] == 1


def test_browser_errors_have_status_and_safe_messages(browser):
    assert browser[1]("/api/matches", {"players": ["a", "a"]})["status"] == 400
    match = create(browser)
    assert browser[1]("/api/match/start", {"turn": []})["status"] == 409
    assert browser[1]("/api/match/answer", {"turn": match["turn"]})["status"] == 400
    assert browser[1]("/missing", {})["status"] == 404
