import cv2
import mediapipe as mp
import pyautogui
import time

# ✅ Global stop flag for UI or thread control
should_run = True

def stop_eye_control():
    global should_run
    should_run = False  # Set flag to stop the loop

def eye_controlled_mouse_left():
    global should_run
    should_run = True  # Reset flag on function start

    # Initialize webcam and FaceMesh
    cam = cv2.VideoCapture(0)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    screen_w, screen_h = pyautogui.size()

    # Blink detection variables
    blinking = False
    last_blink_time = 0
    blink_threshold = 200  # milliseconds

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

            # Detect left eye blink (159 and 145)
            left_eye_top = landmarks[159]
            left_eye_bottom = landmarks[145]
            eye_height = abs(left_eye_top.y - left_eye_bottom.y)

            if eye_height < 0.015:
                current_time = time.time() * 1000
                if not blinking and (current_time - last_blink_time) > blink_threshold:
                    pyautogui.click(button='left')
                    last_blink_time = current_time
                    blinking = True
            else:
                blinking = False

            # Optional: Draw landmarks
            for landmark in landmarks:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        cv2.imshow('Eye Controlled Mouse - Left Blink', frame)

        # Also break loop on 'q' or external stop
        if not should_run or (cv2.waitKey(1) & 0xFF == ord('q')):
            break

    cam.release()
    cv2.destroyAllWindows()
