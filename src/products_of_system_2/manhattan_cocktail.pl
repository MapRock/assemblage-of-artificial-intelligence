% Copy manhattan_options.pl and manhattan_cocktail.pl to c:/temp/.
:- consult('c:/temp/manhattan_options.pl').

recipe_steps(Type, Steps) :-
    base_for_manhattan(Base),
    vermouth_for(Type, Vermouth),
    bitters_for_manhattan(Bitters),
    garnish_for_manhattan(Garnish),

    Steps = [
        add(2, oz, Base),
        add(1, oz, Vermouth),
        add('2-3', dashes, Bitters),
        fill_with(ice),
        stir('20-30_seconds'),
        strain(into_glass),
        garnish(Garnish)

    ].
