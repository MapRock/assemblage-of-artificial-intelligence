% Core entities
chicken(gallus_gallus_domesticus).
site(el_arenal_1, arauco_peninsula, chile).
location(arauco_peninsula, '37°22′15″S', '73°36′45″W').

% Facts from evidence
fact(chicken_bones_recovered(el_arenal_1, 50, min_individuals(5))).
fact(occupation_period(el_arenal_1, ad(700), ad(1390))).  % from TL on ceramics
fact(direct_radiocarbon(chicken_bone(el_arenal_1), '622 ± 35 BP', calibrated(ad(1321..1407), '1σ'), calibrated(ad(1304..1424), '2σ'))).
fact(direct_radiocarbon(chicken_bone(el_arenal_1), '510 ± 30 BP', calibrated_pre_1492)).
fact(direct_radiocarbon(chicken_bone(el_arenal_1), '503 ± 30 BP', calibrated_pre_1492)).
fact(isotope_terrestrial_diet(chicken_bone(el_arenal_1), delta_c13('-20.9‰'), no_marine_reservoir_correction)).
fact(ancient_mtdna_haplogroup(chicken_bone(el_arenal_1), 'Haplogroup E')).
fact(mtdna_match(polynesian_sites, ['Tonga (Mele Havea)', 'Samoa (Fatu-ma-Futi)', 'Easter Island (early Anakena)', 'Hawai\'i (early)'])).
fact(polynesian_chickens_introduced(lapita_expansion, ~3000_bp)).
fact(polynesian_reach(eastern_polynesia, ~ad(1000..1400))).
fact(no_earlier_chicken_remains(south_america, pre_el_arenal)).
fact(chickens_require_human_transport(ocean_crossing)).

% Relations
relation(mtdna_affinity, el_arenal_1, polynesia).
relation(timing_alignment, el_arenal_chickens, late_eastern_polynesian_expansion).
relation(geographic_barrier, pacific_ocean, natural_dispersal_impossible).

% Constraints
constraint(requires_human_transport(chickens, trans_pacific)).
constraint(no_natural_ocean_crossing(gallus_gallus)).
constraint(bottleneck_live_survival(voyage, multiple_individuals)).
constraint(evidence_absence(earlier_sites, south_america)).
constraint(mtdna_not_asian_european_baseline, el_arenal_haplogroup_e).

% Hypotheses (numbered as in original)
hypothesis(1, intentional_polynesian_voyage(contact_or_trade, ~ad(1300..1400))).
hypothesis(2, accidental_drift_voyage(polynesian_canoe, currents)).
hypothesis(3, pre_polynesian_asian_contact(coastal_hopping)).
hypothesis(4, earlier_unknown_mechanism(polynesian_mtdna_convergence)).

% Sample deductions (partial; extensible)
deduction(1, timing, predicts(ad(1000..1400))).
deduction(1, route, trans_pacific_west_to_east).
deduction(1, biology, live_domestic_with_haplogroup_e).
deduction(1, dna, exact_near_match_to_polynesian_prehistoric).
deduction(2, contact, one_way_non_return).
deduction(3, dna, expected_asian_clusters_not_polynesian).
deduction(4, archaeology, expects_widespread_earlier_remains).

% Elimination / pruning results
status(1, survives).
status(2, survives(but_weakened)).
status(3, eliminated(conflicts_with_polynesian_specific_mtdna)).
status(4, eliminated(no_support_for_earlier_absence_natural_mechanism)).

% Best surviving (main conclusion)
best_explanation(polynesian_introduction, intentional_human_mediated, ~ad(1300..1400), from_eastern_polynesia_to_chilean_coast).
% Variant (weak): includes accidental element in broader contact context
