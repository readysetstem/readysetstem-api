#!/usr/bin/env python3

#
# Copyright (c) 2014, Scott Silver Labs, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time
import os
import random
import sys

# notify of progress
print("P25")
sys.stdout.flush()

from rstem import led_matrix
import RPi.GPIO as GPIO

# notify of progress
print("P50")
sys.stdout.flush()

# initialization
#led_matrix.init_grid(angle=270)  # make longwise
led_matrix.init_matrices([(0,8),(8,8),(8,0),(0,0)])

GPIO.setmode(GPIO.BCM)

# notify of progress
print("P70")
sys.stdout.flush()

# game variables
score = 0
BLINKING_TIME = 7 # number of cycles to blink full lines
speed = 0.5  # speed of piece falling down (at start)
init_speed = speed

class State(object):
    IDLE, RESET, MOVINGDOWN, BLINKING, DONE, EXIT = range(6)
    
curr_state = State.IDLE
curr_piece = None
next_piece = None
stack = None
sidebar = None
blinking_clock = 0

# setup buttons
UP = 25
DOWN = 24
LEFT = 23
RIGHT = 18
SELECT = 22
START = 27
A = 4
B = 17

"""Shape names as described in U{http://en.wikipedia.org/wiki/Tetris}"""
SHAPES = "IJLOSTZ"
shape_sprites = {}
for shape in SHAPES:
    # store LEDSprite of tetris piece
    sprite = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tetris_sprites", shape + ".spr")
    shape_sprites[shape] = led_matrix.LEDSprite(sprite)

# notify of progress
print("P80")
sys.stdout.flush()

def valid_shape(shape):
    """
    @returns: True if given shape is a valid tetris shape
    """
    return shape in SHAPES and len(shape) == 1

class Sidebar(object):
    """Represents the side bar to the right of the stack. Will show score and next piece"""
    def __init__(self, x_pos):
        self.x_pos = x_pos
        
    def draw(self):
        led_matrix.line((self.x_pos, 0), (self.x_pos, led_matrix.height()-1))
        # draw the next piece
        next_piece.draw(pos=(self.x_pos + 3, led_matrix.height() - 5))
        # draw the score (aligned nicely)
        if score < 10:
            led_matrix.text(str(score), (self.x_pos + 5, 1))
        else:
            led_matrix.text(str(score), (self.x_pos + 1, 1))

class Stack(object):
    """Represents the stack of rested tetris pieces"""
    def __init__(self, width=None):
        self.points = [] # 2D list that represents stacks's color for each point
        # if width is none, use the entire screen
        if width is None:
            self.width = led_matrix.width()
        else:
            self.width = width
        
    def height(self):
        return len(self.points)
        
        
    def add(self, piece):
        """Adds given piece to the stack
        @param piece: piece to add to stack, should be touching current stack
        @type piece: L{Piece}
        """
        for y_offset, line in enumerate(reversed(piece.sprite.bitmap)): # iterate going up
            # check if we need to add a new line to the stack
            if (piece.pos[1] + y_offset) > (len(stack.points) - 1):
                assert piece.pos[1] + y_offset == len(stack.points)
                # add a new line to stack and fill with transparent pixels (this is new top of stack)
                self.points.append([16 for i in range(self.width)])
            # add line of piece to top of stack
            for x_offset, pixel in enumerate(line):
                # add piece if not transparent
                if pixel != 16:
                    stack.points[piece.pos[1] + y_offset][piece.pos[0] + x_offset] = pixel
                    
    def draw(self, blinking_off=False):
        """Draws stack on led display
        @param blinking_off: If set, it will display full lines as a line of all color == 0.
            Useful for blinking full lines.
        @type blinking_off: boolean
        """
        for y, line in enumerate(self.points):
            # show a line of color == 0 for full lines if currently blinking off
            if blinking_off and all(pixel != 16 for pixel in line):  # short-circuit avoids heavy computation if not needed
                led_matrix.line((0,y), (self.width-1, y), color=0)
            else:
                for x, pixel in enumerate(line):
                    led_matrix.point(x, y, pixel)
                    
    def coverage(self):
        """
        @returns: A set of the points that make up the stack
        """
        ret = set()
        for y, line in enumerate(self.points):
            for x, pixel in enumerate(line):
                if pixel != 16:
                    ret.add((x, y))
        return ret
            
                    
    def remove_full_lines(self):
        """Removes lines that are full from stack
        @returns: number of full lines removed
        @rtype: int        
        """
        # remove lines in reverse so we don't mess it up if multiple lines need to be removed
        score = 0
        for y, line in reversed(list(enumerate(self.points))):
            if all(pixel != 16 for pixel in line):
                score += 1
                del self.points[y]
        return score
    


class Piece(object):

    def __init__(self, shape, pos=None):
        if not valid_shape(shape):
            raise ValueError("Not a valid shape")
        if pos is None:
            self.pos = (int(stack.width/2 - 1), int(led_matrix.height()))
        else:
            self.pos = pos
        self.sprite = shape_sprites[shape].copy()  # get a copy of sprite
        
    def rotate(self, clockwise=True):
        """Rotates the piece clockwise or counter-clockwise"""
        # TODO: probably fix this, because I don't think it will rotate like I want it to
        if clockwise:
            self.sprite.rotate(90)
        else:
            self.sprite.rotate(270)
            
        # move piece over if goes off display
        while self.pos[0] + self.sprite.width - 1 >= stack.width:
            self.pos = (self.pos[0] - 1, self.pos[1])
        
    def coverage(self, pos=None):
        """Returns the set of points that the piece is covering.
        @param pos: Set if we want to test the coverage as if the piece was at
            that location.
        @type pos: (x,y)
        @returns: A set of points that the piece is covering
        @rtype: set of 2 tuples
        """
        if pos is None:
            pos = self.pos
        coverage = set()
        for y, line in enumerate(reversed(self.sprite.bitmap)):
            for x, pixel in enumerate(line):
                if pixel != 16:  # ignore transparent pixels in converage
                    coverage.add((pos[0] + x, pos[1] + y))
        return coverage
            
    def can_movedown(self):
        """Tests whether piece can move down without colliding with other piece
        or falling off edge (hit bottom)
        @param stack: current stack object
        @type stack: L{Stack}
        @rtype: boolean
        """
        # check if it is at bottom of screen
        if self.pos[1] <= 0:
            return False
        
        # get coverage pretending we moved down
        pos = (self.pos[0], self.pos[1] - 1)
        self_coverage = self.coverage(pos)
        stack_coverage = stack.coverage()
        return (len(self_coverage.intersection(stack.coverage())) == 0)
        
    def movedown(self):
        """Moves piece down one pixel."""
        self.pos = (self.pos[0], self.pos[1] - 1)
        
    def moveright(self):
        new_pos = (self.pos[0] + 1, self.pos[1])
        # if we are not running off the stack width and not running into the stack, change position
        if self.pos[0] + self.sprite.width < stack.width  \
            and len(self.coverage(new_pos).intersection(stack.coverage())) == 0:
            self.pos = new_pos
    
    def moveleft(self):
        new_pos = (self.pos[0] - 1, self.pos[1])
        # if we are not running off the display and not running into the stack, change position
        if self.pos[0] - 1 >= 0  \
            and len(self.coverage(new_pos).intersection(stack.coverage())) == 0:
            self.pos = new_pos
        
    def draw(self, pos=None):
        """Draws piece on led matrix"""
        if pos is None:
            led_matrix.sprite(self.sprite, self.pos)
        else:
            led_matrix.sprite(self.sprite, pos)
   

# what to do when button is pressed
def button_handler(channel):
    global curr_state
    if channel in [START, SELECT]:
        curr_state = State.EXIT
        return
    if curr_state == State.MOVINGDOWN and curr_piece is not None:
        try:
            if channel == LEFT:
                while GPIO.input(LEFT) == 0:
                    curr_piece.moveleft()
                    time.sleep(.2)
            elif channel == RIGHT:
                while GPIO.input(RIGHT) == 0:
                    curr_piece.moveright()
                    time.sleep(.2)
            elif channel == A or channel == UP:
                curr_piece.rotate(90)
        except AttributeError:
            # catch AttributeError that can happen if curr_piece is NoneType
            pass
    elif (curr_state == State.IDLE or curr_state == State.DONE) and channel == A:
        curr_state = State.RESET

# set button handler to physical buttons 
GPIO.setmode(GPIO.BCM)
for button in [UP, DOWN, LEFT, RIGHT, SELECT, START, A, B]:
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(button, GPIO.FALLING, callback=button_handler, bouncetime=100)

# notify of progress
print("P90")
sys.stdout.flush()
    
# create intro title (a vertical display of "TETRIS")
title = led_matrix.LEDText("S").rotate(90)
for character in reversed("TETRI"):
    # append a 1 pixel wide (high) spacing
    title.append(led_matrix.LEDSprite(width=1, height=title.height))
    # append next character
    title.append(led_matrix.LEDText(character).rotate(90))
# rotate title up
title.rotate(-90)


# notify menu we are ready for the led matrix
print("READY")
sys.stdout.flush()
        
while True:
    # state when a piece is slowly moving down the display
    if curr_state == State.MOVINGDOWN:
        # up speed if score is a multiple of 5
        if score != 0 and score % 5 == 0:
            new_speed = init_speed - (score/5*0.1)
            if new_speed > 0:
                speed = new_speed
    
        # check if stack hit the top of display
        if stack.height() >= led_matrix.height() - 1:
            curr_state = State.DONE
            continue
            
        # check if piece can't move down, and if so, add piece to stack and start blinking any full lines
        if not curr_piece.can_movedown():
            stack.add(curr_piece)  # add piece to stack
            curr_piece = None      # piece is no longer curr_piece
            blinking_clock = BLINKING_TIME  # set up blinking clock 
            curr_state = State.BLINKING     # goto blinking state
            continue
            
        # otherwise move piece down
        curr_piece.movedown()
        
        # show screen
        led_matrix.erase()
        curr_piece.draw()
        stack.draw()
        if sidebar is not None:
            sidebar.draw()
        led_matrix.show()
        
        # speed up delay if DOWN button is held down
        if GPIO.input(DOWN) == 0:
            time.sleep(.005)
        else:
            time.sleep(speed)

    # when piece has hit that stack and we determine if a line has been filled
    elif curr_state == State.BLINKING:
        # when blinking clock counts down to zero, remove full lines and start a new piece
        if blinking_clock == 0:
            score += stack.remove_full_lines() # add full lines to total score
            # make a new next_piece and goto moving the new curr_piece down
            curr_piece = next_piece
            next_piece = Piece(random.choice(SHAPES))
            curr_state = State.MOVINGDOWN
        else:
            # draw blinking full lines (if any)
            led_matrix.erase()
            # draw stack with full lines off every other cycle
            stack.draw(blinking_off=(blinking_clock % 2))
            if sidebar is not None:
                sidebar.draw()
            led_matrix.show()
            blinking_clock -= 1
            time.sleep(.1)
        
    elif curr_state == State.IDLE:
        # display scrolling virtical text
        y_pos = - title.height
        while y_pos < led_matrix.height():
            # if state changes stop scrolling and go to that state
            if curr_state != State.IDLE:
                break
            # display title in the center of the screen
            led_matrix.erase()
            led_matrix.sprite(title, (int(led_matrix.width()/2) - int(title.width/2), y_pos))
            led_matrix.show()
            y_pos += 1
            time.sleep(.1)
        
    elif curr_state == State.RESET:
        score = 0
        stack = None
        if led_matrix.width() < 16:
            stack = Stack()
        else:
            stack = Stack(8)  # if screen too width only use left half for stack
            sidebar = None
            sidebar = Sidebar(8)
        curr_piece = Piece(random.choice(SHAPES))
        next_piece = Piece(random.choice(SHAPES))
        curr_state = State.MOVINGDOWN
        
    elif curr_state == State.DONE:
        led_matrix.erase()
        led_matrix.text(str(score))
        led_matrix.show()
        
    elif curr_state == State.EXIT:
        GPIO.cleanup()
        led_matrix.cleanup()
        sys.exit(0)
        
        
