class Piece:
    def __init__(self, *, value: float, name: str, prefix: str | None = None):
        self._value = value
        self._name = name
        self._prefix = prefix


PAWN = Piece(value=1.0, name="Pawn")
BISHOP = Piece(value=3.05, name="Bishop", prefix="B")
KNIGHT = Piece(value=3.0, name="Knight", prefix="N")
ROOK = Piece(value=5.0, name="Rook", prefix="R")
QUEEN = Piece(value=9.0, name="Queen", prefix="Q")
KING = Piece(value=float("inf"), name="King", prefix="K")
