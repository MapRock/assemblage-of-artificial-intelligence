% ============================================================
% Wikidata alignment facts for California coastline system
% ============================================================

% wikidata_match(PrologObject, QID, Confidence).
% wikidata_label(QID, Label).

% --- Kelp beds / forests ---
wikidata_match(kelp_bed_health, q575913, 0.78).
wikidata_label(q575913, "kelp forest").

% --- Coastal geomorphology ---
wikidata_match(coastline_erosion, q1542312, 0.95).
wikidata_label(q1542312, "coastal erosion").

% --- Sea urchins (taxonomic class used as proxy for population) ---
wikidata_match(sea_urchin_population, q83483, 0.70).
wikidata_label(q83483, "Echinoidea").

% --- Sea otters ---
wikidata_match(sea_otter_population, q41407, 0.97).
wikidata_label(q41407, "sea otter").

% --- Hunting pressure (modeled via general hunting activity) ---
wikidata_match(otter_pelt_hunting_pressure, q36963, 0.62).
wikidata_label(q36963, "hunting").

% --- Market / fashion demand layer ---
% Approximated via the broader fur trade economic system
wikidata_match(otter_shawl_sales, q878138, 0.45).
wikidata_label(q878138, "fur trade").

% ============================================================
% Optional helper rules
% ============================================================

% Retrieve full match bundle
wikidata_entity(PrologObject, QID, Label, Confidence) :-
    wikidata_match(PrologObject, QID, Confidence),
    wikidata_label(QID, Label).

% Example query:
% ?- wikidata_entity(X, QID, Label, Confidence).
%
% Example targeted query:
% ?- wikidata_entity(coastline_erosion, QID, Label, Confidence).
