# 🚀 Quick Start Guide - ระบบ Router Reboot

## การติดตั้งและรันแบบเร็ว

### ขั้นตอนที่ 1: ติดตั้งระบบ
```bash
python setup_and_run.py
```

### ขั้นตอนที่ 2: ตั้งค่าเร้าเตอร์
แก้ไขไฟล์ `router_config.json`:
```json
{
    "router": {
        "host": "192.168.1.1",  // IP ของเร้าเตอร์
        "port": 22,
        "username": "root",
        "password": "your_password_here"  // รหัสผ่าน SSH
    },
    "reboot_settings": {
        "reboot_every_n_accounts": 10,  // รีบูททุก 10 ไอดี
        "wait_after_reboot": 60,
        "max_retries": 3
    }
}
```

### ขั้นตอนที่ 3: ทดสอบการเชื่อมต่อ
```bash
python test_router_reboot.py
```

### ขั้นตอนที่ 4: รันระบบ
```bash
python ok_with_router_integration.py
```

## ไฟล์สำคัญ

- `setup_and_run.py` - ติดตั้งและรันระบบ
- `router_config.json` - ตั้งค่าเร้าเตอร์
- `ok_with_router_integration.py` - ระบบรวม (แนะนำ)
- `test_router_reboot.py` - ทดสอบการเชื่อมต่อ

## การแก้ไขปัญหา

### ไม่สามารถเชื่อมต่อ SSH
1. ตรวจสอบ IP address ของเร้าเตอร์
2. ตรวจสอบ username/password
3. ตรวจสอบว่า SSH เปิดใช้งาน

### รีบูทไม่สำเร็จ
1. ตรวจสอบสิทธิ์ของผู้ใช้ SSH
2. ตรวจสอบคำสั่งรีบูทในเร้าเตอร์
3. เพิ่ม wait time หลังรีบูท

## Log Files

- `router_reboot.log` - Log การทำงาน
- `account_ok.txt` - บัญชีที่สำเร็จ
- `account_failed.txt` - บัญชีที่ล้มเหลว

## คำสั่งที่ใช้บ่อย

```bash
# ติดตั้งระบบ
python setup_and_run.py

# ทดสอบการเชื่อมต่อ
python test_router_reboot.py

# รันระบบรวม
python ok_with_router_integration.py

# รันระบบแยก
python router_reboot_system.py

# รันแบบง่าย
python run_system.py
```

## การตั้งค่าขั้นสูง

### เปลี่ยนจำนวนไอดีก่อนรีบูท
แก้ไขใน `router_config.json`:
```json
"reboot_every_n_accounts": 5  // รีบูททุก 5 ไอดี
```

### เพิ่มการแจ้งเตือน Discord
```json
"notification": {
    "discord_webhook": "YOUR_DISCORD_WEBHOOK_URL"
}
```

### เพิ่มการแจ้งเตือน Telegram
```json
"notification": {
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID"
}
```

## ความปลอดภัย

⚠️ **สำคัญ**: 
- เก็บ password ไว้อย่างปลอดภัย
- ใช้ SSH key แทน password ถ้าเป็นไปได้
- ตรวจสอบสิทธิ์การเข้าถึงไฟล์ config

## สนับสนุน

หากมีปัญหา:
1. ตรวจสอบ log files
2. ทดสอบการเชื่อมต่อ SSH
3. ตรวจสอบการตั้งค่าเร้าเตอร์
4. ตรวจสอบ dependencies