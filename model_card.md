# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
