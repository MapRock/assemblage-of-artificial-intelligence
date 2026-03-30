% --------------------------------------------
% belief_sample.pl
% A tiny probabilistic tuple demo for SWI-Prolog
% --------------------------------------------

% belief(Hypothesis, EvidenceList, Probability).

belief(
    hypothesis(bear),
    evidence([class(animal), covering(fur), color(black), size(big),legs(4)]),
    0.60
).

belief(
    hypothesis(bigfoot),
    evidence([covering(fur), color(black), size(big),legs(2)]),
    0.90
).

belief(
    hypothesis(cat),
    evidence([class(animal), covering(fur), color(black), size(small)]),
    0.75
).

belief(
    hypothesis(dog),
    evidence([class(animal), covering(fur), color(brown), size(medium)]),
    0.70
).

belief(
    hypothesis(panda),
    evidence([class(animal), covering(fur), color(black_white), size(big)]),
    0.85
).

belief(
    hypothesis(bear),
    evidence([class(animal), covering(fur), color(brown), size(big)]),
    0.80
).

% --------------------------------------------
% True if all items in Needed are found in Have
% This lets you query with partial evidence
% --------------------------------------------

subset_list([], _).
subset_list([H|T], L) :-
    member(H, L),
    subset_list(T, L).

% --------------------------------------------
% match_belief(+ObservedEvidence, -Hypothesis, -Probability)
% Finds beliefs whose stored evidence contains all observed evidence
% --------------------------------------------

match_belief(Observed, Hypothesis, Probability) :-
    belief(
        hypothesis(Hypothesis),
        evidence(StoredEvidence),
        Probability
    ),
    subset_list(Observed, StoredEvidence).

% --------------------------------------------
% best_match(+ObservedEvidence, -Hypothesis, -Probability)
% Returns the highest-probability matching hypothesis
% --------------------------------------------

best_match(Observed, BestHypothesis, BestProbability) :-
    findall(
        Probability-Hypothesis,
        match_belief(Observed, Hypothesis, Probability),
        Pairs
    ),
    Pairs \= [],
    keysort(Pairs, Sorted),
    reverse(Sorted, [BestProbability-BestHypothesis | _]).

% --------------------------------------------
% explain_match(+ObservedEvidence)
% Prints all matches
% --------------------------------------------

explain_match(Observed) :-
    match_belief(Observed, Hypothesis, Probability),
    write('Observed evidence: '), writeln(Observed),
    write('Matches hypothesis: '), writeln(Hypothesis),
    write('Probability: '), writeln(Probability),
    nl,
    fail.
explain_match(_).

% --------------------------------------------
% Some example queries
% --------------------------------------------
%
% ?- belief(H, E, P).
%
% ?- match_belief([class(animal), color(black)], H, P).
%
% ?- best_match([class(animal), covering(fur), size(big)], H, P).
%
% ?- explain_match([class(animal), covering(fur)]).
%
