from fastapi import FastAPI, Header, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from usbpum_db import (
    save_pattern, get_stats,
    create_verification_token, verify_email_token, is_email_verified
)

# โหลดค่าตั้งค่า
load_dotenv()
MASTER_KEY = os.getenv("USBPUM_MASTER_KEY", "สนักตัวแรกชื่อโชดา")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

app = FastAPI(title="USBPUM API - ระบบล็อก")

# --------------------------
# ระบบตรวจสอบรหัสหลัก
# --------------------------
def verify_master_key(x_api_key: str = Header(None, description="รหัสปลดล็อกระบบ")):
    if not x_api_key or x_api_key != MASTER_KEY:
        raise HTTPException(
            status_code=403,
            detail="❌ ไม่สามารถเข้าใช้งานได้: รหัสไม่ถูกต้อง ต้องการเข้าถึงโปรดติดต่อผู้พัฒนา หรือขอคำใบ้"
        )
    return True

# --------------------------
# ฟังก์ชันส่งอีเมล์ยืนยัน
# --------------------------
def send_verification_email(email: str, token: str):
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASSWORD]):
        raise HTTPException(500, detail="❌ ระบบส่งเมล์ยังไม่ได้รับการตั้งค่า")

    verify_link = f"http://localhost:8006/verify-email?token={token}"
    msg = MIMEText(f"""
    สวัสดีครับ,

    คลิกลิงก์นี้เพื่อยืนยันอีเมล์และรับคำใบ้:
    {verify_link}

    ลิงก์นี้ใช้ได้ 7 วันเท่านั้น
    """, "plain", "utf-8")
    
    msg["Subject"] = "ยืนยันอีเมล์เพื่อรับคำใบ้ - USBPUM"
    msg["From"] = SMTP_USER
    msg["To"] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())
        return True
    except Exception as e:
        raise HTTPException(500, detail=f"❌ ส่งเมล์ไม่สำเร็จ: {str(e)}")

# --------------------------
# โมเดลข้อมูล
# --------------------------
class SubmitData(BaseModel):
    query: str
    response: str
    category: str = "general"
    success: int = 1

class HintRequest(BaseModel):
    email: EmailStr

# --------------------------
# API Endpoints
# --------------------------
@app.get("/")
def read_root():
    return {
        "system": "USBPUM API",
        "status": "🔒 ล็อกอยู่",
        "message": "ต้องใส่รหัสหลักใน Header X-API-Key เพื่อใช้งาน",
        "hint": "ต้องการคำใบ้? ส่งอีเมล์มาที่ /request-hint"
    }

@app.post("/submit", dependencies=[Depends(verify_master_key)])
def submit_data(data: SubmitData):
    save_pattern(data.model_dump())
    return {"status": "✅ บันทึกข้อมูลสำเร็จ"}

@app.get("/stats", dependencies=[Depends(verify_master_key)])
def get_statistics():
    return get_stats()

@app.post("/request-hint")
def request_hint(data: HintRequest):
    """ขอส่งลิงก์ยืนยันอีเมล์เพื่อรับคำใบ้"""
    token = create_verification_token(data.email)
    send_verification_email(data.email, token)
    return {
        "status": "✅ ส่งลิงก์ยืนยันไปที่อีเมล์แล้ว",
        "message": "คลิกลิงก์ในเมล์เพื่อรับคำใบ้"
    }

@app.get("/verify-email")
def verify_email(token: str):
    """ยืนยันอีเมล์และแสดงคำใบ้"""
    if verify_email_token(token):
        return {
            "status": "✅ ยืนยันสำเร็จ",
            "hint": "💡 คำใบ้: รหัสเริ่มต้นด้วยคำว่า 'สนัก' ตามด้วยชื่อสัตว์เลี้ยงตัวแรกของผู้สร้างระบบ"
        }
    else:
        return JSONResponse(
            status_code=400,
            content={"status": "❌ ไม่ถูกต้อง", "message": "ลิงก์ไม่ถูกต้องหรือหมดอายุ"}
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 USBPUM ทำงานที่: http://localhost:8006")
    print("🔒 ระบบล็อก: ใช้รหัส 'สนักตัวแรกชื่อโชดา' เพื่อเข้าใช้งาน")
    print("💡 ขอคำใบ้ได้ที่: POST /request-hint")
    uvicorn.run("main:app", host="0.0.0.0", port=8006)

