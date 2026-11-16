# AI Interactions Log

> Stretch feature attempted: **Challenge 2: Multiple Scoring Modes** (design pattern).

---

## Design Pattern (SF10)

**Which design pattern did you use?**

A lightweight **Strategy** pattern. Each scoring strategy is a `ScoringMode` (a frozen
dataclass of weights: genre, mood, energy, acoustic). They live in the `SCORING_MODES` registry:
`genre-first`, `mood-first` and `energy-focused`. The scoring rule itself (`score_song`) stays
the same and takes the strategy as a `mode` argument, so any mode can be swapped in without
touching the loop or the ranking code.

**How did AI help you brainstorm or implement it?**

Prompt (with `recommender.py` attached):
> "I want users to switch between Genre-First, Mood-First and Energy-Focused ranking in
> main.py. Suggest a simple design pattern that keeps recommender.py modular. Compare a
> class-per-strategy approach with something lighter."

The AI suggested two options: (1) a classic Strategy with an abstract `ScoringStrategy` class
and one subclass per mode, each overriding `score()`; (2) since all three modes use the *same*
rule with *different weights*, make each strategy a data object holding the weights and keep a
single scoring function. I picked option 2 because the modes only differ in numbers, so
subclasses would have repeated the same scoring code three times. It also made the Phase 4
weight experiment (double energy, halve genre) a one-line addition: the `energy-focused` mode.

**How does the pattern appear in your final code?**

- `ScoringMode` dataclass and `SCORING_MODES` registry: `src/recommender.py`
- `get_mode()` resolves a name to a strategy and raises a clear error for unknown names.
- `score_song(user_prefs, song, mode=...)` and `recommend_songs(..., mode=...)` use the strategy.
- `src/main.py` exposes it as `python -m src.main --mode mood-first`.
- `tests/test_recommender.py::test_scoring_modes_change_weights` checks that switching modes
  changes the score the way the weights say it should.

**What I verified manually:** I ran all 7 profiles in all 3 modes and compared the top 5
(results are in the README "Experiments You Tried" section). I checked that the default mode
still gives exactly the same output as before the refactor, and that the max score for each
mode matches the sum of its weights (5.0, 5.0, 5.5).
