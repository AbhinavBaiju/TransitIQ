import cv2
import numpy as np
from ultralytics import YOLO

def count_cars_in_regions(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Could not load image at path: {image_path}")
    
    # Get image dimensions
    height, width = image.shape[:2]
    
    # Define regions based on the intersection layout
    regions = {
        "North": [(width - width//4, 0), (width, height//4)],  # Top-right corner
        "South": [(0, height - height//4), (width//4, height)],  # Bottom-left corner
        "East": [(width - width//4, height - height//4), (width, height)],  # Bottom-right corner
        "West": [(0, 0), (width//4, height//4)]  # Top-left corner
    }
    
    # Load YOLO model
    model = YOLO('yolov8n.pt')
    
    # Perform detection with lower confidence threshold
    results = model(image, conf=0.2)[0]
    
    # Initialize car counts
    car_counts = {
        "North": 0,
        "South": 0,
        "East": 0,
        "West": 0
    }
    
    # Create a copy of the image for visualization
    display_image = image.copy()
    
    # Get class names from YOLO model
    class_names = model.names
    
    # Count cars in each region
    for detection in results.boxes.data:
        x1, y1, x2, y2, conf, cls = detection
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        cls = int(cls)
        
        # Print detected object class for debugging
        print(f"Detected: {class_names[cls]} with confidence {conf:.2f}")
        
        # Draw detection box with class name
        label = f'{class_names[cls]} {conf:.2f}'
        cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(display_image, label, (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Calculate center of detected object
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Check which region the detection belongs to
        for direction, ((x1_reg, y1_reg), (x2_reg, y2_reg)) in regions.items():
            if (x1_reg <= center_x <= x2_reg and 
                y1_reg <= center_y <= y2_reg and 
                cls in [2, 3, 5, 7]):  # car, motorcycle, bus, truck
                car_counts[direction] += 1
    
    # Draw regions
    colors = {
        "North": (255, 0, 0),   # Blue
        "South": (0, 0, 255),   # Red
        "East": (0, 255, 0),    # Green
        "West": (255, 255, 0)   # Cyan
    }
    
    for direction, ((x1, y1), (x2, y2)) in regions.items():
        cv2.rectangle(display_image, (x1, y1), (x2, y2), colors[direction], 2)
        cv2.putText(display_image, direction, (x1, y1 - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[direction], 2)
    
    # Show the image
    cv2.imshow('Traffic Detection', display_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return car_counts

def main():
    # Use absolute path or ensure the image exists in the correct location
    image_path = '/Users/abhinav/Desktop/Univeresity/emergingTechnology/Project/traffic_placeholder.png'
    try:
        car_counts = count_cars_in_regions(image_path)
        print("Car counts in each direction:", car_counts)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure the image file exists at the specified path.")

if __name__ == "__main__":
    main()