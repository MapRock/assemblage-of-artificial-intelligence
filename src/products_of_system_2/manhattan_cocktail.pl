% Facts: the recipe as an ordered list of steps
manhattan_steps([
    add(2, oz, rye_whiskey),
    add(1, oz, sweet_vermouth),
    add(2, dashes, angostura_bitters),  % or 3 dashes – we can vary later
    fill_with(ice),
    stir(20, seconds),                   % or 30
    strain(into(chilled(coupe))),
    garnish(with(cherry))
]).

% The "executor" predicate – recursive traversal
make_cocktail(RecipeName) :-
    recipe_steps(RecipeName, Steps),
    format('Making a ~w:~n', [RecipeName]),
    execute_steps(Steps).

execute_steps([]) :-
    format('~nDone! Enjoy your drink.~n').

execute_steps([Step | Rest]) :-
    describe_step(Step),
    execute_steps(Rest).

% Human-readable description for each kind of step
describe_step(add(Amount, Unit, Ingredient)) :-
    format('  - Add ~w ~w of ~w~n', [Amount, Unit, Ingredient]).

describe_step(fill_with(ice)) :-
    format('  - Fill the mixing glass with ice~n').

describe_step(stir(Time, seconds)) :-
    format('  - Stir for ~w seconds~n', [Time]).

describe_step(strain(into(chilled(Glass)))) :-
    format('  - Strain into a chilled ~w glass~n', [Glass]).

describe_step(garnish(with(Item))) :-
    format('  - Garnish with a ~w~n', [Item]).

% Entry point: define which recipe to use
recipe_steps(manhattan, Steps) :- manhattan_steps(Steps).
