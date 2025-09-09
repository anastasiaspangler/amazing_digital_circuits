import cv2
import os
from replicate_helper import send_to_replicate


def capture_and_process(name):
    """Capture from webcams and process through replicate_utils automatically"""
    # Create local storage directory for this capture (like original)
    curr_obj = "local_storage/" + name
    os.makedirs(curr_obj, exist_ok=True)
    
    try:
        # Initialize webcams (same as original code)
        video_capture_0 = cv2.VideoCapture(0)
        video_capture_1 = cv2.VideoCapture(2)
        
        if not video_capture_0.isOpened() or not video_capture_1.isOpened():
            raise Exception("Could not access webcams")
        
        # Capture first set of images
        ret0, frame0 = video_capture_0.read()
        ret1, frame1 = video_capture_1.read()
        
        if not ret0 or not ret1:
            raise Exception("Failed to capture from webcams")
        
        # Save first images to local storage
        img_a1_path = os.path.join(curr_obj, "img_a1.png")
        img_b1_path = os.path.join(curr_obj, "img_b1.png")
        cv2.imwrite(img_a1_path, frame0)
        cv2.imwrite(img_b1_path, frame1)
        
        # Flush buffer for fresh frames (like original)
        for _ in range(5):
            ret0, frame0 = video_capture_0.read()
            ret1, frame1 = video_capture_1.read()
        
        # Capture second set of images
        ret0, frame0 = video_capture_0.read()
        ret1, frame1 = video_capture_1.read()
        
        if not ret0 or not ret1:
            raise Exception("Failed to capture second set from webcams")
        
        # Save second images to local storage
        img_a2_path = os.path.join(curr_obj, "img_a2.png")
        img_b2_path = os.path.join(curr_obj, "img_b2.png")
        cv2.imwrite(img_a2_path, frame0)
        cv2.imwrite(img_b2_path, frame1)
        
        # Release webcams
        video_capture_0.release()
        video_capture_1.release()
        
        # Run replicate_utils with the 4 images
        abs_paths = [img_a1_path, img_b1_path, img_a2_path, img_b2_path]
        api_response = send_to_replicate(name, abs_paths)
        
        return {
            "success": bool(api_response),
            "name": name,
            "response": api_response
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "name": name
        }
