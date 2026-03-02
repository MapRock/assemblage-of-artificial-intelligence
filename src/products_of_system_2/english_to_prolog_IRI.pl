% ============================================================
% California Coastline: ecological + economic cascading system
% ============================================================

% --- Entities (for readability / validation) ---
entity(wd:Q575913).  % kelp_bed_health → kelp forest
entity(wd:Q1542312). % coastline_erosion → coastal erosion
entity(wd:Q83483).   % sea_urchin_population → Echinoidea (sea urchins)
entity(wd:Q41407).   % sea_otter_population → sea otter
entity(wd:Q36963).   % otter_pelt_hunting_pressure → hunting
entity(wd:Q878138).  % otter_shawl_sales → fur trade

% --- Signed relationships (direct vs inverse) ---
% direct(A,B)  : as A goes up, B tends to go up (all else equal)
% inverse(A,B) : as A goes up, B tends to go down (all else equal)

% Healthy kelp stabilizes coast -> reduces erosion (inverse)
inverse(wd:Q575913, wd:Q1542312).

% Urchins graze kelp -> more urchins, less kelp (inverse)
inverse(wd:Q83483, wd:Q575913).

% Otters prey on urchins -> more otters, fewer urchins (inverse)
inverse(wd:Q41407, wd:Q83483).

% Hunting reduces otters -> more hunting, fewer otters (inverse)
inverse(wd:Q36963, wd:Q41407).

% Market demand drives hunting -> more shawl sales, more hunting (direct)
direct(wd:Q878138, wd:Q36963).

% Optional symmetry: if you want reasoning in both directions for signs
direct(B,A)  :- direct(A,B).
inverse(B,A) :- inverse(A,B).

% --- Sign composition utilities ---
% A --> B can be "positive" (same direction) or "negative" (opposite direction).
edge(A,B,positive) :- direct(A,B).
edge(A,B,negative) :- inverse(A,B).

% Composition of signs along a chain
compose(positive, positive, positive).
compose(positive, negative, negative).
compose(negative, positive, negative).
compose(negative, negative, positive).

% ============================================================
% Derived reasoning: net effect through chains
% ============================================================

% effect(A,B,Sign) means: increasing A tends to change B with net Sign.
% (Sign is positive = increases, negative = decreases)
effect(A,B,Sign) :-
    entity(A), entity(B),
    path_effect(A,B,Sign,_Path).

% path_effect(A,B,Sign,Path) also returns a witness path A->...->B
path_effect(A,B,Sign,[A,B]) :-
    edge(A,B,Sign).
path_effect(A,B,Sign,[A|Rest]) :-
    edge(A,C,S1),
    C \= A,
    path_effect(C,B,S2,Rest),
    compose(S1,S2,Sign),
    \+ member(A,Rest).   % simple cycle avoidance

% Pretty-print helper for interpretation
interpret(positive, 'increases').
interpret(negative, 'decreases').

% ============================================================
% Domain-specific "story" query helpers
% ============================================================

% The full mediated fashion-demand chain to erosion:
% shawl sales -> hunting -> otters -> urchins -> kelp -> erosion
fashion_to_erosion(Sign, Path) :-
    path_effect(wd:Q878138, wd:Q1542312, Sign, Path).

% The core trophic cascade (otters -> kelp)
otters_to_kelp(Sign, Path) :-
    path_effect(wd:Q41407, wd:Q575913, Sign, Path).

% The habitat-to-geomorphology link (kelp -> erosion)
kelp_to_erosion(Sign, Path) :-
    path_effect(wd:Q575913, wd:Q1542312, Sign, Path).

% ============================================================
% Example queries (run in a Prolog REPL)
% ============================================================
%
% 1) What is the net effect of shawl sales on coastline erosion?
% ?- fashion_to_erosion(Sign, Path), interpret(Sign, Meaning).
%
% Expected:
%   Sign = positive,
%   Meaning = 'increases',
%   Path = [wd:Q878138, wd:Q36963,
%           wd:Q41407, wd:Q83483,
%           wd:Q575913, wd:Q1542312].
%
% 2) Do more otters help kelp?
% ?- otters_to_kelp(Sign, Path), interpret(Sign, Meaning).
%
% Expected: Sign = positive (more otters -> more kelp).
%
% 3) Does healthier kelp reduce erosion?
% ?- kelp_to_erosion(Sign, Path), interpret(Sign, Meaning).
%
% Expected: Sign = negative (more kelp -> less erosion).
%
% 4) Ask any pair:
% ?- effect(wd:Q83483, wd:Q1542312, Sign),
%    interpret(Sign, Meaning).
%
% Expected: Meaning = 'increases' (more urchins -> less kelp -> more erosion).
%
