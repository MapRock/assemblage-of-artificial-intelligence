# SWI-Prolog Tutorial: Bathroom Renovation Project Planner  
*(All-in-One Single File Version)*

This file contains **everything** you need: explanation, full Prolog code, setup steps, interactive queries, and simulation examples.

Goal: Model a bathroom renovation as a dynamic, dependency-aware project plan in Prolog.  
You describe tasks, dependencies, decisions, and conditions → Prolog tells you **what can start next**, handles branches, and simulates progress.

## Why this approach?
- Declarative: Define **what** must happen and **when** — Prolog figures out the order and conditions.
- Dynamic: Use `assert`/`retract` to simulate decisions and completions.
- Interactive: Great for exploring "what if I change the layout?" or "what if we find mold?"

## Step 1: Install SWI-Prolog (if needed)

- Download: https://www.swi-prolog.org
- Install for Windows / macOS / Linux
- Test: open terminal → type `swipl` → see `?-` prompt

(Quick no-install option: https://swish.swi-prolog.org — paste code there)

## Step 2: The Complete Prolog Code (bathroom_renovation_project.pl)

Download bathroom_renovation_project.pl

## Step 3: Load and Play (Interactive Session)Start SWI-Prolog:

swipl

Load the file:

?- [bathroom_renovation_project.pl].     % or consult('bathroom_renovation_project.pl').

Start exploring:Initial state – what's ready?

?- next_tasks(Next).

→ Next = [planning_and_design]Complete first phase

?- simulate_complete(planning_and_design).

Now what's next?

?- next_tasks(Next).

Make decisions

?- assert(resolved(keep_layout_or_move_plumbing, keep)).
?- assert(resolved(permit_or_no_permit, yes)).
?- assert(resolved(damage_found, yes)).     % e.g., found rot during demo

Advance further

?- simulate_complete(permits_and_preparation).
?- simulate_complete(demolition).
?- next_tasks(Next).      % → structural_repair + rough_plumbing + rough_electrical (if conditions met)

Quick Reference QueriesSee completed tasks:
?- findall(T, completed(T), Done).
See decisions made:
?- resolved(Dec, Choice).
Reset simulation:
?- retractall(completed(_)), retractall(resolved(_,_)).
List tasks that require decisions:
?- requires(Task, Dec).
Why can't a task start? (negation example)
?- task(Task), \+ can_start(Task).

Extensions You Can Add

