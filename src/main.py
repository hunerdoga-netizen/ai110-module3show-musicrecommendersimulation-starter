"""
Command line runner for the Music Recommender Simulation.

Run with:
    python -m src.main                       # all profiles, genre-first mode
    python -m src.main --mode mood-first     # switch scoring strategy
    python -m src.main --profile "Chill Lofi"
"""

import argparse

from src.recommender import DEFAULT_MODE, SCORING_MODES, load_songs, recommend_songs

PROFILES = {
    # Core profiles
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
    "Hip-Hop Head": {"genre": "hip-hop", "mood": "confident", "energy": 0.75, "likes_acoustic": False},
    # Adversarial / edge-case profiles
    "Sad but Hyped (conflict)": {"genre": "folk", "mood": "sad", "energy": 0.9, "likes_acoustic": False},
    "Ghost Genre (k-pop, not in catalog)": {"genre": "k-pop", "mood": "happy", "energy": 0.8},
    "Acoustic Headbanger": {"genre": "metal", "mood": "angry", "energy": 0.95, "likes_acoustic": True},
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5, mode: str = DEFAULT_MODE) -> None:
    """Print a readable block of the top k recommendations for one profile."""
    prefs_text = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print("=" * 72)
    print(f"Profile: {name}   (mode: {mode})")
    print(f"Prefs:   {prefs_text}")
    print("=" * 72)
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k, mode), start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    """Load the catalog and print recommendations for each profile in the chosen mode."""
    parser = argparse.ArgumentParser(description="VibeFinder music recommender")
    parser.add_argument("--mode", choices=list(SCORING_MODES), default=DEFAULT_MODE)
    parser.add_argument("--profile", choices=list(PROFILES), help="run a single profile")
    parser.add_argument("-k", type=int, default=5, help="number of recommendations")
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    names = [args.profile] if args.profile else list(PROFILES)
    for name in names:
        print_recommendations(name, PROFILES[name], songs, args.k, args.mode)


if __name__ == "__main__":
    main()
