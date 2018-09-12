#!/bin/sh
# paste the following script in cron job
echo $(date) >> /home/pi/switch_board/switch_board.log
source venv/bin/activate
/home/pi/switch_board/venv/bin/python /home/pi/switch_board/main.py
