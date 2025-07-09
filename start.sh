#!/bin/bash

# Start Flask in the background
python app.py &

# Start Discord bot
python bot.py