"""Thread-safe web lifecycle around the unchanged terminal game engine.

Matches live in this process; only the leaderboard is persisted to JSON.
The browser never supplies scores, elapsed times, or the correct answer.
"""

import logging
import secrets
import threading
import time
import unicodedata
from dataclasses import dataclass, field

from engine import Match, POINTS, ROUNDS, SPEED_BONUS, TIME_LIMIT
from storage import QuestionBank, ScoreBoard

logger = logging.getLogger("quiz.web.game")
RULES = {"rounds": ROUNDS, "time_limit": TIME_LIMIT,
         "points": POINTS, "speed_bonus": SPEED_BONUS}


class GameError(Exception):
    def __init__(self, message, status=400, code="invalid_request"):
        super().__init__(message)
        self.status = status
        self.code = code


def player_names(players):
    if not isinstance(players, list) or len(players) != 2:
        raise GameError("نام هر دو بازیکن را وارد کنید.")
    names = []
    for name in players:
        if not isinstance(name, str):
            raise GameError("نام بازیکن باید متن باشد.")
        name = unicodedata.normalize("NFKC", name).strip()
        if not 1 <= len(name) <= 30 or any(
            unicodedata.category(char).startswith("C") and char != "\u200c"
            for char in name
        ):
            raise GameError("نام باید بین ۱ تا ۳۰ نویسه و بدون نویسهٔ کنترلی باشد.")
        names.append(name)
    if names[0].casefold() == names[1].casefold():
        raise GameError("برای بازیکن‌ها دو نام متفاوت انتخاب کنید.")
    return names


@dataclass
class WebMatch:
    match: Match
    touched: float
    id: str = field(default_factory=lambda: secrets.token_urlsafe(24))
    phase: str = "ready"
    player_index: int = 0
    started: float | None = None
    results: dict = field(default_factory=dict)
    completed_turns: set = field(default_factory=set)
    recorded: bool = False

    @property
    def turn(self):
        return f"{self.id}:{self.match.round}:{self.player_index}"


class GameStore:
    def __init__(self, question_path, leaderboard_path, clock=time.monotonic,
                 ttl=7200, max_matches=512):
        self.question_path = question_path
        self.board = ScoreBoard(leaderboard_path)
        self.clock = clock
        self.ttl = ttl
        self.max_matches = max_matches
        self.matches = {}
        self.lock = threading.RLock()

    def _prune(self):
        now = self.clock()
        for key in list(self.matches):
            if now - self.matches[key].touched >= self.ttl:
                del self.matches[key]

    def create(self, players, previous_id=None):
        names = player_names(players)
        with self.lock:
            self._prune()
            if len(self.matches) >= self.max_matches and previous_id not in self.matches:
                raise GameError("سرور شلوغ است؛ کمی بعد دوباره تلاش کنید.", 503, "capacity")
            try:
                questions = QuestionBank(self.question_path).pick(ROUNDS)
            except (OSError, ValueError, KeyError, TypeError) as error:
                logger.exception("Question bank unavailable")
                raise GameError("بانک سؤال در دسترس نیست؛ فایل questions.json را بررسی کنید.",
                                503, "question_bank") from error
            game = WebMatch(Match(*names, questions), self.clock())
            game.match.start_round()
            self.matches[game.id] = game
            self.matches.pop(previous_id, None)
            logger.info("Match created match=%s", game.id)
            return game.id, self._snapshot(game)

    def _get(self, match_id):
        self._prune()
        game = self.matches.get(match_id)
        if game is None:
            raise GameError("بازی فعال پیدا نشد یا منقضی شده است؛ بازی تازه‌ای شروع کنید.",
                            404, "match_expired")
        game.touched = self.clock()
        if game.phase == "answering" and self.clock() - game.started >= TIME_LIMIT:
            self._submit(game, None, max(TIME_LIMIT + 0.001, self.clock() - game.started))
        return game

    def state(self, match_id):
        with self.lock:
            return self._snapshot(self._get(match_id))

    def start(self, match_id, turn):
        with self.lock:
            game = self._get(match_id)
            if isinstance(turn, str) and turn in game.completed_turns:
                return self._snapshot(game)
            self._check_turn(game, turn)
            if game.phase == "ready":
                game.phase = "answering"
                game.started = self.clock()
                logger.info("Turn started match=%s round=%s player=%s",
                            game.id, game.match.round, game.player_index)
            elif game.phase != "answering":
                raise GameError("این نوبت تمام شده است.", 409, "invalid_phase")
            return self._snapshot(game)

    def answer(self, match_id, turn, choice):
        if choice is not None and (not isinstance(choice, str) or choice not in "ABCD" or len(choice) != 1):
            raise GameError("یکی از گزینه‌های A تا D را انتخاب کنید.")
        with self.lock:
            game = self._get(match_id)
            if isinstance(turn, str) and turn in game.completed_turns:
                return self._snapshot(game)
            self._check_turn(game, turn)
            if game.phase != "answering":
                raise GameError("ابتدا نوبت خود را شروع کنید.", 409, "invalid_phase")
            elapsed = self.clock() - game.started
            if choice is None:
                raise GameError("زمان پاسخ هنوز تمام نشده است.", 409, "time_remaining")
            self._submit(game, choice, elapsed)
            return self._snapshot(game)

    def _check_turn(self, game, turn):
        if not isinstance(turn, str) or turn != game.turn:
            raise GameError("وضعیت بازی تغییر کرده است؛ صفحه را تازه کنید.", 409, "stale_turn")

    def _submit(self, game, choice, elapsed):
        player = game.match.players[game.player_index]
        game.match.submit(player, choice, elapsed)
        game.completed_turns.add(game.turn)
        logger.info("Answer received match=%s round=%s player=%s elapsed=%.3f",
                    game.id, game.match.round, game.player_index, elapsed)
        game.started = None
        if game.player_index == 0:
            game.player_index = 1
            game.phase = "ready"
            return
        game.results = game.match.resolve_round()
        game.phase = "finished" if game.match.is_over() else "round_result"
        logger.info("Round resolved match=%s round=%s", game.id, game.match.round)

    def next_round(self, match_id, turn):
        with self.lock:
            game = self._get(match_id)
            if isinstance(turn, str) and turn in game.completed_turns and turn != game.turn:
                return self._snapshot(game)
            self._check_turn(game, turn)
            if game.phase != "round_result":
                raise GameError("ابتدا هر دو بازیکن باید پاسخ دهند.", 409, "invalid_phase")
            game.match.start_round()
            game.phase = "ready"
            game.player_index = 0
            game.results = {}
            return self._snapshot(game)

    def _record(self, game):
        if game.phase != "finished" or game.recorded:
            return
        match = game.match
        try:
            self.board.record(match.winner(), match.players[0], match.score_of(match.players[0]),
                              match.players[1], match.score_of(match.players[1]))
        except OSError:
            logger.exception("Leaderboard save failed match=%s", game.id)
        else:
            game.recorded = True
            logger.info("Match finished and recorded match=%s", game.id)

    def _snapshot(self, game):
        self._record(game)
        match = game.match
        data = {
            "phase": game.phase, "round": match.round, "turn": game.turn,
            "players": match.players, "scores": match.scores.copy(),
            "active_player": match.players[game.player_index],
            "player_index": game.player_index,
        }
        if game.phase == "answering":
            question = match.questions[match.round - 1]
            data["question"] = {"text": question.text, "options": question.options,
                                "power_up": question.power_up}
            data["remaining_seconds"] = max(0, TIME_LIMIT - (self.clock() - game.started))
        if game.phase in ("round_result", "finished"):
            question = match.questions[match.round - 1]
            data["correct"] = question.correct
            data["correct_text"] = question.correct_text()
            data["results"] = {
                name: {"status": result.status, "points": result.points,
                       "choice": match.answers[name][0],
                       "elapsed": round(match.answers[name][1], 2)}
                for name, result in game.results.items()
            }
        if game.phase == "finished":
            data["winner"] = match.winner()
            data["recorded"] = game.recorded
            if not game.recorded:
                data["warning"] = "بازی تمام شد، اما ذخیرهٔ جدول امتیازها ناموفق بود. برای تلاش دوباره صفحه را تازه کنید."
        return data

    def leaderboard(self):
        with self.lock:
            return [{"name": name, **stats} for name, stats in self.board.top(5)]
