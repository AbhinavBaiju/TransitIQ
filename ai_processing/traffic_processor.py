import cv2
import serial
from ultralytics import YOLO
from serial.tools import list_ports

class TrafficProcessor:
    def __init__(self):
        self.model = YOLO('ai_processing/yolov8n.pt')
        self.cap = cv2.VideoCapture(0)  # USB camera input
        self.ser = self.init_serial()
        
    def init_serial(self):
        arduino_ports = [
            p.device for p in list_ports.comports()
            if 'Arduino' in p.description
        ]
        if not arduino_ports:
            raise IOError("No Arduino found")
        return serial.Serial(arduino_ports[0], 115200, timeout=1)
    
    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        results = self.model(frame, imgsz=640, conf=0.25, verbose=False)[0]
        counts = {'N':0, 'S':0, 'E':0, 'W':0}
        
        for box in results.boxes.xyxy:
            x_center = (box[0] + box[2]) / 2
            y_center = (box[1] + box[3]) / 2
            
            if x_center < 320:
                counts['W' if y_center < 240 else 'N'] += 1
            else:
                counts['E' if y_center < 240 else 'S'] += 1
                
        return counts
    
    def send_counts(self, counts):
        payload = f"{counts['N']},{counts['S']},{counts['E']},{counts['W']}\n"
        self.ser.write(payload.encode('utf-8'))
    
    def run(self):
        try:
            while True:
                counts = self.process_frame()
                if counts:
                    self.send_counts(counts)
        except KeyboardInterrupt:
            self.cap.release()
            self.ser.close()

if __name__ == "__main__":
    TrafficProcessor().run()
