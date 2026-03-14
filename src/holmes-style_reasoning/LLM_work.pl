% === DOMAIN ENTITIES ===
site(el_arenal_1).
location(arauco_peninsula, chile).
country(chile).
ocean(pacific).
species(chicken, gallus_gallus).
origin(chicken, southeast_asia).
polynesian_islands([tonga, samoa, niue, easter_island, hawaii]).
expansion(polynesian, east_polynesia, circa(ad(1000), ad(1200))).

% === FACTS (expanded from all provided information) ===
fact(1, chicken_bones_excavated, el_arenal_1, 50_specimens).
fact(2, minimum_individuals, el_arenal_1, 5).
fact(3, radiocarbon_date, bone_el_arenal, '622 ± 35 BP').
fact(4, calibrated_date, bone_el_arenal, ad(1304, 1424)).
fact(5, calibrated_date_intercepts, bone_el_arenal, ad(1321, 1407)).
fact(6, additional_date_1, bone_el_arenal, '510 ± 30 BP').
fact(7, lab_code_1, additional_date_1, 'NZA 28271').
fact(8, additional_date_2, bone_el_arenal, '503 ± 30 BP').
fact(9, lab_code_2, additional_date_2, 'NZA 28272').
fact(10, site_occupation_range, el_arenal_1, ad(700, 1390)).
fact(11, dating_method_for_range, thermoluminescence, ceramics).
fact(12, ancient_dna_haplogroup, bone_el_arenal, polynesian).
fact(13, ancient_dna_haplotype, bone_el_arenal, identical_to_tonga_samoa).
fact(14, haplotype_variation, bone_el_arenal, 'one_base_difference_from_others_in_Tonga_Niue_Easter_Island_Hawaii').
fact(15, chickens_not_native, americas).
fact(16, pre_columbian_chickens_evidence, only_el_arenal_1_confirmed).
fact(17, no_native_wild_gallus, south_america).
fact(18, human_transport_required, chickens, across(pacific_ocean)).
fact(19, chickens_domesticated, gallus_gallus).
fact(20, polynesian_introduction_to_pacific, chickens, lapita_culture, circa(1000_bc)).
fact(21, voyaging_capability, polynesians, double_hulled_canoes, long_distance).
fact(22, computer_simulations_exist, polynesian_voyaging, drift_and_sailed).
fact(23, drift_landing_bias, simulations, ecuador_peru_more_common_than_chile).
fact(24, return_voyages, polynesia_to_south_america, difficult).
fact(25, araucana_breed_traits, blue_green_eggs, ear_tufts, rumplessness).
fact(26, modern_araucana_genetics, primarily_european_asian_indian).
fact(27, 2014_study_claim, no_polynesian_mtDNA_in_ancient_south_american_chickens).
fact(28, counter_argument, 2014_claim, possible_lab_contamination).
fact(29, european_arrival, americas, ad(1492)).

% === CONSTRAINTS ===
constraint(required, human_mediated_transport) :- transport(chickens, pacific_ocean).
constraint(impossible, independent_dispersal) :- chickens, pacific_ocean.
constraint(low_genetic_diversity, domestic_chickens_mtDNA).
constraint(vulnerable_to, contamination, ancient_dna_analysis).
constraint(vulnerable_to, marine_reservoir_effect, radiocarbon_dating_coastal).
constraint(temporal_alignment, polynesian_reach_east, ad(1000, 1200), chicken_date(ad(1304, 1424))).
constraint(geographic_challenge, distance, easter_island, chile, thousands_km).
constraint(archaeological_rarity, polynesian_artifacts, south_american_coast).

% === RELATIONS ===
relation(site_contains, el_arenal_1, chicken_bones).
relation(dna_evidence_supports, polynesian_haplogroup, pre_columbian).
relation(dating_supports, calibrated_ad(1304,1424), pre_columbian).
relation(conflicts_with, european_introduction, calibrated_ad(1304,1424)).

% === OPEN QUESTIONS ===
open_question(exact_source_island, polynesia, tonga_samoa_easter_island).
open_question(one_time_vs_repeated_contact).
open_question(why_limited_modern_polynesian_signal, araucana_genetics).
open_question(potential_other_pre_columbian_contactors).

% === HYPOTHESES ===
hypothesis(1, deliberate_polynesian_voyage).
hypothesis(2, accidental_polynesian_drift_or_stowaway).
hypothesis(3, unknown_non_polynesian_pre_columbian_group).
hypothesis(4, post_columbian_chickens_misdated_or_contaminated).

% === DEDUCTIONS (core expected consequences) ===
deduction(1, timing, circa(ad(1300, 1400))).
deduction(1, route, trans_pacific, from(east_polynesia)).
deduction(1, biological_form, live_domesticated_chickens).
deduction(1, dna_prediction, polynesian_haplogroup).
deduction(1, contact_type, possible_repeated_or_trade).
deduction(1, archaeological_prediction, possible_other_polynesian_commensals).

deduction(2, timing, circa(ad(1300, 1400))).
deduction(2, route, drift, often_northern_south_america).
deduction(2, biological_form, small_number_survivors).
deduction(2, dna_prediction, polynesian_haplogroup).
deduction(2, contact_type, one_time).

deduction(3, dna_prediction, non_polynesian_haplogroup).
deduction(3, archaeological_prediction, evidence_other_culture).

deduction(4, timing, after(ad(1492))).
deduction(4, dna_prediction, european_asian_indian).
deduction(4, dating_prediction, post_columbian).

% === ELIMINATION / STATUS ===
eliminated(hypothesis(4), Reason) :-
    Reason = direct_conflict(radiocarbon, calibrated_ad(1304,1424)),
    Reason = multiple_dates_consistent(pre_columbian).

eliminated(hypothesis(3), Reason) :-
    Reason = dna_specific_match(polynesian_haplogroup),
    Reason = no_evidence(other_pre_columbian_group).

weakened(hypothesis(2), Reason) :-
    Reason = deliberate_transport_more_plausible(live_chickens),
    Reason = drift_bias_towards_northern_locations.

survives(hypothesis(1)).
survives(hypothesis(2)).  % kept alive but secondary

% === BEST SURVIVING EXPLANATION ===
best_explanation(polynesian_introduction_via_deliberate_contact) :-
    survives(hypothesis(1)),
    fact(12, ancient_dna_haplogroup, bone_el_arenal, polynesian),
    fact(4, calibrated_date, bone_el_arenal, ad(1304, 1424)),
    deduction(1, dna_prediction, polynesian_haplogroup),
    deduction(1, timing, circa(ad(1300, 1400))).

% === TOP-LEVEL QUERY GOAL ===
% How did chickens reach pre-Columbian South America?
reached_pre_columbian(chickens, south_america, Mechanism, Approximate_Time) :-
    best_explanation(polynesian_introduction_via_deliberate_contact),
    Mechanism = deliberate_polynesian_voyage,
    Approximate_Time = circa(ad(1300, 1400)).

% Alternative (weaker) surviving path
reached_pre_columbian(chickens, south_america, Mechanism, Approximate_Time) :-
    survives(hypothesis(2)),
    Mechanism = accidental_polynesian_drift,
    Approximate_Time = circa(ad(1300, 1400)).
