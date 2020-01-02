from game import GameState
import numpy as np

if __name__ == "__main__":
    game_state = GameState()
    running = True

    while running:
        actions = np.zeros(2)
        actions[int(input())] = 1
        res = game_state.step(actions)
        running = bool(res)
