from typing import List

from stockfish import Stockfish

from .entities.eval import Classification
from .entities.game import *


class AnalysisResult:
    def __init__(self, plies: List[Ply]):
        self._plies = plies

    def pretty_print(self):
        best_white = len(
            [
                p
                for p in self._plies
                if p.player == Color.WHITE
                and p.evaluation.classification == Classification.BEST
            ]
        )
        good_white = len(
            [
                p
                for p in self._plies
                if p.player == "white"
                and p.evaluation.classification == Classification.GOOD
            ]
        )
        inaccuracy_white = len(
            [
                p
                for p in self._plies
                if p.player == "white"
                and p.evaluation.classification == Classification.INNACCURACY
            ]
        )
        mistake_white = len(
            [
                p
                for p in self._plies
                if p.player == "white"
                and p.evaluation.classification == Classification.MISTAKE
            ]
        )
        blunder_white = len(
            [
                p
                for p in self._plies
                if p.player == "white"
                and p.evaluation.classification == Classification.BLUNDER
            ]
        )

        best_black = len(
            [
                p
                for p in self._plies
                if p.player == "black"
                and p.evaluation.classification == Classification.BEST
            ]
        )
        good_black = len(
            [
                p
                for p in self._plies
                if p.player == "black"
                and p.evaluation.classification == Classification.GOOD
            ]
        )
        inaccuracy_black = len(
            [
                p
                for p in self._plies
                if p.player == "black"
                and p.evaluation.classification == Classification.INNACCURACY
            ]
        )
        mistake_black = len(
            [
                p
                for p in self._plies
                if p.player == "black"
                and p.evaluation.classification == Classification.MISTAKE
            ]
        )
        blunder_black = len(
            [
                p
                for p in self._plies
                if p.player == "black"
                and p.evaluation.classification == Classification.BLUNDER
            ]
        )

        print(
            f"""Stats for the supplied game:

        Best Moves (White): {best_white}
        Best Moves (Black): {best_black}

        Good Moves (White): {good_white}
        Good Moves (Black): {good_black}

        Blunders (White): {blunder_white}
        Blunders (Black): {blunder_black}

        Mistakes (White): {mistake_white}
        Mistakes (Black): {mistake_black}

        Inaccuracies (White): {inaccuracy_white}
        Inaccuracies (Black): {inaccuracy_black}
        """
        )


class Analyzer:
    def __init__(
        self,
        *,
        engine_path: str = "stockfish",
        depth: int = 10,
        parameters: dict = None,
    ):
        self._engine = Stockfish(path=engine_path, depth=depth, parameters=parameters)

    def evaluate(self, game: Game) -> AnalysisResult:
        prev: float = None
        analyzed_plies = []
        for ply in game.plies:
            top_five = self._engine.get_top_moves()
            is_best = top_five[0]["Move"] == ply.uci
            is_good = (not is_best) and (ply.uci in (m["Move"] for m in top_five))
            self._engine.make_moves_from_current_position([ply.uci])
            current_evaluation = self._engine.get_evaluation()
            is_mate = current_evaluation["type"] == "mate"
            value = current_evaluation["value"]
            evaluation = PlyEval(
                engine_val=float(value), best_uci=top_five[0]["Move"], is_mate=is_mate
            )
            ply.evaluation = evaluation
            if is_best:
                ply.evaluation.classification = Classification.BEST
            elif is_good:
                ply.evaluation.classification = Classification.GOOD
            else:
                if prev is None:
                    prev = value
                else:
                    delta = value - prev
                    abs_delta = abs(delta)
                    if (ply.player == Color.WHITE and delta < 0) or (
                        ply.player == Color.BLACK and delta > 0
                    ):
                        if 20 <= abs_delta < 90:
                            ply.evaluation.classification = Classification.INNACCURACY
                        elif 90 <= abs_delta < 250:
                            ply.evaluation.classification = Classification.MISTAKE
                        elif abs_delta >= 250:
                            ply.evaluation.classification = Classification.BLUNDER
            analyzed_plies.append(ply)
        return AnalysisResult(plies=analyzed_plies)
