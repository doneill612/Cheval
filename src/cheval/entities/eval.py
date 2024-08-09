from typing import Literal

from pydantic import BaseModel


class PlyEval(BaseModel):
    engine_val: float
    best_uci: str
    is_mate: bool
    classification: Literal[
        "Brilliant",
        "Great",
        "Best",
        "Good",
        "Inaccuracy",
        "Mistake",
        "Blunder",
    ] | None = None
    remarks: str | None = None
