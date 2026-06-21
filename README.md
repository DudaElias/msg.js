# Rise of Babel

A multi-player word guessing game inspired by the legendary Tower of Babel. Each round, three players receive different sensory clues (sound, phrase, touch, image) and must work together to guess the hidden word. Progress lights up your Pico board!

## What it does

- Interactive pygame game with 3 player sections per round
- **Each player has ONE clue of the same type** (all Image clues, all Phrase clues, etc.)
- Three clue types available:
  - 🔊 **Sound** - Click to play audio file
  - 💬 **Phrase** - Text descriptions and hints
  - 🖼️ **Image** - Visual placeholders (replace with actual images)
- Players take turns clicking their button to **reveal/hide** their clue
  - With tooltips warning "⚠️ Apenas Jogador X pode olhar!" (Only Player X can look)
- Based on honesty and trust - players read their clue privately and hide it before guessing
- Guess the word by typing it in (with keyboard input)
- Serial commands to control Pico LEDs:
  - `HIT` - Correct guess (turn LED on)
  - `MISS` - Wrong guess (turn LED off)
  - `SCORE <n>` - Progress indication
  - `READY` - Round started
  - `GAME_OVER` - Game finished

## How to play

### Setup

1. Install dependencies:
```bash
make install
```

2. Run the game with your Pico:
```bash
make play PORT=COM5
```

3. Or test without hardware (mock mode):
```bash
make play-mock
```

### Start Screen

When you launch the game, you'll see:

- **Main Menu** with quick rules and instructions
  - 👥 3 Jogadores por rodada
  - 🔍 Cada jogador tem 3 pistas diferentes
  - 💭 Mostrem e ocultam as pistas estrategicamente
  - ⌨️ Digitam juntos a palavra correta
  - 💡 Acertos acendem LEDs no Pico!

- **Two buttons**: COMEÇAR (Start) or INSTRUÇÕES (Instructions)
- **Keyboard shortcuts**:
  - **SPACE**: Start the game
  - **I**: View full instructions
  - **ESC**: Quit

### Full Instructions Screen

Accessible from the menu, provides detailed information about:
- Objective and game rules
- Types of clues (Sound, Phrase, Touch, Image)
- How to play step by step
- All game controls
- Tips for cooperative play

### Gameplay

**Round Structure:**
1. **Player 1 reads clue**: Player 1 clicks the button (👁️ Mostrar) to reveal their clue, reads it privately
2. **Player 1 hides clue**: Clicks again (🔒 Oculto) to hide their clue
3. **Player 2 & 3 do the same**: Each player takes a turn to read and hide their clue
4. **Guess Together**: All players discuss and type the word together
5. **Submit Guess**: Press ENTER to check if correct
6. **Next Round**: After correct guess, click the green **"Próxima →"** button in the bottom right corner

**Game Flow:**
- 5 rounds total, each with a different clue type (Image, Phrase, Sound, Touch, etc.)
- All players in a round get clues of the SAME TYPE but different content
- Trust is key - honor the hidden clues!
- Score increases with each correct guess

**Controls:**
- **Click Clue Button**: Reveal/hide your player's clue (👁️ or 🔒)
- **Click "Próxima →" Button**: Go to next round (appears after correct guess)
- **A-Z**: Type letters to guess (including R for TOWER)
- **ENTER**: Submit guess
- **BACKSPACE**: Delete last letter
- **DELETE**: Clear entire guess
- **R**: Restart game (only at game over)
- **SPACE**: Restart game (only at game over)
- **ESC**: Quit

## Project structure

```
msg.js/
├── src/
│   ├── pico/
│   │   ├── Teste.c
│   │   ├── CMakeLists.txt
│   │   └── pico_sdk_import.cmake
│   └── pc/
│       ├── __init__.py
│       ├── main.py           - Entry point and main game loop
│       ├── screens.py        - Start screen with instructions
│       ├── game.py           - Game logic (BabelGame class)
│       ├── renderer.py       - Rendering and UI (images, sounds, text)
│       ├── models.py         - Data models (Clue, Round, GameState)
│       ├── game_data.py      - Game rounds and clue definitions
│       ├── config.py         - Configuration constants
│       ├── serial_link.py    - Serial communication with Pico
│       └── mock_serial.py    - Mock serial connection for testing
├── assets/
│   ├── images/
│   │   └── placeholder.png   - Placeholder image (used for all image clues)
│   └── sounds/
│       └── placeholder.mp3   - Placeholder sound (used for all audio clues)
├── Makefile
├── requirements.txt
└── README.md
```

## Makefile commands

```bash
make install      # Install Python requirements
make clean        # Remove cache files
make list-ports   # Show available serial ports
make play PORT=COMx  # Run with real Pico (e.g., make play PORT=COM5)
make play-mock    # Run in mock mode (no hardware needed)
make help         # Show all available commands
```

## Game rounds

| Round | Word | Clue Type | Example |
|-------|------|-----------|---------|
| 1 | PYTHON | 💬 Phrase | "Uma cobra verde e amarela enroscada em uma maçã..." |
| 2 | TOWER | 🖼️ Image | Uses placeholder.png |
| 3 | LIGHT | 🔊 Sound | Uses placeholder.mp3 (click to play) |
| 4 | SOUND | 💬 Phrase | "Ondas invisíveis que viajam no ar..." |
| 5 | DIGITAL | 🖼️ Image | Uses placeholder.png |

**Note**: Image and sound clues use the placeholder files. Replace them with actual content for each round.

## Building the Pico firmware

```bash
cd src/pico
mkdir build
cd build
cmake ..
make
```

Flash the `Teste.uf2` to your Pico in BOOTSEL mode.

## Serial protocol

The PC sends commands to the Pico:
- `READY` - Round initialization
- `HIT` - Correct answer (lights LED)
- `MISS` - Wrong answer (turns off LED)
- `SCORE <n>` - Progress indicator
- `GAME_OVER` - End of game session

The Pico can send back status messages that appear in console.

## Next steps

- Add more word rounds
- Implement sound effects for clues
- Add timer for timed rounds
- Integrate actual image display for visual clues
- Create custom clue editor
