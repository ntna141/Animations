# Leetcode solution animation creator

Python script to automate video animations for Leetcode solutions. Uses the Anthropic API for Claude and ElevenLabs for voiceovers

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On macOS/Linux:
```bash
source venv/bin/activate
```
- On Windows:
```bash
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the visualization for the problem Jump Game:
```bash
python test_animation.py
```

This will create an animation of array operations and save it as `jump_game.mp4`. 