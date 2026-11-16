# 🎵 Music Recommender Simulation

## Project Summary

**VibeFinder 1.0** is a small, content-based music recommender written in Python. It reads a
catalog of songs from `data/songs.csv`, compares each song to a user's "taste profile"
(favorite genre, favorite mood, target energy, and whether they like acoustic sound), gives
every song a score, and prints the top *k* songs, along with the reasons each one was picked.

---

## How The System Works

### How real recommenders work

Big platforms like Spotify, YouTube and TikTok mix two main ideas. **Collaborative filtering**
looks at *behavior*: if many people who like song A also like song B, then someone who likes A
will probably like B too. It needs a lot of user data (plays, likes, skips, saves, playlist
adds, replays, watch time), but it does not need to know anything about the song itself.
**Content-based filtering** looks at *the item*: it describes each song with features (genre,
mood, tempo, energy, valence, danceability, acousticness, even lyrics or raw audio) and
recommends songs whose features are close to what the user already likes. Real systems combine
both, and then a ranking model orders the candidates using context (time of day, device, what
you just skipped). Skips and replays matter a lot, because they are strong, cheap signals of
what someone actually feels about a song.

My version is a **content-based** system only. There are no other users in the simulation, so
it can't do collaborative filtering. It puts **genre** first, then **mood**, and then uses
**energy closeness** to break ties between songs that match on the labels.

### Data types in real systems

| Kind of data | Examples | Used here? |
|---|---|---|
| Explicit feedback | likes, thumbs up/down, follows | No |
| Implicit feedback | plays, skips, replays, listen time, playlist adds | No |
| Song labels | genre, mood, artist | **Yes** |
| Audio features | energy, tempo, valence, danceability, acousticness | **Yes** (energy, acousticness) |
| Context | time of day, device, location | No |

### Features

Each **`Song`** has: `id`, `title`, `artist`, `genre`, `mood`, `energy` (0–1), `tempo_bpm`,
`valence` (0–1), `danceability` (0–1), `acousticness` (0–1).

Each **`UserProfile`** stores: `favorite_genre`, `favorite_mood`, `target_energy` (0–1) and
`likes_acoustic` (True/False). The dictionary version used by `main.py` has the same idea:

```python
user_prefs = {"genre": "hip-hop", "mood": "confident", "energy": 0.75, "likes_acoustic": False}
```

I picked **genre, mood and energy** because they match how I describe a "vibe" myself ("chill
lofi", "intense rock", "hype rap"). Genre and mood are the words people actually use, and
energy is the one number that separates a gym song from a study song. Valence and danceability
are useful too, but in this small catalog they move almost together with energy, so adding them
would mostly count the same thing twice.

### Algorithm Recipe (finalized)

The **Scoring Rule** judges one song at a time:

| Rule | Points |
|---|---|
| Genre matches `favorite_genre` | **+2.0** |
| Mood matches `favorite_mood` | **+1.0** |
| Energy closeness: `1.5 × (1 − |song.energy − target_energy|)` | **0 to +1.5** |
| Acoustic fit: `0.5 × acousticness` if the user likes acoustic, otherwise `0.5 × (1 − acousticness)` | **0 to +0.5** |

Maximum score = **5.0**. Energy uses *closeness* (one minus the gap), not "higher is better",
so a user who wants 0.4 energy is rewarded for 0.4 songs and slowly loses points for both
louder and quieter ones. Genre is worth more than mood because genre is the most stable part
of taste: a hip-hop fan in a "happy" mood still wants hip-hop, not happy country.

The **Ranking Rule** turns those scores into a list: score every song in the catalog, sort from
highest to lowest score, and keep the top *k*. We need both: the scoring rule answers "how good
is this one song for this user?", and the ranking rule answers "which songs should I show
first?" A score on its own means nothing until it is compared with the others.

### Data flow

```
 Input                      Process (the loop)                          Output
┌──────────────┐     ┌───────────────────────────────────────┐     ┌────────────────┐
│ user_prefs   │     │ for each song in songs.csv:           │     │ sort by score, │
│ genre, mood, │ ──► │   score, reasons = score_song(prefs,  │ ──► │ highest first  │
│ energy,      │     │                                song)  │     │ → top k songs  │
│ acoustic     │     │   keep (song, score, reasons)         │     │   + reasons    │
└──────────────┘     └───────────────────────────────────────┘     └────────────────┘
```

### Expected biases

- **Genre over-weighting:** a +2.0 genre match is bigger than the best possible energy score,
  so a song in the right genre but the wrong mood can beat a song with the perfect mood and
  energy in a neighboring genre (for example "indie pop" vs. "pop", which count as different).
- **Exact string matching:** "r&b" and "hip-hop" are treated as totally unrelated, even though
  many listeners enjoy both.
- **Catalog imbalance:** genres with more songs (lofi has 3, hip-hop 2, most others 1) give
  their fans more good options, while fans of rare genres run out of matches after one song.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` with the default "pop / happy" profile:

```
Loaded songs: 21

========================================================================
Profile: Default Pop / Happy
Prefs:   genre=pop, mood=happy, energy=0.8
========================================================================
1. Sunrise City by Neon Echo  [pop / happy]
   Score: 4.47
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)
2. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.31
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.80 (+1.30)
3. Fuego Lento by Sol Marino  [latin / happy]
   Score: 2.50
     - mood match: happy (+1.0)
     - energy 0.80 vs target 0.80 (+1.50)
4. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 2.44
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)
5. Block Party Anthem by Verse Theory  [hip-hop / happy]
   Score: 2.44
     - mood match: happy (+1.0)
     - energy 0.84 vs target 0.80 (+1.44)
```

This matches what I expected: *Sunrise City* is the only song that is pop **and** happy **and**
close to 0.8 energy, so it wins by more than a point. *Gym Hero* comes second only because of the
+2.0 genre bonus, even though its mood is "intense", not happy. Places 3–5 are happy songs from
other genres that have almost exactly the right energy.

---

## Scoring Modes (Strategy pattern)

`src/recommender.py` defines three interchangeable scoring strategies in `SCORING_MODES`. Each
mode is a `ScoringMode` with its own weights, and `score_song` / `recommend_songs` take a `mode`
argument. Switch modes from the command line:

```bash
python -m src.main --mode genre-first      # default recipe: genre 2.0, mood 1.0, energy 1.5, acoustic 0.5
```

```bash
python -m src.main --mode mood-first       # genre 1.0, mood 2.0, energy 1.5, acoustic 0.5
```

```bash
python -m src.main --mode energy-focused   # experiment: genre 1.0, mood 1.0, energy 3.0, acoustic 0.5
```

Run a single profile with `--profile "Hip-Hop Head"`. Full outputs for all 7 profiles are in
[model_card.md](model_card.md#7-evaluation).

---

## Experiments You Tried

### Experiment 1: weight shift (double energy, halve genre)

I changed energy from 1.5 to **3.0** and genre from 2.0 to **1.0** (`--mode energy-focused`). The
math is still valid: every part stays non-negative, energy closeness is still between 0 and 1
before weighting, and the max score is 1 + 1 + 3 + 0.5 = 5.5. Top-5 results compared:

| Profile | genre-first (default) | energy-focused (experiment) |
|---|---|---|
| High-Energy Pop | Sunrise City, **Gym Hero**, Block Party Anthem, Fuego Lento, Rooftop Lights | Sunrise City, Block Party Anthem, **Gym Hero**, Fuego Lento, Rooftop Lights |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts, Slow Burn | Library Rain, Midnight Coding, Focus Flow, Slow Burn, Spacewalk Thoughts |
| Hip-Hop Head | Concrete Crown, Block Party Anthem, Night Drive Loop, Rooftop Lights, Sunrise City | Concrete Crown, Block Party Anthem, Night Drive Loop, Rooftop Lights, Fuego Lento |
| Sad but Hyped | **Paper Boats**, Storm Runner, Gym Hero, Bassline Fever, Block Party Anthem | Storm Runner, Gym Hero, Bassline Fever, Block Party Anthem, Iron Requiem |

The output for the profile that changed the most:

```
========================================================================
Profile: Sad but Hyped (conflict)   (mode: energy-focused)
Prefs:   genre=folk, mood=sad, energy=0.9, likes_acoustic=False
========================================================================
1. Storm Runner by Voltline  [rock / intense]
   Score: 3.42
     - energy 0.91 vs target 0.90 (+2.97)
     - produced/electronic sound fit (+0.45)
2. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.38
     - energy 0.93 vs target 0.90 (+2.91)
     - produced/electronic sound fit (+0.47)
3. Bassline Fever by Pulse District  [edm / euphoric]
   Score: 3.33
     - energy 0.95 vs target 0.90 (+2.85)
     - produced/electronic sound fit (+0.48)
4. Block Party Anthem by Verse Theory  [hip-hop / happy]
   Score: 3.29
     - energy 0.84 vs target 0.90 (+2.82)
     - produced/electronic sound fit (+0.47)
5. Iron Requiem by Grave Signal  [metal / angry]
   Score: 3.27
     - energy 0.97 vs target 0.90 (+2.79)
     - produced/electronic sound fit (+0.48)
```

**Result: mostly *different*, not more accurate.** Clear-taste profiles barely moved (same #1,
small swaps lower down). The big change was the conflicting profile: the only sad folk song,
*Paper Boats*, fell out of the top 5 completely, and the list turned into generic loud songs.
Whether that is "better" depends on what the user meant, which the system can't know. Doubling
energy also made the loud-song bubble stronger: *Gym Hero*, *Bassline Fever* and *Block Party
Anthem* climbed in almost every high-energy list.

### Experiment 2: mood-first mode

Swapping genre and mood weights (`--mode mood-first`) **did** feel more accurate for High-Energy
Pop: *Gym Hero* (pop but "intense") dropped from #2 to #5, and happy songs from other genres
moved up. For Chill Lofi, *Focus Flow* (lofi but "focused") dropped from #3 to #5. So mood-first
fixes the "Gym Hero for happy pop" problem, but it makes genre fans see more songs outside their
genre.

---

## Limitations and Risks

- Only 21 invented songs; most genres have a single song.
- Genres must match exactly, so related genres (hip-hop/r&b, pop/indie pop) get no credit.
- High-energy songs leak into many profiles (a small filter bubble).
- No lyrics, language, popularity or listening history, and no collaborative filtering.
- It never says "nothing matches": unknown genres silently get filler results.

See [model_card.md](model_card.md) for the full bias analysis.

---

## Reflection

Read the full model card, including evaluation and personal reflection:

[**Model Card**](model_card.md)

**How recommenders turn data into predictions:** a recommender is really two steps. A scoring
rule turns each song's features (genre, mood, energy) into one number that says how well it
fits *this* user, and a ranking rule sorts those numbers and keeps the top few. The "prediction"
is just the songs with the highest scores. What counts as a "good" song is decided by the weights
I chose, not learned from real listeners, so there's no ground truth to check against apart from
my own intuition.

**Where bias shows up:** bias came from two places at once: the weights (a big genre bonus) and
the dataset (lots of loud songs, one song for most genres). Together they made *Gym Hero* appear
for very different people, gave rock and metal fans worse lists than lofi fans, and quietly
ignored users whose genre wasn't in the catalog. In a real app with millions of users, the same
small choices would decide which artists get heard and which never get recommended.
