from player import Player


def run_simulation_1vs1(p1, p2, tick_ms):
    """
    Prints in STDOUT what is going on per tick. Prints finally the winner (or if stalemate, then that).

    :param p1: Player 1. Acts (shoots) first but damage-taken calculations are performed after both players have acted.
    :param p2: Player 2. Receives damage first, but this is after both have finished their action per tick.
    :param tick_ms: Similar to "tickrate". The number of milliseconds it takes to complete a single tick. 1000/tickrate
    :return: None.
    """
    tick_count = 0
    while p1.hp > 0 and p2.hp > 0:
        print("[{} ms tick]".format(tick_count * tick_ms))
        # Let both perform their action
        dmg_to_p2 = p1.fight(p2, tick_ms)  # Can be 0 if action is medpack/skill
        dmg_to_p1 = p2.fight(p1, tick_ms)
        # Calculate damage taken separate from action, so it doesn't interfere with action within a single tick
        p2.take_dmg(dmg_to_p2)
        p1.take_dmg(dmg_to_p1)
        tick_count += 1

    winner = p1 if p1.hp > 0 else p2 if p2.hp > 0 else None
    if winner:
        print("{} won, having {}HP ({}%) in the end.".format(winner.name, winner.hp, winner.hp/winner.max_hp))
    else:
        print("Stalemate. {} {}HP, {} {}HP".format(p1.name, p1.hp, p2.name, p2.hp))


def main():
    player_1 = Player("Player 1", None, None, {}, None, None)
    player_2 = Player("Player 2", None, None, {}, None, None)
    run_simulation_1vs1(player_1, player_2, 350)


if __name__ == "__main__":
    main()
