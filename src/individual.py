"""Define o genoma de um individuo (uma "personalidade" de recomendador) e a
funcao de pontuacao (score) que ele aplica sobre o catalogo de filmes.

Cada individuo e um vetor de genes (pesos):
  [0 : n_genres)   -> peso de preferencia por genero (pode ser negativo)
  n_genres + 0     -> peso da nota IMDB
  n_genres + 1     -> peso da popularidade (numero de votos)
  n_genres + 2     -> peso do ano de lancamento (recencia)
  n_genres + 3     -> peso da proximidade da duracao ideal
  n_genres + 4     -> duracao ideal (normalizada 0-1)
"""
import numpy as np

N_EXTRA_GENES = 5
IDX_RATING, IDX_VOTES, IDX_YEAR, IDX_RUNTIME, IDX_PREF_RUNTIME = range(N_EXTRA_GENES)


def genome_size(n_genres: int) -> int:
    return n_genres + N_EXTRA_GENES


def random_population(pop_size: int, n_genres: int, rng: np.random.Generator) -> np.ndarray:
    """Cria uma populacao inicial aleatoria, shape (pop_size, genome_size)."""
    size = genome_size(n_genres)
    population = np.zeros((pop_size, size), dtype=float)
    population[:, :n_genres] = rng.uniform(-1.0, 1.0, size=(pop_size, n_genres))
    population[:, n_genres + IDX_RATING] = rng.uniform(0.0, 1.0, size=pop_size)
    population[:, n_genres + IDX_VOTES] = rng.uniform(0.0, 1.0, size=pop_size)
    population[:, n_genres + IDX_YEAR] = rng.uniform(-1.0, 1.0, size=pop_size)
    population[:, n_genres + IDX_RUNTIME] = rng.uniform(-1.0, 1.0, size=pop_size)
    population[:, n_genres + IDX_PREF_RUNTIME] = rng.uniform(0.0, 1.0, size=pop_size)
    return population


def score_population(population: np.ndarray, catalog) -> np.ndarray:
    """Pontua TODA a populacao contra TODO o catalogo de uma vez.

    Retorna uma matriz (pop_size, n_movies) com o score de cada individuo
    para cada filme.
    """
    n_genres = catalog.n_genres
    genre_weights = population[:, :n_genres]
    w_rating = population[:, n_genres + IDX_RATING]
    w_votes = population[:, n_genres + IDX_VOTES]
    w_year = population[:, n_genres + IDX_YEAR]
    w_runtime = population[:, n_genres + IDX_RUNTIME]
    preferred_runtime = population[:, n_genres + IDX_PREF_RUNTIME]

    genre_score = genre_weights @ catalog.genre_matrix.T
    rating_score = np.outer(w_rating, catalog.rating_norm)
    votes_score = np.outer(w_votes, catalog.votes_norm)
    year_score = np.outer(w_year, catalog.year_norm)

    runtime_closeness = 1.0 - np.abs(catalog.runtime_norm[None, :] - preferred_runtime[:, None])
    runtime_score = w_runtime[:, None] * runtime_closeness

    return genre_score + rating_score + votes_score + year_score + runtime_score


def describe_genome(genome: np.ndarray, catalog, top_n: int = 5) -> dict:
    """Resumo legivel das preferencias aprendidas por um individuo."""
    n_genres = catalog.n_genres
    genre_weights = genome[:n_genres]
    order = np.argsort(genre_weights)[::-1]
    top_genres = [(catalog.genre_names[i], float(genre_weights[i])) for i in order[:top_n]]
    bottom_genres = [(catalog.genre_names[i], float(genre_weights[i])) for i in order[-top_n:]]
    return {
        "top_genres": top_genres,
        "least_liked_genres": list(reversed(bottom_genres)),
        "w_rating": float(genome[n_genres + IDX_RATING]),
        "w_votes": float(genome[n_genres + IDX_VOTES]),
        "w_year": float(genome[n_genres + IDX_YEAR]),
        "w_runtime": float(genome[n_genres + IDX_RUNTIME]),
        "preferred_runtime_norm": float(genome[n_genres + IDX_PREF_RUNTIME]),
    }
