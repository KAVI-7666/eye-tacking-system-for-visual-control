import cv2
import mediapipe as mp
import pyautogui
import time

# ✅ Global stop flag to allow stopping from external UI
stop_flag = False

def eye_controlled_mouse():
    global stop_flag
    stop_flag = False  # Reset when starting the function

    # Initialize webcam and FaceMesh
    cam = cv2.VideoCapture(0)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    screen_w, screen_h = pyautogui.size()

    # Blink detection variables
    blinking_left = False
    blinking_right = False
    last_blink_time_left = 0
    last_blink_time_right = 0
    blink_threshold = 200  # milliseconds

    # Cursor smoothing
    smooth_factor = 0.3
    last_x, last_y = screen_w // 2, screen_h // 2

    while not stop_flag:
        ret, frame = cam.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        frame_h, frame_w, _ = frame.shape

        if output.multi_face_landmarks:
            landmarks = output.multi_face_landmarks[0].landmark

            # Eye blink detection
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

            # Eye tracking for cursor movement
            left_eye_center_x = int((landmarks[158].x + landmarks[133].x) / 2 * frame_w)
            left_eye_center_y = int((landmarks[159].y + landmarks[145].y) / 2 * frame_h)
            right_eye_center_x = int((landmarks[385].x + landmarks[362].x) / 2 * frame_w)
            right_eye_center_y = int((landmarks[386].y + landmarks[374].y) / 2 * frame_h)

            eye_x = (left_eye_center_x + right_eye_center_x) // 2
            eye_y = (left_eye_center_y + right_eye_center_y) // 2

            mapped_x = int(eye_x * (screen_w / frame_w))
            mapped_y = int(eye_y * (screen_h / frame_h))

            last_x += (mapped_x - last_x) * smooth_factor
            last_y += (mapped_y - last_y) * smooth_factor
            pyautogui.moveTo(last_x, last_y)

            # Optional: Draw landmarks
            for landmark in landmarks:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

        cv2.imshow('Eye Controlled Mouse', frame)

        # Break on stop_flag or pressing 'q'
        if stop_flag or (cv2.waitKey(1) & 0xFF == ord('q')):
            break

    cam.release()
    cv2.destroyAllWindows()

# ✅ Function to stop the loop
def stop_eye_control():
    global stop_flag
    stop_flag = True
