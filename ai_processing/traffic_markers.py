# Standard library imports
from pathlib import Path
# Third-party imports
import cv2
import numpy as np
import requests
from serial import Serial
from serialtransfer import SerialTransfer

# This module implements traffic detection using ArUco marker-based lane detection.
# It uses YOLOv3 for car detection and ArUco markers to define lane boundaries.

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
    """Analyzes car positions relative to lanes defined by ArUco markers.
    
    This class uses ArUco markers to define lane boundaries. Each lane is defined by
    a set of 4 markers that form a polygon. Cars are counted based on their position
    relative to these lane polygons.
    """
    
    def __init__(self):
        # ArUco setup for newer OpenCV versions
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        # Lane definitions (marker IDs for each lane)
        self.lane_markers = {
            "North": [0, 1, 2, 3],
            "South": [4, 5, 6, 7],
            "East": [8, 9, 10, 11],
            "West": [12, 13, 14, 15]
        }
    
    def detect_markers(self, image):
        """Detect ArUco markers in the input image.
        
        Args:
            image: numpy.ndarray, Input image in BGR format
            
        Returns:
            tuple: (corners, ids)
                - corners: list of detected marker corners
                - ids: list of corresponding marker IDs
                
        Raises:
            ValueError: If no markers are detected in the image
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = self.aruco_detector.detectMarkers(gray)
        
        if ids is None:
            raise ValueError("No markers detected in the image")
            
        return corners, ids
    
    def create_lane_polygons(self, corners, ids):
        """Create lane polygons from detected ArUco markers.
        
        Args:
            corners: list, Detected marker corners from detect_markers()
            ids: list, Corresponding marker IDs
            
        Returns:
            dict: Mapping of lane names to numpy arrays defining lane polygons
        """
        lane_polygons = {}
        
        for lane_name, marker_ids in self.lane_markers.items():
            lane_corners = []
            for marker_id in marker_ids:
                idx = np.where(ids == marker_id)[0]
                if len(idx) > 0:
                    # Get center of marker
                    marker_corners = corners[idx[0]][0]
                    center = np.mean(marker_corners, axis=0)
                    lane_corners.append(center)
            
            if len(lane_corners) >= 3:  # Need at least 3 points for a polygon
                lane_polygons[lane_name] = np.array(lane_corners, np.int32)
        
        return lane_polygons
    
    def count_cars(self, centers, image):
        """Count cars in each lane based on their positions relative to lane polygons.
        
        Args:
            centers: list, (x, y) coordinates of detected car centers
            image: numpy.ndarray, Input image for marker detection
            
        Returns:
            tuple: (lane_counts, lane_polygons)
                - lane_counts: dict mapping lane names to car counts
                - lane_polygons: dict mapping lane names to polygon coordinates
        """
        corners, ids = self.detect_markers(image)
        lane_polygons = self.create_lane_polygons(corners, ids)
        lane_counts = {lane: 0 for lane in self.lane_markers.keys()}
        
        for center in centers:
            point = np.array(center)
            for lane, polygon in lane_polygons.items():
                if cv2.pointPolygonTest(polygon, (float(point[0]), float(point[1])), False) >= 0:
                    lane_counts[lane] += 1
        
        return lane_counts, lane_polygons

class TrafficAnalyzerApp:
    """Main application class for traffic analysis using ArUco marker-based lane detection.
    
    This class orchestrates the entire traffic analysis process:
    1. Downloads and initializes the YOLO model
    2. Processes input images for car detection
    3. Analyzes car positions relative to ArUco-defined lanes
    4. Sends results via serial communication
    5. Displays visualization of detections and lane boundaries
    """
    
    def __init__(self, model_dir, image_path, serial_port):
        """Initialize the traffic analyzer application.
        
        Args:
            model_dir: pathlib.Path, Directory for YOLO model files
            image_path: pathlib.Path, Path to the traffic image with ArUco markers
            serial_port: str, Serial port for communication with traffic controller
        """
        self.model_dir = model_dir
        self.image_path = image_path
        self.serial_port = serial_port

    def run(self):
        YOLODownloader(self.model_dir).download_files()
        yolomodel = YOLOModel(self.model_dir)
        
        img = cv2.imread(self.image_path)
        if img is None:
            raise FileNotFoundError(f"Could not load image at {self.image_path}")
        
        boxes, _, _, indexes = yolomodel.detect(img)
        
        centers = []
        for i in indexes.flatten():
            x, y, w_box, h_box = boxes[i]
            centers.append((x + w_box//2, y + h_box//2))
        
        analyzer = LaneAnalyzer()
        lane_counts, lane_polygons = analyzer.count_cars(centers, img)
        
        print(f"\nTotal Cars Detected: {len(indexes.flatten())}")
        print("Breakdown of Cars in Each Lane:")
        for lane in ["North", "South", "East", "West"]:
            print(f"{lane}: {lane_counts[lane]}")
        
        self.send_serial_data(lane_counts)
        self._show_detections(img, boxes, indexes, lane_polygons)

    def send_serial_data(self, lane_counts):
        try:
            # Create a SerialTransfer object
            xfer = SerialTransfer(self.serial_port)
            xfer.open()

            # Create a struct that matches Arduino's data structure
            class CarCounts(object):
                def __init__(self):
                    self.north = lane_counts.get("North", 0)
                    self.south = lane_counts.get("South", 0)
                    self.east = lane_counts.get("East", 0)
                    self.west = lane_counts.get("West", 0)

            # Send data using SerialTransfer
            counts = CarCounts()
            xfer.send(counts)
            print(f"Sent car counts: N={counts.north}, S={counts.south}, E={counts.east}, W={counts.west}")
            
            # Close the connection
            xfer.close()
                
        except Exception as e:
            print(f"Serial communication error: {str(e)}")

    def _show_detections(self, img, boxes, indexes, lane_polygons):
        # Draw lane polygons
        debug_image = img.copy()
        for lane, polygon in lane_polygons.items():
            cv2.polylines(debug_image, [polygon], True, (0, 255, 0), 2)
        
        # Draw car detections with thicker borders for better visibility
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (255, 0, 0), 3)  # Increased thickness to 3
            cv2.circle(debug_image, (x+w//2, y+h//2), 5, (0, 0, 255), -1)
        
        # Display the image and wait for a key press
        cv2.imshow("Traffic Detections", debug_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    script_dir = Path(__file__).parent.absolute()
    project_dir = script_dir.parent
    model_dir = script_dir / "dependencies"
    
    app = TrafficAnalyzerApp(
        model_dir=model_dir,
        image_path=project_dir / "test_assets" / "Traffic_Markers.png",
        serial_port="/dev/ttyUSB0"  # Update to your Arduino's port
    )
    app.run()