# Ujala: AI-Powered Traffic Flow Optimization

Ujala is a smart traffic management system that uses a high-resolution camera and an AI-driven object detection model (YOLOv8) to analyze real-time traffic at intersections. By detecting and counting vehicles in designated regions, Ujala provides essential data that can help optimize traffic signal timings for smoother urban flow.

## Features

- **Real-Time Vehicle Detection:** Uses the pre-trained model `yolov8n.pt` to detect vehicles.
- **Region-Based Counting:** Divides the intersection into regions (North, South, East, West) to simulate dynamic traffic control.
- **Visual Feedback:** Displays bounding boxes and region labels on the processed image.
- **Simple & Extendable:** Implemented in Python with OpenCV and Ultralytics YOLO, allowing for further development and integration.

## Directory Structure

abhinavbaiju-ujala/
├── README.md         # Project documentation
├── LICENSE           # MIT License for the project
├── traffic.py        # Main Python script for traffic detection and vehicle counting
└── yolov8n.pt        # Pre-trained YOLOv8 model weights file

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/AbhinavBaiju/Ujala.git
   cd Ujala
   ```

2. **Install required Python packages:**

   ```bash
   pip install opencv-python numpy ultralytics
   ```

## Usage

1. Ensure the `yolov8n.pt` file is in the repository root alongside `traffic.py`.

2. Modify the `image_path` in `traffic.py` to point to your test image (e.g., a snapshot of an intersection).

3. Run the script:

   ```bash
   python traffic.py
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
