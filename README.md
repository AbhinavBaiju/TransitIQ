<<<<<<< HEAD
# TransitIQ: AI-Powered Traffic Flow Optimization

TransitIQ is a smart traffic management system that leverages computer vision and artificial intelligence to optimize traffic flow at intersections. Using a combination of YOLOv8 object detection and ArUco marker-based region mapping, the system provides real-time vehicle detection and counting in designated intersection zones, enabling dynamic traffic signal control for improved urban mobility.

## Features

- **Advanced Vehicle Detection:** Utilizes YOLOv8 neural network (yolov8n.pt) for accurate, real-time vehicle detection
- **ArUco Marker Integration:** Employs ArUco markers for precise traffic zone mapping and calibration
- **Multi-Region Analysis:** Segments intersection into distinct zones (North, South, East, West) for granular traffic monitoring
- **Real-time Processing:** Provides immediate vehicle detection and counting with visual feedback
- **Arduino Integration:** Communicates traffic data to Arduino-based signal controllers via serial protocol
- **Visual Debugging:** Displays detection boxes, region markers, and traffic statistics in real-time

## Directory Structure

```
transitiq/
├── ai_processing/
│   ├── dependencies/
│   │   ├── coco.names                        # COCO dataset class names
│   │   ├── yolov3.cfg                        # YOLOv3 configuration
│   │   └── yolov3.weights                    # YOLOv3 model weights
│   ├── yolov8n.pt                           # YOLOv8 nano model weights
│   ├── traffic_markers.py                    # Traffic analysis w/ aruco markers
│   ├── traffic_masking.py                    # Traffic analysis w/ coloured masking
│   └── requirements.txt                      # Python dependencies
├── arduino_control/
│   └── traffic_controller/
│       ├── traffic_controller.ino            # Arduino signal control logic
│       └── keywords.txt                      # Arduino IDE syntax config
├── documentation/
│   ├── aruco_mappings.md                    # ArUco marker specifications
│   ├── pin_mappings.md                      # Arduino GPIO configurations
│   ├── protocol_spec.md                      # Serial protocol documentation
│   └── aruco_markers/                       # Generated ArUco markers
│       └── M[0-15].svg                      # Individual marker files
└── test_assets/
    ├── Mask.png                             # Region masking template
    ├── Traffic.png                           # Sample traffic image
    ├── Traffic_Markers.jpg                   # Test image with markers
    └── Traffic_Markers.png                   # Additional test image
```

## Technical Components

### AI Processing Module

- **Vehicle Detection:** Implements YOLOv8 nano model for efficient object detection
- **Region Analysis:** Uses ArUco markers to define and track traffic zones
- **Traffic Analytics:** Provides real-time vehicle counting and zone occupancy data
- **Serial Communication:** Implements checksum-verified data packets for reliable Arduino communication

### Arduino Control System

- **Signal Management:** Controls traffic light timing based on AI-processed data
- **Communication Protocol:** Uses 115200 baud rate serial connection with error checking
- **LED Matrix:** Manages multiple traffic signal displays through GPIO pins
=======
# Ujala: AI-Powered Traffic Flow Optimization

Ujala is a smart traffic management system that uses a high-resolution camera and an AI-driven object detection model (YOLOv8) to analyze real-time traffic at intersections. By detecting and counting vehicles in designated regions, Ujala provides essential data that can help optimize traffic signal timings for smoother urban flow.

## Features

- **Real-Time Vehicle Detection:** Uses the pre-trained model `yolov8n.pt` to detect vehicles.
- **Region-Based Counting:** Divides the intersection into regions (North, South, East, West) to simulate dynamic traffic control.
- **Visual Feedback:** Displays bounding boxes and region labels on the processed image.
- **Simple & Extendable:** Implemented in Python with OpenCV and Ultralytics YOLO, allowing for further development and integration.

## Directory Structure

ujala/
├── ai_processing/  
│   ├── yolov8n.pt                            # Pre-trained YOLOv8 model weights  
│   ├── traffic_processor.py                  # Main vehicle detection & serial comms  
│   └── requirements.txt                      # Python dependencies  
├── arduino_control/  
│   ├── traffic_controller/  
│   │   ├── traffic_controller.ino            # Primary Arduino control code  
│   │   └── keywords.txt                      # Arduino IDE syntax highlighting  
│   └── lib/                                  # Custom Arduino libraries  
├── documentation/  
│   ├── wiring_diagram.pdf                    # Tinkercad-generated circuit schematic  
│   ├── pin_mappings.md                       # GPIO to LED matrix configuration  
│   └── protocol_spec.md                      # Serial communication specifications  
├── test_assets/  
│   ├── test_videos/                          # Sample traffic footage  
│   └── calibration_images/                   # Camera calibration patterns  
└── README.md                                 # Comprehensive setup guide  
>>>>>>> dfb34fe6b9906401cf53677317d7e17972301446

## Installation

1. **Clone the repository:**
<<<<<<< HEAD
   ```bash
   git clone https://github.com/AbhinavBaiju/TransitIQ.git
   cd TransitIQ
   ```

2. **Install Python dependencies:**
   ```bash
   cd ai_processing
   pip install -r requirements.txt
   ```

3. **Arduino Setup:**
   - Open `arduino_control/traffic_controller/traffic_controller.ino` in Arduino IDE
   - Install required Arduino libraries through Library Manager
   - Upload the code to your Arduino board

## Usage

1. **Prepare the intersection setup:**
   - Print and place ArUco markers (found in `documentation/aruco_markers/`)
   - Connect the Arduino controller according to `documentation/pin_mappings.md`
   - Position the camera to capture all markers and traffic lanes

2. **Configure the system:**
   - Verify serial port settings in `traffic_markers.py`
   - Adjust detection parameters if needed

3. **Run the traffic analysis:**
   ```bash
   cd ai_processing
   python traffic_markers.py
   ```

4. **Monitor the output:**
   - View real-time detection window showing vehicle tracking
   - Check console for zone-wise vehicle counts
   - Verify Arduino receiving and processing traffic data

## Contributing

Contributions are welcome! Please read our contribution guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLOv8
- [OpenCV](https://opencv.org/) for computer vision capabilities
- [ArUco](https://docs.opencv.org/master/d5/dae/tutorial_aruco_detection.html) for marker detection

## Project Team

- Muhammad Afsah Mumtaz
- Abhinav Baiju
- Chetana Venkatesh
- Ujwal Kumar Reddy
- Aman Rakesh Krishnan

## Contact

For questions, issues, or collaboration opportunities, please open an issue on GitHub or contact the project maintainers.

## Lane Analysis Methods

### Marker-Based Analysis
The system employs ArUco markers for precise traffic zone definition and analysis. These markers serve as reference points to map and track distinct traffic zones at intersections.

![Traffic Analysis with Markers](test_assets/Traffic_Markers.png)
*ArUco markers define distinct traffic zones for vehicle detection and counting*

### Masking-Based Analysis
In addition to marker-based analysis, the system supports region masking for defining specific areas of interest. This approach allows for flexible zone definition through mask templates.

![Region Masking](test_assets/Mask.png)
*Mask template defining traffic analysis zones*

![Traffic Analysis](test_assets/Traffic.png)
*Real-time traffic monitoring with defined analysis zones*
=======

   ```bash
   git clone https://github.com/AbhinavBaiju/Ujala.git
   cd Ujala
   ```

2. **Install required Python packages:**

   ```bash
   pip install opencv-python numpy ultralytics pyserial
   ```

## Usage

1. Ensure the `yolov8n.pt` file is in the repository root alongside `traffic_processor.py`.

2. Modify the `image_path` in `traffic_processor.py` to point to your test image (e.g., a snapshot of an intersection).

3. Run the script:

   ```bash
   python traffic_processor.py
   ```

4. The script will display the image with detected vehicles and region outlines, and print the vehicle counts for each region in the console.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) for providing the YOLO model framework.
- OpenCV for its powerful computer vision libraries.
- Project Contributors:
  - Muhammad Afsah Mumtaz
  - Abhinav Baiju
  - Chetana Venkatesh
  - Ujwal Kumar Reddy
  - Aman Rakesh Krishnan

## Contact

For inquiries or contributions, please open an issue on GitHub or contact the project maintainer.

---
>>>>>>> dfb34fe6b9906401cf53677317d7e17972301446
