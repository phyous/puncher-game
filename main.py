#!/usr/bin/env python3
"""
Puncher! - A superhero side-scrolling adventure game
Fight alien invaders with various powers and abilities!
"""

import pygame
import sys
import random
from enum import Enum
from typing import List, Tuple
import math
from sprites import (create_player_sprite, create_player_sneaking_sprite, 
                    create_alien_sprite, create_treasure_sprite, 
                    create_powerup_sprite, create_background_elements)

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 139)
DARK_GREEN = (0, 100, 0)

class PowerUpType(Enum):
    FIREBALL = "fireball"
    GUN = "gun"
    SHIELD = "shield"
    SWORD = "sword"
    BOW = "bow"
    LASER_EYES = "laser_eyes"

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LEVEL_COMPLETE = "level_complete"

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Puncher! - Save the World!")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        self.level = 1
        self.score = 0
        
        # Game objects
        self.player = None
        self.enemies = pygame.sprite.Group()
        self.treasures = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.level_goal = None
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Camera system
        self.camera_x = 0
        self.world_width = 3000  # Total world width
        
        # Debug mode for collision visualization
        self.debug_mode = False
        
        self.init_game()
    
    def init_game(self):
        """Initialize a new game"""
        self.player = Player(100, SCREEN_HEIGHT - 150)
        self.all_sprites.add(self.player)
        self.enemies.empty()
        self.treasures.empty()
        self.power_ups.empty()
        self.projectiles.empty()
        if self.level_goal:
            self.level_goal.kill()
        
        # Generate initial level content
        self.generate_level_content()
    
    def generate_level_content(self):
        """Generate random enemies, treasures, and power-ups for current level"""
        # Number of enemies increases with level (balanced for kids)
        num_enemies = 4 + (self.level * 2)  # More enemies for better action
        num_treasures = 3 + self.level  # More treasures for positive feedback
        num_power_ups = 1 + (self.level // 2)  # Guaranteed power-up per level
        
        # Spawn enemies throughout the world
        for i in range(num_enemies):
            x = random.randint(200, self.world_width - 200)
            y = SCREEN_HEIGHT - 120  # Adjusted to match player ground level
            enemy = Enemy(x, y, self.level)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # Spawn treasures throughout the world - fixed positioning
        for i in range(num_treasures):
            x = random.randint(100, self.world_width - 100)
            # Keep treasures closer to ground level for easier pickup
            y = random.randint(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 120)
            treasure = Treasure(x, y)
            self.treasures.add(treasure)
            self.all_sprites.add(treasure)
        
        # Spawn power-ups throughout the world - fixed positioning  
        for i in range(num_power_ups):
            x = random.randint(300, self.world_width - 300)
            # Keep power-ups at reachable heights
            y = random.randint(SCREEN_HEIGHT - 220, SCREEN_HEIGHT - 130)
            power_type = random.choice(list(PowerUpType))
            power_up = PowerUp(x, y, power_type)
            self.power_ups.add(power_up)
            self.all_sprites.add(power_up)
        
        # Create level goal at the end of the world
        self.level_goal = LevelGoal(self.world_width - 200, SCREEN_HEIGHT - 200)
        self.all_sprites.add(self.level_goal)
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                elif event.key == pygame.K_RETURN:
                    if self.state == GameState.MENU:
                        self.state = GameState.PLAYING
                        self.init_game()
                    elif self.state == GameState.GAME_OVER:
                        self.state = GameState.MENU
                        self.level = 1
                        self.score = 0
                elif event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
                    self.player.punch()
                elif event.key == pygame.K_d and self.state == GameState.PLAYING:
                    # Toggle debug mode with 'D' key
                    self.debug_mode = not self.debug_mode
                elif self.state == GameState.PLAYING:
                    # Power-up hotkeys (numbers 1-6)
                    power_keys = {
                        pygame.K_1: PowerUpType.FIREBALL,
                        pygame.K_2: PowerUpType.GUN,
                        pygame.K_3: PowerUpType.SHIELD,
                        pygame.K_4: PowerUpType.SWORD,
                        pygame.K_5: PowerUpType.BOW,
                        pygame.K_6: PowerUpType.LASER_EYES
                    }
                    if event.key in power_keys:
                        self.player.use_power(power_keys[event.key], self)
    
    def update(self):
        """Update game state"""
        if self.state != GameState.PLAYING:
            return
        
        # Update all sprites
        self.all_sprites.update()
        
        # Update camera to follow player
        target_camera_x = self.player.rect.x - SCREEN_WIDTH // 3
        self.camera_x = max(0, min(target_camera_x, self.world_width - SCREEN_WIDTH))
        
        # Check collisions with improved detection
        self.check_collisions()
        
        # Remove off-screen sprites
        self.cleanup_sprites()
        
        # Level completion is now handled by reaching the goal
        
        # Check game over
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
    
    def check_collisions(self):
        """Check all collision interactions with improved detection"""
        # Player punch vs enemies - more generous collision
        if self.player.is_punching:
            for enemy in self.enemies:
                # Larger punch collision area
                punch_area = pygame.Rect(
                    self.player.punch_rect.x - 10,
                    self.player.punch_rect.y - 10,
                    self.player.punch_rect.width + 20,
                    self.player.punch_rect.height + 20
                )
                if punch_area.colliderect(enemy.rect):
                    enemy.take_damage(self.player.punch_damage)
                    if enemy.health <= 0:
                        self.score += enemy.points
                        enemy.kill()
        
        # Player vs enemies (taking damage) - improved collision
        for enemy in self.enemies:
            # More generous collision detection
            distance = math.sqrt((self.player.rect.centerx - enemy.rect.centerx)**2 + 
                               (self.player.rect.centery - enemy.rect.centery)**2)
            if distance < 50 and not self.player.invulnerable:  # 50 pixel collision radius
                self.player.take_damage(enemy.damage)
        
        # Player vs treasures - fixed collision detection
        for treasure in list(self.treasures):
            # Use rectangle collision with expanded pickup area for better detection
            # Create expanded rectangle around treasure for easier pickup
            pickup_area = pygame.Rect(
                treasure.rect.x - 25,  # Expand 25 pixels in each direction
                treasure.rect.y - 25,
                treasure.rect.width + 50,
                treasure.rect.height + 50
            )
            # Also check if player rectangle overlaps with treasure
            if (pickup_area.colliderect(self.player.rect) or 
                self.player.rect.colliderect(treasure.rect)):
                self.score += treasure.points
                treasure.kill()
        
        # Player vs power-ups - fixed collision detection  
        for power_up in list(self.power_ups):
            # Use rectangle collision with expanded pickup area for better detection
            # Create expanded rectangle around power-up for easier pickup
            pickup_area = pygame.Rect(
                power_up.rect.x - 30,  # Expand 30 pixels in each direction (larger for power-ups)
                power_up.rect.y - 30,
                power_up.rect.width + 60,
                power_up.rect.height + 60
            )
            # Also check if player rectangle overlaps with power-up
            if (pickup_area.colliderect(self.player.rect) or 
                self.player.rect.colliderect(power_up.rect)):
                self.player.add_power_up(power_up.power_type)
                power_up.kill()
        
        # Player vs level goal
        if self.level_goal:
            distance = math.sqrt((self.player.rect.centerx - self.level_goal.rect.centerx)**2 + 
                               (self.player.rect.centery - self.level_goal.rect.centery)**2)
            if distance < 80:  # Goal touch distance
                self.level += 1
                if self.level > 5:
                    self.state = GameState.GAME_OVER  # Victory!
                else:
                    # Reset player position for new level
                    self.player.rect.x = 100
                    self.player.rect.y = SCREEN_HEIGHT - 150
                    self.camera_x = 0
                    self.generate_level_content()  # Next level
        
        # Projectiles vs enemies - improved collision
        for projectile in list(self.projectiles):
            for enemy in list(self.enemies):
                # More generous projectile collision
                distance = math.sqrt((projectile.rect.centerx - enemy.rect.centerx)**2 + 
                                   (projectile.rect.centery - enemy.rect.centery)**2)
                if distance < 40:  # 40 pixel hit radius
                    enemy.take_damage(projectile.damage)
                    if enemy.health <= 0:
                        self.score += enemy.points
                        enemy.kill()
                    projectile.kill()
    
    def cleanup_sprites(self):
        """Remove sprites that have moved too far from player or off world"""
        for sprite in list(self.all_sprites):
            if sprite != self.player and sprite != self.level_goal:
                # Remove sprites that are very far from the player or off the world
                if (sprite.rect.x < -200 or 
                    sprite.rect.x > self.world_width + 200 or
                    abs(sprite.rect.x - self.player.rect.x) > 2000):
                    sprite.kill()
    
    def draw_background(self):
        """Draw scrolling background"""
        # Simple gradient background
        for y in range(SCREEN_HEIGHT):
            color_value = int(135 + (y / SCREEN_HEIGHT) * 100)
            color = (color_value // 3, color_value // 2, color_value)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw ground elements based on camera position
        for i in range(int(self.world_width // 300) + 2):
            x = i * 300 - self.camera_x
            if x > -300 and x < SCREEN_WIDTH + 300:  # Only draw visible elements
                pygame.draw.rect(self.screen, DARK_GREEN, (x, SCREEN_HEIGHT - 50, 200, 50))
    
    def draw_sprites_with_camera(self):
        """Draw all sprites with camera offset"""
        for sprite in self.all_sprites:
            screen_x = sprite.rect.x - self.camera_x
            screen_y = sprite.rect.y
            # Only draw sprites that are visible on screen
            if screen_x > -sprite.rect.width and screen_x < SCREEN_WIDTH + sprite.rect.width:
                self.screen.blit(sprite.image, (screen_x, screen_y))
                
                # Debug mode: Draw collision rectangles
                if self.debug_mode:
                    # Draw sprite rectangle
                    pygame.draw.rect(self.screen, GREEN, 
                                   (screen_x, screen_y, sprite.rect.width, sprite.rect.height), 2)
                    
                    # Draw expanded pickup areas for treasures and power-ups
                    if sprite in self.treasures:
                        pickup_area = pygame.Rect(screen_x - 25, screen_y - 25, 
                                                sprite.rect.width + 50, sprite.rect.height + 50)
                        pygame.draw.rect(self.screen, YELLOW, pickup_area, 2)
                    elif sprite in self.power_ups:
                        pickup_area = pygame.Rect(screen_x - 30, screen_y - 30, 
                                                sprite.rect.width + 60, sprite.rect.height + 60)
                        pygame.draw.rect(self.screen, CYAN, pickup_area, 2)
        
        # Draw punch animation
        if self.player.is_punching:
            punch_screen_x = self.player.punch_rect.x - self.camera_x
            punch_screen_y = self.player.punch_rect.y
            # Draw punch effect
            pygame.draw.circle(self.screen, (255, 255, 0), 
                             (punch_screen_x + 40, punch_screen_y + 30), 
                             30 - (self.player.punch_timer * 3), 3)
    
    def draw_ui(self):
        """Draw game UI elements"""
        # Health bar
        health_width = 200
        health_height = 20
        health_x = 20
        health_y = 20
        
        # Background
        pygame.draw.rect(self.screen, RED, (health_x, health_y, health_width, health_height))
        # Current health
        current_width = int((self.player.health / self.player.max_health) * health_width)
        pygame.draw.rect(self.screen, GREEN, (health_x, health_y, current_width, health_height))
        # Border
        pygame.draw.rect(self.screen, BLACK, (health_x, health_y, health_width, health_height), 2)
        
        # Health text
        health_text = self.font_small.render(f"Health: {self.player.health}/{self.player.max_health}", True, BLACK)
        self.screen.blit(health_text, (health_x, health_y + 25))
        
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 20))
        
        # Level
        level_text = self.font_medium.render(f"Level: {self.level}/5", True, BLACK)
        self.screen.blit(level_text, (SCREEN_WIDTH - 200, 70))
        
        # Power-ups
        if self.player.power_ups:
            power_text = self.font_small.render("Powers (press number):", True, BLACK)
            self.screen.blit(power_text, (20, 80))
            
            power_keys = ['1', '2', '3', '4', '5', '6']
            power_types = [PowerUpType.FIREBALL, PowerUpType.GUN, PowerUpType.SHIELD, 
                          PowerUpType.SWORD, PowerUpType.BOW, PowerUpType.LASER_EYES]
            
            for i, power_type in enumerate(power_types):
                if power_type in self.player.power_ups:
                    power_name = power_type.value.replace('_', ' ').title()
                    if power_type in self.player.weapon_ammo:
                        ammo_count = self.player.weapon_ammo[power_type]
                        power_display = self.font_small.render(f"{power_keys[i]}: {power_name} ({ammo_count})", True, PURPLE)
                    else:
                        power_display = self.font_small.render(f"{power_keys[i]}: {power_name}", True, PURPLE)
                    self.screen.blit(power_display, (20, 110 + i * 25))
        
        # Debug mode indicator
        if self.debug_mode:
            debug_text = self.font_small.render("DEBUG MODE: ON (Press 'D' to toggle)", True, RED)
            self.screen.blit(debug_text, (20, SCREEN_HEIGHT - 40))
    
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(DARK_BLUE)
        
        title = self.font_large.render("PUNCHER!", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Save the World from Alien Invaders!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(subtitle, subtitle_rect)
        
        instructions = [
            "Arrow Keys: Move and Jump",
            "Space: Punch",
            "Down Arrow: Sneak",
            "Numbers 1-6: Use Power-ups",
            "D: Toggle Debug Mode (show collision areas)",
            "Collect power-ups to upgrade!",
            "",
            "Press ENTER to Start",
            "Press ESC to Pause"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 380 + i * 40))
            self.screen.blit(text, text_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        
        if self.level > 5:
            title = self.font_large.render("VICTORY!", True, GREEN)
            subtitle = self.font_medium.render("You saved the world!", True, WHITE)
        else:
            title = self.font_large.render("GAME OVER", True, RED)
            subtitle = self.font_medium.render("The aliens won this time...", True, WHITE)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 250))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 320))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font_small.render("Press ENTER to return to menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        """Main draw function"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_background()
            self.draw_sprites_with_camera()
            self.draw_ui()
        elif self.state == GameState.PAUSED:
            self.draw_background()
            self.draw_sprites_with_camera()
            self.draw_ui()
            # Pause overlay
            pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            pause_surface.set_alpha(128)
            pause_surface.fill(BLACK)
            self.screen.blit(pause_surface, (0, 0))
            
            pause_text = self.font_large.render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, pause_rect)
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create sprite
        self.normal_sprite = create_player_sprite()
        self.sneaking_sprite = create_player_sneaking_sprite()
        self.image = self.normal_sprite
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 8
        self.jump_power = -18
        self.gravity = 1
        self.on_ground = False
        
        # Combat
        self.health = 100
        self.max_health = 100
        self.punch_damage = 35  # Increased damage
        self.is_punching = False
        self.punch_timer = 0
        self.punch_duration = 10
        self.punch_rect = pygame.Rect(0, 0, 80, 60)
        
        # Status
        self.invulnerable = False
        self.invuln_timer = 0
        self.invuln_duration = 60
        
        # Power-ups and weapons
        # Start with some powers for testing
        self.power_ups = [PowerUpType.SWORD, PowerUpType.FIREBALL, PowerUpType.GUN]
        self.active_powers = {}  # Track active power timers
        self.projectile_timer = 0
        self.weapon_ammo = {
            PowerUpType.FIREBALL: 10,  # Start with ammo
            PowerUpType.GUN: 20,
            PowerUpType.LASER_EYES: 5,
            PowerUpType.BOW: 12
        }
        
        # Animation
        self.facing_right = True
        self.is_sneaking = False
    
    def update(self):
        """Update player state"""
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
            self.facing_right = True
        
        # Jumping
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
        
        # Sneaking
        self.is_sneaking = keys[pygame.K_DOWN]
        
        # Apply gravity
        self.vel_y += self.gravity
        
        # Move
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Ground collision (simple)
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True
        
        # World boundaries (player can move anywhere in the world)
        if self.rect.left < 0:
            self.rect.left = 0
        # Remove right boundary - player can move into the world
        
        # Update punch
        if self.is_punching:
            self.punch_timer -= 1
            if self.punch_timer <= 0:
                self.is_punching = False
            
            # Update punch hitbox with larger area
            if self.facing_right:
                self.punch_rect.x = self.rect.right - 20
                self.punch_rect.y = self.rect.y + 10
            else:
                self.punch_rect.x = self.rect.left - 60
                self.punch_rect.y = self.rect.y + 10
        
        # Update invulnerability
        if self.invulnerable:
            self.invuln_timer -= 1
            if self.invuln_timer <= 0:
                self.invulnerable = False
        
        # Update appearance for sneaking
        if self.is_sneaking:
            self.image = self.sneaking_sprite
            old_bottom = self.rect.bottom
            old_x = self.rect.x
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.x = old_x
        else:
            self.image = self.normal_sprite
            old_bottom = self.rect.bottom
            old_x = self.rect.x
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.x = old_x
        
        # Flash when invulnerable
        if self.invulnerable and self.invuln_timer % 10 < 5:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)
    
    def punch(self):
        """Initiate punch attack"""
        if not self.is_punching:
            self.is_punching = True
            self.punch_timer = self.punch_duration
    
    def take_damage(self, damage):
        """Take damage from enemy"""
        if not self.invulnerable:
            self.health -= damage
            self.invulnerable = True
            self.invuln_timer = self.invuln_duration
            if self.health < 0:
                self.health = 0
    
    def add_power_up(self, power_type):
        """Add a power-up"""
        if power_type not in self.power_ups:
            self.power_ups.append(power_type)
        
        # Add ammo for projectile weapons or enhance abilities
        if power_type == PowerUpType.FIREBALL:
            self.weapon_ammo[power_type] += 10
        elif power_type == PowerUpType.GUN:
            self.weapon_ammo[power_type] += 30
        elif power_type == PowerUpType.LASER_EYES:
            self.weapon_ammo[power_type] += 8
        elif power_type == PowerUpType.BOW:
            self.weapon_ammo[power_type] += 15
        elif power_type == PowerUpType.SHIELD:
            self.max_health += 50
            self.health = min(self.health + 25, self.max_health)
        elif power_type == PowerUpType.SWORD:
            self.punch_damage += 15
    
    def use_power(self, power_type, game):
        """Use a specific power"""
        if power_type not in self.power_ups:
            return
        
        # Check ammo for projectile weapons (but not for sword/shield which don't use ammo)
        if (power_type in self.weapon_ammo and 
            power_type not in [PowerUpType.SWORD, PowerUpType.SHIELD] and 
            self.weapon_ammo[power_type] <= 0):
            return  # No ammo left
        
        if power_type == PowerUpType.FIREBALL:
            # Shoot fireball at enemy center height
            direction = 1 if self.facing_right else -1
            start_x = self.rect.right if self.facing_right else self.rect.left
            target_y = self.rect.centery
            fireball = Projectile(start_x, target_y, direction, 40, ORANGE)
            game.projectiles.add(fireball)
            game.all_sprites.add(fireball)
            self.weapon_ammo[power_type] -= 1
        
        elif power_type == PowerUpType.GUN:
            # Rapid fire bullets at enemy center
            direction = 1 if self.facing_right else -1
            start_x = self.rect.right if self.facing_right else self.rect.left
            target_y = self.rect.centery
            bullet = Projectile(start_x, target_y, direction, 20, WHITE)
            game.projectiles.add(bullet)
            game.all_sprites.add(bullet)
            self.weapon_ammo[power_type] -= 1
        
        elif power_type == PowerUpType.LASER_EYES:
            # Laser beam from eyes at enemy center
            direction = 1 if self.facing_right else -1
            start_x = self.rect.right if self.facing_right else self.rect.left
            target_y = self.rect.centery  # Aim at enemy center too
            laser = Projectile(start_x, target_y, direction, 50, PURPLE)
            laser.speed = 25  # Faster laser
            game.projectiles.add(laser)
            game.all_sprites.add(laser)
            self.weapon_ammo[power_type] -= 1
        
        elif power_type == PowerUpType.BOW:
            # Arrow projectile at enemy center
            direction = 1 if self.facing_right else -1
            start_x = self.rect.right if self.facing_right else self.rect.left
            target_y = self.rect.centery
            arrow = Projectile(start_x, target_y, direction, 35, GREEN)
            game.projectiles.add(arrow)
            game.all_sprites.add(arrow)
            self.weapon_ammo[power_type] -= 1

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        super().__init__()
        self.image = create_alien_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Stats based on level (balanced for kids)
        self.health = 20 + (level * 5)  # Lower enemy health
        self.max_health = self.health
        self.damage = 8 + (level * 3)  # Lower enemy damage
        self.speed = 1.5 + (level * 0.3)  # Slower enemies
        self.points = 75 + (level * 25)  # More points for defeating enemies
        
        # AI
        self.move_timer = 0
        self.move_direction = random.choice([-1, 1])
        
        # Visual effects
        self.hit_flash_timer = 0
        self.original_image = self.image.copy()
    
    def update(self):
        """Update enemy behavior"""
        # Simple AI - move towards player general area and randomly
        self.move_timer += 1
        if self.move_timer > 60:  # Change direction every second
            self.move_direction = random.choice([-1, 1])
            self.move_timer = 0
        
        self.rect.x += self.move_direction * self.speed
        
        # Simple ground collision
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
        
        # Handle hit flash effect
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            # Create red tinted version
            self.image = self.original_image.copy()
            self.image.fill((255, 100, 100), special_flags=pygame.BLEND_MULT)
        else:
            self.image = self.original_image
    
    def take_damage(self, damage):
        """Take damage"""
        self.health -= damage
        # Create a temporary red flash effect without destroying the sprite
        self.hit_flash_timer = 5  # Flash for 5 frames

class Treasure(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = create_treasure_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.points = random.randint(150, 400)  # More generous treasure points
        
        # Animation
        self.bounce_timer = 0
        self.original_y = y
    
    def update(self):
        """Update treasure animation"""
        self.bounce_timer += 0.2
        self.rect.y = self.original_y + math.sin(self.bounce_timer) * 5

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        self.image = create_powerup_sprite(power_type.value)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Animation
        self.float_timer = 0
        self.original_y = y
    
    def update(self):
        """Update power-up animation"""
        self.float_timer += 0.15
        self.rect.y = self.original_y + math.sin(self.float_timer) * 8

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, damage, color=WHITE):
        super().__init__()
        # Make projectiles larger and more visible
        if color == ORANGE:  # Fireball
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, ORANGE, (10, 10), 10)
            pygame.draw.circle(self.image, YELLOW, (10, 10), 6)
        elif color == PURPLE:  # Laser
            self.image = pygame.Surface((25, 8), pygame.SRCALPHA)
            pygame.draw.rect(self.image, PURPLE, (0, 0, 25, 8))
            pygame.draw.rect(self.image, WHITE, (2, 2, 21, 4))
        elif color == GREEN:  # Arrow
            self.image = pygame.Surface((15, 3), pygame.SRCALPHA)
            pygame.draw.rect(self.image, GREEN, (0, 0, 15, 3))
            pygame.draw.polygon(self.image, GREEN, [(15, 0), (20, 1), (15, 3)])
        else:  # Bullet
            self.image = pygame.Surface((8, 4))
            self.image.fill(color)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 15
        self.direction = direction
        self.damage = damage
    
    def update(self):
        """Update projectile movement"""
        self.rect.x += self.direction * self.speed
        
        # Remove if off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

class LevelGoal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a large, visible goal post
        self.image = pygame.Surface((100, 150), pygame.SRCALPHA)
        
        # Draw a goal post/portal
        pygame.draw.rect(self.image, (0, 255, 255), (10, 0, 20, 150))  # Left post
        pygame.draw.rect(self.image, (0, 255, 255), (70, 0, 20, 150))  # Right post
        pygame.draw.rect(self.image, (0, 255, 255), (10, 0, 80, 20))   # Top bar
        
        # Add some sparkle effects
        for i in range(10):
            spark_x = random.randint(20, 80)
            spark_y = random.randint(20, 130)
            pygame.draw.circle(self.image, (255, 255, 0), (spark_x, spark_y), 3)
        
        # Add "GOAL" text
        font = pygame.font.Font(None, 24)
        text = font.render("GOAL", True, (255, 255, 255))
        text_rect = text.get_rect(center=(50, 75))
        self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Animation
        self.glow_timer = 0
    
    def update(self):
        """Update goal animation"""
        self.glow_timer += 0.2
        # Add pulsing glow effect
        glow_alpha = int(128 + 127 * math.sin(self.glow_timer))
        self.image.set_alpha(glow_alpha)

if __name__ == "__main__":
    game = Game()
    game.run()
