import sys
import pygame
import os
from game_class import Game, screen, clock

game = Game(0, 0)  # Create a single game instance with default score and session number

# Main loop
run_game = True
while run_game:

    if game.process_events():
        run_game = False
    game.run_logic()

    game.display_frame(screen)

    clock.tick(60)
pygame.quit()
sys.exit()