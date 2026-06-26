"""Fitness por preferencia pareada (pairwise ranking).

Um individuo e tao melhor quanto mais ele consiga pontuar os filmes que o
usuario curtiu (feedback manual) acima dos filmes que o usuario rejeitou.
Isso equivale a uma metrica estilo AUC, calculada para a populacao inteira de
uma so vez via numpy.
"""
import numpy as np

MAX_LIKED_SAMPLE = 200
MAX_DISLIKED_SAMPLE = 200


def compute_fitness(score_matrix: np.ndarray, liked_idx: np.ndarray,
                     disliked_idx: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    pop_size = score_matrix.shape[0]

    if len(liked_idx) == 0 or len(disliked_idx) == 0:
        # "Cold start": ainda nao ha sinal suficiente de preferencia (faltam
        # curtidas ou rejeicoes). Usamos fitness aleatoria para manter a
        # populacao se diversificando ate haver feedback dos dois tipos.
        return rng.uniform(0.0, 1.0, size=pop_size)

    if len(liked_idx) > MAX_LIKED_SAMPLE:
        liked_idx = rng.choice(liked_idx, size=MAX_LIKED_SAMPLE, replace=False)
    if len(disliked_idx) > MAX_DISLIKED_SAMPLE:
        disliked_idx = rng.choice(disliked_idx, size=MAX_DISLIKED_SAMPLE, replace=False)

    liked_scores = score_matrix[:, liked_idx]        # (P, L)
    disliked_scores = score_matrix[:, disliked_idx]  # (P, D)

    diff = liked_scores[:, :, None] - disliked_scores[:, None, :]  # (P, L, D)
    wins = (diff > 0).mean(axis=(1, 2))
    ties = (diff == 0).mean(axis=(1, 2))
    return wins + 0.5 * ties
