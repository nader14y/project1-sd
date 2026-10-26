import json
import logging
from concurrent.futures import ThreadPoolExecutor

import pytest

from engine import ROUNDS, TIME_LIMIT
from web import create_app


@pytest.fixture
def setup(tmp_path):
    questions = tmp_path / "questions.json"
    questions.write_text(json.dumps([
        {"text": f"سؤال {i}", "options": ["درست", "دو", "سه", "چهار"], "correct": "A"}
        for i in range(ROUNDS + 2)
    ]), encoding="utf-8")
    now = [100.0]
    app = create_app({
        "TESTING": True, "SECRET_KEY": "test-only", "LOG_PATH": None,
        "QUESTIONS_PATH": questions, "LEADERBOARD_PATH": tmp_path / "leaderboard.json",
        "CLOCK": lambda: now[0],
    })
    client = app.test_client()
    token = client.get("/api/state").json["csrf_token"]
    return app, client, {"X-CSRF-Token": token}, now


def create(setup, players=None):
    _, client, headers, _ = setup
    response = client.post("/api/matches", json={"players": players or ["سارا", "علی"]}, headers=headers)
    assert response.status_code == 201
    return response.json["match"]


def post(setup, action, match, **extra):
    _, client, headers, _ = setup
    return client.post(f"/api/match/{action}", json={"turn": match["turn"], **extra}, headers=headers)


def play_round(setup, match, first="A", second="B"):
    for choice in (first, second):
        response = post(setup, "start", match)
        assert response.status_code == 200
        match = response.json["match"]
        setup[3][0] += 2
        response = post(setup, "answer", match, choice=choice)
        assert response.status_code == 200
        match = response.json["match"]
    return match


def finish(setup):
    match = create(setup)
    for index in range(ROUNDS):
        match = play_round(setup, match)
        if index < ROUNDS - 1:
            match = post(setup, "next", match).json["match"]
    return match


def test_home_is_persian_rtl_and_assets_are_local(setup):
    response = setup[1].get("/")
    assert response.status_code == 200
    assert 'lang="fa" dir="rtl"' in response.text
    for path in ("/static/app.js", "/static/style.css", "/static/favicon.svg"):
        assert setup[1].get(path).status_code == 200
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]


def test_initial_state_has_rules_and_no_match(setup):
    response = setup[1].get("/api/state")
    assert response.json["match"] is None
    assert response.json["rules"]["rounds"] == ROUNDS
    assert response.json["leaderboard"] == []
    assert response.headers["Cache-Control"] == "no-store"
    cookie = setup[0].test_client().get("/api/state").headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Strict" in cookie


@pytest.mark.parametrize("players", [None, {}, "سارا", ["a"], [1, "b"], ["", "b"],
                                     ["a" * 31, "b"], ["same", " SAME "], ["Ａ", "A"],
                                     ["bad\nname", "b"], ["a\u202eb", "b"]])
def test_invalid_names_are_rejected(setup, players):
    _, client, headers, _ = setup
    response = client.post("/api/matches", json={"players": players}, headers=headers)
    assert response.status_code == 400
    assert response.json["error"]["message"]


def test_names_are_trimmed_and_zwnj_is_allowed(setup):
    assert create(setup, [" سارا ", "علی\u200cرضا"])["players"] == ["سارا", "علی\u200cرضا"]


def test_correct_answer_is_hidden_until_both_players_finish(setup):
    match = create(setup)
    assert "question" not in match
    match = post(setup, "start", match).json["match"]
    assert "correct" not in json.dumps(match)
    assert match["question"]["options"][0] == "درست"
    match = post(setup, "answer", match, choice="A").json["match"]
    assert match["phase"] == "ready"
    assert match["scores"] == {"سارا": 0, "علی": 0}
    assert "correct" not in match and "results" not in match
    match = post(setup, "start", match).json["match"]
    match = post(setup, "answer", match, choice="B").json["match"]
    assert match["correct"] == "A"
    assert match["scores"]["سارا"] == 13


def test_timer_uses_server_clock_and_survives_refresh(setup):
    match = create(setup)
    setup[3][0] += 100
    match = post(setup, "start", match).json["match"]
    assert match["remaining_seconds"] == TIME_LIMIT
    setup[3][0] += 12
    refreshed = setup[1].get("/api/state").json["match"]
    assert refreshed["remaining_seconds"] == TIME_LIMIT - 12
    restarted = post(setup, "start", refreshed).json["match"]
    assert restarted["remaining_seconds"] == TIME_LIMIT - 12


def test_elapsed_from_browser_is_ignored(setup):
    match = post(setup, "start", create(setup)).json["match"]
    setup[3][0] += TIME_LIMIT + 1
    response = post(setup, "answer", match, choice="A", elapsed=0, points=999)
    match = response.json["match"]
    match = post(setup, "start", match).json["match"]
    match = post(setup, "answer", match, choice="B").json["match"]
    assert match["results"]["سارا"]["status"] == "too_late"
    assert match["scores"]["سارا"] == 0


def test_timeout_advances_turn_without_client_answer(setup):
    match = post(setup, "start", create(setup)).json["match"]
    setup[3][0] += TIME_LIMIT
    match = setup[1].get("/api/state").json["match"]
    assert match["phase"] == "ready" and match["player_index"] == 1
    match = post(setup, "start", match).json["match"]
    setup[3][0] += TIME_LIMIT
    match = setup[1].get("/api/state").json["match"]
    assert match["phase"] == "round_result"
    assert all(result["status"] == "too_late" for result in match["results"].values())


def test_null_answer_cannot_skip_an_unexpired_turn(setup):
    match = post(setup, "start", create(setup)).json["match"]
    assert post(setup, "answer", match, choice=None).status_code == 409


@pytest.mark.parametrize("choice", ["", "AA", "E", "a", 1, [], {}, True])
def test_bad_answers_are_rejected(setup, choice):
    match = post(setup, "start", create(setup)).json["match"]
    assert post(setup, "answer", match, choice=choice).status_code == 400


def test_phase_and_turn_are_checked(setup):
    match = create(setup)
    assert post(setup, "answer", match, choice="A").status_code == 409
    assert post(setup, "next", match).status_code == 409
    assert post(setup, "start", {"turn": "fake"}).status_code == 409


def test_duplicate_and_stale_answers_never_award_extra_points(setup):
    match = post(setup, "start", create(setup)).json["match"]
    old = match
    match = post(setup, "answer", old, choice="A").json["match"]
    assert post(setup, "answer", old, choice="B").json["match"] == match
    match = post(setup, "start", match).json["match"]
    match = post(setup, "answer", match, choice="B").json["match"]
    assert post(setup, "answer", old, choice="A").json["match"]["scores"]["سارا"] == 13
    previous = match
    match = post(setup, "next", match).json["match"]
    assert post(setup, "next", previous).json["match"] == match


def test_full_game_records_once_and_reloads_from_json(setup):
    match = finish(setup)
    assert match["phase"] == "finished" and match["recorded"]
    assert match["winner"] == "سارا" and match["scores"]["سارا"] == ROUNDS * 13
    for _ in range(3):
        setup[1].get("/api/state")
    data = json.loads(setup[0].config["LEADERBOARD_PATH"].read_text())
    assert data["سارا"] == {"wins": 1, "points": 65}
    restarted = create_app({**setup[0].config, "LOG_PATH": None})
    state = restarted.test_client().get("/api/state").json
    assert state["match"] is None
    assert state["leaderboard"][0] == {"name": "سارا", "wins": 1, "points": 65}


def test_tie_and_double_scoring(setup):
    path = setup[0].config["QUESTIONS_PATH"]
    data = json.loads(path.read_text())
    for question in data:
        question["power_up"] = "double"
    path.write_text(json.dumps(data))
    match = create(setup)
    for index in range(ROUNDS):
        match = play_round(setup, match, "A", "A")
        if index < ROUNDS - 1:
            match = post(setup, "next", match).json["match"]
    assert match["scores"] == {"سارا": 130, "علی": 100}
    # A separate all-wrong match ends in a draw.
    match = create(setup)
    for index in range(ROUNDS):
        match = play_round(setup, match, "B", "C")
        if index < ROUNDS - 1:
            match = post(setup, "next", match).json["match"]
    assert match["winner"] is None


def test_faster_second_player_gets_speed_bonus(setup):
    match = post(setup, "start", create(setup)).json["match"]
    setup[3][0] += 10
    match = post(setup, "answer", match, choice="A").json["match"]
    match = post(setup, "start", match).json["match"]
    setup[3][0] += 2
    match = post(setup, "answer", match, choice="A").json["match"]
    assert match["scores"] == {"سارا": 10, "علی": 13}


def test_other_browser_cannot_access_match(setup):
    create(setup)
    other = setup[0].test_client()
    token = other.get("/api/state").json["csrf_token"]
    response = other.post("/api/match/start", json={"turn": "fake"}, headers={"X-CSRF-Token": token})
    assert response.status_code == 404
    assert other.get("/api/state").json["match"] is None


def test_csrf_is_required(setup):
    for headers in ({}, {"X-CSRF-Token": "wrong"}, {"X-CSRF-Token": "نامعتبر"}):
        assert setup[1].post("/api/matches", json={"players": ["a", "b"]}, headers=headers).status_code == 403


@pytest.mark.parametrize("turn", [[], {}, 1, True, None])
@pytest.mark.parametrize("action", ["start", "answer", "next"])
def test_malformed_turn_is_a_client_error(setup, turn, action):
    create(setup)
    assert post(setup, action, {"turn": turn}, choice="A").status_code == 409


def test_non_json_malformed_json_and_large_payloads(setup):
    client, headers = setup[1], setup[2]
    assert client.post("/api/matches", data="a", headers=headers).status_code == 415
    assert client.post("/api/matches", data="{", content_type="application/json", headers=headers).status_code == 400
    assert client.post("/api/matches", json=[], headers=headers).status_code == 400
    assert client.post("/api/matches", json={"players": ["a" * 5000, "b"]}, headers=headers).status_code == 413
    assert client.get("/api/matches").status_code == 405
    assert client.get("/missing").status_code == 404


@pytest.mark.parametrize("content", ["{", "{}", "[]", '[{}]', '[1]',
                                     '[{"text":"a","options":null,"correct":"A"}]'])
def test_broken_question_bank_returns_safe_error(setup, content):
    setup[0].config["QUESTIONS_PATH"].write_text(content)
    response = setup[1].post("/api/matches", json={"players": ["a", "b"]}, headers=setup[2])
    assert response.status_code == 503
    assert response.json["error"]["code"] == "question_bank"
    assert "Traceback" not in response.text


def test_missing_question_bank_and_failed_create_preserves_active_match(setup):
    match = create(setup)
    setup[0].config["QUESTIONS_PATH"].unlink()
    response = setup[1].post("/api/matches", json={"players": ["a", "b"]}, headers=setup[2])
    assert response.status_code == 503
    assert setup[1].get("/api/state").json["match"]["turn"] == match["turn"]


def test_expired_matches_are_cleaned_and_can_restart(setup):
    create(setup)
    setup[3][0] += setup[0].config["MATCH_TTL"]
    state = setup[1].get("/api/state").json
    assert state["match"] is None and state["expired"]
    assert not setup[0].extensions["quiz_store"].matches
    assert create(setup)["phase"] == "ready"


def test_new_match_replaces_previous_one_and_old_turn_is_rejected(setup):
    previous = create(setup)
    match = create(setup)
    assert match["turn"] != previous["turn"]
    assert len(setup[0].extensions["quiz_store"].matches) == 1
    assert post(setup, "start", previous).status_code == 409


def test_capacity_is_bounded(setup):
    store = setup[0].extensions["quiz_store"]
    store.max_matches = 1
    create(setup)
    other = setup[0].test_client()
    token = other.get("/api/state").json["csrf_token"]
    response = other.post("/api/matches", json={"players": ["a", "b"]}, headers={"X-CSRF-Token": token})
    assert response.status_code == 503
    create(setup)  # Replacing this browser's existing match still works.


def test_save_failure_keeps_final_result_and_retry_does_not_double_count(setup, monkeypatch):
    board = setup[0].extensions["quiz_store"].board
    real_save = board._save
    monkeypatch.setattr(board, "_save", lambda: (_ for _ in ()).throw(OSError("disk full")))
    match = finish(setup)
    assert match["phase"] == "finished" and not match["recorded"] and match["warning"]
    assert board.is_empty()
    monkeypatch.setattr(board, "_save", real_save)
    assert setup[1].get("/api/state").json["match"]["recorded"]
    setup[1].get("/api/state")
    assert dict(board.top())["سارا"] == {"wins": 1, "points": 65}


def test_concurrent_duplicate_requests_resolve_round_once(setup):
    store = setup[0].extensions["quiz_store"]
    match = post(setup, "start", create(setup)).json["match"]
    match_id = match["turn"].split(":")[0]
    match = store.answer(match_id, match["turn"], "A")
    match = store.start(match_id, match["turn"])
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: store.answer(match_id, match["turn"], "B"), range(16)))
    assert all(result["scores"]["سارا"] == 13 for result in results)


def test_unexpected_error_is_logged_but_not_exposed(setup, monkeypatch, caplog):
    store = setup[0].extensions["quiz_store"]
    def fail(*args):
        raise RuntimeError("PRIVATE INTERNAL DETAILS")
    monkeypatch.setattr(store, "create", fail)
    with caplog.at_level(logging.INFO, logger="quiz.web"):
        response = setup[1].post("/api/matches", json={"players": ["a", "b"]}, headers=setup[2])
    assert response.status_code == 500
    assert "PRIVATE INTERNAL DETAILS" not in response.text
    assert "PRIVATE INTERNAL DETAILS" in caplog.text
    assert response.json["error"]["request_id"] == response.headers["X-Request-ID"]


def test_logs_include_lifecycle_and_requests_without_player_names(setup, caplog):
    with caplog.at_level(logging.INFO, logger="quiz.web"):
        finish(setup)
    assert "Match created" in caplog.text and "Round resolved" in caplog.text
    assert "Match finished and recorded" in caplog.text
    assert "duration_ms=" in caplog.text
    assert "سارا" not in caplog.text and "علی" not in caplog.text
