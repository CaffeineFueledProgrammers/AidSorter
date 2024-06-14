# AidSorter

Automatic goods sorting system. This project is the final output for the
_Intelligent Systems_ course at Baliuag University.

## Requirements

### Hardware Components

- **Host/SBC**: Xunlong Orange Pi PC
- **MCU**: Arduino UNO R3

### Software Components

#### Host / Single Board Computer (SBC)

- **Operating System**: Armbian 24.8.0 Bookworm
- **Python**: 3.11.2
- **Poetry**: 1.3.2

#### Microcontroller Unit (MCU)

## Host / Single Board Computer (SBC) Development Setup

1. Clone the repository.

   ```bash
   git clone https://github.com/CaffeineFueledProgrammers/AidSorter.git
   cd ./AidSorter/host
   ```

2. Install the requirements.

   ```bash
    # You can let Poetry create a virtual environment for you...
    poetry install

    # ...or you can use your own. (my preferred method)
    python -m venv venv
    source ./venv/bin/activate
    poetry install
   ```

3. Run the application.

   ```bash
   # If you let Poetry create a virtual environment for you...
   poetry run python -m aidsorter

   # ...or if you use your own virtual environment.
   python -m aidsorter
   ```

## Microcontroller Unit (MCU) Development Setup

1. Clone the repository.

   ```bash
   git clone https://github.com/CaffeineFueledProgrammers/AidSorter.git
   cd ./AidSorter/mcu/aidsorter
   ```

2. Upload the sketch to the board.

   ```bash
   # NOTE: you can also use the Arduino IDE to upload the sketch,
   #       but I prefer using the terminal so here it is.
   arduino-cli compile --fqbn arduino:avr:uno .
   ```
