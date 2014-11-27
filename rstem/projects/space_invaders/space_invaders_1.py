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
#This is the first project in the "Space invaders" series.
#This project shows how to make the players dot move with the
#accelerometer and keep track of its position.
#Imports
from rstem import led_matrix
from rstem import accel
import RPi.GPIO as GPIO
import time

#Initialize matrix, accelerometer, and GPIO, the matrix layout and accelerometer channel may changes from user to user
led_matrix.init_grid(2)
accel.init(1)
#Game entity data
player_pos = [7, 0]

#Function to clamp data to the size of the screen
def clamp(x):
    return max(0, min(x, 15))

try:
#    Start game
    while True:

#       Clear previous framebuffer    
        led_matrix.fill(0)
        
#       Get angles from accelerometer
        data = accel.angles()

#       Generate smooth movement data using IIR filter, and make a 1/4 turn move
#       the player to the edge of the screen
        player_pos[0] = player_pos[0] + (clamp(data[0]*8*4/90 + 7) - player_pos[0])*0.1
    
#       Draw player
        led_matrix.point(int(round(player_pos[0])), int(round(player_pos[1])))

#       Show framebuffer
        led_matrix.show()

#       Delay one game tick, in this case 1ms
        time.sleep(0.001)

#Stop if player hits Ctrl-C
except KeyboardInterrupt:
        pass

#Clean everything up
finally:
        led_matrix.cleanup()
