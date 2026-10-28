# Hand Gesture LED Controller 🎯✋

Control five LEDs using real-time hand gestures captured by a webcam.

This project uses **Python, OpenCV, MediaPipe, and ESP32** to detect hand landmarks and control LEDs wirelessly over Wi-Fi.

## ✨ Features

- ✋ Real-time hand tracking using a webcam
- 🖐️ Control five LEDs using individual fingers
- 📡 Wireless communication between Python and ESP32 over HTTP
- 🔌 ESP32 GPIO control
- 🛡️ Automatic LED shutdown after a communication timeout

## 🧰 Technologies

- Python
- OpenCV
- MediaPipe
- ESP32
- PlatformIO
- C++
- Wi-Fi / HTTP

## 📁 Project Structure

```text
hand-led-wifi/
├── computer/
│   └── hand_control.py
├── include/
├── lib/
├── src/
│   └── main.cpp
├── test/
├── platformio.ini
└── README.md
```

## ⚙️ Setup

### 1. Flash the ESP32

Open this project in VS Code with PlatformIO, configure your Wi-Fi credentials in `src/main.cpp`, and upload the firmware to your ESP32.

### 2. Install Python dependencies

Activate your Python virtual environment and install the dependencies required by `computer/hand_control.py`.

### 3. Configure the connection

Update the ESP32 IP address in `computer/hand_control.py` to match your device.

### 4. Start hand tracking

Connect your webcam and run:

```bash
python computer/hand_control.py
```

Move your fingers in front of the webcam to control the LEDs.

## 🔌 LED Pin Configuration

| Finger | ESP32 GPIO |
|---|---:|
| Thumb | 18 |
| Index | 19 |
| Middle | 21 |
| Ring | 22 |
| Little | 23 |

## 🔒 Safety

The firmware includes a timeout that turns the LEDs off if commands stop arriving.

**Note:** Configure your Wi-Fi credentials locally. Do not publish passwords or other secrets in a public repository.

## 🚀 Future Improvements

- Gesture-based commands
- A live control dashboard
- Improved detection stability
- Support for additional devices

## 📄 License

Choose a license before distributing or reusing this project.
