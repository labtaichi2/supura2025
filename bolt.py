import cv2
import numpy as np
import time
import random
#import supura_ink_adjustment0620 as add
import ball_class
import icon_class

import pygame
import glob

from importlib import resources
import soundfile, imagefile

const_game_time = 60
class mouseParam:
    def __init__(self, input_img_name):
        #マウス入力用のパラメータ
        self.mouseEvent = {"x":None, "y":None, "event":None, "flags":None}
        #マウス入力の設定
        cv2.setMouseCallback(input_img_name, self.__CallBackFunc, None)
    
    #コールバック関数
    def __CallBackFunc(self, eventType, x, y, flags, userdata):
        self.mouseEvent["x"] = x
        self.mouseEvent["y"] = y
        self.mouseEvent["event"] = eventType    
        self.mouseEvent["flags"] = flags    

    #マウス入力用のパラメータを返すための関数
    def getData(self):
        return self.mouseEvent
    
    #マウスイベントを返す関数
    def getEvent(self):
        return self.mouseEvent["event"]                

    #マウスフラグを返す関数
    def getFlags(self):
        return self.mouseEvent["flags"]                

    #xの座標を返す関数
    def getX(self):
        return self.mouseEvent["x"]  

    #yの座標を返す関数
    def getY(self):
        return self.mouseEvent["y"]  

    #xとyの座標を返す関数
    def getPos(self):
        return (self.mouseEvent["x"], self.mouseEvent["y"])
    
def overlay(fore_img, back_img, shift):
 
    '''
    fore_img：合成する画像
    back_img：背景画像
    shift：左上を原点としたときの移動量(x, y)
    '''
 
    shift_x, shift_y = shift
 
    fore_h, fore_w = fore_img.shape[:2]
    fore_x_min, fore_x_max = 0, fore_w
    fore_y_min, fore_y_max = 0, fore_h
 
    back_h, back_w = back_img.shape[:2]
    back_x_min, back_x_max = shift_x, shift_x+fore_h
    back_y_min, back_y_max = shift_y, shift_y+fore_w
 
    if back_x_min < 0:
        fore_x_min = fore_x_min - back_x_min
        back_x_min = 0
         
    if back_x_max > back_w:
        fore_x_max = fore_x_max - (back_x_max - back_w)
        back_x_max = back_w
 
    if back_y_min < 0:
        fore_y_min = fore_y_min - back_y_min
        back_y_min = 0
         
    if back_y_max > back_h:
        fore_y_max = fore_y_max - (back_y_max - back_h)
        back_y_max = back_h  
 
    back_img[back_y_min:back_y_max, back_x_min:back_x_max] = fore_img[fore_y_min:fore_y_max, fore_x_min:fore_x_max]
 
    return back_img

def initial_screen_setup(window_name, sound_path,capture_img):
    # ボタンが押されるとここが呼び出される
    x = [0] * 4
    y = [0] * 4
    i = 0
    
    #frame2 = cv2.imread('c:\\ensyuu\\sample.png')

    soundeffect_path=sound_path.joinpath('soundeffect') #soundeffectファイルパス
    pygame.mixer.init()    # 初期設定

    #画面範囲の指定
    while (i <  4):     
        #入力画像
        _, frame = capture_img.read()
        #画像の表示
        cv2.imshow(window_name, frame)
        #コールバックの設定
        mouseData = mouseParam(window_name)
    
        cv2.waitKey(20)
        #左クリックがあったら表示
        if mouseData.getEvent() == cv2.EVENT_LBUTTONDOWN:
            print(mouseData.getX() )
            x[i] = mouseData.getX()
            y[i] = mouseData.getY()
            print(x[i],y[i])
            pygame.mixer.music.load(soundeffect_path.joinpath("ok.mp3"))     # 音楽ファイルの読み込み
            pygame.mixer.music.play(1) #1回鳴らす
            i += 1
            
            #右クリックがあったら終了
        #elif mouseData.getEvent() == cv2.EVENT_RBUTTONDOWN:
            #   break;
        
    pts1 = np.float32([[x[0],y[0]],[x[1],y[1]],[x[2],y[2]],[x[3],y[3]]])
    pts2 = np.float32([[0,0],[640,0],[0,480],[640,480]])
    homo = cv2.getPerspectiveTransform(pts1,pts2) 
    cv2.destroyAllWindows()
    return homo

def title(window_name, img_path, sound_path):
    #タイトル
    tmp = True # 4点指定をミスった時にタイトル画面でescapeしたい
    soundeffect_path=sound_path.joinpath('soundeffect')
    
    pygame.mixer.music.load(soundeffect_path.joinpath("title.mp3"))     # 音楽ファイルの読み込み
    pygame.mixer.music.play(-1) 
    while(1):
        #画像の表示
        #cv2.imshow(window_name, start_frame)
        title = cv2.imread(img_path.joinpath('title1.jpg'))#タイトル画像
        start_text = ' PRESS  ENTER '#表示テキスト

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)#ウィンドウの設定
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)#フルスクリーン
        cv2.putText(title,start_text,(200,650),cv2.FONT_HERSHEY_SIMPLEX,3,(0,217,255),thickness=8)
        cv2.imshow(window_name,title)

        start_key = cv2.waitKey(5) & 0xFF
        if start_key == 13: #Enter
            pygame.mixer.music.stop()#音源の停止
            break 

        k = cv2.waitKey(5) & 0xFF
        if  k == 27:
            tmp = False
            break
    
    # if tmp == False:
    #     break

def tutorial(window_name, sound_path, cap, homo, painted_frame):
    #ゲーム準備画面    
    while(1):
        _, frame = cap.read()
        dst = cv2.warpPerspective(frame,homo,(640,480))
        frame_copy = dst.copy()
        #start_frame = np.zeros((480, 640, 3), np.uint8) + 255

        hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)
        # define range of blue color in HSV
        lower_blue = np.array([90,100, 40])
        upper_blue = np.array([130,255,255])
        lower_red1 = np.array([0,150,60]) 
        upper_red1 = np.array([20,255,255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        mask2 = cv2.inRange(hsv, lower_red1, upper_red1)
        
        kernel = np.ones((25,25), np.uint8)
        mask = cv2.morphologyEx(mask,cv2.MORPH_CLOSE, kernel)
        mask2 = cv2.morphologyEx(mask2,cv2.MORPH_CLOSE, kernel)
        
        kernel = np.ones((3,3),np.uint8)
        mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
        mask2 = cv2.morphologyEx(mask2,cv2.MORPH_OPEN,kernel)

        contours,hierarchy = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        item_time = time.time() #itemが表示される時間
        #最大輪郭の抽出
        if len(contours)>0:
            m_area = 0
            m_area_label = 0
            for x,cnt in enumerate(contours): 
                area = cv2.contourArea(cnt)
                if m_area < area:
                    m_area = area
                    m_area_label = x 
                cnt = contours[m_area_label]
        #輪郭の重心を求める
            M = cv2.moments(cnt) 
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
        try:
            cv2.circle(painted_frame,(cx,cy), 25, (255,0,0),-1,4)
        except NameError:
            pass

        contours2,hierarchy2 = cv2.findContours(mask2,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        #最大輪郭の抽出
        if len(contours2)>0:
            m_area2 = 0
            m_area_label2 = 0
            for x2,cnt2 in enumerate(contours2):
                area2 = cv2.contourArea(cnt2)
                if m_area2 < area2:
                    m_area2 = area2
                    m_area_label2 = x2
            cnt2 = contours2[m_area_label2]        
            M = cv2.moments(cnt2)
            cx2 = int(M['m10']/M['m00'])
            cy2 = int(M['m01']/M['m00'])
        try:
            cv2.circle(painted_frame,(cx2,cy2), 25, (0,0,255),-1,4)
        except NameError:
            pass

        cv2.line(frame_copy,(190,200),(190,250),color=(0, 0, 255),thickness=3,lineType=cv2.LINE_4,shift=0)
        cv2.line(frame_copy,(450,200),(450,250),color=(255, 0, 0),thickness=3,lineType=cv2.LINE_4,shift=0)
        move_text = 'Move to starting point'
        cv2.putText(frame_copy,move_text,(90,100),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0))

        start_text = 'Are you ready?'#(90,290)
        cv2.putText(frame_copy,start_text,(90,400),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0),thickness=8)
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        new_frame = cv2.addWeighted(src1=frame_copy,alpha=0.3,src2=painted_frame,beta = 1.5,gamma=1.0)
        new_frame2 = cv2.addWeighted(src1=frame_copy,alpha=0.5,src2=new_frame,beta=1.5,gamma=1.0)
        cv2.imshow(window_name,new_frame2)
        start_key = cv2.waitKey(5) & 0xFF
        if start_key == 13: #Enter
            break
    
    #splatoon_BGM
    bgm_path=sound_path.joinpath('bgmfile')
    list=glob.glob(f'{bgm_path}/*.wav')
    bgm=random.choice(list)
    pygame.mixer.music.load(bgm)
    pygame.mixer.music.set_volume(0.5)
    return 0

def result(SUM, cap, red_count, blue_count, result_ratio_frame, painted_ratio_bar):
        if SUM > 0:
            red_text  = int(100 * red_count/SUM)
            blue_text = 100 - red_text
            
            if red_count > blue_count:
                result_text = ' red win!!'
                
            else:
                result_text = 'blue win!!'
            text = '   red ' + str(red_text) + ' VS blue ' + str(blue_text) #redの前のスペースは結果を真ん中に表示させるために力技でやったから
           
                
        cv2.putText(result_ratio_frame,result_text,(210,170),cv2.FONT_HERSHEY_SIMPLEX,1.5,(255,255,255),thickness = 8)
        cv2.putText(result_ratio_frame,result_text,(210,170),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,0),thickness = 3)
        cv2.putText(result_ratio_frame,text,(45,320),cv2.FONT_HERSHEY_SIMPLEX,1.5,(255,255,255),thickness = 8)
        cv2.putText(result_ratio_frame,text,(45,320),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0,0,0),thickness = 3)
        cv2.line(painted_ratio_bar, (0,0), (0,480), (0,0,0), thickness=1, lineType=cv2.LINE_8, shift=0)

        result = result_ratio_frame
        cv2.namedWindow('result', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('result', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('result',result)
        return 0

def main():
    img_path=resources.files(imagefile) #画像ファイルパス
    sound_path=resources.files(soundfile) #音楽ファイルパス
    cap = cv2.VideoCapture(0)
    homo = initial_screen_setup("input window",sound_path, cap)
    window_name = "kiyasplatoon"
    running=True #ループ条件
    while(running):
        title(window_name, img_path, sound_path)
        result_ratio_frame = np.zeros((480, 640, 3), np.uint8) + 255
        painted_frame = np.zeros((480, 640, 3), np.uint8) # 対戦中の塗られたエリアの画像　カメラ画像に重ねる
        tutorial(window_name, sound_path, cap, homo, painted_frame)
        
            
        #カウントダウン
        test = 3
        while(test > 0):
            start_frame = np.zeros((480, 640, 3), np.uint8) + 255
            #game_time = 3 - (time.time()  -  start_time)
            #time1_text = str(round(game_time,2))
            #print(time1_text)
            cv2.putText(start_frame,str(test),(270,290),cv2.FONT_HERSHEY_SIMPLEX,4,(0,0,0),thickness=8)
            cv2.namedWindow('result_ratio_frame', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('result_ratio_frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('result_ratio_frame',start_frame)
            #if game_time <= 0:
                #break
            cv2.waitKey(1)
            time.sleep(1)
            test = test - 1
        
        cv2.destroyAllWindows()

        
        start_time = time.time()
        test_mask = np.zeros((480, 640, 3), np.uint8)

        ink_max = 10000
        blue = ball_class.ball("blue")
        red = ball_class.ball("red")
        bg = icon_class.bigger(img_path.joinpath("bigger.png"))
        bm = icon_class.bomb(img_path.joinpath("bomb.png"))
        wp = icon_class.weapon(img_path.joinpath("buki.jpg"))
        ir = icon_class.ink_refill(img_path.joinpath("ink_refill.png"))
        mi = icon_class.missile(img_path.joinpath("missile.png"))
        #blue_ink = ink_max
        #red_ink = ink_max
        pre_cx, pre_cy = 0, 0
        pre_cx2, pre_cy2 = 0, 0
        blue_state_mini = np.zeros((50, 50, 3), np.uint8) + 255
        red_state_mini = np.zeros((50, 50, 3), np.uint8) + 255
        pygame.mixer.music.play(-1)

        while(1):
            # Take each frame
            
            _, frame = cap.read()
            dst = cv2.warpPerspective(frame,homo,(640,480))
            frame_copy = dst.copy()
            #frame3 = np.zeros((480, 640, 3), np.uint8) + 255 #frame3　対戦状況
            painted_ratio_bar = np.zeros((15, 610, 3), np.uint8) + 255
            frame4 = np.zeros((15, 640, 3), np.uint8) + 255

            # blue = ball(ink_max=ink_max)
            # red = ball(ink_max=ink_max)
        
            # Convert BGR to HSV
            hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)
            
            # define range of blue color in HSV
            lower_blue = np.array([90,100, 40])
            upper_blue = np.array([130,255,255])
            
            lower_red1 = np.array([0,150,60]) 
            upper_red1 = np.array([20,255,255])
        
            # Threshold the HSV image to get only blue colors
            
            #iterations = 2
            #mask = cv2.dilate(mask,kernel,iterations = iterations)
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            #mask2 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red1, upper_red1)
            #mask2 = cv2.bitwise_or(mask2_1,mask2_2)
            #オープン、クローズ処理
            
            
            kernel = np.ones((25,25), np.uint8)
            mask = cv2.morphologyEx(mask,cv2.MORPH_CLOSE, kernel)
            mask2 = cv2.morphologyEx(mask2,cv2.MORPH_CLOSE, kernel)
            
            kernel = np.ones((3,3),np.uint8)
            mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
            mask2 = cv2.morphologyEx(mask2,cv2.MORPH_OPEN,kernel)

        #青玉を見つける   
            #追加輪郭
            contours,hierarchy = cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            item_time = time.time() #itemが表示される時間
            #最大輪郭の抽出
            if len(contours)>0:
                m_area = 0
                m_area_label = 0
                for x,cnt in enumerate(contours): 
                    area = cv2.contourArea(cnt)
                    if m_area < area:
                        m_area = area
                        m_area_label = x 

                cnt = contours[m_area_label]
            #輪郭の重心を求める
                
                blue.set_center(cnt)
            #重心部分と輪郭内の描画
                cv2.circle(dst,(blue.cx,blue.cy), 10, (255,0,0),-1,4)
        #    

        #青のイベント発生判定
            if blue.down == False:
                if(item_time - bg.while_time >bg.appear_time):#bunustime
                    if bg.rx <blue.cx < (bg.rx + 50) and bg.ry < blue.cy < (bg.ry + 50)  :
                        bg.sound.play()
                        bg.update()
                        paint_power = 50
                        blue.set_state('bigger')
                        if blue.pre_state == "weapon":
                            wp.sound.stop()
                
                if(item_time - wp.while_time > wp.appear_time):
                    if wp.rx <blue.cx < (wp.rx + 50) and wp.ry < blue.cy < (wp.ry + 50)  :
                        wp.sound.play(maxtime=10000)
                        wp.update()
                        #paint_power = 50
                        blue.set_state('weapon')

                if(item_time - bm.while_time >bm.appear_time):
                    if bm.rx <blue.cx < (bm.rx + 50) and bm.ry < blue.cy < (bm.ry + 50) :
                        bm.sound.play(maxtime=1000)
                        cv2.circle(result_ratio_frame,(blue.cx,blue.cy), 80, (255,0,0),-1,4)
                        cv2.circle(test_mask,(blue.cx,blue.cy), 80, (255,0,0),-1,4)
                        # cv2.circle(frame_copy,(blue.cx,blue.cy), 100, (254,255,0),-1,4)
                        bm.update()
                
                if(item_time - ir.while_time >ir.appear_time):
                    if ir.rx <blue.cx < (ir.rx + 50) and ir.ry < blue.cy < (ir.ry + 50) :
                        ir.sound.play(maxtime=1000)
                        blue.ink_refill()
                        ir.update()

                if(item_time - mi.while_time >mi.appear_time):
                    if mi.rx <blue.cx < (mi.rx + 50) and mi.ry < blue.cy < (mi.ry + 50) :
                        blue.set_state('shot')
                        i = 0
                        mi.update()



        # 青のpaint,回復判定
            rr = 3 # recover range
            if ((pre_cx-rr < blue.cx < pre_cx+rr) and (pre_cy-rr < blue.cy < pre_cy+rr)) or blue.down == True:
                blue.ink_recover()
                if item_time - blue.down_time >= 5:
                    blue.down = False
            else:

                if blue.ink > 0:
                    if  bg.effect_time>0 and item_time - bg.start < bg.effect_time and blue.state == 'bigger':
                        result_ratio_frame, test_mask,frame_copy = blue.paint(result_ratio_frame, test_mask,frame_copy)
                        blue_state_mini = bg.image

                    elif wp.effect_time>0 and item_time - wp.start < wp.effect_time and blue.state == 'weapon':
                        result_ratio_frame, test_mask,frame_copy = blue.paint(result_ratio_frame, test_mask,frame_copy)
                        blue_state_mini = wp.image
                        frame_copy = overlay(wp.image, frame_copy, (blue.cx, blue.cy))
                        #test_mask  = overlay(wp.image, test_mask, (blue.cx, blue.cy))
                    
                    else:
                        if blue.state != 'shot':
                            blue.set_state('normal')
                            result_ratio_frame, test_mask,frame_copy = blue.paint(result_ratio_frame, test_mask,frame_copy)
                            blue_state_mini = np.zeros((50, 50, 3), np.uint8) + 255
          
        # 青の着弾アイテム
            if blue.state == 'shot':                
                if i == 0:
                    landing_point = [np.random.randint(480),np.random.randint(640)]
                    mi.sound.play(maxtime=1000)
                    cv2.circle(result_ratio_frame,(landing_point[0],landing_point[1]), mi.missile_radius, (255,0,0),-1,4)
                    cv2.circle(test_mask,(landing_point[0],landing_point[1]), mi.missile_radius, (255,0,0),-1,4)
                    impact_time = time.time()
                    i += 1
                else:
                    if (time.time() - impact_time > mi.impact_interval ):
                        landing_point = [np.random.randint(480),np.random.randint(640)]
                        mi.sound.play(maxtime=1000)
                        cv2.circle(result_ratio_frame,(landing_point[0],landing_point[1]), mi.missile_radius, (255,0,0),-1,4)
                        cv2.circle(test_mask,(landing_point[0],landing_point[1]), mi.missile_radius, (255,0,0),-1,4)
                        # cv2.circle(frame_copy,(landing_point[0],landing_point[1]), 100, (254,255,0),-1,4)
                        impact_time = time.time()
                        i += 1
                    if i == 5:
                        blue.set_state('normal')          

        #赤玉を見つける       
            #追加輪郭 赤
            contours2,hierarchy2 = cv2.findContours(mask2,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            #最大輪郭の抽出
            if len(contours2)>0:
                m_area2 = 0
                m_area_label2 = 0
                for x2,cnt2 in enumerate(contours2):
                    area2 = cv2.contourArea(cnt2)
                    if m_area2 < area2:
                        m_area2 = area2
                        m_area_label2 = x2

                cnt2 = contours2[m_area_label2]
            
                
                red.set_center(cnt2)
                #重心部分と輪郭内の描画
                cv2.circle(dst,(red.cx,red.cy), 10, (0,0,255),-1,4)
        #

        #赤のイベント発生判定
            if red.down == False:
                if(item_time - bg.while_time > bg.appear_time):#bunustime
                    if bg.rx <red.cx < (bg.rx + 50) and bg.ry < red.cy < (bg.ry + 50) :
                        bg.sound.play()
                        bg.update()                           
                        paint_power2 = 50
                        red.set_state('bigger')  
                        if red.pre_state == "weapon":
                            wp.sound.stop()

                if(item_time - wp.while_time > wp.appear_time):
                    if wp.rx <red.cx < (wp.rx + 50) and wp.ry < red.cy < (wp.ry + 50)  :
                        wp.sound.play(maxtime=10000)
                        wp.update()
                        red.set_state('weapon')

                if(item_time - bm.while_time >bm.appear_time):
                    if bm.rx <red.cx < (bm.rx + 50) and bm.ry < red.cy < (bm.ry + 50) :
                        bm.sound.play(maxtime=1000)
                        cv2.circle(result_ratio_frame,(red.cx,red.cy), 80, (0,0,255),-1,4)
                        cv2.circle(test_mask,(red.cx,red.cy), 80, (0,0,255),-1,4)
                        # cv2.circle(frame_copy,(red.cx,red.cy), 100, (0,254,254),-1,4)
                        bm.update()
                        
                if(item_time - ir.while_time >ir.appear_time):
                    if ir.rx <red.cx < (ir.rx + 50) and ir.ry < red.cy < (ir.ry + 50) :
                        ir.sound.play(maxtime=1000)
                        red.ink_refill()
                        ir.update()
                
                if(item_time - mi.while_time >mi.appear_time):
                    if mi.rx <red.cx < (mi.rx + 50) and mi.ry < red.cy < (mi.ry + 50) :
                        red.set_state('shot')
                        i = 0
                        mi.update()



        # 赤のpaint,回復判定
            if ((pre_cx2-rr < red.cx < pre_cx2+rr) and (pre_cy2-rr < red.cy < pre_cy2+rr)) or red.down == True:
                red.ink_recover()
                if item_time - red.down_time >= 5:
                    red.down = False
            else:

                if red.ink > 0:
                    if bg.effect_time > 0 and item_time - bg.start < bg.effect_time and red.state == "bigger":
                        result_ratio_frame, test_mask,frame_copy = red.paint(result_ratio_frame, test_mask,frame_copy)
                        red_state_mini = bg.image
                    
                    elif wp.effect_time>0 and item_time - wp.start < wp.effect_time and red.state == 'weapon':
                        result_ratio_frame, test_mask,frame_copy = red.paint(result_ratio_frame, test_mask,frame_copy) 
                        red_state_mini = wp.image
                        frame_copy = overlay(wp.image, frame_copy,(red.cx, red.cy))
                        
                    else:
                        if red.state != 'shot':
                            red.set_state('normal')
                            result_ratio_frame, test_mask,frame_copy = red.paint(result_ratio_frame, test_mask,frame_copy) 
                            red_state_mini = np.zeros((50, 50, 3), np.uint8) + 255
        # 赤の着弾アイテム
            if red.state == 'shot':
                # i:発射回数
                if i == 0:
                    landing_point = [np.random.randint(480),np.random.randint(640)]
                    mi.sound.play(maxtime=1000)
                    cv2.circle(result_ratio_frame,(landing_point[0],landing_point[1]), mi.missile_radius, (0,0,255),-1,4)
                    cv2.circle(test_mask,(landing_point[0],landing_point[1]), mi.missile_radius, (0,0,255),-1,4)
                    impact_time = time.time()
                    i += 1
                else:
                    if (time.time() - impact_time > mi.impact_interval ):
                        landing_point = [np.random.randint(480),np.random.randint(640)]
                        mi.sound.play(maxtime=1000)
                        cv2.circle(result_ratio_frame,(landing_point[0],landing_point[1]), mi.missile_radius, (0,0,255),-1,4)
                        cv2.circle(test_mask,(landing_point[0],landing_point[1]), mi.missile_radius, (0,0,255),-1,4)
                        # cv2.circle(frame_copy,(landing_point[0],landing_point[1]), 100, (254,255,0),-1,4)
                        impact_time = time.time()
                        i += 1
                    if i == 5:
                        red.set_state('normal') 
                    
            if np.sqrt(np.power(blue.cx-red.cx, 2) + np.power(blue.cy-red.cy, 2)) <= blue.radius + red.radius + 2:
                if blue.state == 'weapon':
                    blue.attack()
                    red.attacked()
                    print("blue attacked to red!")
                    wp.sound.stop()
                elif red.state == 'weapon':
                    red.attack()
                    blue.attacked()
                    print("red attacked to blue!")
                    wp.sound.stop()
                else:
                    pass


            try:
                pre_cx = blue.cx
                pre_cy = blue.cy
            except NameError:
                pass
            try:
                pre_cx2 = red.cx
                pre_cy2 = red.cy
            except  NameError:
                pass

            key = cv2.waitKey(5) & 0xFF
            if key == 27: #Escape
                test_mask = np.zeros((480, 640, 3), np.uint8)
                break

        #対戦状況の表示(painted_ratio_bar)
            b,g,r = cv2.split(result_ratio_frame) # RGB分離
            blue_count = np.count_nonzero((b >= 254) & (g == 0) & (r == 0))# + np.count_nonzero(green2== 128)
            red_count = np.count_nonzero((b == 0) & (g == 0) & (r >= 254)) #+ np.count_nonzero(red2 == 254)
        
            
            SUM = red_count + blue_count
            if SUM > 0:
                
                red_text  = f"{100 * red_count/SUM:5.2f}"
                blue_text = f"{100 * blue_count/SUM:5.2f}"
                
                painted_ratio_bar[ :, 0:round((red_count/SUM)*610), 0] =  0
                painted_ratio_bar[ :, 0:round((red_count/SUM)*610), 1] =  0
                    
                painted_ratio_bar[ :,round((red_count/SUM)*610):610, 1] =  0
                painted_ratio_bar[ :,round((red_count/SUM)*610):610, 2] =  0
                text = ' red ' + red_text + ' VS blue' + blue_text 
                cv2.putText(painted_ratio_bar,text,(222,10),cv2.FONT_HERSHEY_SIMPLEX,0.4,(255,255,255),thickness = 1)
                
                painted_ratio_bar = cv2.hconcat([cv2.resize(red_state_mini,(15,15)), painted_ratio_bar, cv2.resize(blue_state_mini,(15,15))])
        
        
        #    
            #各windowの表示
            
            process_time = time.time()  -  start_time
            process_time2 = const_game_time - process_time
            time_text = str(round(process_time2,1))
            time_text = ' Time : ' + time_text
            
            cv2.rectangle(frame4, (0,0), (int(640*(process_time2/float(const_game_time))),480),(0,255,0), -1)#残り時間
            cv2.putText(frame4,time_text,(0,10),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,0),thickness = 1)

            new_frame = cv2.addWeighted(src1=frame_copy,alpha=0.3,src2=test_mask,beta = 1.5,gamma=1.0)
            new_frame2 = cv2.addWeighted(src1=frame_copy,alpha=0.5,src2=new_frame,beta=1.5,gamma=1.0)
        #イベントマークの設置        
            #painted_ratio_barの赤、青の比
            if(item_time - bg.while_time >bg.appear_time):#if flag1 != 1 and flag2 != 1:
                new_frame2[bg.ry:bg.ry+bg.image.shape[0],bg.rx:bg.rx+bg.image.shape[1] ] = bg.image
            
            if(item_time - bm.while_time >bm.appear_time):
                new_frame2[bm.ry:bm.ry+bm.image.shape[0],bm.rx:bm.rx+bm.image.shape[1] ] = bm.image
            
            if(item_time - wp.while_time >wp.appear_time):
                new_frame2[wp.ry:wp.ry+wp.image.shape[0],wp.rx:wp.rx+wp.image.shape[1] ] = wp.image

            if(item_time - ir.while_time >ir.appear_time):
                new_frame2[ir.ry:ir.ry+ir.image.shape[0],ir.rx:ir.rx+ir.image.shape[1] ] = ir.image
            
            if(item_time - mi.while_time >mi.appear_time):
                new_frame2[mi.ry:mi.ry+mi.image.shape[0],mi.rx:mi.rx+mi.image.shape[1] ] = mi.image

            cv2.putText(new_frame2,str(red.ink),(red.cx, red.cy+50),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0, 0, 0),thickness = 8)
            cv2.putText(new_frame2,str(red.ink),(red.cx, red.cy+50),cv2.FONT_HERSHEY_SIMPLEX,1.5,(255*(1-red.ink/red.ink_max),255*(1-red.ink/red.ink_max),255),thickness = 3)

            cv2.putText(new_frame2,str(blue.ink),(blue.cx, blue.cy+50),cv2.FONT_HERSHEY_SIMPLEX,1.5,(0, 0, 0),thickness = 8)
            cv2.putText(new_frame2,str(blue.ink),(blue.cx, blue.cy+50),cv2.FONT_HERSHEY_SIMPLEX,1.5,(255,255*(1-blue.ink/blue.ink_max),255*(1-blue.ink/blue.ink_max)),thickness = 3)
            
            united_frame = cv2.vconcat([painted_ratio_bar,new_frame2,frame4])
            
            cv2.namedWindow('united_frame', cv2.WINDOW_NORMAL)
            cv2.setWindowProperty('united_frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('united_frame',united_frame)
                
            k = cv2.waitKey(1) & 0xFF
            if  k == 27 or process_time >= const_game_time: #エスケープ
                break
        cv2.destroyAllWindows()
        wp.sound.stop()
        
        result(SUM, cap, red_count, blue_count, result_ratio_frame, painted_ratio_bar)
        key2 = cv2.waitKey(0) & 0xFF
        if key2 == 27:  #27=escape 13=Enter
            pygame.mixer.music.stop()
            running = False
            cap.release()
        elif key2 == 13:
            pygame.mixer.music.stop()
    

if __name__ == '__main__':
    main()
