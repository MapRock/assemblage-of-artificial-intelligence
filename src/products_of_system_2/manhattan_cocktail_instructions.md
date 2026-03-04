# The Easiest Real Prolog Example: SWI-Prolog

If you want to try a simple working Prolog example, the easiest path is to use **SWI-Prolog**, the most widely used modern Prolog implementation.

---

## Install SWI-Prolog

Download and install it like any normal program:

https://www.swi-prolog.org

After installation you will have access to the `swipl` command-line interpreter.

---

# Example: A Manhattan Cocktail Recipe

This simple example demonstrates how Prolog can assemble a recipe by combining facts and rules.

The logic is split into two files:

- `manhattan_options.pl`
- `manhattan_recipe.pl`

These files already exist in the GitHub repository and can be referenced directly.

---

## File: `manhattan_options.pl`

This file defines the **ingredients and configuration facts** for different types of Manhattan cocktails.

See the source file:


---

## File: `manhattan_recipe.pl`

This file defines the **recipe rule** that assembles the steps using the ingredient facts.

See the source file:



---

# Running the Example

Open a terminal and start the Prolog interpreter:

```bash
swipl

?- consult('manhattan_recipe.pl').

?- recipe_steps(classic, Steps).

Steps = [
 add(2,oz,rye_whiskey),
 add(1,oz,sweet_vermouth),
 add(2_3,dashes,angostura_bitters),
 fill_with(ice),
 stir(20_30_seconds),
 strain(into_glass),
 garnish(maraschino_cherry)
].
