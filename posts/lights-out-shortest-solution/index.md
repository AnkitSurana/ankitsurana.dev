Lights Out is a grid of lights. Press one and it toggles, along with its neighbours. Clear the board and you win. NoByte's version has a hint button, and a hint is only useful if it points at a good move, not just a move that is technically part of some winning sequence.

The solver treats the board as linear algebra over GF(2), the integers mod 2. Every cell is an equation, every possible press is an unknown, and toggling is addition mod 2, because pressing the same button twice is the same as never pressing it. Gaussian elimination solves the system. If a row reduces to zero on the left and one on the right, the board cannot be cleared, and the hint button knows to stay quiet.

## What actually happened

The first solver cleared every board I threw at it, so I shipped it and used the hint myself while testing other things. It kept suggesting presses that felt like detours. The board got solved, but the route was longer than the one I could see by eye.

The reason is that a solved board does not have one solution. The 5 by 5 system has a null space of dimension four, which means once you have any solution you can add any of sixteen "quiet" press patterns, presses that cancel out and leave the board unchanged, and still clear it. Sixteen valid answers, all correct, most of them longer than they need to be. Gaussian elimination hands you one of the sixteen, whichever falls out of the arithmetic, and it has no reason to be the shortest.

> Solvable and solved-well are different properties. The linear algebra guarantees the first for free. The second you have to go and ask for.

## The fix

Enumerate the null space and pick the best member. There are only sixteen candidates, which is nothing to a computer, so the solver takes its one arithmetic solution, adds each of the sixteen quiet patterns in turn, and keeps whichever result needs the fewest presses. That is the one the hint shows.

The payoff is that a hint now sits on a shortest path, not merely a legal one. Press what it suggests and the number of moves left drops by a sensible amount, instead of sending you on a scenic loop that happens to end at a cleared board.

## The bit worth keeping

I nearly left it, because "the solver works" was true and the tests were green. They checked that a solution clears the board, which every one of the sixteen does. What they did not check was that it was the shortest, and once I added that assertion the naive solver failed it on exactly the boards where the difference mattered.

Correct was easy. The maths gives you correct for nothing. Good took a second question I had not thought to ask.
