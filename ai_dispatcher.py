import os
import sys
import subprocess
from dotenv import load_dotenv

# โหลดค่าคอนฟิกจากไฟล์ .env
load_dotenv()

class AICommandDispatcher:
    def __init__(self):
        self.system_name = os.getenv("SYSTEM_NAME", "usbpum-core")
        print(f"[{self.system_name}] AI Command Dispatcher initialized successfully.")

    def execute_command(self, action: str, target: str = "", payload: dict = None):
        """
        ประมวลผลและกระจายคำสั่งที่ได้รับจาก AI ไปยังระบบที่ติดตั้ง
        """
        payload = payload or {}
        print(f"-> Dispatching action '{action}' to target '{target}' with payload: {payload}")

        if action == "update_code":
            return self._cmd_update_code()
        elif action == "run_script":
            script_name = payload.get("script", "main.py")
            return self._cmd_run_script(script_name)
        elif action == "device_control":
            device_id = target
            command_state = payload.get("state", "off")
            return self._cmd_device_control(device_id, command_state)
        else:
            return {"status": "error", "message": f"Unknown command action: {action}"}

    def _cmd_update_code(self):
        """คำสั่งอัปเดตโค้ดจาก Git อัตโนมัติ"""
        try:
            result = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True, check=True)
            return {"status": "success", "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"status": "failed", "error": e.stderr}

    def _cmd_run_script(self, script_name):
        """คำสั่งรันสคริปต์ภายในระบบ"""
        try:
            result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
            return {"status": "success", "output": result.stdout}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _cmd_device_control(self, device_id, state):
        """จำลองการส่งคำสั่งไปควบคุมอุปกรณ์ฮาร์ดแวร์หรือปั๊มผ่าน USB"""
        # สามารถเขียนโค้ดเชื่อมต่อ Serial / PySerial ตรงนี้เพิ่มเติมได้
        print(f"[Hardware Control] Device {device_id} -> State: {state}")
        return {"status": "success", "device": device_id, "state": state}

# ตัวอย่างการทดสอบใช้งานเมื่อเรียกไฟล์นี้โดยตรง
if __name__ == "__main__":
    dispatcher = AICommandDispatcher()
    
    # จำลอง AI ส่งคำสั่งควบคุมอุปกรณ์
    response = dispatcher.execute_command(
        action="device_control", 
        target="USB_PUMP_01", 
        payload={"state": "on"}
    )
    print("Result:", response)
