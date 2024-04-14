# 10001
Calculate the best strategy in the dice game 10000.

## The game
10000 is played with 6 dice and the goal is to be the first person to reach 10.000 points.
On their turn, the player throws 6 dice and looks for "scoring dice".
These are 1, 5, any group of 3 or more of the same dice, or the special rolls three pairs or (1, 2, 3, 4, 5, 6).
The player may choose to keep any amount of scoring dice, but must keep at least one from each throw.
If the player did not roll any scoring dice, they lose their points and their turn ends.
When the player has chosen which dice to keep, they can choose to throw the remaining dice or save their points to their total and end their turn.
If the player keeps all their remaining dice and are left with 0 they may throw all 6 dice while keeping the points accrued in that turn.

At the start of the game, players are not allowed to save their points unless they have accrued at least 1000 points in a single turn (potentially multiple throws).
After the player has saved 1000 points in a single turn, they may end their turn and save their points at any time in future turns.

## Method
We reduce the search space by sorting the dice in each roll, and assigning it a weight based on its probability to come up ((1, 1, 1) is less likely to come up than (1, 2, 3)).
We then consider each possible outcome the player can choose from.

An outcome is described by the points earned and the dice remaining after that choice.
Rolling (1, 5) you have 3 possible outcomes: (50, 1), (100, 1), (150, 6).
We further reduce the search space by considering only the best outcome for each remaining dice count ((100, 1) is clearly better than (50, 1)).
Doing this, different rolls can be treated as equal if they have the same best outcome for each dice count (e.g. (1, 2, 3) and (1, 2, 4)).

Search space reduction from unordered rolls to best outcomes per dice count:
```
Dice: unordered rolls -> ordered rolls -> best outcomes
   1:               6                6 ->             3
   2:              36               21 ->             6
   3:             216               56 ->            14
   4:            1296              126 ->            31
   5:            7776              252 ->            61
   6:           46656              462 ->           119
```

We then compute the expected value for a given (dice count, score) and the chance to reach a given target for a given (dice count, score) using expecti-max with dynamic programming (cached recursion).
The computation for expected value uses an optimization where it records the lowest score at which rolling each dice count gives negative expected value.

## Strategy
Before you have reached 1000 points, you optimize for the probability of reaching 1000 points in your current turn.
This can be done by consulting the table in [results.txt](./results.txt).
After each throw you calculate your best outcome for each remaining dice count, and pick the outcome which gives you the highest chance to reach 1000 this turn.
Note that this optimizes for reaching 1000 points, and not necessarily for expected value or chance to win.
It is probably better to roll again if you have 5 or 6 dice left, even after reaching 1000 points, because of the decent expected value and the low chance of failure.

After reaching 1000 points you optimize for expected value by consulting the table in [results.txt](./results.txt).
This is done in a similiar way to the previous table, but you must remember to add the points the outcome gives you to the expected value of the state it brings you to before comparing with other outcomes.
A simplified version of the strategy is provided in the 'Minimum score for negative EV' table, which lists the score at each dice count where you should save your points and end your turn.
Simlifying this even further, you can keep throwing at 5/6 dice at anything below 3000 points, keep throwing at anything below 1000 at 4 dice, and keep throwing below 300-400 at 3/2/1 dice.

Note that this optimizes for expected value, and not chance to win.
If you are far behind/ahead of your opponent it may be better to play slightly riskier/safer.
If you are playing against many opponents, it may be better to play riskier, as you may need to perform better than the optimal expected value to win.
