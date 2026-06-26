"""Interface manual de feedback via terminal.

Isto e um placeholder deliberado para o futuro layout estilo Tinder em
React + Tailwind: cada filme e mostrado um a um e o usuario decide
like/dislike/skip. Quando o front-end React existir, ele vai chamar
RecommenderEngine.get_next_batch() / submit_feedback() atraves de uma API,
no lugar deste loop de input().
"""
import argparse

from . import config
from .movie_catalog import load_catalog
from .recommender import RecommenderEngine


def _prompt_feedback(movie: dict) -> str:
    print("\n" + "=" * 60)
    print(f"{movie['title']} ({movie['year']})")
    print(f"Genero(s): {', '.join(movie['genres'])}")
    print(f"Nota IMDB: {movie['rating']:.1f}  |  Votos: {movie['votes']:,}  |  "
          f"Duracao: {int(movie['runtime'])} min")
    print("=" * 60)
    while True:
        choice = input("[L]ike  [D]islike  [S]kip  [Q]uit > ").strip().lower()
        if choice in ("l", "like"):
            return "like"
        if choice in ("d", "dislike"):
            return "dislike"
        if choice in ("s", "skip"):
            return "skip"
        if choice in ("q", "quit"):
            return "quit"
        print("Opcao invalida.")


def _print_summary(summary: dict) -> None:
    print("\n" + "-" * 60)
    print(f"Geracao atual: {summary['generation']}")
    print(f"Fitness media da populacao: {summary['fitness_mean']:.3f}  |  "
          f"Melhor individuo: {summary['fitness_best']:.3f}")
    print(f"Feedback acumulado: {summary['total_feedback']}  |  "
          f"Filmes ja exibidos: {summary['total_shown']}")
    genome = summary["best_genome"]
    top = ", ".join(f"{g} ({w:+.2f})" for g, w in genome["top_genres"])
    print(f"Generos favoritos (melhor individuo ate agora): {top}")
    print("-" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Recomendador de filmes por algoritmo genetico (camada de feedback manual via terminal)")
    parser.add_argument("--rebuild-catalog", action="store_true",
                         help="Reprocessa o dataset bruto do IMDb mesmo se o catalogo processado ja existir")
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    print("Carregando catalogo de filmes do IMDb...")
    catalog = load_catalog(rebuild=args.rebuild_catalog)
    print(f"Catalogo com {catalog.n_movies:,} filmes e {catalog.n_genres} generos.\n")

    engine = RecommenderEngine(catalog, seed=args.seed)
    engine.evolve_step()
    _print_summary(engine.summary())

    batch = engine.get_next_batch(args.batch_size)
    if not batch:
        print("Nao ha mais filmes novos para recomendar no catalogo atual.")
        engine.save()
        return

    for movie in batch:
        action = _prompt_feedback(movie)
        if action == "quit":
            break
        if action == "like":
            engine.submit_feedback(movie["id"], movie["title"], True)
        elif action == "dislike":
            engine.submit_feedback(movie["id"], movie["title"], False)
        # skip: nao grava feedback, mas o filme ja fica marcado como exibido

    engine.save()
    print("\nSessao salva. Rode novamente para uma nova geracao de recomendacoes.")


if __name__ == "__main__":
    main()
