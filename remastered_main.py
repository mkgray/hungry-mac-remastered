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

# ADJUST NUMBER OF BUNNIES
NUMBER_OF_BUNS = 3

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
        self.state = 'exists'
        self.timer = 0

    def detect_interaction(self, intended_x, intended_y):
        # Check x coordinate
        if (abs(self.x-intended_x) < TILE_SIZE/2) & (abs(self.y-intended_y) < TILE_SIZE/2):
            return True
        return False

    def perform_interaction(self):
        self.state = 'consuming'
        self.timer = 20
        return 'consume'

    # Placeholder for grass mechanics
    def update(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                state = 'removed'

# # Class for Player/Mac
class Player(Actor):
    HOP_SPEED = 4
    HOP_DURATION = 10
    CONSUME_DURATION = 20

    IDLE_DELAY_AVERAGE = 20
    IDLE_DELAY_VARIANCE = 8

    def __init__(self, pos, anchor=ANCHOR_CENTRE):
        super().__init__("mac", pos, anchor)

        # USed to indicate direction of movement/facing when advanced graphics implemented
        self.direction = 'down'
        self.action = 'none'

        # Used to identify when a motion is being carried out (during movement)
        self.timer = 0

        # Randomize the colour of the bun
        self.colour = random.choice(["white", "black"])

        # Placeholder for Mac mechanics
    def update(self):

        # If idling, count down timer until next action to be performed
        if (self.timer > 0) & (self.action == 'none'):
            self.timer -= 1

        # Perform movement if any is queued up
        if (self.timer > 0) & (self.action == 'hop'):
            if self.direction == 'up':
                self.y -= self.HOP_SPEED
            elif self.direction == 'down':
                self.y += self.HOP_SPEED
            elif self.direction == 'left':
                self.x -= self.HOP_SPEED
            elif self.direction == 'right':
                self.x += self.HOP_SPEED

            self.timer -= 1

            # When hop is over, return to idle state and randomize time until next action
            if self.timer == 0:
                self.action = 'none'
                self.image = 'sit_' + self.direction + '_' + self.colour
                self.timer = random.randint(self.IDLE_DELAY_AVERAGE-self.IDLE_DELAY_VARIANCE, self.IDLE_DELAY_AVERAGE+self.IDLE_DELAY_VARIANCE)

        # Perform consume action if any is queued up
        if (self.timer > 0) & (self.action == 'consume'):
            if (self.timer == self.CONSUME_DURATION):
                sounds.bite.play(0)
            self.timer -= 1

            # When consume is over, return to idle state and randomize time until next action
            if self.timer == 0:
                self.action = 'none'
                self.image = 'sit_' + self.direction + '_' + self.colour
                self.timer = random.randint(self.IDLE_DELAY_AVERAGE-self.IDLE_DELAY_VARIANCE, self.IDLE_DELAY_AVERAGE+self.IDLE_DELAY_VARIANCE)

        # Only check for movemenets if not hopping
        if (self.timer == 0) & (self.action == 'none'):
            # Pick random direction for now
            # TODO: Add ability to determine if movement is valid or not
            intended_direction = random.choice(["up", "down", "left", "right"])
            if intended_direction == 'up':
                intended_y = self.y - self.HOP_SPEED*self.HOP_DURATION
                intended_x = self.x
            elif intended_direction == 'down':
                intended_y = self.y + self.HOP_SPEED*self.HOP_DURATION
                intended_x = self.x
            elif intended_direction == 'left':
                intended_x = self.x - self.HOP_SPEED*self.HOP_DURATION
                intended_y = self.y
            elif intended_direction == 'right':
                intended_x = self.x + self.HOP_SPEED*self.HOP_DURATION
                intended_y = self.y

            # For validity check: Loop through all collission objects to check if any collision, if so invoke the appropriate response
            movement_allowed = True
            interaction_type = 'none'

            # Movement must be within game boundaries
            if (intended_x < 0) | (intended_x > WIDTH):
                movement_allowed = False
                interaction_type = 'blocked'

            if (intended_y < 0) | (intended_y > HEIGHT):
                movement_allowed = False
                interaction_type = 'blocked'

            for obj in game.foreground_layer:
                if obj.detect_interaction(intended_x, intended_y):
                    movement_allowed = False
                    interaction_type = obj.perform_interaction()

            if movement_allowed:
                self.direction = intended_direction
                self.timer = self.HOP_DURATION
                self.action = 'hop'
                self.image = 'jump_' + intended_direction + '_' + self.colour

            if ~movement_allowed:
                if interaction_type == 'consume':
                    self.direction = intended_direction
                    self.image = 'sit_' + intended_direction + '_' + self.colour
                    #TODO: TRIGGER CHOMP ACTION
                    self.timer = self.CONSUME_DURATION
                    self.action = "consume"



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

        player_spawns = [self.generate_player_spawn(tiles_height, tiles_width) for x in range(NUMBER_OF_BUNS)]

        # Generate grass and ignore player tile since grass cannot exist on player
        grass_mask = self.generate_grass_mask(n_tiles_height, n_tiles_width, GRASS_PERCENTAGE)

        # Remove all grass tiles that a bun spawns on
        for x in player_spawns:
            grass_mask[x[0]][x[1]] = False

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

                # Generate bunnies if at predetermined coordinates
                for x in player_spawns:
                    if column == x[0]:
                        if row == x[1]:
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

        # Update relevant objects to clean up any objects no longer active
        self.foreground_layer = [x for x in self.foreground_layer if x.state == 'exists']


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