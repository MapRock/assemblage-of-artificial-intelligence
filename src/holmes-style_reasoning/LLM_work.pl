% A. Restated problem (as comment)
% Problem: Is there evidence that chickens reached South America before 1492 AD, and if so, how?

% B. Fact inventory (selected core facts as Prolog facts)
fact(chickens_domesticated_southeast_asia, approx_8000_years_ago).
fact(chickens_in_polynesia, dated_2000_to_3000_years_ago).
fact(european_contact_south_america, year(1492)).
fact(spanish_introduced_chickens, around_year(1528)).
fact(el_arenal_1_bones, 50_chicken_bones, min_5_individuals).
fact(el_arenal_1_radiocarbon, one_bone, calibrated_ad(1304,1424)).
fact(el_arenal_1_dna, haplogroup_e, matches_some_polynesian_and_worldwide).
fact(haplogroup_e, common_worldwide, including_europe_asia_polynesia_chile).
fact(2014_study, possible_modern_dna_contamination, no_unique_polynesian_south_american_match).
fact(2018_re_excavation, no_additional_chicken_bones, new_dates_ad(1300,1640)).
fact(distance_easter_island_chile, approx_2000_miles).
fact(chickens_cannot_cross_ocean_naturally).
fact(sweet_potatoes, south_american_origin, found_pre_columbian_polynesia).
fact(no_other_confirmed_pre_1492_chicken_bones_south_america).

% C. Factual/clue space (as relations and constraints)
relation(chicken_bones_el_arenal_1, associated_mapuche_culture).
relation(mt_dna_haplogroup_e, connects_el_arenal_to_polynesia_and_modern).
relation(sweet_potatoes, evidence_pre_columbian_contact_polynesia_south_america).

constraint(radiocarbon_dates, straddle_pre_post_1492, vulnerable_to_error).
constraint(ocean_distance, requires_human_transport).
constraint(haplogroup_e, not_unique_to_polynesia).
constraint(absence_other_sites, single_site_evidence_only).
constraint(2018_re_excavation, failed_replicate_chicken_find).
constraint(contamination_risk, high_for_ancient_dna).

% D. Candidate hypotheses
hypothesis(1, polynesian_intentional_transport, ad_1300, live_chickens).
hypothesis(2, post_columbian_intrusion, after_1492, spanish_introduction).
hypothesis(3, accidental_drift_voyage, sporadic_pre_1492, few_survivors).
hypothesis(4, misidentification_contamination, no_pre_columbian, modern_material).
hypothesis(5, asian_non_polynesian_trade, pre_1492_early, asian_landraces).

% Simple deduction rules (what each hypothesis predicts / is consistent with)
deduction(1, predicts_pre_1492_arrival).
deduction(1, predicts_polynesian_dna_markers).
deduction(1, sensitive_to_contamination).
deduction(1, implies_repeated_contact).

deduction(2, predicts_post_1492).
deduction(2, predicts_european_haplogroups).
deduction(2, consistent_with_dates_up_to_1640).

deduction(3, predicts_low_survival).
deduction(3, implausible_without_human_care).

deduction(4, predicts_no_pre_columbian).
deduction(4, explains_disputed_dna_via_contamination).

deduction(5, predicts_asian_artifacts).
deduction(5, no_supporting_evidence).

% E. Elimination / pruning rules
conflict(1, contamination_evidence) :- fact(2014_study, possible_modern_dna_contamination).
conflict(1, failed_replication) :- fact(2018_re_excavation, no_additional_chicken_bones).
conflict(1, haplogroup_not_unique) :- constraint(haplogroup_e, not_unique_to_polynesia).

conflict(3, biological_implausibility) :- fact(chickens_cannot_cross_ocean_naturally), deduction(3, predicts_low_survival).

conflict(5, lack_evidence) :- deduction(5, predicts_asian_artifacts), not(fact(asian_artifacts_pre_columbian)).

% Weakened hypotheses remain possible but damaged
weakened(1) :- conflict(1, contamination_evidence); conflict(1, failed_replication).
weakened(5) :- conflict(5, lack_evidence).

% Eliminated hypotheses
eliminated(3) :- conflict(3, biological_implausibility).
eliminated(H) :- hypothesis(H, _, _), conflict(H, _), not(weakened(H)).

% Surviving hypotheses (not fully eliminated)
survives(H) :- hypothesis(H, _, _), not(eliminated(H)).

% Query examples:
% ?- survives(H).               % Which hypotheses survive?
% ?- weakened(1).               % Is Polynesian transport weakened?
% ?- eliminated(3).             % Is drift voyage eliminated?
