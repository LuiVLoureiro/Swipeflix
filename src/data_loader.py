"""Processa os arquivos brutos do IMDb (data/raw) em um catalogo limpo
(data/processed/movies.csv), e carrega esse catalogo para uso do algoritmo
genetico.
"""
import pandas as pd

from . import config
from .download_dataset import download_imdb_dataset


def _read_basics() -> pd.DataFrame:
    usecols = ["tconst", "titleType", "primaryTitle", "isAdult", "startYear",
               "runtimeMinutes", "genres"]
    dtype = {"tconst": "string", "titleType": "category",
             "primaryTitle": "string", "genres": "string"}
    df = pd.read_csv(
        config.IMDB_BASICS_RAW_PATH,
        sep="\t",
        usecols=usecols,
        dtype=dtype,
        na_values="\\N",
        low_memory=False,
    )
    df = df[df["titleType"] == "movie"]
    df = df[df["isAdult"].astype(str) == "0"]
    df = df.dropna(subset=["startYear", "runtimeMinutes", "genres", "primaryTitle"])
    df["startYear"] = pd.to_numeric(df["startYear"], errors="coerce")
    df["runtimeMinutes"] = pd.to_numeric(df["runtimeMinutes"], errors="coerce")
    df = df.dropna(subset=["startYear", "runtimeMinutes"])
    df = df[(df["runtimeMinutes"] >= 40) & (df["runtimeMinutes"] <= 300)]
    return df[["tconst", "primaryTitle", "startYear", "runtimeMinutes", "genres"]]


def _read_ratings() -> pd.DataFrame:
    df = pd.read_csv(
        config.IMDB_RATINGS_RAW_PATH,
        sep="\t",
        dtype={"tconst": "string"},
        na_values="\\N",
    )
    return df


def build_processed_catalog(min_votes: int = config.MIN_VOTES) -> pd.DataFrame:
    """Le os TSVs brutos do IMDb, filtra e gera o CSV processado."""
    if not config.IMDB_BASICS_RAW_PATH.exists() or not config.IMDB_RATINGS_RAW_PATH.exists():
        download_imdb_dataset()

    print("Lendo title.basics.tsv.gz ...")
    basics = _read_basics()
    print(f"  {len(basics):,} filmes apos filtro de tipo/idade/duracao")

    print("Lendo title.ratings.tsv.gz ...")
    ratings = _read_ratings()

    movies = basics.merge(ratings, on="tconst", how="inner")
    movies = movies[movies["numVotes"] >= min_votes]
    movies = movies.rename(columns={
        "primaryTitle": "title",
        "startYear": "year",
        "runtimeMinutes": "runtime",
        "averageRating": "rating",
        "numVotes": "votes",
    })
    movies = movies.reset_index(drop=True)
    print(f"  {len(movies):,} filmes com >= {min_votes} votos (catalogo final)")

    config.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    movies.to_csv(config.MOVIES_CSV_PATH, index=False)
    print(f"Catalogo salvo em {config.MOVIES_CSV_PATH}")
    return movies


def load_processed_catalog(rebuild: bool = False) -> pd.DataFrame:
    """Carrega o catalogo processado, gerando-o primeiro se necessario."""
    if rebuild or not config.MOVIES_CSV_PATH.exists():
        return build_processed_catalog()
    return pd.read_csv(config.MOVIES_CSV_PATH)


if __name__ == "__main__":
    build_processed_catalog()
