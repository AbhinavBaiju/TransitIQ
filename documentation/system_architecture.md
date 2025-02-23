# TransitIQ System Architecture and Workflow

## System Overview

TransitIQ is an AI-powered traffic flow optimization system that uses computer vision to detect vehicles and control traffic signals adaptively. The system consists of two main components:

1. Python-based Traffic Detection System (traffic_markers.py)
2. Arduino-based Traffic Controller (traffic_controller.ino)

## System Architecture

```
+------------------------+     Serial      +------------------------+
|   Traffic Detection    |  Communication  |   Traffic Controller   |
|      (Python)         |<--------------->|      (Arduino)         |
+------------------------+                 +------------------------+
         |                                           |
         v                                           v
+------------------------+                 +------------------------+
|    Computer Vision    |                 |    Traffic Signals    |
|     Processing        |                 |    Control Logic      |
+------------------------+                 +------------------------+
```

## Traffic Detection System (traffic_markers.py)

### Components and Data Flow

```
+----------------+     +----------------+     +----------------+
|  YOLO Model    |     |  ArUco Marker  |     |  Lane Analysis  |
|  Car Detection |---->|  Detection     |---->|  & Counting    |
+----------------+     +----------------+     +----------------+
                                                     |
                                                     v
                                            +----------------+
                                            | Serial Data    |
                                            | Transmission   |
                                            +----------------+
```

### Lane Detection using ArUco Markers

```
    [0]---[1]         North Lane        [2]---[3]
     |                                    |
     |                                    |
[12] |                                    | [8]
West |                                    | East
Lane |                                    | Lane
     |                                    |
     |                                    |
    [15]---[14]       South Lane       [9]---[10]

Marker IDs:
- North: [0,1,2,3]
- South: [4,5,6,7]
- East:  [8,9,10,11]
- West:  [12,13,14,15]
```

### Implementation Details

1. **Vehicle Detection (YOLOModel class)**
   - Uses YOLOv3 for real-time vehicle detection
   - Processes frames at 416x416 resolution
   - Filters detections to focus on car class
   - Applies non-maximum suppression for overlapping detections

2. **Lane Analysis (LaneAnalyzer class)**
   - Uses ArUco markers to define lane boundaries
   - Creates polygons from marker positions
   - Counts vehicles within each lane polygon
   - Provides real-time lane occupancy data

3. **Data Transmission**
   - Uses pySerialTransfer for reliable communication
   - Sends structured data containing car counts for each lane
   - Maintains continuous updates at 115200 baud rate

## Traffic Controller System (traffic_controller.ino)

### Hardware Configuration

```
Pin Layout:
North: R[8], Y[9], G[10]
South: R[5], Y[6], G[7]
East:  R[2], Y[3], G[4]
West:  R[11],Y[12],G[13]

R = Red, Y = Yellow, G = Green
```

### Control Logic Flow

```
[Start]
   |
   v
Receive Car Counts
   |
   v
Analyze Traffic
   |     No Cars
   |--------------> Rotate Every 5s
   v
Find Direction with Cars
   |
   v
Transition Signals
   |
   v
Calculate Green Duration
(4s per car)
   |
   v
Update Current Direction
   |
   v
[Repeat]
```

### Signal Transition Sequence

```
Current Phase    Transition Phase    Next Phase
[R][G][R][R] -> [R][Y][R][R] -> [R][R][G][R]
                 (1s delay)

R = Red, Y = Yellow, G = Green
```

## System Operation

1. **Initialization**
   - Python system initializes YOLO model and camera
   - Arduino configures pins and serial communication

2. **Detection Cycle**
   - Camera captures traffic scene
   - YOLO detects vehicles
   - ArUco markers define lane boundaries
   - System counts vehicles per lane

3. **Control Cycle**
   - Car counts transmitted to Arduino
   - Controller determines optimal signal timing
   - Signals transition with safety delays
   - System continuously updates based on new data

## Performance Considerations

1. **Detection Accuracy**
   - YOLO confidence threshold: 0.5
   - NMS threshold: 0.4
   - ArUco marker detection with error handling

2. **Timing Parameters**
   - Yellow light duration: 1 second
   - Green light: 4 seconds per detected vehicle
   - Minimum cycle time: 5 seconds (no cars)

3. **Safety Features**
   - Graceful fallback to image file if camera fails
   - Proper signal transition sequences
   - Error handling for serial communication

## Integration Testing

To test the system:
1. Print and position ArUco markers
2. Configure serial port settings
3. Run traffic_markers.py
4. Monitor detection window and console output
5. Verify Arduino receives and processes data correctly