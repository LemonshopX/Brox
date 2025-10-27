# ระบบ SSH Reboot เร้าเตอร์ GEL.iNet GL-XE300C4

ระบบนี้จะรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password และให้รันต่อเนื่องกันเลย

## คุณสมบัติ

- 🔄 รีบูทเร้าเตอร์อัตโนมัติทุกๆ 10 ไอดี
- 🔐 เชื่อมต่อ SSH โดยไม่ต้องถาม Password
- 📊 ติดตามสถานะการทำงานแบบ Real-time
- 🔔 แจ้งเตือนผ่าน Discord/Telegram
- 📡 ตรวจสอบการเปลี่ยนแปลง IP
- 🛡️ ระบบ Retry อัตโนมัติ
- 🤖 รวมกับระบบเจนอีเมลเดิม

## การติดตั้งและรัน

### วิธีที่ 1: ใช้ไฟล์ Setup (แนะนำ)
```bash
python setup_and_run.py
```

### วิธีที่ 2: ติดตั้งด้วยตนเอง
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

### 1. ทดสอบระบบ Router Reboot
```bash
python test_router_reboot.py
```

### 2. รันระบบรวม (แนะนำ)
```bash
python ok_with_router_integration.py
```

### 3. รันระบบแยก
```bash
python router_reboot_system.py
```

### 4. รันระบบเดิมพร้อม Router Reboot
```bash
python ok_with_router_reboot.py
```

## การตั้งค่า

### Router Configuration
- `host`: IP address ของเร้าเตอร์ (เช่น 192.168.1.1)
- `port`: SSH port (ปกติคือ 22)
- `username`: ชื่อผู้ใช้ SSH (เช่น root)
- `password`: รหัสผ่าน SSH
- `key_file`: ไฟล์ SSH key (ถ้าใช้)

### Reboot Settings
- `reboot_every_n_accounts`: จำนวนอีเมลก่อนรีบูท (ค่าเริ่มต้น: 10)
- `wait_after_reboot`: เวลารอหลังรีบูท (วินาที)
- `max_retries`: จำนวนครั้งที่ลองใหม่
- `connection_timeout`: เวลาหมดเวลาการเชื่อมต่อ

### Notification Settings
- `discord_webhook`: Discord webhook URL
- `telegram_bot_token`: Telegram bot token
- `telegram_chat_id`: Telegram chat ID

## ไฟล์ที่สำคัญ

- `router_reboot_system.py`: ระบบหลักสำหรับ Router Reboot
- `router_config.json`: การตั้งค่าเร้าเตอร์
- `ok_with_router_integration.py`: ระบบรวมกับระบบเดิม (แนะนำ)
- `ok_with_router_reboot.py`: ระบบรวมแบบอื่น
- `test_router_reboot.py`: ไฟล์ทดสอบ
- `setup_and_run.py`: ไฟล์ติดตั้งและรัน
- `integrated_system.py`: ระบบรวมแบบแยก

## การแก้ไขปัญหา

### ปัญหาการเชื่อมต่อ SSH
1. ตรวจสอบ IP address ของเร้าเตอร์
2. ตรวจสอบ username และ password
3. ตรวจสอบว่า SSH เปิดใช้งานอยู่
4. ตรวจสอบ firewall settings

### ปัญหาการรีบูทไม่สำเร็จ
1. ตรวจสอบคำสั่งรีบูทในเร้าเตอร์
2. ตรวจสอบสิทธิ์ของผู้ใช้ SSH
3. ตรวจสอบ log files

### ปัญหาการรวมกับระบบเดิม
1. ตรวจสอบว่าไฟล์ `ok.py` มีอยู่
2. ตรวจสอบการตั้งค่าใน `config_register.txt`
3. ตรวจสอบ dependencies ทั้งหมด

## Log Files

- `router_reboot.log`: Log ของระบบ Router Reboot
- `account_ok.txt`: บัญชีที่สร้างสำเร็จ
- `account_failed.txt`: บัญชีที่สร้างไม่สำเร็จ

## การแจ้งเตือน

ระบบรองรับการแจ้งเตือนผ่าน:
- Discord Webhook
- Telegram Bot

## การพัฒนา

ระบบนี้พัฒนาด้วย Python 3 และใช้ libraries ต่อไปนี้:
- paramiko: สำหรับ SSH connection
- requests: สำหรับ HTTP requests
- selenium: สำหรับ browser automation
- beautifulsoup4: สำหรับ web scraping
- pyautogui: สำหรับ GUI automation
- webdriver-manager: สำหรับ Chrome driver management

## ขั้นตอนการใช้งาน

1. **ติดตั้งระบบ**: รัน `python setup_and_run.py`
2. **ตั้งค่าเร้าเตอร์**: แก้ไข `router_config.json`
3. **ทดสอบการเชื่อมต่อ**: รัน `python test_router_reboot.py`
4. **รันระบบ**: รัน `python ok_with_router_integration.py`

## ความปลอดภัย

⚠️ **คำเตือน**: 
- เก็บ password ไว้ในไฟล์ config อย่างปลอดภัย
- ใช้ SSH key แทน password ถ้าเป็นไปได้
- ตรวจสอบสิทธิ์การเข้าถึงไฟล์ config

## License

MIT License