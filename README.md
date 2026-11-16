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

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



