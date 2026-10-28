import time
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# Replace this with your ESP32's IP address
ESP32_IP = "192.168.213.223"

MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")
LED_URL = f"http://{ESP32_IP}/leds?state="

# Bypass system proxies for local ESP32 requests
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({})
)


def send_led_state(state):
    """Send a five-bit LED state to the ESP32."""
    try:
        request = urllib.request.Request(
            LED_URL + state,
            method="GET"
        )
        with opener.open(request, timeout=1) as response:
            print("LEDs:", response.read().decode())
    except Exception as error:
        print("ESP32 connection error:", error)


def distance(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


def get_finger_state(hand):
    """
    Return five bits in this order:
    thumb, index, middle, ring, little finger.
    """

    # Thumb landmarks
    thumb_tip = hand[4]
    index_base = hand[5]

    # Finger tip and middle-joint landmarks
    finger_pairs = [
        (8, 6),    # Index
        (12, 10),  # Middle
        (16, 14),  # Ring
        (20, 18),  # Little
    ]

    # Estimate palm size for thumb detection
    palm_size = distance(hand[0], hand[9])

    # Thumb heuristic; works best with palm facing the camera
    thumb_extended = (
        distance(thumb_tip, index_base) > palm_size * 0.65
    )

    state = ["1" if thumb_extended else "0"]

    # For the other four fingers, compare tip and PIP joint height.
    # This assumes your hand is approximately upright.
    for tip_id, joint_id in finger_pairs:
        extended = hand[tip_id].y < hand[joint_id].y
        state.append("1" if extended else "0")

    return "".join(state)


def main():
    if not MODEL_PATH.exists():
        print("Model file not found:", MODEL_PATH)
        return

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(
            model_asset_path=str(MODEL_PATH)
        ),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Could not open webcam. Check the camera connection.")
        return

    last_sent_state = None
    last_send_time = 0
    start_time = time.monotonic()

    try:
        with vision.HandLandmarker.create_from_options(options) as detector:
            while True:
                success, frame = camera.read()

                if not success:
                    print("Could not read webcam frame.")
                    break

                # Mirror the image for a natural webcam view
                frame = cv2.flip(frame, 1)

                rgb_frame = cv2.cvtColor(
                    frame, cv2.COLOR_BGR2RGB
                )

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame,
                )

                timestamp_ms = int(
                    (time.monotonic() - start_time) * 1000
                )

                result = detector.detect_for_video(
                    mp_image, timestamp_ms
                )

                state = "00000"

                if result.hand_landmarks:
                    hand = result.hand_landmarks[0]
                    state = get_finger_state(hand)

                    # Draw hand landmarks
                    height, width, _ = frame.shape

                    for point in hand:
                        x = int(point.x * width)
                        y = int(point.y * height)
                        cv2.circle(
                            frame, (x, y), 5, (0, 255, 0), -1
                        )

                    cv2.putText(
                        frame,
                        f"Fingers: {state}",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )
                else:
                    cv2.putText(
                        frame,
                        "No hand detected",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )

                now = time.monotonic()

                # Send every 0.5 seconds to keep the ESP32 active.
                if (
                    state != last_sent_state
                    or now - last_send_time >= 0.5
                ):
                    send_led_state(state)
                    last_sent_state = state
                    last_send_time = now

                cv2.imshow("ESP32 Hand Gesture Control", frame)

                # Press Q to quit
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        send_led_state("00000")
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()