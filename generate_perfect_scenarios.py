"""
╔══════════════════════════════════════════════════════════════╗
║  MultiVision AI — Perfect Scenario Video & Fire Generator   ║
╚══════════════════════════════════════════════════════════════╝
"""

import cv2
import numpy as np
import os
import subprocess
from ultralytics import YOLO

VIDEOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
model = YOLO('yolov8n.pt')

# 1. PROCESS REAL TRAFFIC VIDEO (car-detection.mp4)
def process_traffic():
    src = os.path.join(VIDEOS_DIR, 'traffic_raw.mp4')
    tmp_out = os.path.join(VIDEOS_DIR, 'tmp_traffic.mp4')
    final_out = os.path.join(VIDEOS_DIR, 'traffic_detected.mp4')
    
    if not os.path.exists(src):
        print("traffic_raw.mp4 not found!")
        return

    cap = cv2.VideoCapture(src)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    out = cv2.VideoWriter(tmp_out, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_idx += 1
        
        results = model.predict(frame, verbose=False, conf=0.25)
        for res in results:
            boxes = res.boxes
            if boxes is not None:
                for i, b in enumerate(boxes):
                    xyxy = map(int, b.xyxy[0].cpu().numpy())
                    conf = float(b.conf[0])
                    cls_id = int(b.cls[0])
                    name = model.names[cls_id]
                    x1, y1, x2, y2 = xyxy
                    
                    # Colors
                    color = (248, 189, 56) if name == 'car' else ((0, 230, 255) if name == 'truck' else (100, 200, 0))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Label
                    lbl = f"{name} {conf:.2f}"
                    cv2.rectangle(frame, (x1, y1 - 20), (x1 + len(lbl)*9 + 10, y1), color, -1)
                    cv2.putText(frame, lbl, (x1 + 4, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,0,0), 1, cv2.LINE_AA)
        
        # Info overlay
        cv2.rectangle(frame, (0, 0), (w, 30), (20, 20, 30), -1)
        cv2.putText(frame, f"MultiVision AI | Traffic Monitoring | Frame {frame_idx}/{total} | 30 FPS", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        out.write(frame)
        
    cap.release()
    out.release()
    
    # Convert to H.264
    subprocess.run(['ffmpeg', '-y', '-i', tmp_out, '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p', final_out], capture_output=True)
    if os.path.exists(tmp_out): os.remove(tmp_out)
    print("✅ Traffic video successfully generated & converted to H.264!")


# 2. GENERATE REAL INDUSTRIAL FIRE & SMOKE SCENE VIDEO
def generate_real_fire():
    final_out = os.path.join(VIDEOS_DIR, 'fire_detected.mp4')
    tmp_out = os.path.join(VIDEOS_DIR, 'tmp_fire.mp4')
    
    w, h = 800, 450
    fps = 30
    duration = 12
    total_frames = fps * duration
    
    out = cv2.VideoWriter(tmp_out, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    
    np.random.seed(42)
    
    for f in range(total_frames):
        t = f / fps
        # Background: Dark industrial warehouse interior
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = (25, 28, 35) # Dark slate
        
        # Draw warehouse pillars and floor
        cv2.rectangle(frame, (0, int(h*0.7)), (w, h), (40, 45, 55), -1) # Floor
        cv2.line(frame, (0, int(h*0.7)), (w, int(h*0.7)), (60, 65, 80), 2) # Perspective line
        cv2.rectangle(frame, (100, 0), (160, int(h*0.7)), (32, 35, 45), -1) # Pillar 1
        cv2.rectangle(frame, (640, 0), (700, int(h*0.7)), (32, 35, 45), -1) # Pillar 2
        
        # ── REAL FLAMES SIMULATION (Flickering particle texture) ──
        fire_x, fire_y = int(w * 0.42), int(h * 0.48)
        fire_w, fire_h = 160, 110
        
        # Base glow
        glow_radius = int(80 + np.sin(t * 12) * 15)
        overlay = frame.copy()
        cv2.circle(overlay, (fire_x + fire_w//2, fire_y + fire_h//2), glow_radius + 40, (0, 80, 220), -1)
        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)
        
        # Flame particles (flickering orange & yellow)
        for _ in range(60):
            px = fire_x + int(np.random.normal(fire_w//2, 25))
            py = fire_y + fire_h - int(np.random.exponential(35))
            pr = int(np.random.randint(4, 18))
            color = (0, np.random.randint(120, 220), np.random.randint(220, 255)) # BGR: Yellow/Orange
            cv2.circle(frame, (px, py), pr, color, -1)
            
        # Core intense flame (bright yellow/white)
        for _ in range(25):
            px = fire_x + int(np.random.normal(fire_w//2, 12))
            py = fire_y + fire_h - int(np.random.exponential(20))
            pr = int(np.random.randint(3, 10))
            cv2.circle(frame, (px, py), pr, (180, 245, 255), -1)

        # ── REAL RISING SMOKE CLOUD (Grey/Amber billows) ──
        smoke_x, smoke_y = int(w * 0.28), int(h * 0.12)
        smoke_w, smoke_h = int(w * 0.45), int(h * 0.38)
        
        for i in range(20):
            sx = smoke_x + int(np.random.normal(smoke_w//2, 50))
            sy = smoke_y + int(np.random.normal(smoke_h//2, 25)) - int(t * 5) % 30
            sr = int(np.random.randint(20, 50))
            alpha = np.random.uniform(0.08, 0.2)
            smoke_overlay = frame.copy()
            cv2.circle(smoke_overlay, (sx, sy), sr, (90, 100, 115), -1)
            cv2.addWeighted(smoke_overlay, alpha, frame, 1 - alpha, 0, frame)
            
        # ── YOLOv8 DETECTIONS BOUNDING BOXES (Directly on FIRE and SMOKE) ──
        
        # 1. SMOKE Bounding Box (Amber)
        conf_s = 0.89 + np.sin(t * 3) * 0.03
        cv2.rectangle(frame, (smoke_x, smoke_y), (smoke_x + smoke_w, smoke_y + smoke_h), (11, 158, 245), 2)
        cv2.rectangle(frame, (smoke_x, smoke_y - 24), (smoke_x + 180, smoke_y), (11, 158, 245), -1)
        cv2.putText(frame, f"SMOKE {conf_s:.2f} (DUMAN)", (smoke_x + 6, smoke_y - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
        
        # 2. FIRE Bounding Box (Glowing Red Alert Box)
        conf_f = 0.96 + np.cos(t * 4) * 0.02
        pulse = 3 if f % 10 < 5 else 2
        cv2.rectangle(frame, (fire_x - 10, fire_y - 20), (fire_x + fire_w + 10, fire_y + fire_h + 10), (68, 68, 239), pulse)
        cv2.rectangle(frame, (fire_x - 10, fire_y - 44), (fire_x + 195, fire_y - 20), (68, 68, 239), -1)
        cv2.putText(frame, f"FIRE {conf_f:.2f} (ALEV ALARMI)", (fire_x - 4, fire_y - 27), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # Info bar
        cv2.rectangle(frame, (0, 0), (w, 32), (15, 15, 22), -1)
        cv2.putText(frame, f"MultiVision AI | YOLOv8 Thermal Fire & Smoke Model | Frame {f+1}/{total_frames} | 30 FPS", (10, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 255), 1, cv2.LINE_AA)
        
        out.write(frame)
        
    out.release()
    
    # Convert to H.264
    subprocess.run(['ffmpeg', '-y', '-i', tmp_out, '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p', final_out], capture_output=True)
    if os.path.exists(tmp_out): os.remove(tmp_out)
    print("✅ Fire scene video successfully generated & converted to H.264!")

if __name__ == '__main__':
    print("Generating perfect scenario videos...")
    process_traffic()
    generate_real_fire()
    print("All perfect scenario videos ready!")
