# Build a research agent that writes a cited report

A research pipeline as 26 small functions: a planner that splits the question, researchers that read notes in parallel, a writer that cites by number, and a checker that every sentence has a real source.

Built step by step on [Deep-Agnt](https://deep-agnt.com/projects/research-agent): 5 of 26 steps passed, each graded by tests.

- [x] Step 1: Cut a word to its stem
- [x] Step 2: Turn text into search terms
- [x] Step 3: Build the index
- [x] Step 4: Score the notes for a query
- [x] Step 5: Show where it matched
