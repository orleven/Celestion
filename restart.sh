#!/bin/bash
echo "restarting process..."
source venv/bin/activate

ps -aux | grep "python celestion.py"| awk '{print $2}' | xargs kill -9
nohup python celestion.py >> log/nohup_celestion.out  &
echo "restarted celestion!"

echo "restarted process!"