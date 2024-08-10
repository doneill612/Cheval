from typing import List, Literal
from uuid import uuid4

from chess import Board
from chess import pgn as pgn_reader
from pydantic import BaseModel

from .eval import PlyEval


class Ply(BaseModel):
    ply_id: str
    player: Literal["White", "Black"]
    uci: str
    san: str
    evaluation: PlyEval | None = None
    variations: List[List["Ply"]] | None = None


class Game(BaseModel):
    game_id: str
    plies: List[Ply]

    @classmethod
    def from_pgn(cls, *, fp: str = None, pgn: str = None) -> "Game":
        if fp:
            with open(fp, "r") as pgnfile:
                game = pgn_reader.read_game(pgnfile)
        elif pgn:
            import io

            sio = io.StringIO(pgn)
            game = pgn_reader.read_game(sio)

        plies: List[Ply] = []
        board = Board()

        for i, ply in enumerate(game.mainline_moves()):
            ply_id = f"pl_{uuid4().hex}"
            uci = ply.uci()
            san = board.san(ply)
            player = "White" if i % 2 == 0 else "Black"
            p = Ply(ply_id=ply_id, player=player, uci=uci, san=san)
            plies.append(p)
            board.push(ply)
        return Game(game_id=f"g_{uuid4().hex}", plies=plies)
