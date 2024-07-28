import cv2
import pandas as pd
from ultralytics import YOLO
import cvzone
import numpy as np
from app.processing.tracker import *
import math
import os
import time
from datetime import datetime

def video_detection(video):
    cap = cv2.VideoCapture(video)
    model = YOLO('app/processing/best.pt')
    my_file = open("app/processing/coco.txt", "r")
    data = my_file.read()
    class_list = data.split("\n")

    count = 0

    trackerHole = Tracker()
    trackerStain = Tracker()
    trackerLine = Tracker()
    trackerKnot = Tracker()
    frame_countHole = 1
    frame_countStain = 1
    frame_countLine = 1
    frame_countKnot = 1
    cy2 = 250
    offset = 8
    countHole = {}
    countStain = {}
    countKnot = {}
    countLine = {}
    Holes = []
    Stains = []
    Knots = []
    Lines = []
    measureUnit = 0.833333
    with open("defect_times.txt", "w") as f:
        startTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        if count % 3 != 0:
            continue
        frame = cv2.resize(frame, (300, 500))

        results = model.predict(frame,conf=0.35, project="D:/tryyolo", name="D:/tryyolo", save=False, save_txt=False, exist_ok=True)
        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")

        listHoles = []
        listStains = []
        listLines = []
        listKnots = []
        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]
            if 'hole' in c:
                listHoles.append([x1, y1, x2, y2])
            elif 'stain' in c:
                listStains.append([x1, y1, x2, y2])
            elif 'line' in c:
                listLines.append([x1, y1, x2, y2])
            elif 'knot' in c:
                listKnots.append([x1, y1, x2, y2])

        bboxHole_idx = trackerHole.update(listHoles)
        bboxStain_idx = trackerStain.update(listStains)
        bboxLine_idx = trackerLine.update(listLines)
        bboxKnot_idx = trackerKnot.update(listKnots)
        for bbox in bboxHole_idx:
            x3, y3, x4, y4, id1 = bbox
            cx3 = int(x3 + x4) // 2
            cy3 = int(y3 + y4) // 2

            if cy2 < (cy3 + offset) and cy2 > (cy3 - offset):
                countHole[id1] = (cx3, cy3)

            if id1 in countHole:
                roi = frame[y3:y4, x3:x4]
                if cy2 < (cy3 + offset) and cy2 > (cy3 - offset):
                    if Holes.count(id1) == 0:
                        Holes.append(id1)
                        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                        image_name = f"Hole_{frame_countHole}_Mask.jpg"
                        cv2.imwrite(f'app\static\defects\Hole_{frame_countHole}_Mask.jpg', roi_gray)
                        # Read the grayscale image
                        # Read the grayscale image
                        # Apply Canny edge detection
                        edges = cv2.Canny(roi_gray, 50, 150)

                        # Step 5: Save the boundary image
                        cv2.imwrite(f'app\static\defects\Hole_{frame_countHole}_boundary.jpg', edges)

                        cv2.circle(frame, (cx3, cy3), 4, (255, 0, 255), -1)
                        cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 0), 2)
                        cvzone.putTextRect(frame, f'{id1}', (x3, y3), 1, 1)

                        image_name = f"app\static\defects\Hole_{frame_countHole}.jpg"
                        cv2.imwrite(image_name, frame)
                        with open("defect_times.txt", "a") as f:

                            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            start_time = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
                            print("Times : ",current_time, start_time)
                            current_datetime = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
                            time_diff = current_datetime - start_time
                            centi = time_diff.total_seconds()
                            value = round(centi/100,2) 
                            
                            meters = round(float(value)*measureUnit,2)
                            if meters == float(0):
                                meters = 0.01
                            f.write(f"Hole_{frame_countHole} {meters} {y3}:{y4}-{x3}:{x4}\n")
                        frame_countHole += 1 
            
        for bbox in bboxStain_idx:
            x5, y5, x6, y6, id2 = bbox
            cx4 = int(x5 + x6) // 2
            cy4 = int(y5 + y6) // 2

            if cy2 < (cy4 + offset) and cy2 > (cy4 - offset):
                countStain[id2] = (cx4, cy4)

            if id2 in countStain:
                roi = frame[y5:y6, x5:x6]
                if cy2 < (cy4 + offset) and cy2 > (cy4 - offset):
                    if Stains.count(id2) == 0:
                        Stains.append(id2)
                        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                        roi_gray_eq = cv2.equalizeHist(roi_gray)
                        image_name = f"Stain_{frame_countStain}_Mask.jpg"
                        cv2.imwrite(f'app\static\defects\Stain_{frame_countStain}_Mask.jpg', roi_gray_eq)
                        # Read the grayscale image
                        # Read the grayscale image
                        # Apply Canny edge detection
                        # Enhance contrast
                        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                        roi_gray = clahe.apply(roi_gray)

                        # Adaptive thresholding
                        blurred = cv2.GaussianBlur(roi_gray, (5, 5), 0)
                        edges = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 4)

                        # Save the boundary image
                        cv2.imwrite(f'app\static\defects\Stain_{frame_countStain}_boundary.jpg', edges)

                        cv2.circle(frame, (cx4, cy4), 4, (255, 0, 255), -1)
                        cv2.rectangle(frame, (x5, y5), (x6, y6), (255, 0, 0), 2)
                        cvzone.putTextRect(frame, f'{id2}', (x5, y5), 1, 1)

                        image_name = f"app\static\defects\Stain_{frame_countStain}.jpg"
                        cv2.imwrite(image_name, frame)
                           
                        with open("defect_times.txt", "a") as f:
                            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            start_time = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
                            current_datetime = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
                            time_diff = current_datetime - start_time
                            centi = time_diff.total_seconds()
                            value = round(centi/100,2) 
                            meters = round(float(value)*measureUnit,2)
                            if meters == float(0):
                                meters = 0.01
                            f.write(f"Stain_{frame_countStain} {meters} {y5}:{y6}-{x5}:{x6}\n")
                        frame_countStain += 1 

        for bbox in bboxKnot_idx:
            x7, y7, x8, y8, id3 = bbox
            cx5 = int(x7 + x8) // 2
            cy5 = int(y7 + y8) // 2

            if cy2 < (cy5 + offset) and cy2 > (cy5 - offset):
                countKnot[id3] = (cx5, cy5)

            if id3 in countKnot:
                roi = frame[y7:y8, x7:x8]
                if cy2 < (cy5 + offset) and cy2 > (cy5 - offset):
                    if Knots.count(id3) == 0:
                        Knots.append(id3)
                        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                        image_name = f"Knot_{frame_countKnot}_Mask.jpg"
                        cv2.imwrite(f'app\static\defects\Knot_{frame_countKnot}_Mask.jpg', roi_gray)
                        # Read the grayscale image
                        # Read the grayscale image
                        # Apply Canny edge detection
                        edges = cv2.Canny(roi_gray, 50, 150)

                        # Step 5: Save the boundary image
                        cv2.imwrite(f'app\static\defects\Knot_{frame_countKnot}_boundary.jpg', edges)

                        cv2.circle(frame, (cx5, cy5), 4, (255, 0, 255), -1)
                        cv2.rectangle(frame, (x7, y7), (x8, y8), (255, 0, 0), 2)
                        cvzone.putTextRect(frame, f'{id3}', (x7, y7), 1, 1)

                        image_name = f"app\static\defects\Knot_{frame_countKnot}.jpg"
                        cv2.imwrite(image_name, frame)
                         
                        with open("defect_times.txt", "a") as f:
                            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            start_time = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
                            current_datetime = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
                            time_diff = current_datetime - start_time
                            centi = time_diff.total_seconds()
                            value = round(centi/100,2) 
                            meters = round(float(value)*measureUnit,2)
                            if meters == float(0):
                                meters = 0.01
                            f.write(f"Knot_{frame_countKnot} {meters} {y7}:{y8}-{x7}:{x8}\n")
                        frame_countKnot += 1

        for bbox in bboxLine_idx:
            x9, y9, x10, y10, id4 = bbox
            cx6 = int(x9 + x10) // 2
            cy6 = int(y9 + y10) // 2

            if cy2 < (cy6 + offset) and cy2 > (cy6 - offset):
                countKnot[id4] = (cx6, cy6)

            if id4 in countLine:
                roi = frame[y9:y10, x9:x10]
                if cy2 < (cy6 + offset) and cy2 > (cy6 - offset):
                    if Lines.count(id4) == 0:
                        Lines.append(id4)
                        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                        image_name = f"Line_{frame_countLine}_Mask.jpg"
                        cv2.imwrite(f'app\static\defects\Line_{frame_countLine}_Mask.jpg', roi_gray)
                        # Read the grayscale image
                        # Read the grayscale image
                        # Apply Canny edge detection
                        edges = cv2.Canny(roi_gray, 50, 150)

                        # Step 5: Save the boundary image
                        cv2.imwrite(f'app\static\defects\Line_{frame_countLine}_boundary.jpg', edges)

                        cv2.circle(frame, (cx6, cy6), 4, (255, 0, 255), -1)
                        cv2.rectangle(frame, (x8, y8), (x10, y10), (255, 0, 0), 2)
                        cvzone.putTextRect(frame, f'{id4}', (x9, y9), 1, 1)

                        image_name = f"app\static\defects\Line_{frame_countLine}.jpg"
                        cv2.imwrite(image_name, frame)
                                 
                        with open("defect_times.txt", "a") as f:
                            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            start_time = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
                            current_datetime = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
                            time_diff = current_datetime - start_time
                            centi = time_diff.total_seconds()
                            value = round(centi/100,2) 
                            meters = round(float(value)*measureUnit,2)
                            if meters == float(0):
                                meters = 0.01
                            

                            f.write(f"Line_{frame_countLine} {meters} {y9}:{y10}-{x9}:{x10}\n")   
                        frame_countLine += 1       
        font_scale = 1.5
        thickness = 2


        bg_color = (0, 0, 0)  
        text_color = (255, 255, 255)  # White
        cv2.line(frame, (3, cy2), (300, cy2), (0, 0, 255), 2)
        cvzone.putTextRect(frame, f'Holes : {len(Holes)}', (15, 130), font_scale, thickness, bg_color, text_color)
        cvzone.putTextRect(frame, f'Stains : {len(Stains)}', (15, 100), font_scale, thickness, bg_color, text_color)
        cvzone.putTextRect(frame, f'Lines : {len(Lines)}', (165, 130), font_scale, thickness, bg_color, text_color)
        cvzone.putTextRect(frame, f'Knots : {len(Knots)}', (165, 100), font_scale, thickness, bg_color, text_color)
        yield frame
    cap.release()
   

