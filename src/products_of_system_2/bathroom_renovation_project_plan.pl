% --------------------------------
% TASK DEFINITIONS
% --------------------------------

task(plan_design).
task(get_permits).
task(order_materials).
task(prepare_site).

task(demolition).

task(structural_repair).
task(rough_plumbing).
task(rough_electrical).

task(inspection).

task(wallboard).
task(waterproofing).

task(tile_work).

task(install_fixtures).
task(electrical_finish).

task(paint_trim).
task(accessories).

task(final_checks).

% --------------------------------
% DEPENDENCIES
% depends(Task, RequiredTask)
% --------------------------------

depends(get_permits, plan_design).
depends(order_materials, plan_design).
depends(prepare_site, order_materials).

depends(demolition, prepare_site).

depends(structural_repair, demolition).
depends(rough_plumbing, demolition).
depends(rough_electrical, demolition).

depends(inspection, rough_plumbing).
depends(inspection, rough_electrical).

depends(wallboard, inspection).
depends(waterproofing, wallboard).

depends(tile_work, waterproofing).

depends(install_fixtures, tile_work).

depends(electrical_finish, install_fixtures).

depends(paint_trim, electrical_finish).

depends(accessories, paint_trim).

depends(final_checks, accessories).

% --------------------------------
% DECISIONS
% --------------------------------

decision(move_plumbing).
decision(damage_found).
decision(add_heated_floor).
decision(add_lighting).

requires(structural_repair, damage_found).
requires(rough_plumbing, move_plumbing).
requires(tile_work, add_heated_floor).
requires(rough_electrical, add_lighting).

% --------------------------------
% RULES
% --------------------------------

dependencies_met(Task, Completed) :-
    forall(depends(Task, Dep),
           member(Dep, Completed)).

decision_conditions_met(Task, Decisions) :-
    forall(requires(Task, Decision),
           member(Decision, Decisions)).

not_completed(Task, Completed) :-
    \+ member(Task, Completed).

can_start(Task, Completed, Decisions) :-
    task(Task),
    not_completed(Task, Completed),
    dependencies_met(Task, Completed),
    decision_conditions_met(Task, Decisions).

% --------------------------------
% FIND NEXT POSSIBLE TASKS
% --------------------------------

next_tasks(Completed, Decisions, Tasks) :-
    findall(Task,
        can_start(Task, Completed, Decisions),
        Tasks).

% --------------------------------
% PROJECT SIMULATION
% --------------------------------

simulate_project(Decisions, Plan) :-
    simulate([], Decisions, Plan).

simulate(Completed, Decisions, []) :-
    next_tasks(Completed, Decisions, []).

simulate(Completed, Decisions, [Task|Rest]) :-
    can_start(Task, Completed, Decisions),
    simulate([Task|Completed], Decisions, Rest).
