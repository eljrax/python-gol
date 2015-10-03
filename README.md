![Demo](/demo.gif?raw=true "Demo")

Simple ncurses based game-of-life implementation of 
[Conway's Game Of Life](https://en.wikipedia.org/wiki/Conway's_Game_of_Life)

Keys:  
'q' quits the program  
'p' pauses the loop  
'+' speeds up the animation  
'-' slows it down  
Enter or Space at any time stops the current grid and restarts with a new one

It wraps borders both horizontally and vertically, and detects true
equilibrium as well as 'constant change' (oscillators) and offers to
re-seed the grid accordingly.

You can give a percentage of cells that should be marked as alive initially
as an argument to this program.
For example:

./gol.py 10

On your average 16:9 monitor, I find a 10% seed yields the most visually
satisfying result.

