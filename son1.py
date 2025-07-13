#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 15:25:53 2025

@author: izzet
"""

import cv2, time, serial, threading
import numpy as np


video = cv2.VideoCapture(0)

frame_width = 1920
frame_height = 1080

xy_list = []
bounding_list = []
contour_list = []

prev_frame_time = 0
new_frame_time = 0
second = 0
totalFrame = 0
prev_contour = 0
lastCoordinate = 0
staticFrame = 0


sensitivity = 65

isArduinoAvailable = True

def reset():
    if isArduinoAvailable:
        arduino.write(("250 1600").encode())
        time.sleep(0.1)
        arduino.write(("250 540").encode())

def toggle():
    if isArduinoAvailable:
        arduino.write("9999 9999".encode())

def turn_off():
    if isArduinoAvailable:
        arduino.write("9998 9998".encode())

def turn_on():
    if isArduinoAvailable:
        arduino.write("9998 9999".encode())

def reset_position():
    global second
    while True:
        second += 1
        if second == 20:
            reset()
        time.sleep(0.5)
        if second < 0:
            break

try:
    arduino = serial.Serial(port='/dev/cu.usbserial-1130', baudrate=2000000, timeout=10)
    time.sleep(0.001)
    turn_on()
except serial.serialutil.SerialException:
    print("Arduino bağlantısı başarısız")
    isArduinoAvailable = False


motion_list = [None, None]
static_back = None

font = cv2.QT_FONT_NORMAL

if isArduinoAvailable:
    (threading.Thread(target=reset_position)).start() 
        
while True:
    totalFrame +=1
    
    check, frame = video.read()
    
    try:
        frame = cv2.resize(frame, (frame_width, frame_height))
        motion = 0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except:
        reset()
        time.sleep(0.001)
        turn_off()
        second = -1
        break


    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    gray = cv2.blur(gray, (5, 5))


    if static_back is None:
        static_back = gray
        continue
    


    diff_frame = cv2.absdiff(static_back, gray) 




    thresh_frame = cv2.threshold(diff_frame, sensitivity, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, np.ones([20, 20]), iterations=6)


    cnts, _ = cv2.findContours(thresh_frame.copy(),
                               cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in cnts:
        if (cv2.contourArea(contour) > 20000):
            motion = 1
            contour_list.append(cv2.contourArea(contour))
            (x, y, w, h) = cv2.boundingRect(contour)
            bounding_list.append([x, y, w, h])
            xy_list.append(int((x+(w/2))*(y+(h/2))))

        else:
            continue

        
   
    if len(contour_list) != 0:
       
        prev_contour = min(xy_list, key=lambda a:abs(a-prev_contour))
        
        
        (x, y, w, h) = (bounding_list[xy_list.index(prev_contour)])
        cv2.putText(frame, str(w*h), (x+20, y+30), font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), thickness=3)
        
                
        top_mid = (x + w // 2, y)
        bottom_mid = (x + w // 2, y + h)
        left_mid = (x, y + h // 2)
        right_mid = (x + w, y + h // 2)
        

        parallelogram_points = [top_mid, right_mid, bottom_mid, left_mid]
        
    
        red_dark = (0, 0, 139)
        
     
        for i in range(4):
            cv2.line(frame, parallelogram_points[i], parallelogram_points[(i + 1) % 4], red_dark, 4)
        
     
        cv2.line(frame, top_mid, bottom_mid, red_dark, 4)
        cv2.line(frame, left_mid, right_mid, red_dark, 4)
        
     
        white = (255, 255, 255)
        blue_dark = (139, 0, 0)
        
     
        for point in parallelogram_points:
            cv2.circle(frame, point, 10, white, -1)  
            cv2.circle(frame, point, 6, blue_dark, -1)  
        
     
        center_point = (x + w // 2, y + h // 2)
        cv2.circle(frame, center_point, 10, white, -1)
        cv2.circle(frame, center_point, 6, blue_dark, -1)

      
        print(f"Area({len(xy_list)}) : " + str(xy_list))
        print(f"x : {x} | y : {y}\n")


        alan = w * h
        hiz_etiketi = "Hiz Tanimlaniyor"
        renk = (255, 255, 255)

        if alan > 800000:
            hiz_etiketi = "Cok Hizli Hareket"
            renk = (0, 0, 255)  
        elif 800000 > alan > 300000:
            hiz_etiketi = "Hizli Hareket"
            renk = (0, 165, 255)  
        elif 300000 > alan > 100000:
            hiz_etiketi = "Normal Hareket"
            renk = (0, 255, 255)  
        else:
            hiz_etiketi = "Yavas Hareket" 
            renk = (0, 255, 0)  

        cv2.putText(frame, hiz_etiketi, (x, y - 10), font, 1, renk, 2, cv2.LINE_AA)


    new_frame_time = time.time()
    fps = 1/(new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    fps = int(fps)

    if fps > 20:
        cv2.putText(frame, str(fps) + "/" + str(len(xy_list)), (5, 20), font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    elif (fps <= 20) & (fps >= 10):
        cv2.putText(frame, str(fps) + "/" + str(len(xy_list)), (5, 20), font, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    else:
        cv2.putText(frame, str(fps) + "/" + str(len(xy_list)), (5, 20), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    cv2.imshow("Threshold Frame", thresh_frame)
    cv2.imshow("Color Frame", frame)

    if len(xy_list) != 0:
        if (x != 0) & (isArduinoAvailable):
            try:
                 center_x = int(1920 - ((x + w / 2) * (1920 / frame_width)))
                 center_y = int((y + h / 2) * (1080 / frame_height))  
                 arduino.write(f"{center_x} {center_y}".encode())

            except NameError:
                pass
        x,y = 0,0
        contour_list.clear()
        bounding_list.clear()
        xy_list.clear()

    static_back = gray

    key = cv2.waitKey(1)

    if key == ord('q'):
        video.release()
        reset()
        time.sleep(0.001)
        turn_off()
        
        second = -1
        break
    if key == ord('l'):
        toggle()
    if key == ord('r'):
        reset()
    if key == ord('1'):
        turn_on()
    if key == ord("2"):
        turn_off()

    continue

cv2.destroyAllWindows()