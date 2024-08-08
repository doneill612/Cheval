from enum import Enum
from typing import Literal

from pydantic import BaseModel


class PlyClassification(BaseModel):
    name: Literal[
        "Brilliant", "Great", "Best", "Good", "Inaccuracy", "Mistake", "Blunder"
    ]
    identifier: Literal["!!", "!", "*", "-", "?!", "?", "??"]


class Classification(Enum):
    BRILLIANT = PlyClassification(name="Brilliant", identifier="!!")
    GREAT = PlyClassification(name="Great", identifier="!")
    BEST = PlyClassification(name="Best", identifier="*")
    GOOD = PlyClassification(name="Good", identifier="-")
    INNACCURACY = PlyClassification(name="Inaccuracy", identifier="?!")
    MISTAKE = PlyClassification(name="Mistake", identifier="?")
    BLUNDER = PlyClassification(name="Blunder", identifier="??")


class Evaluation(BaseModel):
    engine_val: float
    classification: Literal[
        Classification.BRILLIANT,
        Classification.GREAT,
        Classification.BEST,
        Classification.GOOD,
        Classification.INNACCURACY,
        Classification.MISTAKE,
        Classification.BLUNDER,
    ]
    remarks: str | None
