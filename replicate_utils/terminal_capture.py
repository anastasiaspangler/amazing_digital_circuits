import cv2
import random
import string
import os
import datetime
import requests

def forward_request(name, curr_obj, paths: list[str]):
    abs_paths = []
    for path in paths:
        abs_paths.append(curr_obj + "/" + path + ".png")

    data = {
        "type": "rep_out",
        "path_a": abs_paths[0],
        "path_b": abs_paths[1],
        "path_c": abs_paths[2],
        "path_d": abs_paths[3],
        "timestamp": datetime.datetime.now().isoformat(),
        "name": name,
    }
    print("Sending to queue...")
    r = requests.post('http://127.0.0.1:5000/replicate', data=data)
    print(r.json())

def random_name():
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(10))

def capture_feed():
    print("To begin a capture, position your item and hit the 'a' key.")
    print("This will take the first two images.")
    video_capture_0 = cv2.VideoCapture(0)
    video_capture_1 = cv2.VideoCapture(2)

    curr_obj = None
    name = None
    waiting_for_second = False

    while True:
        ret0, frame0 = video_capture_0.read()
        ret1, frame1 = video_capture_1.read()

        if ret0:
            cv2.imshow('Cam 0', frame0)
        if ret1:
            cv2.imshow('Cam 2', frame1)

        key = cv2.waitKey(1) & 0xFF

        # Step 1: start new object capture (first shots)
        if key == ord('a') and not waiting_for_second:
            name = random_name()
            curr_obj = "local_storage/" + name
            os.makedirs(curr_obj, exist_ok=True)

            if ret0:
                cv2.imwrite(curr_obj + "/img_a1.png", frame0)
            if ret1:
                cv2.imwrite(curr_obj + "/img_b1.png", frame1)

            print(f"Object {name}: first shots saved. Adjust pose, then press 'n' for second shots.")
            waiting_for_second = True

        # Step 2: finish capture (second shots)
        elif key == ord('n') and waiting_for_second:
            # flush buffer for fresh frames
            for _ in range(5):
                ret0, frame0 = video_capture_0.read()
                ret1, frame1 = video_capture_1.read()

            if ret0:
                cv2.imwrite(curr_obj + "/img_a2.png", frame0)
            if ret1:
                cv2.imwrite(curr_obj + "/img_b2.png", frame1)

            print(f"Object {os.path.basename(curr_obj)}: second shots saved. Capture complete.")
            forward_request(name, curr_obj, paths=["img_a1", "img_b1", "img_a2", "img_b2"])

            waiting_for_second = False
            curr_obj = None

        # Quit program
        elif key == ord('q'):
            break

    video_capture_0.release()
    video_capture_1.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    capture_feed()