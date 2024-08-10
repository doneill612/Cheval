from stockfish import Stockfish

from .entities.game import *

_DEFAULT_STOCKFISH_PARAMS = {
    "Debug Log File": "",
    "Contempt": 0,
    "Min Split Depth": 0,
    "Threads": 1,
    "Ponder": "false",
    "Hash": 16,
    "MultiPV": 1,
    "Skill Level": 20,
    "Move Overhead": 10,
    "Minimum Thinking Time": 20,
    "Slow Mover": 100,
    "UCI_Chess960": "false",
    "UCI_LimitStrength": "false",
    "UCI_Elo": 1350,
}


class Analyzer:
    def __init__(
        self,
        *,
        engine_path: str = "stockfish",
        depth: int = 10,
        parameters: dict = None,
    ):
        self._engine = Stockfish(path=engine_path, depth=depth, parameters=parameters)

    @staticmethod
    def _cp_to_prob(cp: float, is_white: bool = True, is_mate: bool = False):
        _cp = cp if not is_mate else 10000
        return 1 / (1 + 10 ** (-_cp * (1 if is_white else -1) / 400))

    def _analyze_ply(self, ply: Ply) -> PlyEval:
        # find the best move in the position, determine if ply is best
        best_move = self._engine.get_best_move()
        is_best = best_move == ply.uci

        # before pushing the move to the engine, calculate the eval + prob to win (color dependent)
        current_evaluation = self._engine.get_evaluation()
        is_currently_mate = current_evaluation["type"] == "mate"
        current_cp = current_evaluation["value"]
        p_win_before = self._cp_to_prob(
            current_cp, ply.player == "White", is_currently_mate
        )

        # push move to the engine, calculate the eval + prob to win (color dependent)
        self._engine.make_moves_from_current_position([ply.uci])
        new_evaluation = self._engine.get_evaluation()
        is_now_mate = new_evaluation["type"] == "mate"
        new_cp = new_evaluation["value"]
        p_win_after = self._cp_to_prob(new_cp, ply.player == "White", is_now_mate)

        # calculate the change in probability of winning (color dependent), classify move
        delta = abs(p_win_after - p_win_before)
        if (ply.player == "White" and p_win_after < p_win_before) or (
            ply.player == "Black" and p_win_after > p_win_before
        ):
            if 0.1 <= delta < 0.2:
                evaluation.classification = "Inaccuracy"
            elif 0.2 <= delta < 0.3:
                evaluation.classification = "Mistake"
            elif delta >= 0.3:
                evaluation.classification = "Blunder"
        elif is_best:
            evaluation.classification = "Best"
        else:
            evaluation.classification = "Good"

        previous_evaluation = self._engine.get_evaluation()
        previously_mate = previous_evaluation["type"] == "mate"
        prev_eval = previous_evaluation["value"]
        if previously_mate:
            p_win_before = 1.0 if ply.player == "White" and value > 0 else 0.0
        else:
            p_win_before = self._cp_to_prob(prev_eval, ply.player != "White")
        self._engine.make_moves_from_current_position([ply.uci])
        current_evaluation = self._engine.get_evaluation()
        is_mate = current_evaluation["type"] == "mate"
        value = current_evaluation["value"]
        if is_mate:
            p_win_after = 1.0 if ply.player == "White" and value > 0 else 0.0
        else:
            p_win_after = self._cp_to_prob(value, ply.player == "White")
        evaluation = PlyEval(
            engine_val=float(value),
            best_uci=best_move,
            is_mate=is_mate,
            previous_ply_val=prev_eval,
            p_win=p_win_after,
        )
        evaluation.previous_ply_val = value if not prev_eval else prev_eval

        delta = abs(p_win_after - p_win_before)

        if (ply.player == "White" and p_win_after < p_win_before) or (
            ply.player == "Black" and p_win_after > p_win_before
        ):
            if 0.1 <= delta < 0.2:
                evaluation.classification = "Inaccuracy"
            elif 0.2 <= delta < 0.3:
                evaluation.classification = "Mistake"
            elif delta >= 0.3:
                evaluation.classification = "Blunder"
        elif is_best:
            evaluation.classification = "Best"
        else:
            evaluation.classification = "Good"

        return evaluation

    def evaluate(self, game: Game):
        for ply in game.plies:
            evaluation = self._analyze_ply(ply)
            evaluation.previous_ply_val
            ply.evaluation = evaluation
