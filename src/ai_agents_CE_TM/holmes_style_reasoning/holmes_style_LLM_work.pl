% =========================================================
% CHICKENS IN SOUTH AMERICA
% Bottom-up reconstruction encoded in Prolog
% Date context: 2026-03-14
% =========================================================

% ---------------------------------------------------------
% A. PROBLEM DEFINITION
% ---------------------------------------------------------

question(chickens_arrival_south_america).

question_axis(first_arrival_anywhere).
question_axis(main_establishment_route).
question_axis(pre_columbian_presence).

ambiguous_term(arrive, first_physical_entry).
ambiguous_term(arrive, sustained_breeding_population).
ambiguous_term(arrive, continent_wide_establishment).

region_scope(south_america).
regional_subscope(pacific_south_america).
regional_subscope(chile).

chronology_partition(pre_1500).
chronology_partition(post_1500).

transport_basis(european_colonial).
transport_basis(polynesian_transpacific).
transport_basis(non_polynesian_transpacific).
transport_basis(mixed_multiple_introductions).
transport_basis(artifact_or_error).

% ---------------------------------------------------------
% B. FIRST-PRINCIPLES CONSTRAINTS
% ---------------------------------------------------------

entity(chicken).
entity(human_transport).
entity(archaeological_site).
entity(ancient_dna).
entity(modern_population_genetics).
entity(radiocarbon_date).
entity(historical_record).

necessary_condition(any_real_introduction, human_transport_required).
necessary_condition(any_real_introduction, live_birds_or_fertile_eggs_required).
necessary_condition(any_real_introduction, route_within_human_seafaring_capability).
necessary_condition(any_real_introduction, trace_expected_in_archaeology_history_or_genetics).

impossible_mechanism(natural_transoceanic_self_dispersal).
impossible_mechanism(native_south_american_domestication_origin).

constraint(no_natural_ocean_crossing_by_chickens).
constraint(domestication_origin_asia_not_south_america).
constraint(first_arrival_not_same_as_main_establishment).
constraint(modern_populations_can_be_overwritten_by_later_introgression).
constraint(single_site_does_not_equal_continent_wide_establishment).

% ---------------------------------------------------------
% C. MECHANISM SPACE
% ---------------------------------------------------------

mechanism(m1_european_colonial_only).
mechanism(m2_polynesian_pre_columbian).
mechanism(m3_non_polynesian_asian_or_pacific_pre_columbian).
mechanism(m4_pre_columbian_local_plus_later_european_replacement).
mechanism(m5_artifact_error_false_signal).
mechanism(m6_hybrid_multiple_introductions).

mechanism_label(m1_european_colonial_only, 'European colonial introduction after 1500 only').
mechanism_label(m2_polynesian_pre_columbian, 'Pre-Columbian Polynesian introduction to Pacific South America').
mechanism_label(m3_non_polynesian_asian_or_pacific_pre_columbian, 'Pre-Columbian trans-Pacific arrival, source not specifically Polynesian').
mechanism_label(m4_pre_columbian_local_plus_later_european_replacement, 'Small earlier introduction plus later European replacement').
mechanism_label(m5_artifact_error_false_signal, 'Pre-Columbian signal is artifact, contamination, or dating/context error').
mechanism_label(m6_hybrid_multiple_introductions, 'Multiple introductions with later admixture and partial loss of early lineages').

expected_trace(m1_european_colonial_only, post_1500_historical_records).
expected_trace(m1_european_colonial_only, modern_south_american_chickens_cluster_with_european_or_iberian).
expected_trace(m1_european_colonial_only, no_secure_pre_1500_archaeological_chicken).

expected_trace(m2_polynesian_pre_columbian, secure_pre_1500_pacific_south_american_chicken_bones).
expected_trace(m2_polynesian_pre_columbian, ancient_dna_link_to_polynesian_lineages).
expected_trace(m2_polynesian_pre_columbian, localized_pacific_coast_distribution_possible).

expected_trace(m3_non_polynesian_asian_or_pacific_pre_columbian, secure_pre_1500_remains).
expected_trace(m3_non_polynesian_asian_or_pacific_pre_columbian, ancient_dna_asian_or_pacific_affinity_without_unique_polynesian_assignment).
expected_trace(m3_non_polynesian_asian_or_pacific_pre_columbian, weak_historical_documentation).

expected_trace(m4_pre_columbian_local_plus_later_european_replacement, isolated_pre_1500_signal).
expected_trace(m4_pre_columbian_local_plus_later_european_replacement, modern_populations_mostly_european).
expected_trace(m4_pre_columbian_local_plus_later_european_replacement, mismatch_between_ancient_local_and_modern_continental_patterns).

expected_trace(m5_artifact_error_false_signal, contested_single_site).
expected_trace(m5_artifact_error_false_signal, non_replicated_or_non_diagnostic_ancient_dna).
expected_trace(m5_artifact_error_false_signal, failure_of_source_assignment_under_reanalysis).

expected_trace(m6_hybrid_multiple_introductions, mixed_chronology).
expected_trace(m6_hybrid_multiple_introductions, mixed_source_signals).
expected_trace(m6_hybrid_multiple_introductions, modern_overprinting_of_earlier_lineages).

% ---------------------------------------------------------
% D. EVIDENCE ADMISSIBILITY
% ---------------------------------------------------------

admissible_evidence(directly_dated_archaeological_chicken_bones).
admissible_evidence(ancient_dna_from_secure_provenience).
admissible_evidence(ancient_dna_authentication_controls).
admissible_evidence(stratigraphic_context).
admissible_evidence(historical_records_of_animal_transfer).
admissible_evidence(modern_population_genetics_as_secondary_evidence).
admissible_evidence(replication_across_sites_or_labs).

weak_evidence(morphology_alone).
weak_evidence(non_diagnostic_short_mtdna_fragment).
weak_evidence(review_summary_without_primary_data).
weak_evidence(argument_from_absence_without_strong_sampling_model).

bias_entry_point(source_selection).
bias_entry_point(variable_definition).
bias_entry_point(sample_selection).
bias_entry_point(preservation_effects).
bias_entry_point(processing_effects).
bias_entry_point(publication_bias).
bias_entry_point(narrative_framing).
bias_entry_point(statistical_aggregation).
bias_entry_point(interpreting_absence_as_disproof).

% ---------------------------------------------------------
% E. EVIDENCE INVENTORY
% ---------------------------------------------------------

% Evidence item 1
evidence(e1_el_arenal_bones).
observation(e1_el_arenal_bones, chicken_bones_recovered_from_el_arenal_1_chile).
evidence_type(e1_el_arenal_bones, direct_archaeological_remains).
assumption_required(e1_el_arenal_bones, correct_taxonomic_identification).
assumption_required(e1_el_arenal_bones, secure_site_context).
assumption_required(e1_el_arenal_bones, no_later_intrusion).
bears_on(e1_el_arenal_bones, supports, m2_polynesian_pre_columbian).
bears_on(e1_el_arenal_bones, supports, m3_non_polynesian_asian_or_pacific_pre_columbian).
bears_on(e1_el_arenal_bones, supports, m4_pre_columbian_local_plus_later_european_replacement).
bears_on(e1_el_arenal_bones, supports, m6_hybrid_multiple_introductions).
bears_on(e1_el_arenal_bones, weakens, m1_european_colonial_only).
limitation(e1_el_arenal_bones, single_site).
limitation(e1_el_arenal_bones, contextual_debate).
limitation(e1_el_arenal_bones, not_continent_wide_evidence).

% Evidence item 2
evidence(e2_el_arenal_radiocarbon).
observation(e2_el_arenal_radiocarbon, one_chicken_bone_reported_as_622_plus_minus_35_bp_calibrated_ad_1304_1424).
evidence_type(e2_el_arenal_radiocarbon, radiocarbon_lab_result).
assumption_required(e2_el_arenal_radiocarbon, uncontaminated_collagen).
assumption_required(e2_el_arenal_radiocarbon, appropriate_calibration).
assumption_required(e2_el_arenal_radiocarbon, negligible_or_corrected_diet_offset).
bears_on(e2_el_arenal_radiocarbon, supports, m2_polynesian_pre_columbian).
bears_on(e2_el_arenal_radiocarbon, supports, m3_non_polynesian_asian_or_pacific_pre_columbian).
bears_on(e2_el_arenal_radiocarbon, supports, m4_pre_columbian_local_plus_later_european_replacement).
bears_on(e2_el_arenal_radiocarbon, supports, m6_hybrid_multiple_introductions).
bears_on(e2_el_arenal_radiocarbon, weakens, m1_european_colonial_only).
limitation(e2_el_arenal_radiocarbon, single_direct_date_not_source_specific).
limitation(e2_el_arenal_radiocarbon, local_not_continent_wide).

% Evidence item 3
evidence(e3_2007_ancient_mtdna_polynesian_claim).
observation(e3_2007_ancient_mtdna_polynesian_claim, ancient_mtdna_from_el_arenal_reported_and_interpreted_as_consistent_with_polynesian_chickens).
evidence_type(e3_2007_ancient_mtdna_polynesian_claim, ancient_dna_lab_result).
assumption_required(e3_2007_ancient_mtdna_polynesian_claim, no_contamination).
assumption_required(e3_2007_ancient_mtdna_polynesian_claim, haplotype_source_diagnostic).
assumption_required(e3_2007_ancient_mtdna_polynesian_claim, adequate_comparison_dataset).
bears_on(e3_2007_ancient_mtdna_polynesian_claim, supports, m2_polynesian_pre_columbian).
limitation(e3_2007_ancient_mtdna_polynesian_claim, later_authentication_dispute).
limitation(e3_2007_ancient_mtdna_polynesian_claim, limited_source_resolution).

% Evidence item 4
evidence(e4_2008_global_mtdna_critique).
observation(e4_2008_global_mtdna_critique, comparative_study_argued_chilean_and_pacific_chickens_not_uniquely_polynesian_and_showed_broader_indo_european_and_asian_origins).
evidence_type(e4_2008_global_mtdna_critique, comparative_genetic_study).
assumption_required(e4_2008_global_mtdna_critique, comparative_sampling_sufficient).
assumption_required(e4_2008_global_mtdna_critique, chosen_mtdna_region_informative).
bears_on(e4_2008_global_mtdna_critique, weakens, m2_polynesian_pre_columbian).
bears_on(e4_2008_global_mtdna_critique, supports, m1_european_colonial_only).
bears_on(e4_2008_global_mtdna_critique, supports, m4_pre_columbian_local_plus_later_european_replacement).
bears_on(e4_2008_global_mtdna_critique, supports, m5_artifact_error_false_signal).
bears_on(e4_2008_global_mtdna_critique, supports, m6_hybrid_multiple_introductions).
limitation(e4_2008_global_mtdna_critique, modern_or_broad_comparison_does_not_negate_local_earlier_event).

% Evidence item 5
evidence(e5_2014_thomson_reassessment).
observation(e5_2014_thomson_reassessment, previous_pacific_chicken_studies_argued_to_be_affected_by_modern_dna_contamination_and_no_evidence_for_polynesian_dispersal_to_pre_columbian_south_america_claimed).
evidence_type(e5_2014_thomson_reassessment, ancient_dna_methodological_reassessment).
assumption_required(e5_2014_thomson_reassessment, contamination_controls_adequate).
assumption_required(e5_2014_thomson_reassessment, diagnostic_polynesian_haplotypes_correctly_defined).
bears_on(e5_2014_thomson_reassessment, strongly_weakens, m2_polynesian_pre_columbian).
bears_on(e5_2014_thomson_reassessment, supports, m1_european_colonial_only).
bears_on(e5_2014_thomson_reassessment, supports, m5_artifact_error_false_signal).
bears_on(e5_2014_thomson_reassessment, partially_supports, m4_pre_columbian_local_plus_later_european_replacement).
bears_on(e5_2014_thomson_reassessment, partially_supports, m6_hybrid_multiple_introductions).
limitation(e5_2014_thomson_reassessment, attacks_source_assignment_more_than_raw_pre_1500_date).

% Evidence item 6
evidence(e6_storey_matisoosmith_rebuttal).
observation(e6_storey_matisoosmith_rebuttal, rebuttal_argued_ancient_pacific_haplogroup_e_preceded_later_d_dominance_and_chilean_sequences_were_independently_reproduced).
evidence_type(e6_storey_matisoosmith_rebuttal, published_rebuttal).
assumption_required(e6_storey_matisoosmith_rebuttal, independent_replication_valid).
assumption_required(e6_storey_matisoosmith_rebuttal, haplogroup_e_can_reflect_ancient_pacific_movement).
bears_on(e6_storey_matisoosmith_rebuttal, supports, m2_polynesian_pre_columbian).
bears_on(e6_storey_matisoosmith_rebuttal, supports, m4_pre_columbian_local_plus_later_european_replacement).
bears_on(e6_storey_matisoosmith_rebuttal, supports, m6_hybrid_multiple_introductions).
bears_on(e6_storey_matisoosmith_rebuttal, weakens, m5_artifact_error_false_signal).
limitation(e6_storey_matisoosmith_rebuttal, not_decisive_new_discriminating_data).

% Evidence item 7
evidence(e7_beavan_radiocarbon_defense).
observation(e7_beavan_radiocarbon_defense, response_argued_no_evidence_that_contamination_or_diet_offset_invalidated_el_arenal_chicken_dates).
evidence_type(e7_beavan_radiocarbon_defense, chronometric_methodological_response).
assumption_required(e7_beavan_radiocarbon_defense, collagen_prep_and_isotopic_reasoning_sound).
bears_on(e7_beavan_radiocarbon_defense, supports, m2_polynesian_pre_columbian).
bears_on(e7_beavan_radiocarbon_defense, supports, m3_non_polynesian_asian_or_pacific_pre_columbian).
bears_on(e7_beavan_radiocarbon_defense, supports, m4_pre_columbian_local_plus_later_european_replacement).
bears_on(e7_beavan_radiocarbon_defense, supports, m6_hybrid_multiple_introductions).
bears_on(e7_beavan_radiocarbon_defense, weakens, m5_artifact_error_false_signal).
limitation(e7_beavan_radiocarbon_defense, chronology_not_same_as_source_assignment).

% Evidence item 8
evidence(e8_modern_mainland_genetics_2020).
observation(e8_modern_mainland_genetics_2020, most_modern_mainland_south_american_chickens_in_haplogroup_e_with_close_affinity_to_european_especially_iberian_populations_and_no_haplogroup_d_observed).
evidence_type(e8_modern_mainland_genetics_2020, modern_population_genetics).
assumption_required(e8_modern_mainland_genetics_2020, modern_populations_retaining_information_about_major_establishment_route).
bears_on(e8_modern_mainland_genetics_2020, strongly_supports, m1_european_colonial_only).
bears_on(e8_modern_mainland_genetics_2020, strongly_supports, m4_pre_columbian_local_plus_later_european_replacement).
bears_on(e8_modern_mainland_genetics_2020, strongly_supports, m6_hybrid_multiple_introductions).
bears_on(e8_modern_mainland_genetics_2020, weakens, m2_polynesian_pre_columbian).
limitation(e8_modern_mainland_genetics_2020, weak_for_first_arrival_due_to_possible_replacement).

% Evidence item 9
evidence(e9_first_recorded_european_intro_brazil_1500).
observation(e9_first_recorded_european_intro_brazil_1500, secondary_literature_reports_first_recorded_european_introduction_to_continental_south_america_in_1500_with_cabral_in_brazil).
evidence_type(e9_first_recorded_european_intro_brazil_1500, historical_report_secondary_summary).
assumption_required(e9_first_recorded_european_intro_brazil_1500, historical_transmission_correct).
bears_on(e9_first_recorded_european_intro_brazil_1500, supports, m1_european_colonial_only).
bears_on(e9_first_recorded_european_intro_brazil_1500, supports, m4_pre_columbian_local_plus_later_european_replacement).
bears_on(e9_first_recorded_european_intro_brazil_1500, supports, m6_hybrid_multiple_introductions).
limitation(e9_first_recorded_european_intro_brazil_1500, first_recorded_not_same_as_first_actual).

% Evidence item 10
evidence(e10_2025_reassessment).
observation(e10_2025_reassessment, reassessment_reportedly_reconfirmed_pre_columbian_date_but_found_no_evidence_of_contact_with_polynesia_and_instead_evidence_of_south_american_interregional_interaction).
evidence_type(e10_2025_reassessment, recent_archaeological_reassessment).
assumption_required(e10_2025_reassessment, abstract_level_summary_matches_final_analysis).
bears_on(e10_2025_reassessment, weakens, m2_polynesian_pre_columbian).
bears_on(e10_2025_reassessment, supports, m3_non_polynesian_asian_or_pacific_pre_columbian).
bears_on(e10_2025_reassessment, supports, m4_pre_columbian_local_plus_later_european_replacement).
bears_on(e10_2025_reassessment, supports, m6_hybrid_multiple_introductions).
bears_on(e10_2025_reassessment, weakens, m5_artifact_error_false_signal).
limitation(e10_2025_reassessment, full_dataset_not_encoded_here).

% ---------------------------------------------------------
% F. CONSTRAINT MAP
% ---------------------------------------------------------

constraint_map_entity(chickens).
constraint_map_entity(el_arenal_1).
constraint_map_entity(modern_mainland_south_american_populations).
constraint_map_entity(european_colonial_networks).
constraint_map_entity(pacific_maritime_networks).

constraint_map_quantity(single_widely_cited_pre_1500_direct_date).
constraint_map_quantity(modern_mainland_signal_predominantly_european).
constraint_map_quantity(pre_columbian_evidence_sparse).

constraint_map_dependency(polynesian_claim_depends_on_pre_1500_chronology).
constraint_map_dependency(polynesian_claim_depends_on_source_diagnostic_ancient_dna).
constraint_map_dependency(continent_wide_establishment_not_inferred_from_single_local_find).

open_question(is_el_arenal_pre_1500_signal_fully_secure).
open_question(is_any_pre_1500_signal_specifically_polynesian).
open_question(was_any_pre_1500_arrival_local_or_broader).
open_question(was_any_early_signal_later_replaced).

known_variability(repeated_human_mediated_chicken_movement).
known_variability(mtDNA_lineage_replacement_over_time).
known_variability(local_archaeological_preservation_bias).

known_limitation(sparse_ancient_samples).
known_limitation(source_resolution_of_short_mtdna_fragments_limited).
known_limitation(single_site_overinterpretation_risk).
known_limitation(modern_genetics_can_miss_earlier_lost_introductons).

% ---------------------------------------------------------
% G. CANDIDATE HYPOTHESES
% ---------------------------------------------------------

hypothesis(h1_mainstream_strong).
maps_to(h1_mainstream_strong, m1_european_colonial_only).
hypothesis_type(h1_mainstream_strong, mainstream).

hypothesis(h2_mainstream_moderate).
hypothesis_type(h2_mainstream_moderate, mainstream).
hypothesis_text(h2_mainstream_moderate,
                'The continent-wide established South American chicken population mainly derives from European post-1500 introductions, regardless of whether any earlier local arrival occurred.').

hypothesis(h3_polynesian_first_arrival).
maps_to(h3_polynesian_first_arrival, m2_polynesian_pre_columbian).
hypothesis_type(h3_polynesian_first_arrival, mainstream_contrarian_debate_target).

hypothesis(h4_mixed_local_early_plus_later_replacement).
maps_to(h4_mixed_local_early_plus_later_replacement, m4_pre_columbian_local_plus_later_european_replacement).
hypothesis_type(h4_mixed_local_early_plus_later_replacement, mixed).

hypothesis(h5_artifact_only).
maps_to(h5_artifact_only, m5_artifact_error_false_signal).
hypothesis_type(h5_artifact_only, artifact_error).

hypothesis(h6_real_pre1500_not_demonstrably_polynesian).
maps_to(h6_real_pre1500_not_demonstrably_polynesian, m3_non_polynesian_asian_or_pacific_pre_columbian).
hypothesis_type(h6_real_pre1500_not_demonstrably_polynesian, contrarian).

% ---------------------------------------------------------
% H. DEDUCTIONS
% ---------------------------------------------------------

deduction(h1_mainstream_strong, no_secure_pre_1500_chicken_should_survive_scrutiny).
deduction(h1_mainstream_strong, modern_mainland_populations_should_be_european_like).
deduction(h1_mainstream_strong, earliest_reliable_evidence_should_be_post_1500_historical).

deduction(h2_mainstream_moderate, modern_continent_wide_population_should_be_mostly_european_even_if_small_earlier_event_occurred).
deduction(h2_mainstream_moderate, first_arrival_and_main_establishment_can_differ).

deduction(h3_polynesian_first_arrival, at_least_one_secure_pre_1500_pacific_site_should_exist).
deduction(h3_polynesian_first_arrival, ancient_dna_should_link_to_authentic_polynesian_lineages).
deduction(h3_polynesian_first_arrival, evidence_should_cluster_on_pacific_coast).

deduction(h4_mixed_local_early_plus_later_replacement, possible_pattern_is_local_early_signal_plus_overwhelmingly_european_modern_signal).
deduction(h4_mixed_local_early_plus_later_replacement, modern_dna_can_fail_to_recover_first_arrival).

deduction(h5_artifact_only, pre_columbian_case_should_rely_on_fragile_non_replicated_evidence).
deduction(h5_artifact_only, improved_methods_should_remove_or_reclassify_early_signal).

deduction(h6_real_pre1500_not_demonstrably_polynesian, pre_1500_date_can_survive_while_polynesian_source_assignment_fails).
deduction(h6_real_pre1500_not_demonstrably_polynesian, evidence_should_look_pre_columbian_but_not_source_diagnostic).

% ---------------------------------------------------------
% I. PRUNING / STATUS
% ---------------------------------------------------------

status(h1_mainstream_strong, weakened).
status_reason(h1_mainstream_strong, e2_el_arenal_radiocarbon).
status_reason(h1_mainstream_strong, e10_2025_reassessment).

status(h2_mainstream_moderate, survives_strongly).
status_reason(h2_mainstream_moderate, e8_modern_mainland_genetics_2020).
status_reason(h2_mainstream_moderate, e9_first_recorded_european_intro_brazil_1500).

status(h3_polynesian_first_arrival, weakened).
status_reason(h3_polynesian_first_arrival, e3_2007_ancient_mtdna_polynesian_claim).
status_reason(h3_polynesian_first_arrival, e5_2014_thomson_reassessment).
status_reason(h3_polynesian_first_arrival, e10_2025_reassessment).

status(h4_mixed_local_early_plus_later_replacement, survives_strongly).
status_reason(h4_mixed_local_early_plus_later_replacement, e2_el_arenal_radiocarbon).
status_reason(h4_mixed_local_early_plus_later_replacement, e8_modern_mainland_genetics_2020).
status_reason(h4_mixed_local_early_plus_later_replacement, e9_first_recorded_european_intro_brazil_1500).
status_reason(h4_mixed_local_early_plus_later_replacement, e10_2025_reassessment).

status(h5_artifact_only, weakened).
status_reason(h5_artifact_only, e5_2014_thomson_reassessment).
status_reason(h5_artifact_only, e7_beavan_radiocarbon_defense).
status_reason(h5_artifact_only, e10_2025_reassessment).

status(h6_real_pre1500_not_demonstrably_polynesian, survives).
status_reason(h6_real_pre1500_not_demonstrably_polynesian, e2_el_arenal_radiocarbon).
status_reason(h6_real_pre1500_not_demonstrably_polynesian, e5_2014_thomson_reassessment).
status_reason(h6_real_pre1500_not_demonstrably_polynesian, e10_2025_reassessment).

% ---------------------------------------------------------
% J. BEST SURVIVING EXPLANATIONS
% ---------------------------------------------------------

best_surviving_explanation(main_establishment_route,
    european_post_1500_colonial_introduction).

best_surviving_explanation(first_arrival_anywhere,
    unresolved_between_local_pre_columbian_arrival_and_post_1500_european_first_arrival).

best_surviving_explanation(pre_columbian_presence,
    possible_but_not_securely_proven_as_polynesian).

conclusion(main_continent_wide_establishment,
           'South America''s established chicken population is best explained by post-1500 European, especially Iberian, introduction.').

conclusion(first_arrival_localized_pacific_question,
           'A localized pre-Columbian arrival to Pacific South America remains possible and may be real chronologically, but the specifically Polynesian attribution is not strongly established.').

conclusion(polynesian_claim,
           'Polynesian introduction is not eliminated, but it is weakened and not proven.').

% ---------------------------------------------------------
% K. RESIDUAL UNCERTAINTIES
% ---------------------------------------------------------

residual_uncertainty(el_arenal_full_security).
residual_uncertainty(source_specificity_of_any_pre1500_signal).
residual_uncertainty(scale_and_duration_of_any_pre1500_population).

why_unresolved(el_arenal_full_security, sparse_sites_and_methodological_dispute).
why_unresolved(source_specificity_of_any_pre1500_signal, short_mtdna_limited_resolution).
why_unresolved(scale_and_duration_of_any_pre1500_population, later_replacement_and_sparse_archaeology).

resolving_evidence_needed(multiple_independent_pre_1500_sites).
resolving_evidence_needed(genome_scale_ancient_dna).
resolving_evidence_needed(independent_lab_replication).
resolving_evidence_needed(stable_isotope_and_husbandry_evidence).
resolving_evidence_needed(clear_association_with_transpacific_contact_materials).

% ---------------------------------------------------------
% L. COMPARISON WITH PREVAILING ANSWER
% ---------------------------------------------------------

prevailing_answer('Chickens were brought to South America by Europeans after Columbus.').

comparison_with_prevailing_answer(survives_for_continent_wide_establishment).
comparison_with_prevailing_answer(becomes_weaker_for_absolute_first_arrival_anywhere).
comparison_with_prevailing_answer(polynesian_definite_first_arrival_does_not_survive_strongly).

% ---------------------------------------------------------
% HELPER RULES
% ---------------------------------------------------------

supports(Evidence, Mechanism) :-
    bears_on(Evidence, supports, Mechanism).
supports(Evidence, Mechanism) :-
    bears_on(Evidence, strongly_supports, Mechanism).
supports(Evidence, Mechanism) :-
    bears_on(Evidence, partially_supports, Mechanism).

weakens(Evidence, Mechanism) :-
    bears_on(Evidence, weakens, Mechanism).
weakens(Evidence, Mechanism) :-
    bears_on(Evidence, strongly_weakens, Mechanism).

survivor(Hypothesis) :-
    status(Hypothesis, survives).
survivor(Hypothesis) :-
    status(Hypothesis, survives_strongly).

best_hypothesis_for_main_establishment(h2_mainstream_moderate).
best_hypothesis_for_main_establishment(h4_mixed_local_early_plus_later_replacement).

best_hypothesis_for_first_arrival(h4_mixed_local_early_plus_later_replacement).
best_hypothesis_for_first_arrival(h6_real_pre1500_not_demonstrably_polynesian).

not_proven(polynesian_specific_source).
not_ruled_out(polynesian_specific_source).
strongly_supported(european_main_establishment).

% ---------------------------------------------------------
% SAMPLE QUERIES
% ---------------------------------------------------------
%
% ?- status(H, S).
% ?- supports(E, m2_polynesian_pre_columbian).
% ?- weakens(E, m2_polynesian_pre_columbian).
% ?- best_surviving_explanation(main_establishment_route, X).
% ?- conclusion(Topic, Text).
% ?- survivor(H).
%
% ---------------------------------------------------------
