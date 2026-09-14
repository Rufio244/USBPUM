#!/bin/bash

# แสดงสถานะเริ่มต้น
echo "=========================================="
echo " [Chat vider] USBPUM Auto-Sync & Execute "
echo "=========================================="

# อัปเดตโค้ดล่าสุดจาก GitHub
echo "[1/4] Pulling latest code from GitHub..."
git pull origin main

# ตรวจสอบและสร้าง Virtual Environment ถ้ายังไม่มี
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment (venv)..."
    python3 -m venv venv
else
    echo "[2/4] Virtual environment already exists."
fi

# เปิดใช้งาน venv และติดตั้ง dependencies
echo "[3/4] Installing / Updating dependencies..."
source venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# รันระบบหลัก main.py
echo "[4/4] Starting main application (main.py)..."
python main.py
