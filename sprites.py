"""
Sprite creation utilities for Puncher! game
Creates simple but appealing sprites programmatically
"""

import pygame
import math

def create_player_sprite(width=60, height=80, color=(0, 100, 255)):
    """Create a superhero player sprite"""
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Body (blue suit)
    pygame.draw.rect(sprite, color, (15, 25, 30, 45))
    
    # Head (skin tone)
    pygame.draw.circle(sprite, (255, 220, 177), (30, 20), 12)
    
    # Cape
    pygame.draw.polygon(sprite, (200, 0, 0), [(45, 25), (55, 25), (60, 70), (45, 65)])
    
    # Arms
    pygame.draw.rect(sprite, color, (5, 30, 10, 25))
    pygame.draw.rect(sprite, color, (45, 30, 10, 25))
    
    # Legs
    pygame.draw.rect(sprite, color, (18, 65, 8, 15))
    pygame.draw.rect(sprite, color, (34, 65, 8, 15))
    
    # Eyes
    pygame.draw.circle(sprite, (255, 255, 255), (26, 18), 2)
    pygame.draw.circle(sprite, (255, 255, 255), (34, 18), 2)
    pygame.draw.circle(sprite, (0, 0, 0), (26, 18), 1)
    pygame.draw.circle(sprite, (0, 0, 0), (34, 18), 1)
    
    # Chest emblem (star)
    star_points = []
    for i in range(5):
        angle = i * 2 * math.pi / 5 - math.pi / 2
        x = 30 + 6 * math.cos(angle)
        y = 40 + 6 * math.sin(angle)
        star_points.append((x, y))
    pygame.draw.polygon(sprite, (255, 255, 0), star_points)
    
    return sprite

def create_player_sneaking_sprite(width=60, height=40, color=(0, 100, 255)):
    """Create sneaking version of player sprite"""
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Body (crouched)
    pygame.draw.rect(sprite, color, (15, 10, 30, 25))
    
    # Head
    pygame.draw.circle(sprite, (255, 220, 177), (30, 12), 10)
    
    # Cape (shorter)
    pygame.draw.polygon(sprite, (200, 0, 0), [(40, 10), (50, 10), (55, 35), (40, 30)])
    
    # Arms
    pygame.draw.rect(sprite, color, (5, 15, 10, 15))
    pygame.draw.rect(sprite, color, (45, 15, 10, 15))
    
    # Legs (bent)
    pygame.draw.rect(sprite, color, (18, 30, 8, 10))
    pygame.draw.rect(sprite, color, (34, 30, 8, 10))
    
    # Eyes
    pygame.draw.circle(sprite, (255, 255, 255), (27, 10), 2)
    pygame.draw.circle(sprite, (255, 255, 255), (33, 10), 2)
    pygame.draw.circle(sprite, (0, 0, 0), (27, 10), 1)
    pygame.draw.circle(sprite, (0, 0, 0), (33, 10), 1)
    
    return sprite

def create_alien_sprite(width=50, height=60, color=(255, 0, 100)):
    """Create an alien enemy sprite"""
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Body
    pygame.draw.ellipse(sprite, color, (10, 20, 30, 35))
    
    # Head (large)
    pygame.draw.ellipse(sprite, color, (5, 5, 40, 30))
    
    # Eyes (large alien eyes)
    pygame.draw.ellipse(sprite, (0, 255, 0), (12, 12, 8, 12))
    pygame.draw.ellipse(sprite, (0, 255, 0), (30, 12, 8, 12))
    pygame.draw.ellipse(sprite, (0, 0, 0), (14, 16, 4, 6))
    pygame.draw.ellipse(sprite, (0, 0, 0), (32, 16, 4, 6))
    
    # Antennae
    pygame.draw.line(sprite, color, (18, 5), (15, 0), 2)
    pygame.draw.line(sprite, color, (32, 5), (35, 0), 2)
    pygame.draw.circle(sprite, (255, 255, 0), (15, 0), 2)
    pygame.draw.circle(sprite, (255, 255, 0), (35, 0), 2)
    
    # Arms
    pygame.draw.rect(sprite, color, (2, 25, 8, 15))
    pygame.draw.rect(sprite, color, (40, 25, 8, 15))
    
    # Legs
    pygame.draw.rect(sprite, color, (15, 50, 6, 10))
    pygame.draw.rect(sprite, color, (29, 50, 6, 10))
    
    return sprite

def create_treasure_sprite(width=30, height=30):
    """Create a treasure sprite (gem)"""
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Gem shape
    points = [
        (15, 5),   # top
        (25, 15),  # right
        (15, 25),  # bottom
        (5, 15)    # left
    ]
    pygame.draw.polygon(sprite, (255, 215, 0), points)  # Gold
    
    # Inner highlight
    inner_points = [
        (15, 8),
        (20, 15),
        (15, 22),
        (10, 15)
    ]
    pygame.draw.polygon(sprite, (255, 255, 150), inner_points)
    
    # Sparkle effect
    pygame.draw.circle(sprite, (255, 255, 255), (12, 12), 2)
    pygame.draw.circle(sprite, (255, 255, 255), (18, 18), 1)
    
    return sprite

def create_powerup_sprite(power_type, width=50, height=50):
    """Create power-up sprites based on type"""
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Base circle (larger)
    base_colors = {
        'fireball': (255, 100, 0),
        'gun': (80, 80, 80),
        'shield': (0, 200, 255),
        'sword': (192, 192, 192),
        'bow': (139, 69, 19),
        'laser_eyes': (255, 0, 255)
    }
    
    color = base_colors.get(power_type, (255, 255, 255))
    pygame.draw.circle(sprite, color, (25, 25), 22)
    pygame.draw.circle(sprite, (255, 255, 255), (25, 25), 22, 3)
    
    # Icon based on type (adjusted for larger sprite)
    if power_type == 'fireball':
        # Flame shape
        pygame.draw.polygon(sprite, (255, 255, 0), [(25, 12), (20, 30), (30, 30)])
        pygame.draw.circle(sprite, (255, 200, 0), (25, 27), 8)
    elif power_type == 'gun':
        # Simple gun shape
        pygame.draw.rect(sprite, (40, 40, 40), (15, 23, 20, 5))
        pygame.draw.rect(sprite, (40, 40, 40), (32, 20, 4, 10))
    elif power_type == 'shield':
        # Shield shape
        pygame.draw.polygon(sprite, (100, 150, 255), [(25, 10), (33, 18), (33, 30), (25, 37), (17, 30), (17, 18)])
    elif power_type == 'sword':
        # Sword shape
        pygame.draw.rect(sprite, (220, 220, 220), (24, 10, 3, 25))
        pygame.draw.rect(sprite, (139, 69, 19), (21, 32, 8, 8))
    elif power_type == 'bow':
        # Bow shape
        pygame.draw.arc(sprite, (101, 67, 33), (15, 13, 20, 25), 0.5, 2.6, 4)
        pygame.draw.line(sprite, (139, 69, 19), (17, 15), (33, 35), 3)
    elif power_type == 'laser_eyes':
        # Eye with laser
        pygame.draw.ellipse(sprite, (255, 255, 255), (15, 18, 20, 12))
        pygame.draw.circle(sprite, (255, 0, 0), (25, 24), 5)
        pygame.draw.line(sprite, (255, 0, 0), (30, 24), (42, 24), 3)
    
    return sprite

def create_background_elements():
    """Create background elements like buildings, clouds, etc."""
    elements = {}
    
    # Simple building
    building = pygame.Surface((100, 200), pygame.SRCALPHA)
    pygame.draw.rect(building, (80, 80, 80), (0, 0, 100, 200))
    # Windows
    for i in range(3):
        for j in range(8):
            pygame.draw.rect(building, (255, 255, 150), (15 + i * 25, 20 + j * 20, 8, 12))
    elements['building'] = building
    
    # Cloud
    cloud = pygame.Surface((80, 40), pygame.SRCALPHA)
    pygame.draw.circle(cloud, (255, 255, 255), (20, 25), 15)
    pygame.draw.circle(cloud, (255, 255, 255), (35, 20), 18)
    pygame.draw.circle(cloud, (255, 255, 255), (50, 25), 15)
    pygame.draw.circle(cloud, (255, 255, 255), (60, 25), 12)
    elements['cloud'] = cloud
    
    return elements
