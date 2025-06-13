from bdb import effective
from math import e
import cv2
import numpy as np
import time
import random
import pygame
from importlib import resources
from soundfile import soundeffect
sounddir = resources.files(soundeffect)

class eventIcon():
    def __init__(self, img_path):
        self.image = cv2.imread(img_path)
        self.rx = random.randint(0,590)          # アイコンの出現位置x 旧bonus_rangex, small_bonus_rangex,etc..
        self.ry = random.randint(0,300)          # アイコンの出現位置y 旧bonus_rangey, etc..
        self.while_time = time.time()           # ↓で使用する変数
        self.appear_time = random.randint(3,10) # 〇秒後にアイコンが出現する時間　旧big_time,small_time,etc..
        self.effect_time = 0                    # イベントの効果時間　旧power_time
        self.start = 0                          # アイコンに触れた瞬間のtime　旧start_bonus, start_reverse, etc..

    def update(self): # アイコンに触れた判定の時，実行する
        self.rx = random.randint(0,590)
        self.ry = random.randint(0,300)
        self.while_time = time.time()
        self.effect_time = 5
        self.appear_time = random.randint(self.effect_time,10)
        self.start = time.time() # <- while_timeでよくね？

    def appear(self, frame2, test_mask): # イベントアイコンの設置
        frame2[self.ry : self.ry+self.image.shape[0], self.rx : self.rx+self.image.shape[1] ] = self.image
        test_mask[self.ry : self.ry+self.image.shape[0], self.rx : self.rx+self.image.shape[1] ] = self.image


class bigger(eventIcon):
    def __init__(self, img):
        super().__init__(img) # インスタンス生成後にeventIconのメンバ変数がインスタンス固有のものになるかは未検証
        self.sound = pygame.mixer.Sound(sounddir.joinpath('big.mp3'))
        self.sound.set_volume(1.0)


class weapon(eventIcon):
    def __init__(self, img):
        super().__init__(img)
        self.sound = pygame.mixer.Sound(sounddir.joinpath('weapon1.mp3'))
        self.sound.set_volume(1.0)

    def update(self):
        super().update()
        self.effect_time = 10
        self.appear_time = 10
    

class bomb(eventIcon):
    def __init__(self, img):
        super().__init__(img)
        self.sound = pygame.mixer.Sound(sounddir.joinpath('bom.mp3'))
        self.sound.set_volume(1.0)
    
class ink_refill(eventIcon):
    def __init__(self, img):
        super().__init__(img)
        self.sound = pygame.mixer.Sound(sounddir.joinpath('ink_refill.mp3'))
        self.sound.set_volume(1.0)
        
class missile(eventIcon):
    def __init__(self, img):
        super().__init__(img) # インスタンス生成後にeventIconのメンバ変数がインスタンス固有のものになるかは未検証
        self.sound = pygame.mixer.Sound(sounddir.joinpath('bom.mp3'))
        self.sound.set_volume(1.0)
        self.missile_radius = 60
        self.missile_num = 5
        self.impact_interval = 1

