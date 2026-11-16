# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**: a tiny, explainable, content-based music recommender.

---

## 2. Intended Use  

**Goal / task:** given one listener's taste profile (favorite genre, favorite mood, target
energy, and whether they like acoustic sound), VibeFinder suggests the top 5 songs from a small
catalog and explains why each one was picked.

**Assumptions about the user:** they can describe their taste with one genre and one mood, and
that taste doesn't change during the session.

**Intended use:** classroom exploration of how recommenders turn data into rankings, and a way
to see bias in a simple scoring rule.

**Not intended for:** real users or a real product. It should not be used to decide what music
gets promoted or paid, to judge artists, or to make claims about what any real person "should"
listen to. It has no feedback loop, no listening history and only 21 made-up songs.

---

## 3. How the Model Works  

VibeFinder works like a judge with a scorecard. For every song in the catalog it asks four
questions and hands out points:

1. **Is it your favorite genre?** If yes, +2 points. This is the biggest prize, because genre is
   the most stable part of someone's taste.
2. **Is it your favorite mood?** If yes, +1 point.
3. **How close is its energy to the energy you want?** Up to +1.5 points. A perfect match gets
   all 1.5; the further away the song is (louder *or* quieter), the fewer points it gets. It does
   not reward "more energy", only "the right energy".
4. **Does it sound the way you like?** Up to +0.5 points. If you like acoustic music, more
   acoustic songs get more of this bonus; if you don't, more produced/electronic songs do.

After every song has a score, the songs are sorted from highest to lowest and the top 5 are shown,
each with the list of reasons that earned its points (for example "genre match: pop (+2.0)").

Changes from the starter: the starter returned the first *k* songs with no scoring. I added CSV
loading with number conversion, the four-part score above, a reason list for every score, sorting
with `sorted()` (which builds a new list and leaves the original catalog unchanged, unlike
`.sort()`), and the same logic in the `Recommender` class so the tests pass.

---

## 4. Data  

- **Size:** 21 songs in `data/songs.csv`. The starter had 10; I added 11 to cover hip-hop, r&b,
  edm, metal, classical, country, reggae, folk and latin.
- **Features per song:** genre, mood, energy, tempo_bpm, valence, danceability, acousticness
  (plus id, title, artist). The scorer only uses genre, mood, energy and acousticness.
- **Genres:** 16 different genres, but very uneven: lofi has 3 songs; pop, hip-hop and r&b have
  2; everything else has 1.
- **Moods:** 13 moods (happy, chill, intense, confident, sad, angry, euphoric...). "happy" and
  "chill" have 4 songs each, while most moods have one.
- **Limits:** the songs are invented, not real tracks. There are no lyrics, language, release
  year, popularity or listening history. Some combinations don't exist at all (for example a
  loud *and* acoustic song), so some tastes can never be satisfied.

---

## 5. Strengths  

- **Clear, single-genre tastes work well.** Every core profile (pop, lofi, rock, hip-hop) got
  the obvious "perfect" song at #1 with a score near 4.9 out of 5.
- **Energy closeness behaves sensibly.** The Chill Lofi profile never gets a gym track in its
  top 5, and the rock profile never gets a sleepy one, because energy is judged by distance from
  the target and not by "more is better".
- **Every result explains itself.** Each recommendation lists the exact points it earned, so it
  is easy to see *why* a strange pick showed up, which made debugging the weights fast.

---

## 6. Limitations and Bias 

**Main weakness I found: high-energy songs leak into everyone's list, and a genre match can
override the mood the user asked for.** *Gym Hero* (pop / intense, energy 0.93) shows up in the
top 3 for **four of seven** profiles: High-Energy Pop, Deep Intense Rock, Sad but Hyped and
Acoustic Headbanger. For the "happy pop" listener it ranks #2 only because of the +2.0 genre
bonus, even though its mood is "intense", not happy. The catalog makes this worse: 6 of the 21
songs have energy above 0.8, so any user who wants high energy keeps getting the same
handful of loud tracks, whatever their genre. That is a small "filter bubble".

Other limitations:

- **Exact-match genres create hard walls.** "pop" and "indie pop" count as totally different,
  and so do "hip-hop" and "r&b". My Hip-Hop Head profile got synthwave and indie pop at #3–#5
  instead of the R&B songs I'd actually want next.
- **Rare-genre fans run out fast.** Fans of genres with one song (metal, folk, latin...) get one
  real match and then four "same energy, unrelated genre" filler picks.
- **Unknown genres fail silently.** The "k-pop" profile matched no genre, so the highest
  possible score dropped to 2.5 and the system never told the user it had no k-pop.
- **The acoustic preference barely matters.** It is worth at most 0.5 points, so the
  "Acoustic Headbanger" got the same loud electronic songs as everyone else.
- **Conflicting preferences get handled in a hidden way.** For "sad but energy 0.9", genre-first
  mode quietly decides the label wins; energy-focused mode quietly decides energy wins.

---

## 7. Evaluation  

**How I tested:** I ran `python -m src.main` with 7 profiles: 4 normal tastes and 3 adversarial
ones meant to trick the scorer (conflicting mood and energy, a genre missing from the catalog,
and an impossible "loud but acoustic" request). I read each top 5 and asked: does #1 make
sense? Do positions 2–5 feel like reasonable next songs? Then I re-ran everything in the other
two scoring modes (the weight experiment). There are also 7 automated tests in
`tests/test_recommender.py` (`pytest`), all passing.

### Outputs (genre-first mode, default weights)

#### Core profiles

**High-Energy Pop**

```
========================================================================
Profile: High-Energy Pop   (mode: genre-first)
Prefs:   genre=pop, mood=happy, energy=0.85, likes_acoustic=False
========================================================================
1. Sunrise City by Neon Echo  [pop / happy]
   Score: 4.87
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.85 (+1.46)
     - produced/electronic sound fit (+0.41)
2. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.85
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.85 (+1.38)
     - produced/electronic sound fit (+0.47)
3. Block Party Anthem by Verse Theory  [hip-hop / happy]
   Score: 2.96
     - mood match: happy (+1.0)
     - energy 0.84 vs target 0.85 (+1.48)
     - produced/electronic sound fit (+0.47)
4. Fuego Lento by Sol Marino  [latin / happy]
   Score: 2.80
     - mood match: happy (+1.0)
     - energy 0.80 vs target 0.85 (+1.43)
     - produced/electronic sound fit (+0.38)
5. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 2.69
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.85 (+1.36)
     - produced/electronic sound fit (+0.33)
```

**Chill Lofi**

```
========================================================================
Profile: Chill Lofi   (mode: genre-first)
Prefs:   genre=lofi, mood=chill, energy=0.38, likes_acoustic=True
========================================================================
1. Library Rain by Paper Lanterns  [lofi / chill]
   Score: 4.88
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.35 vs target 0.38 (+1.46)
     - acoustic sound fit (+0.43)
2. Midnight Coding by LoRoom  [lofi / chill]
   Score: 4.79
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.42 vs target 0.38 (+1.44)
     - acoustic sound fit (+0.35)
3. Focus Flow by LoRoom  [lofi / focused]
   Score: 3.86
     - genre match: lofi (+2.0)
     - energy 0.40 vs target 0.38 (+1.47)
     - acoustic sound fit (+0.39)
4. Spacewalk Thoughts by Orbit Bloom  [ambient / chill]
   Score: 2.81
     - mood match: chill (+1.0)
     - energy 0.28 vs target 0.38 (+1.35)
     - acoustic sound fit (+0.46)
5. Slow Burn by Silk Avenue  [r&b / chill]
   Score: 2.70
     - mood match: chill (+1.0)
     - energy 0.38 vs target 0.38 (+1.50)
     - acoustic sound fit (+0.20)
```

**Deep Intense Rock**

```
========================================================================
Profile: Deep Intense Rock   (mode: genre-first)
Prefs:   genre=rock, mood=intense, energy=0.92, likes_acoustic=False
========================================================================
1. Storm Runner by Voltline  [rock / intense]
   Score: 4.93
     - genre match: rock (+2.0)
     - mood match: intense (+1.0)
     - energy 0.91 vs target 0.92 (+1.48)
     - produced/electronic sound fit (+0.45)
2. Gym Hero by Max Pulse  [pop / intense]
   Score: 2.96
     - mood match: intense (+1.0)
     - energy 0.93 vs target 0.92 (+1.48)
     - produced/electronic sound fit (+0.47)
3. Bassline Fever by Pulse District  [edm / euphoric]
   Score: 1.94
     - energy 0.95 vs target 0.92 (+1.46)
     - produced/electronic sound fit (+0.48)
4. Iron Requiem by Grave Signal  [metal / angry]
   Score: 1.91
     - energy 0.97 vs target 0.92 (+1.43)
     - produced/electronic sound fit (+0.48)
5. Block Party Anthem by Verse Theory  [hip-hop / happy]
   Score: 1.85
     - energy 0.84 vs target 0.92 (+1.38)
     - produced/electronic sound fit (+0.47)
```

**Hip-Hop Head**

```
========================================================================
Profile: Hip-Hop Head   (mode: genre-first)
Prefs:   genre=hip-hop, mood=confident, energy=0.75, likes_acoustic=False
========================================================================
1. Concrete Crown by Verse Theory  [hip-hop / confident]
   Score: 4.92
     - genre match: hip-hop (+2.0)
     - mood match: confident (+1.0)
     - energy 0.78 vs target 0.75 (+1.46)
     - produced/electronic sound fit (+0.46)
2. Block Party Anthem by Verse Theory  [hip-hop / happy]
   Score: 3.83
     - genre match: hip-hop (+2.0)
     - energy 0.84 vs target 0.75 (+1.36)
     - produced/electronic sound fit (+0.47)
3. Night Drive Loop by Neon Echo  [synthwave / moody]
   Score: 1.89
     - energy 0.75 vs target 0.75 (+1.50)
     - produced/electronic sound fit (+0.39)
4. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 1.81
     - energy 0.76 vs target 0.75 (+1.48)
     - produced/electronic sound fit (+0.33)
5. Sunrise City by Neon Echo  [pop / happy]
   Score: 1.80
     - energy 0.82 vs target 0.75 (+1.40)
     - produced/electronic sound fit (+0.41)
```

#### Adversarial / edge-case profiles

**Sad but Hyped (conflict)**

```
========================================================================
Profile: Sad but Hyped (conflict)   (mode: genre-first)
Prefs:   genre=folk, mood=sad, energy=0.9, likes_acoustic=False
========================================================================
1. Paper Boats by Ember & Oak  [folk / sad]
   Score: 3.65
     - genre match: folk (+2.0)
     - mood match: sad (+1.0)
     - energy 0.30 vs target 0.90 (+0.60)
     - produced/electronic sound fit (+0.05)
2. Storm Runner by Voltline  [rock / intense]
   Score: 1.94
     - energy 0.91 vs target 0.90 (+1.48)
     - produced/electronic sound fit (+0.45)
3. Gym Hero by Max Pulse  [pop / intense]
   Score: 1.93
     - energy 0.93 vs target 0.90 (+1.46)
     - produced/electronic sound fit (+0.47)
4. Bassline Fever by Pulse District  [edm / euphoric]
   Score: 1.91
     - energy 0.95 vs target 0.90 (+1.43)
     - produced/electronic sound fit (+0.48)
5. Block Party Anthem by Verse Theory  [hip-hop / happy]
   Score: 1.88
     - energy 0.84 vs target 0.90 (+1.41)
     - produced/electronic sound fit (+0.47)
```

**Ghost Genre (k-pop, not in catalog)**

```
========================================================================
Profile: Ghost Genre (k-pop, not in catalog)   (mode: genre-first)
Prefs:   genre=k-pop, mood=happy, energy=0.8
========================================================================
1. Fuego Lento by Sol Marino  [latin / happy]
   Score: 2.50
     - mood match: happy (+1.0)
     - energy 0.80 vs target 0.80 (+1.50)
2. Sunrise City by Neon Echo  [pop / happy]
   Score: 2.47
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)
3. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 2.44
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)
4. Block Party Anthem by Verse Theory  [hip-hop / happy]
   Score: 2.44
     - mood match: happy (+1.0)
     - energy 0.84 vs target 0.80 (+1.44)
5. Concrete Crown by Verse Theory  [hip-hop / confident]
   Score: 1.47
     - energy 0.78 vs target 0.80 (+1.47)
```

**Acoustic Headbanger**

```
========================================================================
Profile: Acoustic Headbanger   (mode: genre-first)
Prefs:   genre=metal, mood=angry, energy=0.95, likes_acoustic=True
========================================================================
1. Iron Requiem by Grave Signal  [metal / angry]
   Score: 4.49
     - genre match: metal (+2.0)
     - mood match: angry (+1.0)
     - energy 0.97 vs target 0.95 (+1.47)
     - acoustic sound fit (+0.02)
2. Bassline Fever by Pulse District  [edm / euphoric]
   Score: 1.51
     - energy 0.95 vs target 0.95 (+1.50)
     - acoustic sound fit (+0.01)
3. Gym Hero by Max Pulse  [pop / intense]
   Score: 1.50
     - energy 0.93 vs target 0.95 (+1.47)
     - acoustic sound fit (+0.03)
4. Storm Runner by Voltline  [rock / intense]
   Score: 1.49
     - energy 0.91 vs target 0.95 (+1.44)
     - acoustic sound fit (+0.05)
5. Fuego Lento by Sol Marino  [latin / happy]
   Score: 1.40
     - energy 0.80 vs target 0.95 (+1.28)
     - acoustic sound fit (+0.12)
```

### Comparing profiles (pair by pair)

- **High-Energy Pop vs. Chill Lofi:** no overlap at all. Pop gets songs around 0.8 energy with
  produced sound; lofi gets songs around 0.35–0.4 with high acousticness. This makes sense: the
  energy target and the acoustic preference both point in opposite directions.
- **High-Energy Pop vs. Deep Intense Rock:** both lists include *Gym Hero*. For pop it gets in
  through the genre match; for rock it gets in through the "intense" mood match plus almost
  identical energy. Same song, two different reasons, which shows how one loud song can fit
  many profiles.
- **High-Energy Pop vs. Hip-Hop Head:** *Block Party Anthem* (hip-hop / happy) is #3 for pop
  (happy mood + energy) and #2 for hip-hop (genre). *Sunrise City* is #1 for pop but only #5 for
  hip-hop, where it gets in through energy alone. The genre bonus moves songs by whole ranks.
- **Chill Lofi vs. Deep Intense Rock:** the two most opposite profiles. Lofi's top 3 are all lofi
  and rock's #1 is the only rock song; after that rock falls back to edm, metal and hip-hop
  because they are loud. Rock fans get worse lists only because the catalog has one rock song.
- **Chill Lofi vs. Hip-Hop Head:** lofi has 3 genre matches, so its top 3 are all near-perfect;
  hip-hop has 2, so its list "falls off a cliff" from 3.83 to 1.89 at #3. More songs in your
  genre means a better list.
- **Deep Intense Rock vs. Hip-Hop Head:** both end up padded with "anything with similar energy"
  after their genre songs run out, which shows the system has no idea that rock is closer to
  metal, or hip-hop to r&b.
- **Sad but Hyped vs. Deep Intense Rock:** once you get past *Paper Boats* (#1 only because of
  folk + sad), the conflict profile's #2–#5 are almost the same as the rock profile's loud songs.
  Asking for energy 0.9 pulls you toward the same loud cluster no matter what mood you asked for.
- **Ghost Genre vs. High-Energy Pop:** almost the same songs (all "happy" and ~0.8 energy), but
  the k-pop user's scores max out at 2.5 instead of 4.87, with no warning that their genre is
  missing.
- **Acoustic Headbanger vs. Deep Intense Rock:** nearly the same loud songs. The acoustic bonus
  is so small (and no loud acoustic songs exist) that "likes acoustic" changed almost nothing.

### Why does *Gym Hero* keep showing up for "Happy Pop"? (plain language)

The scorer gives pop songs a big +2 head start for being pop. There are only two pop songs, and
*Gym Hero* is one of them. Even though it is a workout song and not a happy one, that head start
plus its high energy (close to what the pop listener asked for) is enough to beat every happy
song from other genres. The system isn't saying "this is a happy song". It's saying "this is
pop and it's loud, which is close enough."

### Why did *Concrete Crown* rank #1 for Hip-Hop Head?

It's the only song that earns all four bonuses: genre hip-hop (+2.0), mood confident (+1.0),
energy 0.78 vs. target 0.75 (+1.46), and low acousticness for a user who likes produced sound
(+0.46), for 4.92 total. The next song, *Block Party Anthem*, misses the mood bonus, and nothing
else is hip-hop, so the gap after #2 is huge.

### Does it feel right? (my intuition check, Hip-Hop Head)

#1 and #2 feel exactly right; *Concrete Crown* is the kind of confident, mid-tempo track I'd
expect. But #3–#5 (synthwave, indie pop, pop) feel wrong to me. If I'm in a hip-hop mood, my next
pick would be R&B like *Late Night Text* or *Slow Burn*, and neither one is in the top 5, because
the system thinks r&b has nothing to do with hip-hop and both songs are lower energy than my
target. So the list is "correct by the math", but there is no **ground truth** here, and my own
taste disagrees with places 3–5.

### Surprises

- How often a single song (*Gym Hero*) wins for very different people.
- For "Sad but Hyped", the genre-first scorer put a very quiet song (*Paper Boats*, energy 0.30)
  at #1 for someone who asked for 0.9 energy, because the labels outweighed a 0.6 energy gap.
- The system never says "I don't have what you want". It always returns 5 confident-looking
  results, even for k-pop.

---

## 8. Future Work  

1. **Genre similarity instead of exact matches.** Give partial credit for related genres (pop ↔
   indie pop, hip-hop ↔ r&b, rock ↔ metal) using a small similarity table.
2. **Diversity in the top 5.** Penalize repeating the same artist or genre so lists don't fill up
   with the same loud cluster, and flag when the user's genre isn't in the catalog at all.
3. **Learn from feedback.** Add likes and skips so weights can shift per user over time, which is
   the first step toward collaborative filtering. Also use valence and tempo, and let users give
   a list of moods instead of one.

---

## 9. Personal Reflection  

**Biggest learning moment:** seeing *Gym Hero* show up for four different profiles. I had
expected the genre weight to be the main source of bias, but the real issue was the mix of the
genre bonus *and* the fact that a lot of the catalog is loud. Bias came from the data and the
weights together, not from one "bad" line of code.

**How AI helped and where I double-checked it:** I used an AI coding assistant (Claude Code) to
draft the CSV loader, the scoring function, the expanded dataset and the docs, and to suggest
adversarial profiles. I still had to check its work. The starter's `main.py` imported
`from recommender import ...`, which breaks under `python -m src.main`, so that had to change to
`src.recommender`. The first output printed scores as "x / 5.00", which is wrong for profiles
without an acoustic preference (their max is 4.5). And the AI's first idea was to also score
valence and danceability, but in this catalog they move almost in step with energy, so they
would have double-counted the same thing. I ran the code and read every top 5 myself instead of
trusting that the math "looked right".

**What surprised me:** four simple rules and 21 songs already *feel* like a real recommender.
The reasons ("genre match: hip-hop (+2.0)") make the output sound confident and personal, even
when places 3–5 are basically "anything with similar energy". That confidence is a little
dangerous: an explanation makes a result look justified even when it isn't a good pick.

**What I'd try next:** genre-similarity scores so hip-hop fans get R&B, a diversity penalty, and
a fake "listening history" so I could try a basic collaborative-filtering version and compare it
with this content-based one.
