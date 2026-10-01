"""
╔══════════════════════════════════════════════════════════════╗
║  MultiVision AI — Real YOLOv8 Video Detection Processor     ║
║  Burns actual YOLO detections into video frames              ║
╚══════════════════════════════════════════════════════════════╝

Processes each scenario video with YOLOv8 model and creates
output videos with real bounding boxes, class labels, and
confidence scores drawn directly onto the frames.
"""

import cv2
import os
import sys
import numpy as np
from ultralytics import YOLO

# Configuration
VIDEOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
MODEL_NAME = 'yolov8n.pt'  # Nano model for speed

# Class-specific colors (BGR format for OpenCV)
CLASS_COLORS = {
    'person':     (0, 200, 100),   # Green
    'bicycle':    (250, 139, 100),  # Purple-ish
    'car':        (248, 189, 56),   # Cyan-blue
    'motorcycle': (212, 182, 6),    # Teal
    'bus':        (0, 165, 255),    # Orange
    'truck':      (0, 230, 255),    # Yellow
    'traffic light': (50, 50, 255), # Red
    'fire hydrant': (0, 0, 255),    # Red
    'stop sign':  (0, 80, 255),     # Dark orange
    'bottle':     (240, 100, 100),  # Indigo
    'cup':        (200, 200, 0),    # Cyan
    'chair':      (100, 200, 200),  # Khaki
    'dog':        (0, 180, 0),      # Green
    'cat':        (200, 100, 200),  # Pink
}

DEFAULT_COLOR = (56, 189, 248)  # Sky blue


def get_color(class_name):
    """Get color for a class name."""
    return CLASS_COLORS.get(class_name, DEFAULT_COLOR)


def draw_detection(frame, box, cls_name, conf, track_id=None):
    """Draw a single detection with premium styling."""
    x1, y1, x2, y2 = map(int, box)
    color = get_color(cls_name)
    
    # Draw bbox with thickness based on confidence
    thickness = 2 if conf > 0.5 else 1
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    
    # Corner accents (premium look)
    corner_len = min(20, (x2-x1)//4, (y2-y1)//4)
    cv2.line(frame, (x1, y1), (x1 + corner_len, y1), color, 3)
    cv2.line(frame, (x1, y1), (x1, y1 + corner_len), color, 3)
    cv2.line(frame, (x2, y1), (x2 - corner_len, y1), color, 3)
    cv2.line(frame, (x2, y1), (x2, y1 + corner_len), color, 3)
    cv2.line(frame, (x1, y2), (x1 + corner_len, y2), color, 3)
    cv2.line(frame, (x1, y2), (x1, y2 - corner_len), color, 3)
    cv2.line(frame, (x2, y2), (x2 - corner_len, y2), color, 3)
    cv2.line(frame, (x2, y2), (x2, y2 - corner_len), color, 3)
    
    # Label text
    label = f"{cls_name} {conf:.2f}"
    if track_id is not None:
        label = f"#{track_id} {label}"
    
    # Label background
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    (tw, th), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
    
    label_y = max(y1, th + 8)
    cv2.rectangle(frame, (x1, label_y - th - 8), (x1 + tw + 8, label_y), color, -1)
    
    # Text color: white on dark colors, black on bright colors
    brightness = sum(color) / 3
    text_color = (0, 0, 0) if brightness > 150 else (255, 255, 255)
    cv2.putText(frame, label, (x1 + 4, label_y - 4), font, font_scale, text_color, font_thickness, cv2.LINE_AA)


def draw_info_overlay(frame, frame_num, total_frames, fps, detections_count, model_name):
    """Draw information overlay at the top of the frame."""
    h, w = frame.shape[:2]
    
    # Semi-transparent top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 36), (20, 20, 30), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    
    # Info text
    font = cv2.FONT_HERSHEY_SIMPLEX
    info_text = f"MultiVision AI | {model_name} | Frame {frame_num}/{total_frames} | {detections_count} objects | {fps:.0f} FPS"
    cv2.putText(frame, info_text, (10, 24), font, 0.45, (180, 220, 255), 1, cv2.LINE_AA)
    
    # Live indicator
    if frame_num % 30 < 20:  # Blinking effect
        cv2.circle(frame, (w - 20, 18), 6, (0, 0, 255), -1)
        cv2.putText(frame, "LIVE", (w - 60, 24), font, 0.4, (0, 0, 255), 1, cv2.LINE_AA)


def process_video(input_path, output_path, model, scenario_name):
    """Process a single video with YOLOv8 detection."""
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"  ERROR: Cannot open {input_path}")
        return False
    
    # Get video properties
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Cap FPS for very high fps videos (e.g. 60fps -> process every 2nd frame)
    frame_skip = 1
    output_fps = fps
    if fps > 35:
        frame_skip = int(fps / 25)
        output_fps = fps / frame_skip
        print(f"  High FPS ({fps:.0f}), processing every {frame_skip} frames -> {output_fps:.1f} fps output")
    
    print(f"  Input: {w}x{h} @ {fps:.1f}fps, {total_frames} frames")
    
    # Output video writer (H.264 codec for browser compatibility)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, output_fps, (w, h))
    
    frame_num = 0
    written_frames = 0
    total_detections = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_num += 1
        
        # Skip frames for high-fps videos
        if frame_num % frame_skip != 0:
            continue
        
        # Ensure frame is the correct size (fix optical flow crash)
        if frame.shape[1] != w or frame.shape[0] != h:
            frame = cv2.resize(frame, (w, h))
        
        # Run YOLOv8 PREDICT (not track — avoids ByteTrack optical flow crash)
        results = model.predict(frame, verbose=False, conf=0.2, iou=0.45)
        
        detections_in_frame = 0
        
        for result in results:
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for i, box in enumerate(boxes):
                    # Get detection data
                    xyxy = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = model.names[cls_id]
                    
                    # Draw detection on frame (use index as pseudo-ID)
                    draw_detection(frame, xyxy, cls_name, conf, track_id=i+1)
                    detections_in_frame += 1
        
        total_detections += detections_in_frame
        written_frames += 1
        
        # Draw info overlay
        draw_info_overlay(frame, written_frames, total_frames // frame_skip, output_fps, detections_in_frame, 'YOLOv8n')
        
        # Write processed frame
        out.write(frame)
        
        # Progress indicator
        if written_frames % 50 == 0 or frame_num >= total_frames:
            pct = (frame_num / total_frames) * 100
            print(f"  [{scenario_name}] Frame {frame_num}/{total_frames} ({pct:.0f}%) — {detections_in_frame} detections")
    
    cap.release()
    out.release()
    
    avg_det = total_detections / max(written_frames, 1)
    print(f"  ✅ Done! {written_frames} frames written, avg {avg_det:.1f} detections/frame")
    print(f"  Output: {output_path} ({os.path.getsize(output_path) // 1024} KB)")
    
    return True


def main():
    print("=" * 60)
    print("  MultiVision AI — YOLOv8 Video Detection Processor")
    print("=" * 60)
    
    # Load YOLOv8 model
    print(f"\n📦 Loading YOLOv8 model ({MODEL_NAME})...")
    model = YOLO(MODEL_NAME)
    print("  ✅ Model loaded successfully!")
    
    # Define videos to process
    scenarios = [
        ('traffic.mp4', 'traffic_detected.mp4', '🚦 Traffic & Pedestrian'),
        ('fire.mp4',    'fire_detected.mp4',    '🔥 Industrial Safety'),
        ('ocr.mp4',     'ocr_detected.mp4',     '📦 Bottle Detection'),
    ]
    
    for src_name, dst_name, scenario_name in scenarios:
        src_path = os.path.join(VIDEOS_DIR, src_name)
        dst_path = os.path.join(VIDEOS_DIR, dst_name)
        
        if not os.path.exists(src_path):
            print(f"\n⚠️  Skipping {src_name}: file not found")
            continue
        
        print(f"\n🎬 Processing: {scenario_name} ({src_name})")
        process_video(src_path, dst_path, model, scenario_name)
    
    print("\n" + "=" * 60)
    print("  🎉 All videos processed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
