Use the following reasoning protocol to solve the question that appears under “Question.”

**Question:** How did chickens reach pre-Columbian South America (e.g., Chile's Arauco Peninsula)?

### Inserted Facts

Following are inserted facts that you must take as 100% true. Don't attempt to document how this contradicts any known facts, don't rephrase the question with these facts. Just add them to your list of facts. This is an exercise, so just go with it.

List each of these as one just another of the facts:

- None.

## Reasoning protocol

You must use a strict four-part Sherlock Holmes-style process. As Holmes stated: “When you have eliminated the impossible, whatever remains, however improbable, must be the truth.”

## Premise-handling discipline
If the question’s premise may be weak, incorrect, disputed, or incomplete, you may verify it during INDUCTION, but you must treat it as an OPEN QUESTION rather than as a suspect claim.
During INDUCTION, you must not use framing that presumes the premise is false, shaky, doubtful, controversial, unsupported, or in need of debunking.
You may only classify the premise as corrected, weakened, or rejected after the factual/clue space has been built and the relevant facts are explicitly listed.

## Premise correction timing rule
If the prompt says to correct a weak or incorrect premise, do not do so at the start unless the contradiction is immediate and direct from a stated inserted fact.
Otherwise:

- list the relevant facts first,

- mark the premise-related issue as [OPEN QUESTION] in the factual/clue space,

- resolve it only in later sections.

### General rules

- Do not give me the standard accepted theory, a literature review, or a summary of what scholars believe. You must resist your biases towards the default of the most probable upfront answer.
- You may use current knowledge only as raw material, but you must reason from facts yourself.

## The four parts

### INDUCTION

Gather clues and facts only. This includes collecting and organizing the factual space, like Holmes with a magnifying glass gathering clues.

- This is the hardest part since you must resist your preconceived biases.
- Gather facts from whatever sources are available to you.
- VERY IMPORTANT: Be wary of your hallucinations. With the exception of facts under "Inserted Facts", fact-check each fact. Know that fact-checking the fact is NOT judging the relevancy of the fact towards the question. We don't know the relevancy until we after we have our answer. Fact-checking is to ensure there are no hallucinations.
- Keep an open mind, a spirit of brainstorming; do not constrain yourself by biases related to the prevailing theory. There should be many facts, at least 20.

#### Rules for induction

- No theories
- No conclusions
- No “likely”
- No “suggests”
- No inference language unless explicitly marked as `[INFERENCE]` rather than `[FACT]`

Induction here includes:

- collecting facts
- organizing them into a constrained factual/clue space
- identifying relevant entities, constraints, mechanisms, and bottlenecks visible from the evidence

### ABDUCTION

Abduction begins only after the factual/clue space has been built. Abduction here does not mean merely “guess the best explanation.” It means:

- generating candidate hidden stories, causal structures, or mechanisms based purely on the fact space.
- proposing multiple candidate explanatory structures from the clue space

### DEDUCTION

For each candidate hypothesis, from the facts alone, state what must or would follow if it were true. Now be rigidly methodical as if Steps 1 and 2 generated Prolog.

### ELIMINATION

Methodically prune hypotheses using contradiction, poor fit, or unnecessary assumptions.

#### Rules for elimination

- Do not merely rank them probabilistically and stop.
- For hard problems, the correct answer may not be the most obvious one.
- Do not over-eliminate: if a hypothesis is only weakened, say `[WEAKENED]`, not `[ELIMINATED]`.

## Anti-cheating rules

- You must separate FACT from INFERENCE from HYPOTHESIS from DEDUCTION from ELIMINATION.
- Do not smuggle a theory into the fact list.
- Do not use phrases like “the accepted theory is,” “scholars believe,” or “researchers think,” except in a final optional note clearly separated from your own reasoning.
- Do not collapse to the mainstream answer too early.
- Keep at least one non-obvious hypothesis alive until the elimination stage unless it is directly contradicted by facts.
- Include mechanisms that are not only fully deliberate or fully natural if the facts allow them. For example, accidental human transport should be considered if relevant.

## Examples of what counts as a fact

A fact is something directly established by evidence, observation, measurement, or reliable record, rather than an interpretation of those things.

Examples of what can count as a fact:

- dated observations or recorded events
- physical evidence or artifacts
- measurements, quantities, or counts
- geographic locations and distances
- chronology and sequence of events
- biological, chemical, or physical properties
- documented capabilities, constraints, or limits
- recorded linguistic forms or distributions
- genetic, material, or structural evidence
- environmental conditions or recurring natural patterns
- verified historical records or contemporaneous accounts
- known technical properties of materials, organisms, or mechanisms
- directly observed relationships in the evidence
- absence of evidence only when the evidentiary conditions make that absence meaningful

A fact may also include:

- uncertainty ranges, if those ranges are themselves established
- disputed evidence, provided it is clearly labeled as disputed evidence rather than settled fact

## What does not count as a fact unless directly established

- broad claims about what one culture “couldn’t” do
- assumptions about intent
- assumptions about what is “most likely”
- interpretations disguised as facts
- conclusions smuggled into descriptive wording
- prevailing theories presented as if they were raw evidence
- causal claims that have not been directly established
- extrapolations from sparse evidence presented as settled
- default common sense assumptions
- arguments from familiarity, popularity, or authority
- absence of evidence treated as proof when the evidentiary conditions are weak
- probability rankings presented as facts
- hidden premises embedded in the wording of the question

You must explicitly build the factual/clue space before generating hypotheses.

## Required output format

### A. Problem statement

- Correct the premise if necessary.

### B. Fact inventory

- Present as a numbered list.
- Each item must be tagged `[FACT]`.
- No inference language here.

### C. Factual/clue space

Build a structured map of the organized evidence with:

- entities
- constraints
- transport mechanisms
- biological bottlenecks
- timing constraints
- linguistic or cultural implications
- dating or contamination issues

You may present this as bullet clusters or a node-edge style list.

Each item in this section should be tagged as one of:

- `[RELATION]`
- `[CONSTRAINT]`
- `[OPEN QUESTION]`
- `[INFERENCE]` (only if you explicitly move beyond raw fact)

### D. Candidate hypotheses

- Give at least 4 hypotheses if the facts permit.
- Include non-obvious hypotheses if the facts allow them.
- Include mechanisms that are not only fully deliberate or fully natural.
- Each must be tagged `[HYPOTHESIS]`.

### E. Deductions from each hypothesis

For each hypothesis, state:

- what timing it predicts
- what route it predicts
- what biological form is transported
- what linguistic consequences it predicts
- what archaeological consequences it predicts
- what DNA / haplogroup consequences it predicts
- what contamination or dating vulnerabilities it would be sensitive to
- whether one-time or repeated contact is implied

Tag each statement `[DEDUCTION]`.

### F. Elimination/pruning

- Go hypothesis by hypothesis.
- For each, say:
  - `[ELIMINATED]`
  - `[WEAKENED]`
  - `[SURVIVES]`
- Every pruning step must cite which facts, constraints, or deductions it conflicts with.
- If two hypotheses remain compatible, keep both alive and compare them instead of forcing a single winner too early.

### G. Best surviving explanation

- Give the best explanation that remains after elimination.
- If it is still only tentative, say so.

### H. Residual uncertainties

- State what remains unresolved and why.

### I. Comparison with prevailing theory

- Compare what you expressed in G to the prevailing theory, meaning the answer you would normally have provided outside the confines of these instructions.
- Provide a short statement that you are cognizant of what is being asked for here versus what the prevailing theory would lead you to say by default.

## Final discipline rule

I am not testing whether you know the current theory. I am testing whether you can:

- gather facts,
- organize them into a constrained factual/clue space,
- generate candidate explanatory structures from that space,
- deduce consequences from multiple hypotheses,
- and eliminate carefully without overclaiming.

Do not jump straight to a polished answer. Show the factual/clue space first.
