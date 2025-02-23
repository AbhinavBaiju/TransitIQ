# Standard library imports
import os
import struct

# Third-party imports
import cv2
import numpy as np
import requests
from pathlib import Path
import serial

# This module implements traffic detection using color-based lane masking.
# It uses YOLOv3 for car detection and a color mask image to identify lanes.

class YOLODownloader:
    """Handles downloading of YOLO model files from official sources.
    
    This class manages the download of required YOLO model files (weights, config, and class names)
    with proper error handling and progress tracking.
    """
    
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.yolo_files = {
            "yolov3.weights": "https://pjreddie.com/media/files/yolov3.weights",
            "yolov3.cfg": "https://github.com/pjreddie/darknet/raw/master/cfg/yolov3.cfg",
            "coco.names": "https://github.com/pjreddie/darknet/raw/master/data/coco.names"
        }

    def download_files(self):
        self.model_dir.mkdir(parents=True, exist_ok=True)
        for file_name, url in self.yolo_files.items():
            file_path = self.model_dir / file_name
            if not file_path.exists():
                print(f"Downloading {file_name}...")
                try:
                    stream = True if file_name == "yolov3.weights" else False
                    response = requests.get(url, stream=stream)
                    response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        if stream:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        else:
                            f.write(response.content)
                    print(f"Successfully downloaded {file_name}")
                except Exception as e:
                    print(f"Failed to download {file_name}: {str(e)}")
                    raise
            else:
                print(f"{file_name} already exists")

class YOLOModel:
    """Implements YOLOv3-based car detection.
    
    This class loads and initializes the YOLOv3 model for detecting cars in images.
    It handles all aspects of inference including preprocessing, detection, and
    non-maximum suppression.
    """
    
    def __init__(self, model_dir):
        self.net = cv2.dnn.readNet(str(model_dir/"yolov3.weights"), str(model_dir/"yolov3.cfg"))
        with open(model_dir/"coco.names", "r") as f:
            self.classes = [line.strip() for line in f]
        
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i-1] for i in self.net.getUnconnectedOutLayers()]
        self.conf_threshold = 0.5
        self.nms_threshold = 0.4

    def detect(self, image):
        """Detect cars in the input image using YOLOv3.
        
        Args:
            image: numpy.ndarray, Input image in BGR format
            
        Returns:
            tuple: (boxes, confidences, class_ids, indexes)
                - boxes: list of [x, y, w, h] coordinates for each detection
                - confidences: list of confidence scores
                - class_ids: list of class IDs (only cars in this case)
                - indexes: indices of valid detections after NMS
        """
        height, width = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        boxes, confidences, class_ids = [], [], []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.conf_threshold and self.classes[class_id] == "car":
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
        return boxes, confidences, class_ids, indexes

class LaneAnalyzer:
    """Analyzes car positions relative to color-coded lanes.
    
    This class uses a color mask image where each lane is marked with a specific color.
    It matches detected car positions with lane colors to determine car distribution.
    """
    
    def __init__(self, mask, lane_colors, tolerance=20):
        """Initialize the lane analyzer.
        
        Args:
            mask: numpy.ndarray, Color mask image where each lane has a unique color
            lane_colors: dict, Mapping of lane names to BGR color tuples
            tolerance: int, Color matching tolerance (default: 20)
        """
        self.mask = mask
        self.lane_colors = lane_colors
        self.tolerance = tolerance

    def count_cars(self, centers):
        """Count cars in each lane based on their positions.
        
        Args:
            centers: list of (x, y) coordinates representing car centers
            
        Returns:
            dict: Mapping of lane names to car counts
        """
        lane_counts = {lane: 0 for lane in self.lane_colors}
        h, w = self.mask.shape[:2]
        
        for cx, cy in centers:
            cx = np.clip(cx, 0, w-1)
            cy = np.clip(cy, 0, h-1)
            mask_color = self.mask[cy, cx]
            
            best_match = None
            min_dist = float('inf')
            for lane, color in self.lane_colors.items():
                dist = np.linalg.norm(mask_color - color)
                if dist < min_dist and dist <= self.tolerance:
                    min_dist = dist
                    best_match = lane
            
            if best_match:
                lane_counts[best_match] += 1
                
        return lane_counts

class TrafficAnalyzerApp:
    """Main application class for traffic analysis using color-based lane detection.
    
    This class orchestrates the entire traffic analysis process:
    1. Downloads and initializes the YOLO model
    2. Processes input images for car detection
    3. Analyzes car positions relative to lanes
    4. Sends results via serial communication
    """
    
    def __init__(self, model_dir, image_path, mask_path, serial_port):
        """Initialize the traffic analyzer application.
        
        Args:
            model_dir: pathlib.Path, Directory for YOLO model files
            image_path: pathlib.Path, Path to the traffic image
            mask_path: pathlib.Path, Path to the lane color mask image
            serial_port: str, Serial port for communication with traffic controller
        """
        self.model_dir = model_dir
        self.image_path = image_path
        self.mask_path = mask_path
        self.serial_port = serial_port
        self.lane_colors = {
            "North": (255, 0, 0),
            "South": (0, 255, 0),
            "East": (0, 0, 255),
            "West": (255, 255, 0)
        }

    def run(self):
        YOLODownloader(self.model_dir).download_files()
        yolomodel = YOLOModel(self.model_dir)
        
        img = cv2.imread(self.image_path)
        if img is None:
            raise FileNotFoundError(f"Could not load image at {self.image_path}")
        
        mask = cv2.imread(self.mask_path)
        if mask is None:
            raise FileNotFoundError(f"Could not load mask at {self.mask_path}")
        
        h, w = img.shape[:2]
        if mask.shape[:2] != (h, w):
            mask = cv2.resize(mask, (w, h))
        
        boxes, _, _, indexes = yolomodel.detect(img)
        
        centers = []
        for i in indexes.flatten():
            x, y, w_box, h_box = boxes[i]
            centers.append((
                np.clip(x + w_box//2, 0, w-1),
                np.clip(y + h_box//2, 0, h-1)
            ))
        
        analyzer = LaneAnalyzer(mask, self.lane_colors)
        lane_counts = analyzer.count_cars(centers)
        
        print(f"\nTotal Cars Detected: {len(indexes.flatten())}")
        print("Breakdown of Cars in Each Lane:")
        for lane in ["North", "South", "East", "West"]:
            print(f"{lane}: {lane_counts[lane]}")
        
        self.send_serial_data(lane_counts)
        self._show_detections(img, boxes, indexes)

    def send_serial_data(self, lane_counts):
        try:
            north = lane_counts.get("North", 0)
            south = lane_counts.get("South", 0)
            east = lane_counts.get("East", 0)
            west = lane_counts.get("West", 0)

            # Pack data into 4 unsigned shorts (little-endian)
            data = struct.pack('<4H', north, south, east, west)
            
            # Calculate checksum (XOR of all bytes including start byte)
            start_byte = 0xAA
            checksum = start_byte
            for byte in data:
                checksum ^= byte
            
            # Construct packet
            packet = bytes([start_byte]) + data + bytes([checksum])
            
            # Send via serial
            with serial.Serial(self.serial_port, 115200, timeout=1) as ser:
                ser.write(packet)
                print(f"Sent packet: {packet.hex().upper()}")
        except Exception as e:
            print(f"Serial communication error: {str(e)}")

    def _show_detections(self, img, boxes, indexes):
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(img, (x+w//2, y+h//2), 5, (255, 0, 0), -1)
        
        cv2.imshow("Traffic Detections", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    script_dir = Path(__file__).parent.absolute()
    project_dir = script_dir.parent
    model_dir = script_dir / "dependencies"
    
    app = TrafficAnalyzerApp(
        model_dir=model_dir,
        image_path=project_dir / "test_assets" / "Traffic.png",
        mask_path=project_dir / "test_assets" / "Mask.png",
        serial_port="/dev/ttyUSB0"  # Update to your Arduino's port
    )
    app.run()