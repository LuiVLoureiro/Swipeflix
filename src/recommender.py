"""Orquestra catalogo + algoritmo genetico + feedback + estado persistido.

Esta e a peca central: a cada execucao ela evolui a populacao com base no
feedback acumulado e gera o proximo lote (lista "segmentada") de filmes para
o usuario avaliar. E o ponto de integracao que, no futuro, uma API por tras
do layout Tinder em React vai chamar em vez do CLI.
"""
import numpy as np

from . import config
from .feedback_store import FeedbackStore
from .fitness import compute_fitness
from .genetic_algorithm import GeneticAlgorithm
from .individual import describe_genome, score_population
from .state_store import GAState, StateStore


class RecommenderEngine:
    def __init__(self, catalog, feedback_store: FeedbackStore = None,
                 state_store: StateStore = None, seed: int = None):
        self.catalog = catalog
        self.feedback_store = feedback_store or FeedbackStore()
        self.state_store = state_store or StateStore()
        self.rng = np.random.default_rng(seed)
        self.ga = GeneticAlgorithm(catalog.n_genres, self.rng)

        loaded = self.state_store.load(catalog.genre_names)
        if loaded is None:
            self.population = self.ga.init_population()
            self.generation = 0
            self.shown_ids = set()
        else:
            self.population = loaded.population
            self.generation = loaded.generation
            self.shown_ids = loaded.shown_ids

        self.fitness = None

    def _feedback_indices(self):
        feedback = self.feedback_store.load()
        liked_idx, disliked_idx = [], []
        for movie_id, liked in feedback.items():
            idx = self.catalog.index_of(movie_id)
            if idx is None:
                continue
            (liked_idx if liked else disliked_idx).append(idx)
        return np.array(liked_idx, dtype=int), np.array(disliked_idx, dtype=int)

    def evolve_step(self) -> np.ndarray:
        """Avalia a fitness da populacao atual contra o feedback acumulado e
        evolui para a proxima geracao. Retorna a fitness da populacao
        anterior (util para mostrar progresso ao usuario)."""
        liked_idx, disliked_idx = self._feedback_indices()
        score_matrix = score_population(self.population, self.catalog)
        fitness = compute_fitness(score_matrix, liked_idx, disliked_idx, self.rng)

        self.population = self.ga.evolve(self.population, fitness)
        self.generation += 1

        new_scores = score_population(self.population, self.catalog)
        self.fitness = compute_fitness(new_scores, liked_idx, disliked_idx, self.rng)
        return fitness

    def get_next_batch(self, n: int = config.BATCH_SIZE) -> list:
        if self.fitness is None:
            self.evolve_step()

        elite_count = min(config.N_ELITE_RECOMMENDERS, len(self.population))
        elite_indices = np.argsort(self.fitness)[::-1][:elite_count]
        elite_scores = score_population(self.population[elite_indices], self.catalog)
        aggregate_score = elite_scores.mean(axis=0)

        available_mask = np.array([mid not in self.shown_ids for mid in self.catalog.ids])
        available_indices = np.where(available_mask)[0]
        if len(available_indices) == 0:
            return []

        ranked = available_indices[np.argsort(aggregate_score[available_indices])[::-1]]

        selected = []
        genre_counts = {}
        leftovers = []
        for idx in ranked:
            genres = self.catalog.genres[idx]
            primary = genres[0] if genres else None
            count = genre_counts.get(primary, 0)
            if count < config.MAX_PER_PRIMARY_GENRE:
                selected.append(idx)
                genre_counts[primary] = count + 1
            else:
                leftovers.append(idx)
            if len(selected) >= n:
                break

        if len(selected) < n:
            selected.extend(leftovers[: n - len(selected)])

        batch = []
        for idx in selected:
            movie_id = self.catalog.ids[idx]
            self.shown_ids.add(movie_id)
            batch.append({
                "id": movie_id,
                "title": self.catalog.titles[idx],
                "year": int(self.catalog.years[idx]),
                "genres": self.catalog.genres[idx],
                "rating": float(self.catalog.rating[idx]),
                "votes": int(self.catalog.votes[idx]),
                "runtime": float(self.catalog.runtime[idx]),
            })
        return batch

    def submit_feedback(self, movie_id: str, title: str, liked: bool) -> None:
        self.feedback_store.add(movie_id, title, liked, self.generation)

    def save(self) -> None:
        state = GAState(self.population, self.generation, self.shown_ids,
                         self.catalog.genre_names)
        self.state_store.save(state)

    def summary(self) -> dict:
        fitness = self.fitness if self.fitness is not None else np.zeros(len(self.population))
        best_idx = int(np.argmax(fitness))
        return {
            "generation": self.generation,
            "population_size": len(self.population),
            "fitness_mean": float(fitness.mean()),
            "fitness_best": float(fitness[best_idx]),
            "best_genome": describe_genome(self.population[best_idx], self.catalog),
            "total_feedback": len(self.feedback_store.rated_ids()),
            "total_shown": len(self.shown_ids),
        }
