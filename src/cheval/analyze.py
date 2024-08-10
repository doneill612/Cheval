import os

import chess.polyglot as book
from chess import Board
from chess.polyglot import MemoryMappedReader
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
        book_path: str = None
    ):
        self._engine = Stockfish(path=engine_path, depth=depth, parameters=parameters)
        self._book_path = book_path or os.environ.get("BOOK_PATH")

    @staticmethod
    def _cp_to_prob(cp: float, is_white: bool = True, is_mate: bool = False):
        _cp = cp if not is_mate else 10000
        return 1 / (1 + 10 ** (-_cp * (1 if is_white else -1) / 400))

    def _analyze_ply(
        self, ply: Ply, opening_book: MemoryMappedReader = None, board: Board = None
    ) -> PlyEval:
        if opening_book and board:
            # determine if we're in book - if we are, quickly eval the position and classify as a book move
            if len([_ for _ in opening_book.find_all(board)]) > 0:
                best_move = self._engine.get_best_move()
                self._engine.make_moves_from_current_position([ply.uci])
                book_evaluation = self._engine.get_evaluation()
                p_win = self._cp_to_prob(
                    book_evaluation["value"], ply.player == "White"
                )
                return PlyEval(
                    engine_val=book_evaluation["value"],
                    p_win=p_win,
                    best_uci=best_move,
                    is_mate=False,
                    classification="Book",
                )

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

        # build eval entity
        evaluation = PlyEval(
            engine_val=new_cp,
            p_win=p_win_after,
            best_uci=best_move,
            is_mate=is_now_mate,
        )

        # calculate the change in probability of winning (color independent), classify move
        delta = abs(p_win_after - p_win_before)

        if p_win_after < p_win_before:
            if not is_currently_mate and is_now_mate:
                evaluation.classification = "Blunder"
            elif 0.1 <= delta < 0.2:
                evaluation.classification = "Inaccuracy"
            elif 0.2 <= delta < 0.3:
                evaluation.classification = "Mistake"
            elif delta >= 0.3:
                evaluation.classification = "Blunder"
            else:
                evaluation.classification = "Good"
        elif is_best:
            evaluation.classification = "Best"
        else:
            evaluation.classification = "Good"
        return evaluation

    def evaluate(self, game: Game):
        if self._book_path and os.path.exists(self._book_path):
            board = Board()
            with book.open_reader(self._book_path) as reader:
                for ply in game.plies:
                    board.push_uci(ply.uci)
                    evaluation = self._analyze_ply(
                        ply, opening_book=reader, board=board
                    )
                    ply.evaluation = evaluation
        else:
            for ply in game.plies:
                evaluation = self._analyze_ply(ply)
                ply.evaluation = evaluation
                reader.get()
