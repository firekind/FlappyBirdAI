from game import GameState

if __name__ == "__main__":
    game_state = GameState()
    running = True

    while running:
        res = game_state.step()
        running = res['running']
