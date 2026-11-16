import csv
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Union



@dataclass(frozen=True)
class ScoringMode:
    """A scoring strategy: the point weights used by score_song."""
    name: str
    genre: float
    mood: float
    energy: float
    acoustic: float


# Strategy pattern: each mode is an interchangeable set of weights for the same scoring rule.
SCORING_MODES: Dict[str, ScoringMode] = {
    # Default Algorithm Recipe (see README).
    "genre-first": ScoringMode("genre-first", genre=2.0, mood=1.0, energy=1.5, acoustic=0.5),
    # Mood matters most; genre is a smaller bonus.
    "mood-first": ScoringMode("mood-first", genre=1.0, mood=2.0, energy=1.5, acoustic=0.5),
    # Phase 4 experiment: energy weight doubled (1.5 -> 3.0), genre weight halved (2.0 -> 1.0).
    "energy-focused": ScoringMode("energy-focused", genre=1.0, mood=1.0, energy=3.0, acoustic=0.5),
}
DEFAULT_MODE = "genre-first"

NUMERIC_INT_FIELDS = {"id"}
NUMERIC_FLOAT_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

    def to_prefs(self) -> Dict:
        """Convert the profile into the dictionary format used by score_song."""
        return {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "likes_acoustic": self.likes_acoustic,
        }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog of Song objects."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for this user, best first."""
        prefs = user.to_prefs()
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(prefs, asdict(song))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable sentence listing why this song got its score."""
        score, reasons = score_song(user.to_prefs(), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read the songs CSV into a list of dicts, converting numeric columns to int/float."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            song: Dict = {}
            for key, value in row.items():
                key = key.strip()
                value = value.strip()
                if key in NUMERIC_INT_FIELDS:
                    song[key] = int(value)
                elif key in NUMERIC_FLOAT_FIELDS:
                    song[key] = float(value)
                else:
                    song[key] = value
            songs.append(song)
    return songs


def get_mode(mode: Union[str, ScoringMode]) -> ScoringMode:
    """Look up a scoring mode by name (or pass a ScoringMode through unchanged)."""
    if isinstance(mode, ScoringMode):
        return mode
    if mode not in SCORING_MODES:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(SCORING_MODES)}")
    return SCORING_MODES[mode]


def score_song(user_prefs: Dict, song: Dict, mode: Union[str, ScoringMode] = DEFAULT_MODE) -> Tuple[float, List[str]]:
    """Score one song against the user's prefs and return (score, list of reasons)."""
    weights = get_mode(mode)
    GENRE_POINTS, MOOD_POINTS = weights.genre, weights.mood
    ENERGY_POINTS, ACOUSTIC_POINTS = weights.energy, weights.acoustic
    score = 0.0
    reasons: List[str] = []

    fav_genre = str(user_prefs.get("genre", "")).lower()
    if fav_genre and song["genre"].lower() == fav_genre:
        score += GENRE_POINTS
        reasons.append(f"genre match: {song['genre']} (+{GENRE_POINTS:.1f})")

    fav_mood = str(user_prefs.get("mood", "")).lower()
    if fav_mood and song["mood"].lower() == fav_mood:
        score += MOOD_POINTS
        reasons.append(f"mood match: {song['mood']} (+{MOOD_POINTS:.1f})")

    if "energy" in user_prefs:
        gap = abs(song["energy"] - float(user_prefs["energy"]))
        energy_points = ENERGY_POINTS * (1 - gap)
        score += energy_points
        reasons.append(
            f"energy {song['energy']:.2f} vs target {float(user_prefs['energy']):.2f} (+{energy_points:.2f})"
        )

    if "likes_acoustic" in user_prefs:
        acousticness = song["acousticness"]
        fit = acousticness if user_prefs["likes_acoustic"] else 1 - acousticness
        acoustic_points = ACOUSTIC_POINTS * fit
        score += acoustic_points
        label = "acoustic" if user_prefs["likes_acoustic"] else "produced/electronic"
        reasons.append(f"{label} sound fit (+{acoustic_points:.2f})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, mode: Union[str, ScoringMode] = DEFAULT_MODE
) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort highest-first, and return the top k as (song, score, explanation)."""
    scored = [(song, *score_song(user_prefs, song, mode)) for song in songs]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
