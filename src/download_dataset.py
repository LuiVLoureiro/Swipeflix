"""Baixa o dataset oficial e nao-comercial do IMDb (datasets.imdbws.com).

Arquivos baixados para data/raw/:
  - title.basics.tsv.gz  (titulo, ano, generos, duracao, tipo)
  - title.ratings.tsv.gz (nota media e numero de votos)
"""
import urllib.request

from . import config


def _download(url: str, dest_path) -> None:
    print(f"Baixando {url} -> {dest_path}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = dest_path.with_suffix(dest_path.suffix + ".part")
    urllib.request.urlretrieve(url, tmp_path)
    tmp_path.replace(dest_path)
    size_mb = dest_path.stat().st_size / (1024 * 1024)
    print(f"OK ({size_mb:.1f} MB)")


def download_imdb_dataset(force: bool = False) -> None:
    if force or not config.IMDB_BASICS_RAW_PATH.exists():
        _download(config.IMDB_BASICS_URL, config.IMDB_BASICS_RAW_PATH)
    else:
        print(f"Ja existe: {config.IMDB_BASICS_RAW_PATH}")

    if force or not config.IMDB_RATINGS_RAW_PATH.exists():
        _download(config.IMDB_RATINGS_URL, config.IMDB_RATINGS_RAW_PATH)
    else:
        print(f"Ja existe: {config.IMDB_RATINGS_RAW_PATH}")


if __name__ == "__main__":
    download_imdb_dataset()
