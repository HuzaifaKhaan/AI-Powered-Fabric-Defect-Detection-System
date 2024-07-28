import cv2
import numpy as np
import time

# Load YOLO
net = cv2.dnn.readNet("/content/yolov3.weights", "/content/yolov3.cfg")

classes = []
with open("/content/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]

# Function to detect objects and save frames
def detect_and_save(frame, frame_count):
    height, width, channels = frame.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Showing information on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    detected_frame = frame.copy()  # Create a copy of the frame for saving the detected video
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            cv2.rectangle(detected_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(detected_frame, label, (x, y + 30), font, 3, (0, 255, 0), 3)

    # Save the frame with detected objects
    cv2.imwrite("/content/detected_frames/detected_frame_{}.jpg".format(frame_count), detected_frame)

    return detected_frame

# Open the video file
cap = cv2.VideoCapture("/content/cricket.mp4")

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object
out = cv2.VideoWriter('/content/detected_video.avi', cv2.VideoWriter_fourcc(*'MJPG'), fps, (frame_width,frame_height))

frame_count = 0
start_time = time.time()
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    print("Processing frame:", frame_count)  # Check if frames are read correctly

    # Detect objects and save frame
    detected_frame = detect_and_save(frame, frame_count)

    # Write the frame to the output video
    out.write(detected_frame)
    

    # Check if 3 seconds have passed
    if time.time() - start_time >= 10:
        start_time = time.time()  # Reset start time for next detection
        cv2_imshow(detected_frame)

cap.release()
out.release()
cv2.destroyAllWindows()
