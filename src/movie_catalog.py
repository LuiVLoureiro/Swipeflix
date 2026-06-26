"""Representacao vetorizada do catalogo de filmes, usada pelo GA para pontuar
toda a populacao contra todos os filmes de uma vez (com numpy), de forma
eficiente.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data_loader import load_processed_catalog


def _normalize(values: np.ndarray, low_pct: float = 1.0, high_pct: float = 99.0) -> np.ndarray:
    """Normaliza para [0, 1] usando percentis (robusto a outliers)."""
    lo, hi = np.percentile(values, [low_pct, high_pct])
    if hi <= lo:
        return np.zeros_like(values, dtype=float)
    norm = (values - lo) / (hi - lo)
    return np.clip(norm, 0.0, 1.0)


@dataclass
class MovieCatalog:
    ids: np.ndarray          # str, tconst
    titles: np.ndarray       # str
    years: np.ndarray        # int
    runtime: np.ndarray      # float, minutos
    rating: np.ndarray       # float, 0-10
    votes: np.ndarray        # float
    genres: list             # list[list[str]], generos por filme
    genre_names: list        # list[str], vocabulario ordenado de generos

    genre_matrix: np.ndarray   # (n_movies, n_genres), normalizado por linha
    rating_norm: np.ndarray
    votes_norm: np.ndarray
    year_norm: np.ndarray
    runtime_norm: np.ndarray

    id_to_index: dict

    @property
    def n_movies(self) -> int:
        return len(self.ids)

    @property
    def n_genres(self) -> int:
        return len(self.genre_names)

    def index_of(self, movie_id: str):
        return self.id_to_index.get(movie_id)


def build_catalog(df: pd.DataFrame) -> MovieCatalog:
    genre_lists = df["genres"].apply(lambda s: [g for g in s.split(",") if g])
    genre_names = sorted({g for genres in genre_lists for g in genres})
    genre_index = {g: i for i, g in enumerate(genre_names)}

    n_movies = len(df)
    n_genres = len(genre_names)
    genre_matrix = np.zeros((n_movies, n_genres), dtype=float)
    for row, genres in enumerate(genre_lists):
        if not genres:
            continue
        cols = [genre_index[g] for g in genres]
        genre_matrix[row, cols] = 1.0 / len(genres)

    years = df["year"].to_numpy(dtype=float)
    runtime = df["runtime"].to_numpy(dtype=float)
    rating = df["rating"].to_numpy(dtype=float)
    votes = df["votes"].to_numpy(dtype=float)

    catalog = MovieCatalog(
        ids=df["tconst"].to_numpy(dtype=str),
        titles=df["title"].to_numpy(dtype=str),
        years=years.astype(int),
        runtime=runtime,
        rating=rating,
        votes=votes,
        genres=list(genre_lists),
        genre_names=genre_names,
        genre_matrix=genre_matrix,
        rating_norm=_normalize(rating),
        votes_norm=_normalize(np.log1p(votes)),
        year_norm=_normalize(years),
        runtime_norm=_normalize(runtime),
        id_to_index={tconst: i for i, tconst in enumerate(df["tconst"].to_numpy(dtype=str))},
    )
    return catalog


def load_catalog(rebuild: bool = False) -> MovieCatalog:
    df = load_processed_catalog(rebuild=rebuild)
    return build_catalog(df)
