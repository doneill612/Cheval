from typing import List

from chess import Board
from chess import Move as ChessMove
from chess import pgn as pgn_reader
from pydantic import BaseModel

from .eval import Evaluation


class Ply(BaseModel):
    uci: str
    evaluation: Evaluation | None = None


class Move(BaseModel):
    white_ply: Ply
    black_ply: Ply


class Game(BaseModel):
    moves: List[Move]
    accuracy: float

    @staticmethod
    def _iter_plies(plies: List[ChessMove]):
        n_plies = len(plies)
        if n_plies % 2 != 0:
            plies.append(None)
        for i in range(0, n_plies, 2):
            yield plies[i], plies[i + 1]

    @classmethod
    def from_pgn(cls, *, fp: str = None, pgn: str = None):
        if fp:
            with open(fp, "r") as pgnfile:
                game = pgn_reader.read_game(pgnfile)
        elif pgn:
            import io

            sio = io.StringIO(pgn)
            game = pgn_reader.read_game(sio)
        board: Board = game.board()
        plies: List[ChessMove] = game.mainline_moves()
        moves: List[Move] = []
        for white_ply_uci, black_ply_uci in Game._iter_plies(plies):
            moves.append(
                Move(white_ply=Ply(uci=white_ply_uci), black_ply=Ply(black_ply_uci))
            )
