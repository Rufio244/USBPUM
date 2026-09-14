#!/bin/bash
cd /path/to/usbpum
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
echo "System updated and synchronized successfully at $(date)"
