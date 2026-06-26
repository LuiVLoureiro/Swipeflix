"""Operadores classicos de algoritmo genetico: selecao por torneio, crossover
uniforme, mutacao gaussiana e elitismo. Atua sobre genomas definidos em
individual.py.
"""
import numpy as np

from . import config
from .individual import (IDX_PREF_RUNTIME, IDX_RATING, IDX_RUNTIME, IDX_VOTES,
                          IDX_YEAR, genome_size, random_population)


class GeneticAlgorithm:
    def __init__(self, n_genres: int, rng: np.random.Generator,
                 pop_size: int = config.POPULATION_SIZE,
                 elite_size: int = config.ELITE_SIZE,
                 tournament_size: int = config.TOURNAMENT_SIZE,
                 crossover_rate: float = config.CROSSOVER_RATE,
                 mutation_rate: float = config.MUTATION_RATE,
                 mutation_sigma: float = config.MUTATION_SIGMA):
        self.n_genres = n_genres
        self.rng = rng
        self.pop_size = pop_size
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.size = genome_size(n_genres)

        self.low_bounds, self.high_bounds = self._build_bounds()
        self.mutation_sigma_vector = mutation_sigma * (self.high_bounds - self.low_bounds) / 2.0

    def _build_bounds(self):
        low = np.empty(self.size)
        high = np.empty(self.size)
        low[: self.n_genres] = -1.0
        high[: self.n_genres] = 1.0
        n = self.n_genres
        low[n + IDX_RATING], high[n + IDX_RATING] = 0.0, 1.0
        low[n + IDX_VOTES], high[n + IDX_VOTES] = 0.0, 1.0
        low[n + IDX_YEAR], high[n + IDX_YEAR] = -1.0, 1.0
        low[n + IDX_RUNTIME], high[n + IDX_RUNTIME] = -1.0, 1.0
        low[n + IDX_PREF_RUNTIME], high[n + IDX_PREF_RUNTIME] = 0.0, 1.0
        return low, high

    def init_population(self) -> np.ndarray:
        return random_population(self.pop_size, self.n_genres, self.rng)

    def evolve(self, population: np.ndarray, fitness: np.ndarray) -> np.ndarray:
        """Produz a proxima geracao a partir da populacao e fitness atuais."""
        order = np.argsort(fitness)[::-1]
        elite = population[order[: self.elite_size]].copy()

        children = []
        n_children_needed = self.pop_size - self.elite_size
        while len(children) < n_children_needed:
            parent1 = self._tournament_select(population, fitness)
            parent2 = self._tournament_select(population, fitness)
            child1, child2 = self._crossover(parent1, parent2)
            children.append(self._mutate(child1))
            if len(children) < n_children_needed:
                children.append(self._mutate(child2))

        new_population = np.vstack([elite, np.array(children)])
        return np.clip(new_population, self.low_bounds, self.high_bounds)

    def _tournament_select(self, population: np.ndarray, fitness: np.ndarray) -> np.ndarray:
        idx = self.rng.integers(0, len(population), size=self.tournament_size)
        winner = idx[np.argmax(fitness[idx])]
        return population[winner]

    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray):
        if self.rng.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        mask = self.rng.random(self.size) < 0.5
        child1 = np.where(mask, parent1, parent2)
        child2 = np.where(mask, parent2, parent1)
        return child1, child2

    def _mutate(self, genome: np.ndarray) -> np.ndarray:
        mutate_mask = self.rng.random(self.size) < self.mutation_rate
        noise = self.rng.normal(0.0, 1.0, size=self.size) * self.mutation_sigma_vector
        return genome + mutate_mask * noise
