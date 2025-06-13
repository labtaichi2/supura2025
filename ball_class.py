import cv2
import time
import numpy as np
import pygame
from importlib import resources
import imagefile
from soundfile import soundeffect
imagedir = resources.files(imagefile)
sounddir = resources.files(soundeffect)

class ball():
    def __init__(self,color="blue"or"red"):
        self.cx = 0
        self.cy = 0
        self.ink_max = 300
        self.ink = 300

        if color == "blue":
            self.paint_color = (255,0,0)
        elif color == "red":
            self.paint_color = (0,0,255)
        else:
            pass
       
        self.paint_power = 25

        self.state = "normal"
        self.pre_state = ""
        self.down = False
        self.down_time = 0
        self.sound = pygame.mixer.Sound(sounddir.joinpath('ink.mp3'))
        self.sound2 = pygame.mixer.Sound(sounddir.joinpath('attack.mp3'))
        self.sound.set_volume(0.1)

    def set_state(self, state):
        self.pre_state = self.state
        self.state = state
        if state == "normal":
            self.paint_power = 25
        elif state == "bigger":
            self.paint_power = 50
        elif state == "smaller":
            self.paint_power = 10
        elif state == "turn":
            self.paint_power = 25
        elif state == "weapon":
            self.paint_power = 10


    def set_center(self, cnt):
        center, radius = cv2.minEnclosingCircle(cnt)
        self.cx, self.cy = int(center[0]), int(center[1])
        self.radius = radius
        # M = cv2.moments(cnt) 
        # self.cx = int(M['m10']/M['m00'])
        # self.cy = int(M['m01']/M['m00'])


    def paint(self, frame2, test_mask, frame_copy):
        #self.sound.play(maxtime=1000)
        if self.state == 'turn':
            cv2.circle(frame2,(self.cx,self.cy), self.paint_power, self.paint_color[::-1], -1,4)                 
            cv2.circle(test_mask,(self.cx,self.cy), self.paint_power, (self.paint_color[2]/2, 0, self.paint_color[0]/2), -1,4)
            cv2.circle(frame_copy,(self.cx,self.cy), 15, (self.paint_color[0] ,255 ,self.paint_color[2]), -1,4)            
        else:
            cv2.circle(frame2,(self.cx,self.cy), self.paint_power, self.paint_color, -1,4)                 
            cv2.circle(test_mask,(self.cx,self.cy), self.paint_power, (self.paint_color[0]/2, 0, self.paint_color[2]/2), -1,4)
            cv2.circle(frame_copy,(self.cx,self.cy), 15, (self.paint_color[0] ,255 ,self.paint_color[2]), -1,4)
        self.ink -= 1

        return frame2, test_mask, frame_copy


    def ink_recover(self):
        if self.ink <= self.ink_max-1:
            self.ink += 1
        else:
            self.ink = self.ink_max
    
    def ink_refill(self, recovery_rate=0.2):
        if self.ink <= (1-recovery_rate)*self.ink_max:
            self.ink += int(recovery_rate*self.ink_max)
        else:
            self.ink = self.ink_max
  

    def attack(self):
        self.sound2.play()
        self.state = "normal"
        self.pre_state = "weapon"

    def attacked(self):
        self.down = True
        self.down_time = time.time()



