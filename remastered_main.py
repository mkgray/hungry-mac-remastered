import pgzero, pgzrun, pygame
from enum import Enum
import numpy as np
import random

#***************#
# Game settings #
#***************#

TITLE = "Hungry Mac Remastered"

# Express size in pixels - should be multiple of base tile size (40 pixels)
WIDTH = 640
HEIGHT = 640

# Base tile size
TILE_SIZE = 40

# Constant tile references
DIRT = 0
GRASS = 1
MAC = 2

# STARTING GRASS LIKELYHOOD (in %) OF SPAWNING
GRASS_PERCENTAGE = 0.25

# Other default values
ANCHOR_CENTRE = ("center", "center")

# Class for basic dirt tiles
class Dirt(Actor):
    def __init__(self, pos, anchor=ANCHOR_CENTRE):
        super().__init__("dirt", pos, anchor)

    # Dirt currently has no mechanics beyond background
    def update(self):
        pass

# # Class for basic grass tiles (TODO: Add creeping charlie)
class Grass(Actor):
    def __init__(self, pos, anchor=ANCHOR_CENTRE):
        super().__init__("grass", pos, anchor)

    # Placeholder for grass mechanics
    def update(self):
        pass

# # Class for Player/Mac
class Player(Actor):
    HOP_SPEED = 4
    HOP_DURATION = 10

    def __init__(self, pos, anchor=ANCHOR_CENTRE):
        super().__init__("mac", pos, anchor)

        # USed to indicate direction of movement/facing when advanced graphics implemented
        self.direction = 'down'

        # Used to identify when a motion is being carried out (during movement)
        self.timer = 0

        # Placeholder for Mac mechanics
    def update(self):

        # Perform movement if any is queued up
        if self.timer > 0:
            if self.direction == 'up':
                self.y -= self.HOP_SPEED
            elif self.direction == 'down':
                self.y += self.HOP_SPEED
            elif self.direction == 'left':
                self.x -= self.HOP_SPEED
            elif self.direction == 'right':
                self.x += self.HOP_SPEED

            self.timer -= 1

        # Only check for movemenets if not hopping
        if self.timer == 0:
            # Pick random direction for now
            self.direction = random.choice(["up", "down", "left", "right"])
            self.timer = self.HOP_DURATION



# Class to handle game events
class Game:
    def __init__(self, n_tiles_width, n_tiles_height, tile_size, player=None):
        self.player = player # Should define bot or human player

        self.background_layer = []
        self.foreground_layer = []
        self.player_layer = []

        # Generate initial layout
        # start with dirt for width & height
        background_mask = np.full((tiles_height, tiles_width), 1)

        player_spawn = self.generate_player_spawn(tiles_height, tiles_width)

        # Generate grass and ignore player tile since grass cannot exist on player
        grass_mask = self.generate_grass_mask(n_tiles_height, n_tiles_width, GRASS_PERCENTAGE)
        grass_mask[player_spawn[0]][player_spawn[1]] = False

        for row in range(tiles_height):
            for column in range(tiles_width):
                # Identify coordinates corresponding to tile location
                pos_x = (tile_size/2) + row*tile_size
                pos_y = (tile_size/2) + column*tile_size

                # Generate dirt
                self.background_layer.append(Dirt((pos_x, pos_y)))

                # Generate grass
                if grass_mask[row][column] == True:
                    self.foreground_layer.append(Grass((pos_x, pos_y)))

                # Generate player if at predetermined coordinates
                if column == player_spawn[0]:
                    if row == player_spawn[1]:
                        self.player_layer.append(Player((pos_x, pos_y)))

    def generate_grass_mask(self, rows, columns, probability):
        """Generate a 2D array of boolean values based on a constant random probability."""
        return [[random.random() < probability for _ in range(columns)] for _ in range(rows)]

    def generate_player_spawn(self, n_tiles_height, n_tiles_width):
        x_coord = random.randrange(n_tiles_width)
        y_coord = random.randrange(n_tiles_height)
        return (x_coord, y_coord)

    def update(self):
        # Update all objects
        all_objs = self.background_layer + self.foreground_layer + self.player_layer
        for obj in all_objs:
            if obj:
                obj.update()


    def draw(self):
        # draw all background dirt
        all_objs = self.background_layer + self.foreground_layer + self.player_layer
        for obj in all_objs:
            if obj:
                obj.draw()



# Class to handle game states
class State(Enum):
    MENU = 1
    PLAY = 2
    GAME_OVER = 3

# Update game loop
def update():
    global state, game

    if state == State.MENU:
        if space_pressed():
            # Switch to play state
            state = State.PLAY
            game = Game(Player())
        else:
            game.update()

    elif state == State.PLAY:
        game.update()
        # if game.player.lives < 0:
        #     game.play_sound("over")
        #     state = State.GAME_OVER
        # else:
        #     game.update()

    elif state == State.GAME_OVER:
        if space_pressed():
            # Switch to menu and run a demo game
            state = State.MENU
            game = Game()

def draw_gui():
    # Will be used eventually to put a GUI on the game to show score and whatnot
    pass

# Establish rendering of graphics
def draw():
    game.draw()

    if state == State.MENU:
        # Draw title screen
        screen.blit("title", (0, 0))

    elif state == State.PLAY:
        draw_gui()

    elif state == State.GAME_OVER:
        draw_gui()
        # Draw game over image on top of game
        screen.blit("over", (0, 0))

# Utility function to identify a 'clean' spacebar press
def space_pressed():
    global space_down
    if keyboard.space:
        if space_down:
            return False # Not a press if spacebar was already held down
        else:
            space_down = True
            return True # Only a clean press when spacebar is pressed down when not previously pressed
    else:
        space_down = False
        return False

# Set up inital game state as player
state = State.PLAY

# Convert screen size to tiles
tiles_width = WIDTH//TILE_SIZE
tiles_height = HEIGHT//TILE_SIZE

print(tiles_width)
print(tiles_height)

game = Game(n_tiles_width=tiles_width, n_tiles_height=tiles_height, tile_size=TILE_SIZE)

pgzrun.go()