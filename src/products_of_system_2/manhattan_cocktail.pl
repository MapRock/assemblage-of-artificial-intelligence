manhattan_type(classic).
manhattan_type(dry).
manhattan_type(perfect).

vermouth_for(classic, sweet_vermouth).
vermouth_for(dry, dry_vermouth).
vermouth_for(perfect, half_sweet_half_dry).

base_for_manhattan(rye_whiskey).

bitters_for_manhattan(angostura_bitters).

garnish_for_manhattan(maraschino_cherry).

% Copy manhattan_options.pl and manhattan_cocktail.pl to c:/temp/.

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
