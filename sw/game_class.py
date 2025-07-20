# main.py

import os
import pygame

# Screen constants - defines the game window size
SCREEN_SIZE = (800, 600)  # Width: 800px, Height: 600px
size = [SCREEN_SIZE[0], SCREEN_SIZE[1]]
screen = pygame.display.set_mode(size)  # Create the game window

# Defined colors for usage - RGB color values
WHITE = (255, 255, 255)  # White background color
BLACK = (0, 0, 0)        # Black text color
BLUE = (0, 100, 200)     # Blue background color
CLOUD_GRAY = (180, 180, 180)  # Gray color for transparent clouds

# Miscellaneous variables
clock = pygame.time.Clock()  # Controls game frame rate

class Game(object):
    def __init__(self, score=0, session_number=0):
        # Constructor. Create and initialize all attributes
        self.score = score                    # Player's current score
        self.session_number = session_number  # Number of games played
        self.game_active = False             # Flag to track if game is currently running
        self.cloud_offset = 0                # Offset for cloud movement animation
        pygame.init()                        # Initialize pygame modules
        pygame.mouse.set_visible(False)      # Hide mouse cursor during gameplay
        pygame.display.set_caption('PyShoot') # Set window title

    """ Main game play class """

    def process_events(self):
        # Handle all user input events (keyboard, mouse, window close)
        for event in pygame.event.get():
            # Check if user wants to close the window
            if event.type == pygame.QUIT:
                print("User asked to quit.")
                return True  # Signal to exit the game loop
            
            # Handle space bar key press (down)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                print("User pressed the space bar")
            
            # Handle key releases
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    print("User let go of the space bar key")
                    # Start game only if it's not already active
                    if not self.game_active:
                        self.session_number += 1  # Increment game session
                        self.game_active = True   # Activate the game
                        print('')
                elif event.key == pygame.K_l:
                    print("Lose Game!")
                    self.game_active = False  # End the current game
            
            # Handle mouse button clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button (1=left, 2=middle, 3=right)
                    print("User clicked left mouse button")
                    # Start game only if it's not already active
                    if not self.game_active:
                        self.session_number += 1  # Increment game session
                        self.game_active = True   # Activate the game
                        print('Game started with mouse click')

        return False  # Continue running the game

    def run_logic(self):
        # Execute game logic only when the game is active
        if self.game_active:
            self.begin_game()  # Run the main game logic

    def display_frame(self, screen):
        # Clear screen and draw all visual elements
        screen.fill(BLUE)  # Fill screen with blue background
        
        # Draw clouds on the background for all screens
        self.draw_clouds(screen)
        
        # Display different screens based on game state
        if not self.game_active:
            # Game is not running - show menu screens
            if self.session_number >= 1:
                self.game_over_screen(screen)  # Show game over if we've played before
            else:
                self.title_screen(screen)      # Show title screen for first time
        else:
            # Game is running - show the character and gameplay
            self.user_character(screen)
        
        # Always show debug information in top-left corner
        self.user_debug_display(screen)
        pygame.display.flip()  # Update the display with all drawn elements

    def begin_game(self):
        # Main gameplay logic goes here (currently just a placeholder)
        print('Begin game now')
        
        # Update cloud animation - make clouds move downward smoothly
        self.cloud_offset += 0.5  # Move clouds down by 0.5 pixels per frame for smoother movement

    def game_over_screen(self, screen):
        # Display the game over screen with restart instructions
        print('game over')
        
        # Create fonts for different text sizes
        game_over = pygame.font.SysFont("serif", 25)   # Larger font for main text
        click_enter = pygame.font.SysFont("serif", 15) # Smaller font for instructions
        
        # Render text surfaces with black color
        main_text = game_over.render("Game Over", True, BLACK)
        sub_text = click_enter.render("(Press space or click to play again)", True, BLACK)
        
        # Calculate center position for main text
        center_x = (SCREEN_SIZE[0] // 2) - (main_text.get_width() // 2)
        center_y = (SCREEN_SIZE[1] // 2) - (main_text.get_height() // 2)
        screen.blit(main_text, [center_x, center_y])  # Draw main text
        
        # Calculate center position for sub text (20 pixels below main text)
        center_x = (SCREEN_SIZE[0] // 2) - (sub_text.get_width() // 2)
        center_y = (SCREEN_SIZE[1] // 2) - (sub_text.get_height() // 2 - 20)
        screen.blit(sub_text, [center_x, center_y])   # Draw instruction text

    def title_screen(self, screen):
        # Display the initial title screen with play instructions
        print('title screen')
        
        # Create font for the title text
        new_begin = pygame.font.SysFont("serif", 35)
        begin_text = new_begin.render("Press space or click to play", True, BLACK)
        
        # Calculate center position for the text
        center_x = (SCREEN_SIZE[0] // 2) - (begin_text.get_width() // 2)
        center_y = (SCREEN_SIZE[1] // 2) - (begin_text.get_height() // 2)
        screen.blit(begin_text, [center_x, center_y])  # Draw the text

    def user_debug_display(self, screen):
        # Display debug information in the top-left corner
        info = pygame.font.SysFont("serif", 15)  # Small font for debug text
        
        # Display frames per second (FPS) - shows game performance
        screen.blit(info.render("FPS: " + str(clock.get_fps())[:2], True, BLACK), [0, 0])
        
        # Display session number - how many games have been played
        screen.blit(info.render("S#: " + str(self.session_number)[:2], True, BLACK), [0, 15])
        
        # Display current score
        screen.blit(info.render("Score: " + str(self.score)[:2], True, BLACK), [0, 30])
        
    def user_character(self, screen):
        # Display the player's character (aircraft) that follows the mouse
        
        # Get current mouse position
        mx, my = pygame.mouse.get_pos()
    
        # Load the aircraft image from the resources folder
        file_path = os.path.realpath('./res/aircrafts/images/aircraft_1.png')
        alpha_image_surface = pygame.image.load(file_path).convert_alpha()  # Load with transparency
        
        # Draw the aircraft at the mouse position
        screen.blit(alpha_image_surface, (mx, my))

    def draw_clouds(self, screen):
        # Draw clouds with smooth scrolling animation
        import random
        
        # Set seed for consistent cloud positions
        random.seed(42)
        
        # Base cloud positions - designed for seamless wrapping
        base_cloud_positions = [
            (100, -100), (300, -150), (500, -50), (650, -120),
            (150, 50), (400, 30), (600, 70), (50, 10),
            (250, 150), (480, 170), (700, 130), (80, 200),
            (350, 250), (550, 270), (150, 330), (450, 300),
            (200, 400), (600, 450), (400, 480), (100, 520),
            (500, 550), (300, 600), (700, 580), (50, 650)
        ]
        
        # Cloud pattern repeats every 800 pixels vertically
        pattern_height = 800
        
        # Draw enough cloud layers to cover screen + buffer
        for base_x, base_y in base_cloud_positions:
            # Calculate current position with smooth scrolling
            current_y = (base_y + self.cloud_offset) % pattern_height
            
            # Draw cloud if it's in or near the visible area
            if current_y > -100 and current_y < SCREEN_SIZE[1] + 100:
                self.draw_single_cloud(screen, base_x, current_y)
            
            # Draw the cloud again at the wrapped position for seamless transition
            wrapped_y = current_y - pattern_height
            if wrapped_y > -100 and wrapped_y < SCREEN_SIZE[1] + 100:
                self.draw_single_cloud(screen, base_x, wrapped_y)
    
    def draw_single_cloud(self, screen, x, y):
        # Draw a single transparent gray cloud made of overlapping circles
        # Create a temporary surface for transparency
        cloud_surface = pygame.Surface((100, 60), pygame.SRCALPHA)  # Surface with alpha channel
        
        # Draw cloud circles on the temporary surface with transparency
        # Main cloud body (larger circles) - alpha value of 120 (out of 255) for transparency
        pygame.draw.circle(cloud_surface, (*CLOUD_GRAY, 120), (25, 30), 25)
        pygame.draw.circle(cloud_surface, (*CLOUD_GRAY, 120), (45, 30), 30)
        pygame.draw.circle(cloud_surface, (*CLOUD_GRAY, 120), (65, 35), 25)
        pygame.draw.circle(cloud_surface, (*CLOUD_GRAY, 120), (80, 30), 20)
        
        # Additional smaller circles for cloud detail
        pygame.draw.circle(cloud_surface, (*CLOUD_GRAY, 120), (35, 20), 18)
        pygame.draw.circle(cloud_surface, (*CLOUD_GRAY, 120), (60, 22), 22)
        pygame.draw.circle(cloud_surface, (*CLOUD_GRAY, 120), (70, 45), 15)
        
        # Blit the transparent cloud surface to the main screen
        screen.blit(cloud_surface, (x - 25, y - 30))