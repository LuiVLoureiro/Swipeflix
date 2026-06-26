"""Persistencia do feedback manual do usuario (curtiu / nao curtiu um filme).

Hoje a coleta e feita via terminal (cli.py), simulando o futuro layout estilo
Tinder em React + Tailwind. A interface publica desta classe (add/load) foi
pensada para nao precisar mudar quando o feedback passar a vir de uma API web:
um endpoint REST so vai chamar `add()` no lugar do prompt de terminal.

Formato: um arquivo JSON Lines (feedback/feedback.jsonl), uma linha por
feedback dado, append-only.
"""
import json
from datetime import datetime, timezone

from . import config


class FeedbackStore:
    def __init__(self, path=config.FEEDBACK_LOG_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, movie_id: str, title: str, liked: bool, generation: int) -> None:
        record = {
            "movie_id": movie_id,
            "title": title,
            "liked": liked,
            "generation": generation,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def load(self) -> dict:
        """Retorna {movie_id: liked_bool}. Se um filme foi avaliado mais de
        uma vez, o feedback mais recente prevalece."""
        feedback = {}
        if not self.path.exists():
            return feedback
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                feedback[record["movie_id"]] = record["liked"]
        return feedback

    def liked_ids(self) -> list:
        return [mid for mid, liked in self.load().items() if liked]

    def disliked_ids(self) -> list:
        return [mid for mid, liked in self.load().items() if not liked]

    def rated_ids(self) -> set:
        return set(self.load().keys())
