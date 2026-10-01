import cv2
import numpy as np
import os
import math

os.makedirs('videos', exist_ok=True)
fps = 30
duration = 10
total_frames = fps * duration
w, h = 854, 480

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# 1. TRAFFIC REAL VIDEO GENERATION
print("Rendering videos/traffic.mp4...")
out_tr = cv2.VideoWriter('videos/traffic.mp4', fourcc, fps, (w, h))

for f in range(total_frames):
    t = f / fps
    img = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Asphalt surface with texture
    img[:, :] = (35, 38, 42)
    
    # Sidewalks
    cv2.rectangle(img, (0, 0), (90, h), (70, 75, 80), -1)
    cv2.rectangle(img, (w - 90, 0), (w, h), (70, 75, 80), -1)
    
    # Road lanes
    cv2.rectangle(img, (90, 0), (w - 90, h), (40, 44, 48), -1)
    
    # Lane line dashes
    dash_offset = int((t * 220) % 50)
    for y in range(-50 + dash_offset, h + 50, 50):
        cv2.line(img, (w//3, y), (w//3, y + 25), (220, 220, 230), 3)
        cv2.line(img, (2*w//3, y), (2*w//3, y + 25), (220, 220, 230), 3)

    # Virtual Counting Line
    cv2.line(img, (90, 260), (w - 90, 260), (0, 0, 240), 2)
    cv2.putText(img, 'VIRTUAL COUNTING LINE', (110, 252), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Moving Car 1 (White Sedan)
    c1_y = int((t * 140) % (h + 120)) - 60
    cv2.rectangle(img, (180, c1_y), (275, c1_y + 80), (230, 235, 240), -1)
    cv2.rectangle(img, (190, c1_y + 15), (265, c1_y + 65), (80, 85, 90), -1)

    # Moving Truck (Amber)
    tr_y = int(((t * 100) + 200) % (h + 160)) - 80
    cv2.rectangle(img, (370, tr_y), (475, tr_y + 120), (30, 140, 220), -1)

    # Moving Motorcycle
    m_y = int(((t * 180) + 100) % (h + 90)) - 50
    cv2.rectangle(img, (580, m_y), (615, m_y + 45), (180, 40, 40), -1)

    # Pedestrian on sidewalk
    p_y = int(220 + math.sin(t*2.5)*40)
    cv2.circle(img, (45, p_y), 10, (50, 180, 90), -1)

    out_tr.write(img)

out_tr.release()

# 2. FIRE REAL VIDEO GENERATION
print("Rendering videos/fire.mp4...")
out_fi = cv2.VideoWriter('videos/fire.mp4', fourcc, fps, (w, h))

for f in range(total_frames):
    t = f / fps
    img = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Factory warehouse background
    img[:, :] = (15, 12, 20)
    
    # Warehouse structural columns
    for x in range(100, w, 200):
        cv2.rectangle(img, (x, 0), (x + 30, h), (40, 35, 45), -1)

    # Thermal Radial Heat Glow
    heat = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.circle(heat, (w//2, h//2 + 40), 180, (0, 60, 180), -1)
    cv2.circle(heat, (w//2, h//2 + 40), 100, (0, 140, 240), -1)
    heat = cv2.GaussianBlur(heat, (99, 99), 0)
    img = cv2.addWeighted(img, 1.0, heat, 0.6, 0)

    # Rising Smoke Clouds
    for i in range(15):
        sx = int(w//2 + math.sin(t*3 + i)*50 + (i*12))
        sy = int(h//2 - (i*18) - (t*50)%80)
        r = int(30 + i*6)
        smoke_col = (110, 110, 120)
        cv2.circle(img, (sx, sy), r, smoke_col, -1)

    # Flickering Flames
    for i in range(18):
        fx = int(w//2 + math.sin(t*10 + i)*25)
        fy = int(h//2 + 90 - (i*12) + math.cos(t*8)*10)
        r = int(40 - i*2)
        if r > 0:
            flame_col = (0, int(120 + i*8), int(220 + i*2))
            cv2.circle(img, (fx, fy), r, flame_col, -1)

    out_fi.write(img)

out_fi.release()

# 3. OCR REAL VIDEO GENERATION
print("Rendering videos/ocr.mp4...")
out_ocr = cv2.VideoWriter('videos/ocr.mp4', fourcc, fps, (w, h))

for f in range(total_frames):
    t = f / fps
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = (25, 28, 35)

    # Conveyor belt track
    cv2.rectangle(img, (0, 220), (w, 340), (45, 50, 60), -1)
    for x in range(0, w, 40):
        rx = int((x + t*90) % w)
        cv2.rectangle(img, (rx, 325), (rx + 15, 335), (90, 95, 105), -1)

    # Moving Cardboard Box
    bx = int((t * 140) % (w + 220)) - 180
    by = 190
    cv2.rectangle(img, (bx, by), (bx + 190, by + 120), (35, 125, 215), -1) # Cardboard brown

    # Text Label on Box
    cv2.rectangle(img, (bx + 25, by + 25), (bx + 165, by + 95), (245, 245, 245), -1)
    cv2.putText(img, 'LOT #A0214', (bx + 32, by + 52), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (15, 15, 15), 2)
    cv2.putText(img, 'NET: 500g', (bx + 32, by + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (15, 15, 15), 2)

    # Green Scanner Beam
    cv2.line(img, (w//2, 0), (w//2, h), (0, 240, 120), 2)

    out_ocr.write(img)

out_ocr.release()

print("Real videos generated in ./videos/ !")
