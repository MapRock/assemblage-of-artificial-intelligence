% ============================================================
% FACTS (tagged as raw, dated, or measured observations only)
% ============================================================

fact(chicken_bones_el_arenal).
fact(radiocarbon_date(el_arenal_1, 1304, 1424)).
fact(mtdna_match(el_arenal, polynesian_ancient)).
fact(domestication_origin(red_junglefowl, southeast_asia)).
fact(oldest_chicken_bones(ban_non_wat, 3250..3650_years_ago)).
fact(chicken_bones_polynesia(vanuatu_tonga, 2800..3000_bp)).
fact(polynesian_settlement(easter_island, around(1200))).
fact(distance(easter_island, south_america_coast, approx(3700, km))).
fact(genetic_admixture(polynesian_south_american, dated(1150..1230))).
fact(sweet_potato_native(south_america)).
fact(sweet_potato_cook_islands, around(1000)).
fact(polynesian_word_sweet_potato(kumara)).
fact(no_native_chicken(americas)).
fact(columbus_chickens(1493)).
fact(south_pacific_gyre_flows(east_to_west)).
fact(polynesian_navigation(outrigger_canoes, stars_swells_winds_birds)).
fact(indigenous_non_spanish_chicken_names(16th_century_south_america)).
fact(araucana_blue_eggs(chile)).

% ============================================================
% CONSTRAINTS & RELATIONSHIPS
% ============================================================

constraint(no_wild_chicken_ancestor(americas)).
constraint(chickens_require_live_transport_or_fertile_eggs).
constraint(pre_columbian => before(1492)).
constraint(ocean_voyage_survival_requires_food_water_shelter).
constraint(eggs_hatch_viability_limited).
constraint(ocean_currents(south_pacific, predominantly_westward)).
constraint(polynesian_settlement(easter_island) => possible_departure_after(1200)).

relation(chickens, polynesians, via(archaeological_bones_polynesia)).
relation(sweet_potato, polynesians, via(archaeological_remains_cook_islands)).
relation(polynesian, south_american, via(genetic_admixture)).
relation(el_arenal_date, polynesian_settlement, overlaps).

% ============================================================
% HYPOTHESES (as named individuals)
% ============================================================

hypothesis(h1, polynesian_to_south_america_deliberate).
hypothesis(h2, south_american_to_polynesia_then_return).
hypothesis(h3, accidental_drift_from_polynesia).
hypothesis(h4, direct_asian_pre_polynesian).
hypothesis(h5, post_columbian_intrusion_or_misdate).

% ============================================================
% DEDUCTIONS (what each hypothesis entails — used for pruning)
% ============================================================

deduction(h1, timing(1150..1424)).
deduction(h1, route(easter_island_or_eastern_polynesia → chile)).
deduction(h1, transport(live_chickens_or_eggs)).
deduction(h1, contact_type(possible_repeated)).
deduction(h1, predicts(polynesian_influence_chicken_names)).

deduction(h2, timing(1150..1424)).
deduction(h2, route(south_america → polynesia → return_against_currents)).
deduction(h2, contact_type(possible_one_time_if_return_successful)).

deduction(h3, route(drift_follows_currents)).
deduction(h3, survival_constraint(very_difficult_long_drift)).

deduction(h4, route(southeast_asia → south_america_direct)).
deduction(h4, predicts(early_asian_artifacts_south_america)).

deduction(h5, timing(after(1492))).
deduction(h5, predicts(no_pre_1492_chicken_bones)).

% ============================================================
% PRUNING RULES (simplified conflict detection)
% ============================================================

eliminated(h3) :-
    constraint(ocean_currents(south_pacific, predominantly_westward)),
    \+ deduction(h3, route(eastward_possible)).

eliminated(h4) :-
    \+ fact(early_asian_artifacts_south_america).

weakened(h2) :-
    constraint(ocean_currents(south_pacific, predominantly_westward)),
    deduction(h2, route(return_against_currents)).

weakened(h5) :-
    fact(radiocarbon_date(el_arenal_1, 1304, 1424)),
    fact(indigenous_non_spanish_chicken_names(16th_century_south_america)).

survives(h1) :-
    fact(radiocarbon_date(el_arenal_1, 1304, 1424)),
    fact(mtdna_match(el_arenal, polynesian_ancient)),
    deduction(h1, timing(1150..1424)),
    fact(genetic_admixture(polynesian_south_american, dated(1150..1230))),
    fact(sweet_potato_cook_islands, around(1000)),
    fact(polynesian_navigation(outrigger_canoes, stars_swells_winds_birds)).

% ============================================================
% QUERY that drove the conclusion
% ============================================================

best_explanation(H) :-
    hypothesis(H, _),
    survives(H),
    \+ eliminated(H),
    \+ (weakened(H), \+ survives_strongly(H)).

% Top-level query actually used (conceptually):
?- best_explanation(H).
