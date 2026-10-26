"""Run the existing Python game in Pyodide, without Flask or a server.

The JavaScript bridge checkpoints this JSON state to localStorage. Nothing in
the checkpoint is evaluated as code. Time and scores are local to the browser.
"""

import json
import logging
import math
import re
import time
from pathlib import Path

from engine import POINTS, ROUNDS, SPEED_BONUS, Question, RoundResult
from web_game import GameError, GameStore, RULES, WebMatch, player_names

logger = logging.getLogger("quiz.pages")


def require(condition):
    if not condition:
        raise ValueError("Invalid browser checkpoint")


def number(value):
    return type(value) in (int, float) and 0 <= value <= 1_000_000_000_000 and math.isfinite(value)


def valid_board(data):
    return isinstance(data, dict) and all(
        isinstance(name, str) and isinstance(stat, dict)
        and all(type(stat.get(key)) is int and stat[key] >= 0 for key in ("wins", "points"))
        for name, stat in data.items()
    )


class BrowserRuntime:
    def __init__(self, question_path, directory, clock=time.time):
        self.question_path = Path(question_path)
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.clock = clock
        self.store = None
        self.match_id = None
        self.warning = None

    def restore(self, saved):
        self.warning = None
        self.match_id = None
        checkpoint = {}
        if saved:
            try:
                require(isinstance(saved, str) and len(saved) <= 1_000_000)
                checkpoint = json.loads(saved)
                require(isinstance(checkpoint, dict) and checkpoint.get("version") == 1)
                require(valid_board(checkpoint.get("board")))
            except (ValueError, TypeError):
                checkpoint = {}
                self.warning = "دادهٔ ذخیره‌شدهٔ مرورگر معتبر نبود؛ یک بازی تازه شروع کنید."
                logger.warning("Invalid browser checkpoint; starting fresh")
        board_path = self.directory / "leaderboard.json"
        board_path.write_text(json.dumps(checkpoint.get("board", {})), encoding="utf-8")
        self.store = GameStore(self.question_path, board_path, clock=self.clock)
        if checkpoint.get("game"):
            try:
                game = self._restore_game(checkpoint["game"])
                self.store.matches[game.id] = game
                self.match_id = game.id
            except (ValueError, TypeError, KeyError, IndexError, GameError):
                self.warning = "بازی ذخیره‌شده معتبر نبود؛ امتیازهای قبلی حفظ شدند. بازی تازه‌ای شروع کنید."
                logger.warning("Invalid saved match; keeping leaderboard")

    def _restore_game(self, data):
        require(isinstance(data, dict))
        names = player_names(data["players"])
        require(names == data["players"])
        require(isinstance(data["id"], str) and re.fullmatch(r"[A-Za-z0-9_-]{20,64}", data["id"]))
        raw_questions = data["questions"]
        require(isinstance(raw_questions, list) and len(raw_questions) == ROUNDS)
        questions = []
        for item in raw_questions:
            require(isinstance(item, dict) and isinstance(item["text"], str) and item["text"].strip())
            require(isinstance(item["options"], list) and all(isinstance(option, str) and option.strip() for option in item["options"]))
            require(item.get("power_up") in (None, "double"))
            questions.append(Question(item["text"], item["options"], item["correct"], item.get("power_up")))
        from engine import Match

        match = Match(*names, questions)
        require(type(data["round"]) is int and 1 <= data["round"] <= ROUNDS)
        require(isinstance(data["scores"], dict) and set(data["scores"]) == set(names))
        require(all(type(score) is int and 0 <= score <= ROUNDS * (POINTS + SPEED_BONUS) * 2 for score in data["scores"].values()))
        require(data["phase"] in ("ready", "answering", "round_result", "finished"))
        require(type(data["player_index"]) is int and data["player_index"] in (0, 1))
        require(type(data["recorded"]) is bool and number(data["touched"]))
        answers = data["answers"]
        require(isinstance(answers, dict) and set(answers) <= set(names))
        for answer in answers.values():
            require(isinstance(answer, list) and len(answer) == 2)
            require(answer[0] is None or (isinstance(answer[0], str) and answer[0] in ("A", "B", "C", "D")))
            require(number(answer[1]))
        completed = data["completed_turns"]
        possible_turns = {f"{data['id']}:{round_number}:{index}" for round_number in range(1, ROUNDS + 1) for index in (0, 1)}
        require(isinstance(completed, list) and len(completed) <= ROUNDS * 2)
        require(all(isinstance(turn, str) and turn in possible_turns for turn in completed))
        results = data["results"]
        require(isinstance(results, dict) and set(results) <= set(names))
        for result in results.values():
            require(isinstance(result, dict) and result["status"] in ("correct", "wrong", "too_late"))
            require(type(result["points"]) is int and 0 <= result["points"] <= (POINTS + SPEED_BONUS) * 2)
        if data["phase"] in ("round_result", "finished"):
            require(set(answers) == set(names) and set(results) == set(names))
            require(data["player_index"] == 1 and data["started"] is None)
            require((data["phase"] == "finished") == (data["round"] == ROUNDS))
        else:
            require(set(answers) == (set() if data["player_index"] == 0 else {names[0]}))
            require(not results and not data["recorded"])
            require(number(data["started"]) if data["phase"] == "answering" else data["started"] is None)
        match.round = data["round"]
        match.scores = data["scores"]
        match.answers = {name: tuple(answer) for name, answer in answers.items()}
        return WebMatch(
            match, min(data["touched"], self.clock()), id=data["id"], phase=data["phase"],
            player_index=data["player_index"], started=data["started"],
            results={name: RoundResult(result["status"], result["points"]) for name, result in results.items()},
            completed_turns=set(completed), recorded=data["recorded"],
        )

    def checkpoint(self):
        game = self.store.matches.get(self.match_id)
        data = None
        if game:
            match = game.match
            data = {
                "id": game.id, "players": match.players, "scores": match.scores,
                "round": match.round, "answers": match.answers,
                "questions": [{"text": question.text, "options": question.options,
                               "correct": question.correct, "power_up": question.power_up}
                              for question in match.questions],
                "phase": game.phase, "player_index": game.player_index,
                "started": game.started, "touched": game.touched,
                "completed_turns": sorted(game.completed_turns), "recorded": game.recorded,
                "results": {name: {"status": result.status, "points": result.points}
                            for name, result in game.results.items()},
            }
        return json.dumps({"version": 1, "board": self.store.board._data, "game": data}, ensure_ascii=False)

    def request(self, path, body=None):
        expired = False
        if path == "/api/state":
            match = None
            if self.match_id:
                try:
                    match = self.store.state(self.match_id)
                except GameError as error:
                    if error.code != "match_expired":
                        raise
                    self.match_id = None
                    expired = True
        else:
            if not isinstance(body, dict):
                raise GameError("درخواست باید یک شیء JSON باشد.")
            if path == "/api/matches":
                self.match_id, match = self.store.create(body.get("players"), self.match_id)
            elif path == "/api/match/start":
                match = self.store.start(self.match_id, body.get("turn"))
            elif path == "/api/match/answer":
                if "choice" not in body:
                    raise GameError("گزینهٔ پاسخ ارسال نشده است.")
                match = self.store.answer(self.match_id, body.get("turn"), body["choice"])
            elif path == "/api/match/next":
                match = self.store.next_round(self.match_id, body.get("turn"))
            else:
                raise GameError("مسیر پیدا نشد.", 404, "not_found")
        result = {"match": match, "rules": RULES, "leaderboard": self.store.leaderboard()}
        if path == "/api/state":
            result.update(csrf_token="browser-local", expired=expired)
        if self.warning:
            result["storage_warning"] = self.warning
        return result

    def dispatch_json(self, raw):
        request = json.loads(raw)
        self.restore(request.get("saved"))
        try:
            data = self.request(request["path"], request.get("body"))
            status = 201 if request["path"] == "/api/matches" else 200
        except GameError as error:
            status = error.status
            data = {"error": {"code": error.code, "message": str(error)}}
        except Exception:
            logger.exception("Unexpected browser game error")
            status = 500
            data = {"error": {"code": "internal_error", "message": "خطایی رخ داد؛ دوباره تلاش کنید."}}
        return json.dumps({"status": status, "data": data, "saved": self.checkpoint()}, ensure_ascii=False)
