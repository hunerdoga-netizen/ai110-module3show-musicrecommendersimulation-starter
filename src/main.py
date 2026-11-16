"""
Command line runner for the Music Recommender Simulation.

Run with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a readable block of the top k recommendations for one profile."""
    prefs_text = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print("=" * 72)
    print(f"Profile: {name}")
    print(f"Prefs:   {prefs_text}")
    print("=" * 72)
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k), start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    """Load the catalog and print recommendations for the default profile."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    print_recommendations("Default Pop / Happy", user_prefs, songs)


if __name__ == "__main__":
    main()
