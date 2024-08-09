from enum import Enum
from typing import Iterable, List, Literal
from uuid import uuid4

from chess import Board
from chess import pgn as pgn_reader
from pydantic import BaseModel

from .eval import PlyEval


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class Ply(BaseModel):
    ply_id: str
    player: Literal[Color.WHITE, Color.BLACK]
    uci: str
    san: str
    evaluation: PlyEval | None = None


class Move(BaseModel):
    move_id: str
    white_ply: Ply
    black_ply: Ply | None = None


class Game(BaseModel):
    game_id: str
    moves: List[Move]

    @property
    def plies(self) -> Iterable[Ply]:
        for move in self.moves:
            yield move.white_ply
            yield move.black_ply

    @classmethod
    def from_pgn(cls, *, fp: str = None, pgn: str = None) -> "Game":
        if fp:
            with open(fp, "r") as pgnfile:
                game = pgn_reader.read_game(pgnfile)
        elif pgn:
            import io

            sio = io.StringIO(pgn)
            game = pgn_reader.read_game(sio)

        moves: List[Move] = []
        cmove: Move = None
        board = Board()

        for i, ply in enumerate(game.mainline_moves()):
            ply_id = f"pl_{uuid4().hex}"
            uci = ply.uci()
            san = board.san(ply)
            if i % 2 == 0:
                move_id = f"mv_{uuid4().hex}"
                cmove = Move(
                    move_id=move_id,
                    white_ply=Ply(ply_id=ply_id, player=Color.WHITE, uci=uci, san=san),
                )
            else:
                cmove.black_ply = Ply(
                    ply_id=ply_id, player=Color.BLACK, uci=uci, san=san
                )
                moves.append(cmove)
            board.push(ply)
        if cmove not in moves:
            moves.append(cmove)  # case of game ending on white move
        return Game(game_id=f"g_{uuid4().hex}", moves=moves)
