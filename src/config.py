"""Configuracao central do projeto: caminhos, URLs do dataset e hiperparametros do GA."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
FEEDBACK_DIR = ROOT_DIR / "feedback"
STATE_DIR = ROOT_DIR / "state"

MOVIES_CSV_PATH = DATA_PROCESSED_DIR / "movies.csv"
FEEDBACK_LOG_PATH = FEEDBACK_DIR / "feedback.jsonl"
STATE_JSON_PATH = STATE_DIR / "state.json"
STATE_POPULATION_PATH = STATE_DIR / "population.npy"

# Dataset oficial e gratuito disponibilizado pela IMDb para uso nao comercial.
# https://developer.imdb.com/non-commercial-datasets/
IMDB_BASICS_URL = "https://datasets.imdbws.com/title.basics.tsv.gz"
IMDB_RATINGS_URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"

IMDB_BASICS_RAW_PATH = DATA_RAW_DIR / "title.basics.tsv.gz"
IMDB_RATINGS_RAW_PATH = DATA_RAW_DIR / "title.ratings.tsv.gz"

# Filtro de relevancia: ignora filmes com poucos votos para manter o catalogo
# em um tamanho tratavel e evitar titulos obscuros/sem relevancia nas recomendacoes.
MIN_VOTES = 1000

# --- Hiperparametros do algoritmo genetico ---
POPULATION_SIZE = 40
ELITE_SIZE = 4
TOURNAMENT_SIZE = 3
CROSSOVER_RATE = 0.7
MUTATION_RATE = 0.15
MUTATION_SIGMA = 0.25

# Quantidade de individuos de elite usados para gerar a lista de recomendacoes.
N_ELITE_RECOMMENDERS = 5

# Tamanho da lista "segmentada" de filmes exibida a cada execucao/sessao.
BATCH_SIZE = 10

# Limite de filmes do mesmo genero principal dentro de um mesmo lote, para
# manter diversidade nas recomendacoes em vez de repetir sempre o mesmo genero.
MAX_PER_PRIMARY_GENRE = 3
