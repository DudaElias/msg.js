# Rise of Babel - Project Structure

## Package Organization

```
src/pc/
├── main.py                 # Entry point
├── __init__.py            # Package initialization
├── STRUCTURE.md           # This file
│
├── core/                  # Core game logic and state
│   ├── __init__.py
│   ├── game.py           # BabelGame - main game class
│   ├── models.py         # Data models (GameState, Round, Clue, etc)
│   ├── game_data.py      # Loads game rounds from YAML
│   └── rounds.yaml       # Game rounds configuration
│
├── events/               # Event system for decoupled communication
│   ├── __init__.py
│   └── bus.py           # EventBus - pub/sub system
│
├── handlers/            # Event handlers for various systems
│   ├── __init__.py
│   └── led_handler.py   # LED control in response to game events
│
├── ui/                  # User interface components
│   ├── __init__.py
│   ├── renderer.py      # Game rendering and UI drawing
│   ├── screens.py       # Menu and instruction screens
│   └── background.py    # Pixel art background renderer
│
├── hardware/            # Hardware communication (serial with Pico)
│   ├── __init__.py
│   ├── pico_link.py     # PicoLink - serial communication wrapper
│   └── mock_serial.py   # MockSerial - for testing without hardware
│
└── utils/               # Utilities and configuration
    ├── __init__.py
    └── config.py        # Constants and configuration
```

## Module Responsibilities

### `core` - Game Logic
- **game.py**: Main game loop, round management, guess handling
- **models.py**: Data structures for game state (GameState, Round, Clue, PlayerSection)
- **game_data.py**: Loads game configuration from YAML
- **rounds.yaml**: Game configuration (word list, clues for each round)

### `events` - Event System
- **bus.py**: Pub/Sub system for decoupled event handling
  - Allows game logic to emit events without knowing about handlers
  - Handlers can subscribe to events and react accordingly

### `handlers` - Event Handlers
- **led_handler.py**: Listens to game events and controls Pico LEDs
  - Easy to extend with more handlers (sound effects, animations, etc)

### `ui` - User Interface
- **renderer.py**: All game rendering and visualization
  - Handles pixel art background, buttons, text, images, modals
- **screens.py**: Menu and instruction screens
- **background.py**: Pixel art Tower of Babel background

### `hardware` - Hardware Communication
- **pico_link.py**: Serial port communication with Pico
- **mock_serial.py**: Mock implementation for testing without hardware

### `utils` - Configuration and Utilities
- **config.py**: Constants, colors, window settings

## Data Flow

```
main.py
  ├── Initialize EventBus
  ├── Initialize LEDHandler (subscribes to events)
  ├── Create BabelGame (with EventBus)
  ├── Create Renderer
  ├── Game Loop:
  │   ├── Handle Input
  │   ├── BabelGame processes actions
  │   ├── BabelGame publishes events (correct_guess, incorrect_guess, etc)
  │   ├── LEDHandler receives events and sends to Pico
  │   ├── Renderer draws game state
  │   └── Update display
```

## Adding New Features

### Example: Add Sound Effects Handler

```python
# handlers/sound_handler.py
from pc.events import EventBus, EventType, GameEvent

class SoundHandler:
    def register(self, event_bus: EventBus):
        event_bus.subscribe(EventType.CORRECT_GUESS, self.on_correct)
        event_bus.subscribe(EventType.INCORRECT_GUESS, self.on_incorrect)

    def on_correct(self, event: GameEvent):
        # Play success sound
        pass

    def on_incorrect(self, event: GameEvent):
        # Play error sound
        pass

# In main.py
from pc.handlers import SoundHandler
sound_handler = SoundHandler()
sound_handler.register(event_bus)
```

## Running the Game

```bash
# From project root
make install      # Install dependencies
make play-mock    # Run in mock mode
make play PORT=COM5  # Run with real Pico
```

## Import Guidelines

- Use absolute imports with `pc` prefix in all files
- Example: `from pc.core import BabelGame`
- Each package's `__init__.py` exports public API
