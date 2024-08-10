from typing import Literal

from pydantic import BaseModel


class PlyEval(BaseModel):
    engine_val: float
    p_win: float
    best_uci: str
    is_mate: bool
    classification: Literal[
        "Brilliant",
        "Great",
        "Best",
        "Good",
        "Book",
        "Inaccuracy",
        "Mistake",
        "Blunder",
    ] | None = None
    remarks: str | None = None


class GameEval(BaseModel):
    white_accuracy: float
    black_accuracy: float
    summary: str
