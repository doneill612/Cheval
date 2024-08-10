from src.cheval.analyze import Analyzer
from src.cheval.entities.game import *

if __name__ == "__main__":
    analyzer = Analyzer()
    pgn = (
        "1. e4 c5 2. Nf3 Nc6 3. d4 cxd4 4. Nxd4 Nf6 5. Nxc6 bxc6 6. Nc3 e5 7. Bc4 Bb4"
        " 8. Qd3 d5 9. exd5 e4 10. Qg3 cxd5 11. Bb5+ Bd7 12. Qe5+ Kf8 13. Bxd7 Qxd7 14."
        " O-O Bd6 15. Qd4 Qc7 16. h3 Be5 17. Qb4+ Kg8 18. Be3 Rb8 19. Qa4 a5 20. Nb5"
        " Qb7 21. c4 dxc4 22. Rad1 h6 23. Nd6 Qb4 24. Qc6 Bxd6 25. Rxd6 Kh7 26. Rxf6"
        " gxf6 27. Qxf6 Qf8 28. Qf5+ Kg8 29. Bd4 Rh7 30. Qg4+ Rg7 31. Bxg7 Qxg7 32."
        " Qxe4 Qxb2 33. Qxc4 Qg7 34. Qc7 Ra8 35. Re1 Kh7 36. Re7 Rf8 37. Qc2+ Kh8 38."
        " Qc7 Rg8 39. g3 Qa1+ 40. Kh2 Qxa2 41. Qf4 Rg7 1-0"
    )
    game = Game.from_pgn(pgn=pgn)
    analysis = analyzer.evaluate(game)
    for ply in game.plies:
        # if ply.player == "White":
        print(ply.evaluation, ply.uci)
