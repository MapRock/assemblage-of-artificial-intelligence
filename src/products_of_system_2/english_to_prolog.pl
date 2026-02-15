% ============================================================
% California Coastline: ecological + economic cascading system
% ============================================================

% --- Entities (for readability / validation) ---
entity(kelp_bed_health).
entity(coastline_erosion).
entity(sea_urchin_population).
entity(sea_otter_population).
entity(otter_pelt_hunting_pressure).
entity(otter_shawl_sales).

% --- Signed relationships (direct vs inverse) ---
% direct(A,B)  : as A goes up, B tends to go up (all else equal)
% inverse(A,B) : as A goes up, B tends to go down (all else equal)

% Healthy kelp stabilizes coast -> reduces erosion (inverse)
inverse(kelp_bed_health, coastline_erosion).

% Urchins graze kelp -> more urchins, less kelp (inverse)
inverse(sea_urchin_population, kelp_bed_health).

% Otters prey on urchins -> more otters, fewer urchins (inverse)
inverse(sea_otter_population, sea_urchin_population).

% Hunting reduces otters -> more hunting, fewer otters (inverse)
inverse(otter_pelt_hunting_pressure, sea_otter_population).

% Market demand drives hunting -> more shawl sales, more hunting (direct)
direct(otter_shawl_sales, otter_pelt_hunting_pressure).

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
    path_effect(otter_shawl_sales, coastline_erosion, Sign, Path).

% The core trophic cascade (otters -> kelp)
otters_to_kelp(Sign, Path) :-
    path_effect(sea_otter_population, kelp_bed_health, Sign, Path).

% The habitat-to-geomorphology link (kelp -> erosion)
kelp_to_erosion(Sign, Path) :-
    path_effect(kelp_bed_health, coastline_erosion, Sign, Path).

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
%   Path = [otter_shawl_sales, otter_pelt_hunting_pressure,
%           sea_otter_population, sea_urchin_population,
%           kelp_bed_health, coastline_erosion].
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
% ?- effect(sea_urchin_population, coastline_erosion, Sign),
%    interpret(Sign, Meaning).
%
% Expected: Meaning = 'increases' (more urchins -> less kelp -> more erosion).
%
