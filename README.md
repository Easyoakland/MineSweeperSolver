- This project solves minesweeper. It's setup to solve minesweeper from the `Minesweeper.html` webpage in the git repo or from `minesweeperonline.com/`, however, it can be setup to solve any minesweeper program as long as the .png files are replaced. It's expected that all images for tile/cell types are the same image size and correctly named.
- In the `functions.py` file there are some configuration options.
    - `timeoutAttemptsNum` controls how long the program is willing to rescan the page for an update. This exists because sometimes the board is screenshotted to be analyzed before the board updates.
    - `maxCombinations` controls how many combinations/permutations the probabilistic guess method is willing to go through before giving up and using a less accurate but quicker guess method instead.
- The `FailedGameStates.txt` file keeps track of good reference board states for testing and improving the program.

![Demo gif](./demo.gif)