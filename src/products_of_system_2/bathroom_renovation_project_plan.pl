% Bathroom Renovation Project Plan in Prolog
% Encodes tasks, subtasks, dependencies, decisions, and dynamic state for execution.
% Based on the MD project plan: Phases as main tasks, with sequences, conditions, and branches.

% Dynamic state predicates (update with assert/retract during simulation)
:- dynamic completed/1.  % completed(Task) - marks a task as done
:- dynamic resolved/2.   % resolved(ConditionOrDecision, Choice) - e.g., resolved(move_plumbing, yes)

% Main tasks (phases from the plan)
task(planning_and_design).
task(permits_and_preparation).
task(demolition).
task(structural_repair).  % Conditional
task(rough_plumbing).
task(rough_electrical).
task(inspection).
task(wallboard_and_waterproofing).
task(flooring_and_tile).
task(fixtures_installation).
task(electrical_finish).
task(painting_and_trim).
task(accessories).
task(final_checks).

% Subtasks under each main task (for detailed tracking if needed)
subtask(planning_and_design, measure_bathroom).
subtask(planning_and_design, sketch_layout).
subtask(planning_and_design, choose_fixtures).
subtask(planning_and_design, choose_tile_and_flooring).
subtask(planning_and_design, establish_budget).
subtask(planning_and_design, order_materials).

subtask(permits_and_preparation, determine_permit_requirements).
subtask(permits_and_preparation, submit_permit_application).
subtask(permits_and_preparation, order_long_lead_items).
subtask(permits_and_preparation, clear_room).
subtask(permits_and_preparation, protect_surrounding_areas).

subtask(demolition, remove_vanity).
subtask(demolition, remove_toilet).
subtask(demolition, remove_tub_or_shower).
subtask(demolition, remove_tile).
subtask(demolition, remove_flooring).
subtask(demolition, remove_drywall_in_wet_areas).

subtask(structural_repair, replace_damaged_studs).
subtask(structural_repair, reinforce_floor_if_needed).
subtask(structural_repair, replace_subfloor).

subtask(rough_plumbing, install_new_supply_lines).
subtask(rough_plumbing, install_drain_lines).
subtask(rough_plumbing, install_shower_valve).
subtask(rough_plumbing, relocate_plumbing_if_layout_changed).

subtask(rough_electrical, install_new_wiring).
subtask(rough_electrical, install_gfci_outlets).
subtask(rough_electrical, install_lighting_boxes).
subtask(rough_electrical, install_exhaust_fan).

subtask(inspection, rough_plumbing_inspection).
subtask(inspection, rough_electrical_inspection).

subtask(wallboard_and_waterproofing, install_cement_backer_board).
subtask(wallboard_and_waterproofing, install_drywall_outside_wet_areas).
subtask(wallboard_and_waterproofing, install_waterproof_membrane).
subtask(wallboard_and_waterproofing, install_shower_pan_or_tub).

subtask(flooring_and_tile, install_floor_tile).
subtask(flooring_and_tile, install_shower_tile).
subtask(flooring_and_tile, install_accent_tile).
subtask(flooring_and_tile, grout_tile).
subtask(flooring_and_tile, seal_grout_if_required).

subtask(fixtures_installation, install_vanity).
subtask(fixtures_installation, install_sink_and_faucet).
subtask(fixtures_installation, install_shower_fixtures).
subtask(fixtures_installation, install_bathtub_or_shower_door).
subtask(fixtures_installation, install_toilet).
subtask(fixtures_installation, install_mirrors).

subtask(electrical_finish, install_lights).
subtask(electrical_finish, install_switches).
subtask(electrical_finish, install_exhaust_fan_cover).
subtask(electrical_finish, install_outlets).

subtask(painting_and_trim, paint_walls_and_ceiling).
subtask(painting_and_trim, install_baseboards).
subtask(painting_and_trim, install_trim).

subtask(accessories, install_mirror).
subtask(accessories, install_towel_bars).
subtask(accessories, install_shelves).
subtask(accessories, install_cabinet_hardware).

subtask(final_checks, check_plumbing_leaks).
subtask(final_checks, test_lighting_and_outlets).
subtask(final_checks, check_fan_airflow).
subtask(final_checks, caulk_edges).

% Dependencies (Task depends on Predecessor)
depends(permits_and_preparation, planning_and_design).
depends(demolition, permits_and_preparation).
depends(structural_repair, demolition).
depends(rough_plumbing, demolition).
depends(rough_electrical, demolition).
depends(inspection, rough_plumbing).
depends(inspection, rough_electrical).
depends(wallboard_and_waterproofing, inspection).  % Or rough if no permit
depends(flooring_and_tile, wallboard_and_waterproofing).
depends(fixtures_installation, flooring_and_tile).
depends(electrical_finish, fixtures_installation).  % Assumes walls ready post-tile
depends(painting_and_trim, wallboard_and_waterproofing).  % Can parallel some finishes
depends(accessories, painting_and_trim).
depends(final_checks, accessories).
depends(final_checks, electrical_finish).

% Conditional tasks (only required if Condition resolved to yes)
conditional_task(structural_repair, damage_found).  % From demo discoveries: mold, rot, etc.

% Decisions and their options (from plan)
decision(keep_layout_or_move_plumbing, [keep, move]).
decision(shower_tub_or_combo, [shower, tub, combo]).
decision(single_or_double_vanity, [single, double]).
decision(tile_floor_vs_vinyl_vs_stone, [tile, vinyl, stone]).
decision(diy_vs_contractor, [diy, contractor]).
decision(permit_or_no_permit, [yes, no]).
decision(partial_demo_or_full_gut, [partial, full]).
decision(move_fixtures, [yes, no]).
decision(upgrade_to_modern_plumbing, [yes, no]).
decision(add_heated_floor, [yes, no]).
decision(add_recessed_lighting, [yes, no]).
decision(upgrade_fan_ventilation, [yes, no]).
decision(waterproofing_method, [membrane, redgard, schluter]).
decision(tile_pattern, [various_patterns]).  % Open-ended
decision(niche_placement, [various_options]).

% Requirements (Task requires resolved(Decision/Condition, _))
requires(rough_plumbing, keep_layout_or_move_plumbing).
requires(rough_plumbing, move_fixtures).
requires(rough_plumbing, upgrade_to_modern_plumbing).
requires(rough_electrical, add_heated_floor).
requires(rough_electrical, add_recessed_lighting).
requires(rough_electrical, upgrade_fan_ventilation).
requires(inspection, permit_or_no_permit).  % Only if yes
requires(wallboard_and_waterproofing, waterproofing_method).
requires(flooring_and_tile, tile_pattern).
requires(flooring_and_tile, niche_placement).
requires(flooring_and_tile, add_heated_floor).  % If added in electrical
requires(demolition, partial_demo_or_full_gut).
requires(structural_repair, damage_found).  % Condition from discoveries

% Rule: Can a task start? (All deps completed, not already done, requirements resolved, condition met if conditional)
can_start(Task) :-
    task(Task),
    \+ completed(Task),
    forall(depends(Task, Dep), completed(Dep)),
    forall(requires(Task, Dec), (resolved(Dec, _))),
    (conditional_task(Task, Cond) -> resolved(Cond, yes) ; true).

% Find all next possible tasks (ready to start)
next_tasks(Next) :-
    findall(Task, can_start(Task), Next).

% Simulate completing a task (update state)
% Usage: simulate_complete(Task).
simulate_complete(Task) :-
    can_start(Task),
    assert(completed(Task)).

% Example queries for execution:
% ?- next_tasks(Next).  % What can start now?
% ?- resolved(damage_found, yes).  % Assume discovery, then assert
% ?- simulate_complete(demolition).  % Advance state
% ?- assert(resolved(permit_or_no_permit, yes)).  % Resolve a decision

% Initial state: No tasks completed, no decisions resolved (simulate from start)
