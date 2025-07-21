# main.py

import os
import pygame
import random

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
        
        # Firing system attributes
        self.is_firing = False               # Flag to track if currently firing
        self.muzzle_flash_frame = 0          # Current frame of muzzle flash animation
        self.muzzle_flash_duration = 8       # How long muzzle flash lasts (frames)
        self.bullets = []                    # List to store active bullets
        self.fire_cooldown = 0               # Cooldown between shots
        self.fire_rate = 5                   # Minimum frames between shots (reduced for faster firing)
        self.mouse_held = False              # Flag to track if mouse button is held down
        
        # Rocket firing system attributes
        self.is_rocket_firing = False        # Flag to track if currently rocket firing
        self.rocket_flash_frame = 0          # Current frame of rocket flash animation
        self.rocket_flash_duration = 8       # How long rocket flash lasts (frames)
        self.rockets = []                    # List to store active rockets
        self.rocket_fire_cooldown = 0        # Cooldown between rocket shots
        self.rocket_fire_rate = 7            # 30% slower than bullets (5 * 1.3 = 6.5, rounded to 7)
        self.right_mouse_held = False        # Flag to track if right mouse button is held down
        
        # Game state attributes
        self.game_started = False            # Flag to track if begin_game has been called for this session
        self.game_paused = False             # Flag to track if game is paused
        self.upgrade_available = False       # Flag to track if upgrade menu should be shown
        self.last_upgrade_score = 0          # Track the last score when upgrade was offered
        
        # Weapon upgrade system
        self.left_weapon_level = 1           # Left click weapon level (bullets)
        self.right_weapon_level = 1          # Right click weapon level (rockets)
        self.upgrade_threshold = 200         # Points needed for first upgrade
        
        # Enemy system attributes
        self.enemies = []                    # List to store active enemies
        self.max_enemies = 10               # Maximum number of enemies on screen at once
        self.enemy_spawn_cooldown = 0       # Cooldown between enemy spawns
        self.enemy_spawn_rate = 60          # Frames between enemy spawns (1 second at 60 FPS)
        self.enemy_health = 6               # Enemy health (6 for bullets=4 hits, rockets=3 hits with 2 damage each)
        self.enemy_sprites = [              # List of available enemy sprite names
            'C1.png', 'C2.png', 'C3.png', 'C4.png', 'C5.png', 'C6.png', 'C7.png', 'C8.png', 'C9.png',
            'C10.png', 'C11.png', 'C12.png', 'C13.png', 'C14.png', 'C15.png', 'C16.png', 'C17.png', 'C18.png'
        ]
        
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
                # Fire weapon if game is active and not paused
                if self.game_active and not self.game_paused:
                    self.fire_weapon()
            
            # Handle ESC key press - exit to main menu
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print("User pressed ESC - returning to main menu")
                if self.game_active:
                    self.game_active = False  # Exit to main menu
                    # Reset game state
                    self.mouse_held = False
                    self.right_mouse_held = False
                    self.is_firing = False
                    self.is_rocket_firing = False
                    self.game_paused = False  # Reset pause state
            
            # Handle P key press - toggle pause
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                if self.game_active:
                    self.game_paused = not self.game_paused  # Toggle pause state
                    if self.game_paused:
                        print("Game paused")
                        # Stop continuous firing when pausing
                        self.mouse_held = False
                        self.right_mouse_held = False
                    else:
                        print("Game unpaused")
            
            # Handle upgrade selection
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                if self.upgrade_available:
                    self.upgrade_left_weapon()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                if self.upgrade_available:
                    self.upgrade_right_weapon()
            
            # Handle key releases
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    print("User let go of the space bar key")
                    # Start game only if it's not already active
                    if not self.game_active:
                        self.session_number += 1  # Increment game session
                        self.game_active = True   # Activate the game
                        self.game_started = False # Reset game started flag for new session
                        print('')
                elif event.key == pygame.K_l:
                    print("Lose Game!")
                    self.game_active = False  # End the current game
            
            # Handle mouse button clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button (1=left, 2=middle, 3=right)
                    print("User clicked left mouse button")
                    if self.game_active and not self.game_paused:
                        # Set mouse held flag for continuous firing
                        self.mouse_held = True
                        # Fire weapon immediately
                        self.fire_weapon()
                    elif not self.game_active:
                        # Start game only if it's not already active
                        self.session_number += 1  # Increment game session
                        self.game_active = True   # Activate the game
                        self.game_started = False # Reset game started flag for new session
                        print('Game started with mouse click')
                elif event.button == 3:  # Right mouse button
                    print("User clicked right mouse button")
                    if self.game_active and not self.game_paused:
                        # Set right mouse held flag for continuous rocket firing
                        self.right_mouse_held = True
                        # Fire rocket immediately
                        self.fire_rocket()
            
            # Handle mouse button releases
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button released
                    print("User released left mouse button")
                    self.mouse_held = False  # Stop continuous firing
                elif event.button == 3:  # Right mouse button released
                    print("User released right mouse button")
                    self.right_mouse_held = False  # Stop continuous rocket firing

        return False  # Continue running the game

    def run_logic(self):
        # Execute game logic only when the game is active and not paused
        if self.game_active and not self.game_paused:
            # Call begin_game only once when the game starts
            if not self.game_started:
                self.begin_game()  # Run the main game initialization
                self.game_started = True  # Mark game as started
            
            # Handle continuous firing while mouse is held
            if self.mouse_held and self.fire_cooldown <= 0:
                self.fire_weapon()
            
            # Handle continuous rocket firing while right mouse is held
            if self.right_mouse_held and self.rocket_fire_cooldown <= 0:
                self.fire_rocket()
            
            # Update bullet positions
            self.update_bullets()
            
            # Update rocket positions
            self.update_rockets()
            
            # Update enemy positions and spawn new enemies
            self.update_enemies()
            self.spawn_enemies()
            
            # Check for bullet-enemy collisions
            self.check_bullet_enemy_collisions()
            
            # Check for rocket-enemy collisions
            self.check_rocket_enemy_collisions()
            
            # Check for upgrade availability
            self.check_upgrade_availability()
            
            # Update muzzle flash animation
            self.update_muzzle_flash()
            
            # Update rocket flash animation
            self.update_rocket_flash()
            
            # Update fire cooldowns
            if self.fire_cooldown > 0:
                self.fire_cooldown -= 1
            if self.rocket_fire_cooldown > 0:
                self.rocket_fire_cooldown -= 1
            if self.enemy_spawn_cooldown > 0:
                self.enemy_spawn_cooldown -= 1
            
            # Update cloud animation - make clouds move downward smoothly
            self.cloud_offset += 0.5  # Move clouds down by 0.5 pixels per frame for smoother movement

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
        elif self.game_paused:
            # Game is paused - show pause screen
            self.user_character(screen)        # Keep showing the game state
            self.pause_screen(screen)          # Overlay pause menu
        elif self.upgrade_available:
            # Upgrade menu is active - show upgrade screen
            self.user_character(screen)        # Keep showing the game state
            self.upgrade_screen(screen)        # Overlay upgrade menu
        else:
            # Game is running - show the character and gameplay
            self.user_character(screen)
        
        # Always show debug information in top-left corner
        self.user_debug_display(screen)
        pygame.display.flip()  # Update the display with all drawn elements

    def begin_game(self):
        # Game initialization logic - runs only once when game starts
        print('Game initialized!')
        
        # Clear any existing projectiles from previous sessions
        self.bullets = []
        self.rockets = []
        self.enemies = []
        
        # Reset firing states
        self.is_firing = False
        self.is_rocket_firing = False
        self.mouse_held = False
        self.right_mouse_held = False
        
        # Reset cooldowns
        self.fire_cooldown = 0
        self.rocket_fire_cooldown = 0

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
        
        # Create fonts for different text sizes
        title_font = pygame.font.SysFont("serif", 35)
        instruction_font = pygame.font.SysFont("serif", 20)
        controls_font = pygame.font.SysFont("serif", 16)
        
        # Render text surfaces
        title_text = title_font.render("PyShoot", True, BLACK)
        start_text = instruction_font.render("Press space or click to play", True, BLACK)
        
        # Control instructions
        left_click_text = controls_font.render("Left Click: Fire bullets (fast, 4 hits to destroy)", True, BLACK)
        right_click_text = controls_font.render("Right Click: Fire rockets (slow, 3 hits to destroy)", True, BLACK)
        move_text = controls_font.render("Mouse: Move character", True, BLACK)
        pause_text = controls_font.render("P: Pause game | ESC: Main menu", True, BLACK)
        
        # Calculate positions - center everything vertically with proper spacing
        screen_center_x = SCREEN_SIZE[0] // 2
        screen_center_y = SCREEN_SIZE[1] // 2
        
        # Title position
        title_x = screen_center_x - (title_text.get_width() // 2)
        title_y = screen_center_y - 100
        screen.blit(title_text, [title_x, title_y])
        
        # Start instruction
        start_x = screen_center_x - (start_text.get_width() // 2)
        start_y = title_y + title_text.get_height() + 20
        screen.blit(start_text, [start_x, start_y])
        
        # Control instructions - positioned below start text
        controls_start_y = start_y + start_text.get_height() + 30
        
        # Left click instruction
        left_x = screen_center_x - (left_click_text.get_width() // 2)
        screen.blit(left_click_text, [left_x, controls_start_y])
        
        # Right click instruction
        right_x = screen_center_x - (right_click_text.get_width() // 2)
        screen.blit(right_click_text, [right_x, controls_start_y + 20])
        
        # Movement instruction
        move_x = screen_center_x - (move_text.get_width() // 2)
        screen.blit(move_text, [move_x, controls_start_y + 40])
        
        # Pause instruction
        pause_x = screen_center_x - (pause_text.get_width() // 2)
        screen.blit(pause_text, [pause_x, controls_start_y + 60])

    def pause_screen(self, screen):
        # Display the pause screen overlay
        print('pause screen')
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_SIZE[0], SCREEN_SIZE[1]))
        overlay.set_alpha(128)  # Semi-transparent (0=transparent, 255=opaque)
        overlay.fill(BLACK)     # Black overlay
        screen.blit(overlay, (0, 0))
        
        # Create fonts for different text sizes
        pause_font = pygame.font.SysFont("serif", 50)    # Large font for "PAUSED"
        instruction_font = pygame.font.SysFont("serif", 25)  # Medium font for instructions
        
        # Render text surfaces with white color for visibility on dark overlay
        pause_text = pause_font.render("PAUSED", True, WHITE)
        resume_text = instruction_font.render("Press P to resume", True, WHITE)
        menu_text = instruction_font.render("Press ESC for main menu", True, WHITE)
        
        # Calculate center positions for text
        # Main "PAUSED" text
        pause_x = (SCREEN_SIZE[0] // 2) - (pause_text.get_width() // 2)
        pause_y = (SCREEN_SIZE[1] // 2) - (pause_text.get_height() // 2) - 40
        screen.blit(pause_text, [pause_x, pause_y])
        
        # Resume instruction
        resume_x = (SCREEN_SIZE[0] // 2) - (resume_text.get_width() // 2)
        resume_y = pause_y + pause_text.get_height() + 20
        screen.blit(resume_text, [resume_x, resume_y])
        
        # Menu instruction
        menu_x = (SCREEN_SIZE[0] // 2) - (menu_text.get_width() // 2)
        menu_y = resume_y + resume_text.get_height() + 10
        screen.blit(menu_text, [menu_x, menu_y])

    def user_debug_display(self, screen):
        # Display debug information in the top-left corner
        info = pygame.font.SysFont("serif", 15)  # Small font for debug text
        
        # Display frames per second (FPS) - shows game performance
        screen.blit(info.render("FPS: " + str(clock.get_fps())[:2], True, BLACK), [0, 0])
        
        # Display session number - how many games have been played
        screen.blit(info.render("S#: " + str(self.session_number)[:2], True, BLACK), [0, 15])
        
        # Display current score
        screen.blit(info.render("Score: " + str(self.score)[:2], True, BLACK), [0, 30])
        
        # Display weapon levels
        screen.blit(info.render("L.Gun: L" + str(self.left_weapon_level), True, BLACK), [0, 45])
        screen.blit(info.render("R.Gun: L" + str(self.right_weapon_level), True, BLACK), [0, 60])
        
    def user_character(self, screen):
        # Display the player's character (aircraft) that follows the mouse
        
        # Get constrained mouse position
        mx, my = self.get_constrained_position()
    
        # Load the aircraft image from the resources folder - use path relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, '..', 'res', 'aircrafts', 'images', 'aircraft_1.png')
        alpha_image_surface = pygame.image.load(file_path).convert_alpha()  # Load with transparency
        
        # Draw the aircraft at the constrained position
        screen.blit(alpha_image_surface, (mx, my))
        
        # Draw muzzle flash if firing
        if self.is_firing:
            self.draw_muzzle_flash(screen, mx, my)
        
        # Draw rocket flash if rocket firing
        if self.is_rocket_firing:
            self.draw_rocket_flash(screen, mx, my)
        
        # Draw bullets
        self.draw_bullets(screen)
        
        # Draw rockets
        self.draw_rockets(screen)
        
        # Draw enemies
        self.draw_enemies(screen)

    def draw_clouds(self, screen):
        # Draw clouds with smooth scrolling animation
        # Use predefined cloud positions instead of random generation to avoid affecting other random calls
        
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
    
    def get_constrained_position(self):
        # Get mouse position constrained to screen boundaries
        mx, my = pygame.mouse.get_pos()
        
        # Load aircraft image to get dimensions (could be optimized by caching)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, '..', 'res', 'aircrafts', 'images', 'aircraft_1.png')
        try:
            alpha_image_surface = pygame.image.load(file_path).convert_alpha()
            aircraft_width = alpha_image_surface.get_width()
            aircraft_height = alpha_image_surface.get_height()
        except:
            # Fallback dimensions if image can't be loaded
            aircraft_width = 50
            aircraft_height = 50
        
        # Apply screen boundaries - keep aircraft fully within screen
        mx = max(0, min(mx, SCREEN_SIZE[0] - aircraft_width))
        my = max(0, min(my, SCREEN_SIZE[1] - aircraft_height))
        
        return mx, my
    
    def fire_weapon(self):
        # Fire a bullet if cooldown allows
        if self.fire_cooldown <= 0:
            # Get constrained position for bullet spawn location
            mx, my = self.get_constrained_position()
            
            # Create a new bullet (x, y, velocity_x, velocity_y)
            # Bullets fire upward from the aircraft position
            bullet = {
                'x': mx + 25,  # Center of aircraft (assuming aircraft width ~50px)
                'y': my,       # Top of aircraft
                'speed': 8 + (self.left_weapon_level - 1) * 2  # Bullet speed increases with level
            }
            
            self.bullets.append(bullet)
            
            # Start muzzle flash animation
            self.is_firing = True
            self.muzzle_flash_frame = 0
            
            # Set cooldown (faster firing at higher levels)
            base_fire_rate = max(2, self.fire_rate - (self.left_weapon_level - 1))
            self.fire_cooldown = base_fire_rate
            
            print(f"Fired bullet at ({mx}, {my})")
    
    def update_bullets(self):
        # Update bullet positions and remove bullets that are off-screen
        bullets_to_remove = []
        
        for i, bullet in enumerate(self.bullets):
            # Move bullet upward
            bullet['y'] -= bullet['speed']
            
            # Remove bullets that have gone off the top of the screen
            if bullet['y'] < -10:
                bullets_to_remove.append(i)
        
        # Remove bullets in reverse order to maintain correct indices
        for i in reversed(bullets_to_remove):
            del self.bullets[i]
    
    def update_muzzle_flash(self):
        # Update muzzle flash animation
        if self.is_firing:
            self.muzzle_flash_frame += 1
            
            # End muzzle flash after duration
            if self.muzzle_flash_frame >= self.muzzle_flash_duration:
                self.is_firing = False
                self.muzzle_flash_frame = 0
    
    def draw_muzzle_flash(self, screen, aircraft_x, aircraft_y):
        # Draw animated muzzle flash
        if self.is_firing and self.muzzle_flash_frame < self.muzzle_flash_duration:
            # Calculate which muzzle flash image to show
            # We have 24 frames (0-23), cycle through them quickly
            frame_index = (self.muzzle_flash_frame * 3) % 24  # Speed up animation
            
            # Load the muzzle flash image
            script_dir = os.path.dirname(os.path.abspath(__file__))
            muzzle_file = os.path.join(script_dir, '..', 'res', 'explosions', 'images', 'muzzle', f'muzzle2_{frame_index:04d}.png')
            
            try:
                muzzle_surface = pygame.image.load(muzzle_file).convert_alpha()
                
                # Position muzzle flash at the front of the aircraft
                muzzle_x = aircraft_x + 25 - (muzzle_surface.get_width() // 2)  # Center horizontally
                muzzle_y = aircraft_y - 10  # Slightly ahead of aircraft
                
                screen.blit(muzzle_surface, (muzzle_x, muzzle_y))
            except pygame.error:
                # If image fails to load, draw a simple yellow circle as fallback
                pygame.draw.circle(screen, (255, 255, 0), (aircraft_x + 25, aircraft_y), 10)
    
    def draw_bullets(self, screen):
        # Draw all active bullets
        for bullet in self.bullets:
            # Draw bullet as a small yellow circle
            pygame.draw.circle(screen, (255, 255, 0), (int(bullet['x']), int(bullet['y'])), 3)
            # Add a white center for better visibility
            pygame.draw.circle(screen, (255, 255, 255), (int(bullet['x']), int(bullet['y'])), 1)
    
    def fire_rocket(self):
        # Fire a rocket if cooldown allows
        if self.rocket_fire_cooldown <= 0:
            # Get constrained position for rocket spawn location
            mx, my = self.get_constrained_position()
            
            # Create a new rocket (x, y, velocity_x, velocity_y)
            # Rockets fire upward from the aircraft position, larger and slower than bullets
            rocket = {
                'x': mx + 25,  # Center of aircraft (assuming aircraft width ~50px)
                'y': my,       # Top of aircraft
                'speed': 6 + (self.right_weapon_level - 1)  # Rocket speed increases with level
            }
            
            self.rockets.append(rocket)
            
            # Start rocket flash animation
            self.is_rocket_firing = True
            self.rocket_flash_frame = 0
            
            # Set cooldown (faster firing at higher levels)
            base_rocket_rate = max(3, self.rocket_fire_rate - (self.right_weapon_level - 1))
            self.rocket_fire_cooldown = base_rocket_rate
            
            print(f"Fired rocket at ({mx}, {my})")
    
    def update_rockets(self):
        # Update rocket positions and remove rockets that are off-screen
        rockets_to_remove = []
        
        for i, rocket in enumerate(self.rockets):
            # Move rocket upward
            rocket['y'] -= rocket['speed']
            
            # Remove rockets that have gone off the top of the screen
            if rocket['y'] < -10:
                rockets_to_remove.append(i)
        
        # Remove rockets in reverse order to maintain correct indices
        for i in reversed(rockets_to_remove):
            del self.rockets[i]
    
    def update_rocket_flash(self):
        # Update rocket flash animation
        if self.is_rocket_firing:
            self.rocket_flash_frame += 1
            
            # End rocket flash after duration
            if self.rocket_flash_frame >= self.rocket_flash_duration:
                self.is_rocket_firing = False
                self.rocket_flash_frame = 0
    
    def draw_rocket_flash(self, screen, aircraft_x, aircraft_y):
        # Draw animated rocket flame flash
        if self.is_rocket_firing and self.rocket_flash_frame < self.rocket_flash_duration:
            # Calculate which rocket flame image to show
            # We have 16 frames (0-15), cycle through them quickly
            frame_index = (self.rocket_flash_frame * 2) % 16  # Speed up animation
            
            # Load the rocket flame image
            script_dir = os.path.dirname(os.path.abspath(__file__))
            rocket_file = os.path.join(script_dir, '..', 'res', 'explosions', 'images', 'rocket_flame', f'rocket_1_{frame_index:04d}.png')
            
            try:
                rocket_surface = pygame.image.load(rocket_file).convert_alpha()
                
                # Position rocket flame at the front of the aircraft
                rocket_x = aircraft_x + 25 - (rocket_surface.get_width() // 2)  # Center horizontally
                rocket_y = aircraft_y - 15  # Slightly ahead of aircraft
                
                screen.blit(rocket_surface, (rocket_x, rocket_y))
            except pygame.error:
                # If image fails to load, draw a simple orange circle as fallback
                pygame.draw.circle(screen, (255, 165, 0), (aircraft_x + 25, aircraft_y), 12)
    
    def draw_rockets(self, screen):
        # Draw all active rockets
        for rocket in self.rockets:
            # Draw rocket as a larger orange circle with red center
            pygame.draw.circle(screen, (255, 165, 0), (int(rocket['x']), int(rocket['y'])), 5)
            # Add a red center for better visibility
            pygame.draw.circle(screen, (255, 0, 0), (int(rocket['x']), int(rocket['y'])), 2)
    
    def spawn_enemies(self):
        # Spawn new enemies if we have fewer than max and cooldown allows
        if len(self.enemies) < self.max_enemies and self.enemy_spawn_cooldown <= 0:
            # Choose a random enemy sprite
            sprite_name = random.choice(self.enemy_sprites)
            
            # Calculate enemy size (10% bigger than player)
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                player_file = os.path.join(script_dir, '..', 'res', 'aircrafts', 'images', 'aircraft_1.png')
                player_surface = pygame.image.load(player_file).convert_alpha()
                enemy_width = int(player_surface.get_width() * 1.1)
                enemy_height = int(player_surface.get_height() * 1.1)
            except:
                enemy_width = int(50 * 1.1)  # Fallback: 55px
                enemy_height = int(50 * 1.1)  # Fallback: 55px
            
            # Choose random spawn location (top, left, right only - no bottom spawning)
            spawn_side = random.choice(['top', 'left', 'right'])
            
            if spawn_side == 'top':
                # Spawn from top, move downward with randomized horizontal position
                spawn_x = random.randint(0, SCREEN_SIZE[0] - enemy_width)
                spawn_y = -enemy_height
                velocity_x = random.uniform(-1.0, 1.0)  # Slight horizontal drift
                velocity_y = random.uniform(1.0, 3.0)   # Downward movement
            elif spawn_side == 'left':
                # Spawn from left side, but only from upper part of screen (top 40% of screen height)
                spawn_x = -enemy_width
                upper_portion = int(SCREEN_SIZE[1] * 0.4)  # Only spawn in top 40% of screen
                spawn_y = random.randint(0, upper_portion - enemy_height)
                velocity_x = random.uniform(1.0, 3.0)   # Rightward movement
                velocity_y = random.uniform(-1.0, 1.0)  # Slight vertical drift
            else:  # spawn_side == 'right'
                # Spawn from right side, but only from upper part of screen (top 40% of screen height)
                spawn_x = SCREEN_SIZE[0]
                upper_portion = int(SCREEN_SIZE[1] * 0.4)  # Only spawn in top 40% of screen
                spawn_y = random.randint(0, upper_portion - enemy_height)
                velocity_x = random.uniform(-3.0, -1.0) # Leftward movement
                velocity_y = random.uniform(-1.0, 1.0)  # Slight vertical drift
            
            # Create new enemy with velocity-based movement
            enemy = {
                'x': spawn_x,
                'y': spawn_y,
                'velocity_x': velocity_x,     # Horizontal movement speed
                'velocity_y': velocity_y,     # Vertical movement speed
                'sprite': sprite_name,
                'surface': None,              # Will be loaded when first drawn
                'health': self.enemy_health,  # Use configurable enemy health
                'max_health': self.enemy_health # For visual health indication
            }
            
            self.enemies.append(enemy)
            
            # Set spawn cooldown
            self.enemy_spawn_cooldown = self.enemy_spawn_rate
            
            print(f"Spawned enemy {sprite_name} at ({spawn_x}, {spawn_y}) from {spawn_side}")
    
    def update_enemies(self):
        # Update enemy positions and remove enemies that are off-screen
        enemies_to_remove = []
        
        for i, enemy in enumerate(self.enemies):
            # Move enemy based on velocity
            enemy['x'] += enemy['velocity_x']
            enemy['y'] += enemy['velocity_y']
            
            # Get enemy dimensions for boundary checking
            if enemy['surface']:
                enemy_width = enemy['surface'].get_width()
                enemy_height = enemy['surface'].get_height()
            else:
                enemy_width = int(50 * 1.1)  # Fallback size
                enemy_height = int(50 * 1.1)
            
            # Remove enemies that have gone completely off-screen (with buffer)
            buffer = 100
            if (enemy['x'] < -enemy_width - buffer or 
                enemy['x'] > SCREEN_SIZE[0] + buffer or
                enemy['y'] < -enemy_height - buffer or 
                enemy['y'] > SCREEN_SIZE[1] + buffer):
                enemies_to_remove.append(i)
        
        # Remove off-screen enemies in reverse order to maintain correct indices
        for i in reversed(enemies_to_remove):
            del self.enemies[i]
    
    def draw_enemies(self, screen):
        # Draw all active enemies
        for enemy in self.enemies:
            # Load enemy sprite if not already loaded
            if enemy['surface'] is None:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                sprite_file = os.path.join(script_dir, '..', 'res', 'SpaceShipsPack', enemy["sprite"])
                
                try:
                    original_surface = pygame.image.load(sprite_file).convert_alpha()
                    
                    # Get player character dimensions for scaling reference
                    player_file = os.path.join(script_dir, '..', 'res', 'aircrafts', 'images', 'aircraft_1.png')
                    try:
                        player_surface = pygame.image.load(player_file).convert_alpha()
                        player_width = player_surface.get_width()
                        player_height = player_surface.get_height()
                    except:
                        # Fallback player dimensions
                        player_width = 50
                        player_height = 50
                    
                    # Calculate enemy size: 10% bigger than player character
                    target_width = int(player_width * 1.1)
                    target_height = int(player_height * 1.1)
                    
                    # Scale the enemy sprite
                    enemy['surface'] = pygame.transform.scale(original_surface, (target_width, target_height))
                    
                except pygame.error:
                    # If image fails to load, create a simple red rectangle as fallback
                    # Make it 10% bigger than default player size
                    fallback_width = int(50 * 1.1)  # 55px
                    fallback_height = int(50 * 1.1)  # 55px
                    enemy['surface'] = pygame.Surface((fallback_width, fallback_height))
                    enemy['surface'].fill((255, 0, 0))  # Red color
            
            # Draw the enemy sprite
            screen.blit(enemy['surface'], (int(enemy['x']), int(enemy['y'])))
            
            # Draw health indicator if enemy is damaged
            if enemy['health'] < enemy['max_health']:
                self.draw_enemy_health(screen, enemy)
    
    def draw_enemy_health(self, screen, enemy):
        # Draw a health bar above the enemy
        bar_width = 40
        bar_height = 4
        bar_x = int(enemy['x'] + (enemy['surface'].get_width() - bar_width) // 2)
        bar_y = int(enemy['y'] - 8)
        
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health (green)
        health_percentage = enemy['health'] / enemy['max_health']
        health_width = int(bar_width * health_percentage)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
    
    def check_bullet_enemy_collisions(self):
        # Check collisions between bullets and enemies
        bullets_to_remove = []
        enemies_to_remove = []
        
        for bullet_idx, bullet in enumerate(self.bullets):
            for enemy_idx, enemy in enumerate(self.enemies):
                if self.check_collision(bullet, enemy):
                    # Bullet hit enemy
                    bullets_to_remove.append(bullet_idx)
                    # Damage increases with weapon level
                    damage = 1.5 + (self.left_weapon_level - 1) * 0.5
                    enemy['health'] -= damage
                    
                    print(f"Enemy hit! Health: {enemy['health']} (Damage: {damage})")
                    
                    # Check if enemy is destroyed
                    if enemy['health'] <= 0:
                        enemies_to_remove.append(enemy_idx)
                        self.score += 10  # Award points for destroying enemy
                        print(f"Enemy destroyed! Score: {self.score}")
                    
                    break  # Bullet can only hit one enemy
        
        # Remove bullets that hit enemies (in reverse order)
        for idx in reversed(bullets_to_remove):
            if idx < len(self.bullets):
                del self.bullets[idx]
        
        # Remove destroyed enemies (in reverse order)
        for idx in reversed(enemies_to_remove):
            if idx < len(self.enemies):
                del self.enemies[idx]
    
    def check_rocket_enemy_collisions(self):
        # Check collisions between rockets and enemies
        rockets_to_remove = []
        enemies_to_remove = []
        
        for rocket_idx, rocket in enumerate(self.rockets):
            for enemy_idx, enemy in enumerate(self.enemies):
                if self.check_collision(rocket, enemy):
                    # Rocket hit enemy
                    rockets_to_remove.append(rocket_idx)
                    # Damage increases with weapon level
                    damage = 2.0 + (self.right_weapon_level - 1) * 0.5
                    enemy['health'] -= damage
                    
                    print(f"Enemy hit by rocket! Health: {enemy['health']} (Damage: {damage})")
                    
                    # Check if enemy is destroyed
                    if enemy['health'] <= 0:
                        enemies_to_remove.append(enemy_idx)
                        self.score += 15  # More points for rocket kills
                        print(f"Enemy destroyed by rocket! Score: {self.score}")
                    
                    break  # Rocket can only hit one enemy
        
        # Remove rockets that hit enemies (in reverse order)
        for idx in reversed(rockets_to_remove):
            if idx < len(self.rockets):
                del self.rockets[idx]
        
        # Remove destroyed enemies (in reverse order)
        for idx in reversed(enemies_to_remove):
            if idx < len(self.enemies):
                del self.enemies[idx]
    
    def check_collision(self, projectile, enemy):
        # Check if a projectile collides with an enemy
        # Simple rectangular collision detection
        projectile_radius = 5  # Approximate projectile size
        
        # Get enemy dimensions
        if enemy['surface']:
            enemy_width = enemy['surface'].get_width()
            enemy_height = enemy['surface'].get_height()
        else:
            # Fallback size (10% bigger than default player size)
            enemy_width = int(50 * 1.1)  # 55px
            enemy_height = int(50 * 1.1)  # 55px
        
        # Check if projectile is within enemy bounds
        return (projectile['x'] >= enemy['x'] and 
                projectile['x'] <= enemy['x'] + enemy_width and
                projectile['y'] >= enemy['y'] and 
                projectile['y'] <= enemy['y'] + enemy_height)

    def check_upgrade_availability(self):
        # Check if player has enough points for an upgrade
        if self.score >= self.last_upgrade_score + self.upgrade_threshold and not self.upgrade_available:
            self.upgrade_available = True
            print(f"Upgrade available! Score: {self.score}")

    def upgrade_screen(self, screen):
        # Display the upgrade selection screen
        print('upgrade screen')
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_SIZE[0], SCREEN_SIZE[1]))
        overlay.set_alpha(128)  # Semi-transparent
        overlay.fill(BLACK)     # Black overlay
        screen.blit(overlay, (0, 0))
        
        # Create fonts
        title_font = pygame.font.SysFont("serif", 40)
        option_font = pygame.font.SysFont("serif", 25)
        info_font = pygame.font.SysFont("serif", 18)
        
        # Calculate upgrade costs
        left_cost = self.get_upgrade_cost(self.left_weapon_level)
        right_cost = self.get_upgrade_cost(self.right_weapon_level)
        
        # Render text
        title_text = title_font.render("WEAPON UPGRADE", True, WHITE)
        left_option = option_font.render(f"1 - Upgrade Left Gun (Level {self.left_weapon_level})", True, WHITE)
        right_option = option_font.render(f"2 - Upgrade Right Gun (Level {self.right_weapon_level})", True, WHITE)
        left_cost_text = info_font.render(f"Cost: {left_cost} points", True, WHITE)
        right_cost_text = info_font.render(f"Cost: {right_cost} points", True, WHITE)
        left_info = info_font.render("+ Speed, + Damage, + Fire Rate", True, WHITE)
        right_info = info_font.render("+ Speed, + Damage, + Fire Rate", True, WHITE)
        score_text = info_font.render(f"Current Score: {self.score}", True, WHITE)
        
        # Position text
        screen_center_x = SCREEN_SIZE[0] // 2
        screen_center_y = SCREEN_SIZE[1] // 2
        
        # Title
        title_x = screen_center_x - (title_text.get_width() // 2)
        title_y = screen_center_y - 120
        screen.blit(title_text, [title_x, title_y])
        
        # Score
        score_x = screen_center_x - (score_text.get_width() // 2)
        score_y = title_y + title_text.get_height() + 20
        screen.blit(score_text, [score_x, score_y])
        
        # Left weapon option
        left_x = screen_center_x - (left_option.get_width() // 2)
        left_y = score_y + score_text.get_height() + 30
        color = WHITE if self.score >= left_cost else (128, 128, 128)  # Gray if can't afford
        left_option_colored = option_font.render(f"1 - Upgrade Left Gun (Level {self.left_weapon_level})", True, color)
        screen.blit(left_option_colored, [left_x, left_y])
        
        # Left weapon cost and info
        left_cost_x = screen_center_x - (left_cost_text.get_width() // 2)
        screen.blit(left_cost_text, [left_cost_x, left_y + 25])
        left_info_x = screen_center_x - (left_info.get_width() // 2)
        screen.blit(left_info, [left_info_x, left_y + 45])
        
        # Right weapon option
        right_x = screen_center_x - (right_option.get_width() // 2)
        right_y = left_y + 90
        color = WHITE if self.score >= right_cost else (128, 128, 128)  # Gray if can't afford
        right_option_colored = option_font.render(f"2 - Upgrade Right Gun (Level {self.right_weapon_level})", True, color)
        screen.blit(right_option_colored, [right_x, right_y])
        
        # Right weapon cost and info
        right_cost_x = screen_center_x - (right_cost_text.get_width() // 2)
        screen.blit(right_cost_text, [right_cost_x, right_y + 25])
        right_info_x = screen_center_x - (right_info.get_width() // 2)
        screen.blit(right_info, [right_info_x, right_y + 45])

    def get_upgrade_cost(self, current_level):
        # Calculate upgrade cost based on current level
        if current_level == 1:
            return 200
        elif current_level == 2:
            return 300
        elif current_level == 3:
            return 400
        else:
            return 500 + (current_level - 4) * 100  # Exponential cost increase

    def upgrade_left_weapon(self):
        # Upgrade left click weapon (bullets)
        cost = self.get_upgrade_cost(self.left_weapon_level)
        if self.score >= cost:
            self.score -= cost
            self.left_weapon_level += 1
            self.upgrade_available = False
            self.last_upgrade_score = self.score
            print(f"Left weapon upgraded to level {self.left_weapon_level}! Score: {self.score}")
        else:
            print("Not enough points for left weapon upgrade!")

    def upgrade_right_weapon(self):
        # Upgrade right click weapon (rockets)
        cost = self.get_upgrade_cost(self.right_weapon_level)
        if self.score >= cost:
            self.score -= cost
            self.right_weapon_level += 1
            self.upgrade_available = False
            self.last_upgrade_score = self.score
            print(f"Right weapon upgraded to level {self.right_weapon_level}! Score: {self.score}")
        else:
            print("Not enough points for right weapon upgrade!")

    def run_main_loop(self):
        # Main game loop - runs the entire game
        import sys
        
        run_game = True
        while run_game:
            # Process events and check if user wants to quit
            if self.process_events():
                run_game = False
            
            # Run game logic
            self.run_logic()
            
            # Draw everything to screen
            self.display_frame(screen)
            
            # Control frame rate (60 FPS)
            clock.tick(60)
        
        # Clean up and exit
        pygame.quit()
        sys.exit()
        
# Create a game instance and run the main loop
if __name__ == "__main__":
    game = Game(0, 0)  # Create a single game instance with default score and session number
    game.run_main_loop()  # Run the main game loop
    