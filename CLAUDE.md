# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

A 6-legged walking robot (hexapod) controlled by a Raspberry Pi. The codebase is split into two independent halves that run on separate machines and communicate over TCP:
- **Server** (`Code/Server/`) — runs on the Raspberry Pi (the robot)
- **Client** (`Code/Client/`) — runs on a PC/Mac/Windows as the controller

## Hardware

- Raspberry Pi with camera, I2C, GPIO
- 2× PCA9685 PWM boards (I2C **0x40** and **0x41**) — 32 servo channels total
- 18 leg servos: legs 1–3 on PCA9685 @ 0x41 (ch 8–15, 31), legs 4–6 on PCA9685 @ 0x40 (ch 0–8, 16–27)
- Camera/head: PCA9685 @ 0x41, channels 0 and 1
- MPU6050 IMU (I2C **0x68**)
- PCF8591 or ADS7830 ADC for battery monitoring (I2C **0x4f** or **0x48**)
- 7 NeoPixel LEDs on GPIO18
- HC-SR04 ultrasonic sensor — trigger GPIO27, echo GPIO22
- Active buzzer on GPIO17
- Servo power enable via GPIO4

## Running the Code

### Server (on the Raspberry Pi)

```bash
cd Code/Server

# With GUI
sudo python3 main.py

# Headless, auto-start TCP (most common for deployment)
sudo python3 main.py -n -t
```

Must be run with `sudo` — requires GPIO, I2C, and NeoPixel (DMA) access.

### Client (on PC/Mac/Windows)

```bash
cd Code/Client
python3 Main.py        # Linux / macOS
python Main.py         # Windows
```

Before connecting, set the robot's IP in `Code/Client/IP.txt`.

### Setup

```bash
sudo bash setup_server.sh   # Raspberry Pi
bash setup_client.sh        # PC / Mac
setup_client.bat            # Windows
```

### Hardware component tests (on RPi, from `Code/Server/`)

```bash
sudo python3 test.py Led
sudo python3 test.py Ultrasonic
sudo python3 test.py Servo
sudo python3 test.py ADC
sudo python3 test.py Buzzer
```

### Custom movement scripts (on RPi, from `Code/Server/`)

`myCode.py` is the intended place to write standalone motion sequences — it imports `Control` directly and calls `c.run(data)` without needing the TCP server.

```bash
sudo python3 myCode.py
```

## Server Files (`Code/Server/`)

| File | Role |
|------|------|
| `main.py` | Entry point. PyQt5 UI or headless (`-n`). `-t` flag auto-starts TCP. |
| `Server.py` | TCP server. Two threads: `transmission_video` and `receive_instruction`. Dispatches commands to subsystems. |
| `Control.py` | Core robot brain: inverse kinematics, gait generation, body balance, calibration. |
| `Servo.py` | Maps angle 0–180° → PCA9685 PWM duty across both chips. |
| `PCA9685.py` | I2C PWM driver (16 channels per chip). |
| `IMU.py` | MPU6050 driver with Mahony complementary filter for roll/pitch/yaw. |
| `Kalman.py` | 1D Kalman filter for per-axis IMU noise reduction. |
| `PID.py` | Incremental PID controller used in the IMU balance loop. |
| `Led.py` | 7-pixel NeoPixel RGB strip on GPIO18. Modes: solid, wipe, chase, rainbow, rainbow cycle. |
| `ADC.py` | Battery voltage monitor. Auto-detects PCF8591 or ADS7830 via I2C. |
| `ADCDevice.py` | Low-level I2C ADC drivers for both chip types. |
| `Ultrasonic.py` | HC-SR04 driver. Returns median of 3 readings. |
| `Buzzer.py` | Active buzzer on GPIO17. |
| `Thread.py` | `stop_thread()` — kills a thread via `ctypes.pythonapi.PyThreadState_SetAsyncExc`. |
| `Command.py` | Shared command string constants. |
| `point.txt` | Calibration data: 6 rows × 3 tab-separated integers (x y z mm offsets per leg). |
| `myCode.py` | User scratch space for custom motion scripts. |
| `test.py` | Hardware component test runner (CLI arg selects component). |

## Client Files (`Code/Client/`)

| File | Role |
|------|------|
| `Main.py` | PyQt5 main window. WASD+Space keyboard control, sliders for speed/roll/height/head. |
| `Client.py` | TCP client. `receiving_video()` decodes JPEG frames. `send_data()` / `receive_data()` for commands. |
| `Calibration.py` | GUI for per-leg servo calibration. Sends `CMD_CALIBRATION` commands. |
| `Face.py` | Face detection (OpenCV Haar cascade) and recognition integrated with the video stream. |
| `ui_client.py` | PyQt5 generated UI layout for main window. |
| `ui_led.py` | PyQt5 LED control panel UI. |
| `ui_face.py` | PyQt5 face recognition panel UI. |
| `Command.py` | Identical copy of server-side command constants. |
| `PID.py` | Client-side PID used for camera/face tracking. |
| `Thread.py` | Same `stop_thread()` utility as server side. |
| `IP.txt` | Last-used server IP address (persisted between sessions). |
| `point.txt` | Client-side calibration reference. |

## Architecture

### Networking

Two TCP connections on the robot's `wlan0` IP:
- **Port 8002** — video stream: 4-byte little-endian length prefix + raw JPEG frame
- **Port 5002** — command channel: UTF-8 text, `\n`-terminated, `#`-delimited fields

### Command Protocol

```
COMMAND#arg1#arg2#...#argN\n
```

Command strings are constants in `Command.py` — **identical copies exist in both `Code/Server/` and `Code/Client/`**. Adding a new command requires updating both files.

| Command | Args | Notes |
|---|---|---|
| `CMD_MOVE` | gait x y speed angle | gait 1=tripod, 2=wave; x/y ±35; speed 2–10 |
| `CMD_ATTITUDE` | roll pitch yaw | body tilt, each ±15° |
| `CMD_POSITION` | x y z | body position shift, x/y ±40, z ±20 |
| `CMD_BALANCE` | 1/0 | IMU self-balance loop on/off |
| `CMD_CALIBRATION` | [one–six x y z] / save | per-leg offset; "save" writes `point.txt` |
| `CMD_LED` | R G B | solid colour |
| `CMD_LED_MOD` | 0–5 | 0=off, 1=solid, 2=wipe, 3=chase, 4=rainbow, 5=rainbow cycle |
| `CMD_SONIC` | — | server replies with distance in cm |
| `CMD_CAMERA` | x y | pan (50–180) / tilt (0–180) for servos 0 and 1 |
| `CMD_HEAD` | servo angle | direct servo angle control |
| `CMD_BUZZER` | 1/0 | buzzer on/off |
| `CMD_POWER` | — | server replies with two battery voltages |
| `CMD_RELAX` | — | toggle servo relaxation |
| `CMD_SERVOPOWER` | 0/1 | GPIO4 servo power rail |

### Kinematics (`Control.py`)

All motion logic lives in `Control.py`. Data flow for any movement:

```
foot target (x,y,z)
  → coordinateTransformation()   # body-frame → leg-local frame (per mounting angle)
  → coordinateToAngle()          # IK: 3D position → joint angles (a,b,c)
  → calibration offsets applied
  → setLegAngle()                # sends final PWM to both PCA9685 chips
```

**Leg geometry** — 3 segments: coxa (33 mm), femur (90 mm), tibia (110 mm). Valid foot reach: 90–248 mm from hip (`checkPoint()` enforces this before any servo move).

**Leg mounting angles** — `coordinateTransformation()` rotates each leg's body-frame coordinates by its mounting angle: leg1=54°, leg2=0°, leg3=−54°, leg4=−126°, leg5=180°, leg6=126°.

**Gait generation** (`Control.run()`): takes `['CMD_MOVE', gait, x, y, speed, angle]`. Speed 2–10 maps to internal frame count F. `angle ≠ 0` disables x/y translation (turning only).
- Gait 1 (tripod): legs 0,2,4 and 1,3,5 alternate
- Gait 2 (wave): one leg at a time in order 5,2,1,0,3,4

**Body posture** (`postureBalance(r,p,y)`): constructs a full 3×3 rotation matrix and applies it to all foot positions to tilt the body.

**Self-balance** (`imu6050()`): tight loop — MPU6050 → Kalman filter → Mahony quaternion filter → PID → `postureBalance()` → servos, ~20 ms per cycle. Exits when any new command arrives.

**Auto-relax**: `condition()` runs in a background thread. After 10 seconds of no commands it calls `relax(True)` to de-energise all servos.

### Calibration

`Code/Server/point.txt` holds 6 rows × 3 tab-separated integers (x y z in mm) — the physical foot position offset for each leg used to compensate for mechanical servo installation error. Modified via the client Calibration GUI or `CMD_CALIBRATION` commands, persisted with `CMD_CALIBRATION#save`.

### Thread Management

`Thread.py`'s `stop_thread()` injects `SystemExit` into a running thread via `ctypes.pythonapi.PyThreadState_SetAsyncExc`. Called 5 times in a loop to ensure delivery. Used in `Server.py` to stop the video and instruction threads on disconnect.

### IMU Sensor Pipeline

MPU6050 raw data → per-axis Kalman filter (`Kalman.py`) → Mahony complementary filter (`IMU.imuUpdate()`) → roll/pitch/yaw in degrees. Startup calibration averages 100 samples to compute bias offsets.
