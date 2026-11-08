# Build a research agent that writes a cited report

A research pipeline as 26 small functions: a planner that splits the question, researchers that read notes in parallel, a writer that cites by number, and a checker that every sentence has a real source.

Built step by step on [Deep-Agnt](https://deep-agnt.com/projects/research-agent): 19 of 26 steps passed, each graded by tests.

- [x] Step 1: Cut a word to its stem
- [x] Step 2: Turn text into search terms
- [x] Step 3: Build the index
- [x] Step 4: Score the notes for a query
- [x] Step 5: Show where it matched
- [x] Step 6: Search
- [x] Step 7: Read the text out of a reply
- [x] Step 8: Read a list the model wrote
- [x] Step 9: Drop the near-duplicates
- [x] Step 10: Plan with a real model
- [x] Step 11: Read a researcher's findings
- [x] Step 12: Brief a researcher
- [x] Step 13: One researcher, on a real model
- [x] Step 14: Researchers in parallel, under a budget
- [x] Step 15: Merge what came back
- [x] Step 16: Number the sources
- [x] Step 17: Brief the writer
- [x] Step 18: Split the report into sentences
- [x] Step 19: Read the citations in a sentence
