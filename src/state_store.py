"""Persistencia do estado evolutivo do algoritmo genetico entre execucoes.

E isso que permite que "a cada execucao" o algoritmo ja comece de onde parou:
populacao atual, numero da geracao e quais filmes ja foram mostrados ao
usuario (para a lista segmentada nunca repetir um filme ja exibido).
"""
import json

import numpy as np

from . import config


class GAState:
    def __init__(self, population: np.ndarray, generation: int,
                 shown_ids: set, genre_names: list):
        self.population = population
        self.generation = generation
        self.shown_ids = shown_ids
        self.genre_names = genre_names


class StateStore:
    def __init__(self, state_path=config.STATE_JSON_PATH,
                 population_path=config.STATE_POPULATION_PATH):
        self.state_path = state_path
        self.population_path = population_path
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, expected_genre_names: list):
        """Carrega o estado salvo, se compativel com o vocabulario de
        generos atual do catalogo. Retorna None se nao houver estado salvo
        ou se o catalogo mudou de forma incompativel (nesse caso o GA recomeca
        do zero, com aviso)."""
        if not self.state_path.exists() or not self.population_path.exists():
            return None

        with open(self.state_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        if meta.get("genre_names") != expected_genre_names:
            print("Aviso: o vocabulario de generos do catalogo mudou desde a "
                  "ultima execucao. Reiniciando a populacao do GA do zero.")
            return None

        population = np.load(self.population_path)
        return GAState(
            population=population,
            generation=meta["generation"],
            shown_ids=set(meta["shown_ids"]),
            genre_names=meta["genre_names"],
        )

    def save(self, state: GAState) -> None:
        np.save(self.population_path, state.population)
        meta = {
            "generation": state.generation,
            "shown_ids": sorted(state.shown_ids),
            "genre_names": state.genre_names,
        }
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
