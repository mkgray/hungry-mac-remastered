import pgzero, pgzrun, pygame
from enum import Enum
import numpy as np

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
# class Grass(Actor):
#     def __init__(self, pos, anchor=ANCHOR_CENTRE):
#         image = "grass"
#         super().__init__("blank", pos, anchor)

# # Class for Player/Mac
# class Player(Actor):
#     image = "grass"
#     super().__init__("Mac", pos, anchor)


# Class to handle game events
class Game:
    def __init__(self, n_tiles_width, n_tiles_height, tile_size, player=None):
        self.player = player # Should define bot or human player

        self.background_layer = []

        # Generate initial layout
        # start with dirt for width & height
        background_mask = np.full((tiles_height, tiles_width), 1)

        for row in range(tiles_height):
            for column in range(tiles_width):
                pos_x = (tile_size/2) + row*tile_size
                pos_y = (tile_size/2) + column*tile_size
                self.background_layer.append(Dirt((pos_x, pos_y)))
                #self.background_layer = [[Dirt((i, j)) for j in range(tiles_width) for i in range(tiles_height)]]

        #interactive_layer = np.zeros((tiles_height, tiles_width))

        #player_x_start = tiles_width//2
        #player_y_start = tiles_height//2
        #player_coordinates = (player_x_start, player_y_start)

    def update(self):
        # Update all objects
        for obj in self.background_layer:
            if obj:
                obj.update()

    def draw(self):
        # draw all background dirt
        for obj in self.background_layer:
            if obj:
                obj.draw()

        # # draw all interactive objects
        # for obj in interactive_objects:
        #     obj.draw()

        # # draw the player
        # self.player.draw()



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