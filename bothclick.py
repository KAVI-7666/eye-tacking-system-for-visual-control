import cv2
import mediapipe as mp
import pyautogui
import time

# ✅ Global flag to control loop externally
should_run = True

def stop_eye_control():
    global should_run
    should_run = False

def eye_controlled_mouse_both():
    global should_run
    should_run = True  # Reset flag when starting

    # Initialize webcam and MediaPipe FaceMesh
    cam = cv2.VideoCapture(0)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    # Blink detection variables
    blinking_left = False
    blinking_right = False
    last_blink_time_left = 0
    last_blink_time_right = 0
    blink_threshold = 200  # ms

    while should_run:
        ret, frame = cam.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        frame_h, frame_w, _ = frame.shape

        if output.multi_face_landmarks:
            landmarks = output.multi_face_landmarks[0].landmark

            # Get left & right eye heights
            left_eye_top = landmarks[159]
            left_eye_bottom = landmarks[145]
            right_eye_top = landmarks[386]
            right_eye_bottom = landmarks[374]

            left_eye_height = abs(left_eye_top.y - left_eye_bottom.y)
            right_eye_height = abs(right_eye_top.y - right_eye_bottom.y)

            current_time = time.time() * 1000

            if left_eye_height < 0.015:
                if not blinking_left and (current_time - last_blink_time_left) > blink_threshold:
                    pyautogui.click(button='left')
                    last_blink_time_left = current_time
                    blinking_left = True
            else:
                blinking_left = False

            if right_eye_height < 0.015:
                if not blinking_right and (current_time - last_blink_time_right) > blink_threshold:
                    pyautogui.click(button='right')
                    last_blink_time_right = current_time
                    blinking_right = True
            else:
                blinking_right = False

            # Optional: Draw landmarks
            for landmark in landmarks:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        cv2.imshow('Eye Controlled Mouse - Both Blinks', frame)

        if not should_run or (cv2.waitKey(1) & 0xFF == ord('q')):
            break

    cam.release()
    cv2.destroyAllWindows()
