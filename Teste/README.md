# Pico Reaction Game

This project is a starter for a small pygame game that sends serial commands to a Raspberry Pi Pico.

## What it does

- `pc_controller.py` runs a pygame reaction game on the PC.
- The game sends commands like `READY`, `HIT`, `MISS`, `SCORE 3`, and `GAME_OVER` to the Pico.
- The Pico firmware listens over USB serial and toggles GPIO 2 as a simple feedback output.

## Files

- `Teste.c`: Pico firmware.
- `pc_controller.py`: pygame game and serial sender.
- `requirements.txt`: Python dependencies.

## Build and flash

1. Build the Pico firmware with your existing build task or:

```powershell
ninja -C build
```

2. Flash the UF2 output to the Pico in BOOTSEL mode:

```powershell
Copy-Item .\build\Teste.uf2 E:\
```

Replace `E:` with the drive letter that appears as `RPI-RP2`.

## PC side

Install the dependencies:

```powershell
pip install -r requirements.txt
```

Run the game and point it at your Pico COM port:

```powershell
python pc_controller.py COM5
```

How to play:

- Click the red target before it expires.
- Press `R` to restart.
- Press `ESC` to quit.

## Serial commands sent

- `READY` when a round starts.
- `HIT` and `SCORE <n>` when you click the target.
- `MISS` when the target expires.
- `GAME_OVER` when the round ends.

## Next step

If you want, the next upgrade is to replace the LED feedback with a buzzer, vibration motor, or an on-screen score sync back from the Pico.