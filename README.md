# ระบบ SSH Reboot เร้าเตอร์ GEL.iNet GL-XE300C4

ระบบนี้จะรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password และให้รันต่อเนื่องกันเลย

## คุณสมบัติ

- 🔄 รีบูทเร้าเตอร์อัตโนมัติทุกๆ 10 ไอดี
- 🔐 เชื่อมต่อ SSH โดยไม่ต้องถาม Password
- 📊 ติดตามสถานะการทำงานแบบ Real-time
- 🔔 แจ้งเตือนผ่าน Discord/Telegram
- 📡 ตรวจสอบการเปลี่ยนแปลง IP
- 🛡️ ระบบ Retry อัตโนมัติ

## การติดตั้ง

1. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

2. แก้ไขไฟล์ `router_config.json`:
```json
{
    "router": {
        "host": "192.168.1.1",
        "port": 22,
        "username": "root",
        "password": "your_password_here"
    },
    "reboot_settings": {
        "reboot_every_n_accounts": 10,
        "wait_after_reboot": 60,
        "max_retries": 3
    }
}
```

## การใช้งาน

### 1. ทดสอบระบบ Router Reboot อย่างเดียว
```bash
python router_reboot_system.py
```

### 2. ใช้งานกับระบบเดิม
```bash
python integrated_system.py
```

### 3. ใช้งานกับระบบเดิมโดยตรง
แก้ไขไฟล์ `ok.py` เพื่อเพิ่ม Router Reboot:

```python
# เพิ่มที่ด้านบนของไฟล์
from router_reboot_system import RouterRebootSystem

# สร้าง instance
router_system = RouterRebootSystem()
router_system.start_monitoring()

# แก้ไขฟังก์ชัน log_success
def log_success(username, password, cookies):
    # โค้ดเดิม...
    
    # เพิ่มการเรียก Router Reboot
    router_system.account_generated()
```

## การตั้งค่า

### Router Settings
- `host`: IP address ของเร้าเตอร์ (default: 192.168.1.1)
- `port`: SSH port (default: 22)
- `username`: SSH username (default: root)
- `password`: SSH password
- `key_file`: SSH key file (ถ้ามี)

### Reboot Settings
- `reboot_every_n_accounts`: จำนวนไอดีก่อนรีบูท (default: 10)
- `wait_after_reboot`: เวลารอหลังรีบูท (วินาที)
- `max_retries`: จำนวนครั้งที่ลองใหม่
- `connection_timeout`: timeout การเชื่อมต่อ SSH

### Notification Settings
- `discord_webhook`: Discord webhook URL
- `telegram_bot_token`: Telegram bot token
- `telegram_chat_id`: Telegram chat ID

## การแก้ไขปัญหา

### 1. ไม่สามารถเชื่อมต่อ SSH ได้
- ตรวจสอบ IP address ของเร้าเตอร์
- ตรวจสอบ username/password
- ตรวจสอบว่า SSH เปิดใช้งานอยู่

### 2. รีบูทไม่สำเร็จ
- ตรวจสอบสิทธิ์ของ user
- ลองเปลี่ยนคำสั่งรีบูทในโค้ด
- เพิ่ม wait time หลังรีบูท

### 3. IP ไม่เปลี่ยน
- ตรวจสอบการตั้งค่า ISP
- ลองรีบูทหลายๆ ครั้ง
- ตรวจสอบ log file

## ไฟล์ Log

ระบบจะสร้างไฟล์ log ดังนี้:
- `router_reboot.log`: Log การทำงานของ Router Reboot
- `account_ok.txt`: บัญชีที่สร้างสำเร็จ
- `router_config.json`: การตั้งค่า

## ความปลอดภัย

⚠️ **คำเตือน**: 
- เก็บ password ไว้ในไฟล์ config อย่างปลอดภัย
- ใช้ SSH key แทน password ถ้าเป็นไปได้
- ตรวจสอบสิทธิ์การเข้าถึงไฟล์ config

## การพัฒนา

### เพิ่มคำสั่งรีบูทใหม่
แก้ไขใน `router_reboot_system.py`:
```python
reboot_commands = [
    "reboot",
    "sync && reboot",
    "/sbin/reboot",
    "killall -9 init && reboot",
    "your_custom_command"  # เพิ่มคำสั่งใหม่
]
```

### เพิ่มการแจ้งเตือนใหม่
แก้ไขฟังก์ชัน `send_notification()` ใน `router_reboot_system.py`

## สนับสนุน

หากมีปัญหา กรุณาตรวจสอบ:
1. Log files
2. การตั้งค่า network
3. สิทธิ์การเข้าถึงเร้าเตอร์
4. การเชื่อมต่ออินเทอร์เน็ต