import cv2
import numpy as np
import os
import math

os.makedirs('videos', exist_ok=True)
fps = 30
duration = 10 # 10 seconds loop
total_frames = fps * duration
width, height = 800, 450

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# 1. TRAFFIC VIDEO GENERATOR
print("Generating videos/traffic.mp4...")
out_traffic = cv2.VideoWriter('videos/traffic.mp4', fourcc, fps, (width, height))

for f in range(total_frames):
    t = f / fps
    # Dark asphalt road
    img = np.ones((height, width, 3), dtype=np.uint8) * 30
    
    # Road lanes
    cv2.rectangle(img, (100, 0), (700, height), (40, 40, 45), -1)
    
    # Lane dashes
    dash_offset = int((t * 200) % 40)
    for y in range(-40 + dash_offset, height + 40, 40):
        cv2.line(img, (300, y), (300, y + 20), (200, 200, 200), 2)
        cv2.line(img, (500, y), (500, y + 20), (200, 200, 200), 2)
        
    # Virtual Counting Line
    cv2.line(img, (100, 250), (700, 250), (0, 0, 255), 2)
    
    # Moving White Sedan Car (Lane 1)
    car1_y = int((t * 120) % (height + 100)) - 50
    cv2.rectangle(img, (160, car1_y), (250, car1_y + 70), (220, 220, 225), -1)
    cv2.rectangle(img, (170, car1_y + 15), (240, car1_y + 55), (100, 100, 110), -1) # Windshield
    cv2.circle(img, (175, car1_y + 70), 5, (255, 255, 200), -1) # Headlights
    cv2.circle(img, (235, car1_y + 70), 5, (255, 255, 200), -1)

    # Moving Amber Truck (Lane 2)
    truck_y = int(((t * 90) + 150) % (height + 140)) - 70
    cv2.rectangle(img, (360, truck_y), (460, truck_y + 110), (30, 140, 220), -1)
    cv2.rectangle(img, (370, truck_y + 20), (450, truck_y + 90), (20, 90, 160), -1)

    # Moving Red Scooter/Motorcycle (Lane 3)
    moto_y = int(((t * 150) + 80) % (height + 80)) - 40
    cv2.rectangle(img, (570, moto_y), (600, moto_y + 40), (50, 50, 220), -1)
    cv2.circle(img, (585, moto_y + 10), 8, (200, 200, 200), -1) # Helmet

    # Moving Pedestrian on sidewalk
    ped_y = int(200 + math.sin(t*3)*30)
    cv2.circle(img, (50, ped_y), 10, (50, 200, 100), -1)
    cv2.rectangle(img, (44, ped_y + 10), (56, ped_y + 35), (50, 200, 100), -1)

    out_traffic.write(img)

out_traffic.release()

# 2. FIRE & SMOKE VIDEO GENERATOR
print("Generating videos/fire.mp4...")
out_fire = cv2.VideoWriter('videos/fire.mp4', fourcc, fps, (width, height))

for f in range(total_frames):
    t = f / fps
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Factory background grid
    for x in range(0, width, 50):
        cv2.line(img, (x, 0), (x, height), (25, 20, 20), 1)
    for y in range(0, height, 50):
        cv2.line(img, (0, y), (width, y), (25, 20, 20), 1)

    # Rising Smoke Particles
    for i in range(12):
        sx = int(400 + math.sin(t*2 + i)*60 + (i*15))
        sy = int(220 - (i*18) - (t*40)%60)
        radius = int(25 + i*5)
        cv2.circle(img, (sx, sy), radius, (100, 100, 110), -1)

    # Flickering Flame Core
    for i in range(15):
        fx = int(400 + math.sin(t*8 + i)*20)
        fy = int(340 - (i*12) + math.cos(t*6)*10)
        radius = int(35 - i*2)
        if radius > 0:
            color = (0, int(100 + i*10), int(220 + i*2)) # Orange to Yellow
            cv2.circle(img, (fx, fy), radius, color, -1)

    out_fire.write(img)

out_fire.release()

# 3. INDUSTRIAL OCR CONVEYOR VIDEO GENERATOR
print("Generating videos/ocr.mp4...")
out_ocr = cv2.VideoWriter('videos/ocr.mp4', fourcc, fps, (width, height))

font = cv2.FONT_HERSHEY_SIMPLEX

for f in range(total_frames):
    t = f / fps
    img = np.ones((height, width, 3), dtype=np.uint8) * 20
    
    # Conveyor Belt Track
    cv2.rectangle(img, (0, 200), (width, 320), (45, 45, 55), -1)
    
    # Belt Rollers
    for x in range(0, width, 40):
        rx = int((x + t*80) % width)
        cv2.rectangle(img, (rx, 305), (rx + 15, 315), (90, 90, 100), -1)

    # Cardboard Box Moving on Belt
    box_x = int((t * 120) % (width + 200)) - 150
    box_y = 170
    
    # Box shape
    cv2.rectangle(img, (box_x, box_y), (box_x + 180, box_y + 110), (30, 120, 210), -1) # Brown cardboard
    cv2.rectangle(img, (box_x + 10, box_y + 10), (box_x + 170, box_y + 100), (20, 90, 170), 2)
    
    # Printed OCR Text Label on Box
    cv2.rectangle(img, (box_x + 25, box_y + 25), (box_x + 155, box_y + 85), (240, 240, 240), -1)
    cv2.putText(img, 'LOT #A0214', (box_x + 32, box_y + 48), font, 0.5, (10, 10, 10), 2)
    cv2.putText(img, 'NET: 500g', (box_x + 32, box_y + 72), font, 0.5, (10, 10, 10), 2)

    # Scanner Laser Line
    cv2.line(img, (400, 0), (400, height), (0, 255, 120), 2)

    out_ocr.write(img)

out_ocr.release()

print("All 3 MP4 videos successfully generated in ./videos/ !")
