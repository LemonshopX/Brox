# คู่มือการติดตั้งและใช้งานระบบ Router Reboot

## 📋 สรุประบบ

ระบบนี้จะรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password และให้รันต่อเนื่องกันเลย สำหรับเร้าเตอร์ GEL.iNet GL-XE300C4

## 🚀 การติดตั้ง

### 1. เปิดใช้งาน Virtual Environment
```bash
source venv/bin/activate
```

### 2. ตรวจสอบ Dependencies
```bash
pip list | grep -E "(paramiko|requests|selenium|beautifulsoup4|pyautogui|webdriver-manager)"
```

## ⚙️ การตั้งค่า

### 1. แก้ไขไฟล์ `router_config.json`
```json
{
    "router": {
        "host": "192.168.1.1",        // IP ของเร้าเตอร์
        "port": 22,                    // SSH Port
        "username": "root",            // SSH Username
        "password": "your_password"    // SSH Password
    },
    "reboot_settings": {
        "reboot_every_n_accounts": 10, // จำนวนไอดีก่อนรีบูท
        "wait_after_reboot": 60,       // เวลารอหลังรีบูท (วินาที)
        "max_retries": 3,              // จำนวนครั้งที่ลองใหม่
        "connection_timeout": 30        // Timeout การเชื่อมต่อ SSH
    }
}
```

### 2. ตั้งค่า Discord/Telegram (ไม่บังคับ)
```json
{
    "notification": {
        "discord_webhook": "YOUR_DISCORD_WEBHOOK_URL",
        "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
        "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID"
    }
}
```

## 🎯 การใช้งาน

### 1. ทดสอบระบบ Router Reboot อย่างเดียว
```bash
python router_reboot_system.py
```

### 2. ใช้งานกับระบบเดิม
```bash
python integrated_system.py
```

### 3. ใช้งานกับระบบเดิมโดยตรง
```bash
python ok_with_router_reboot.py
```

## 📊 ฟีเจอร์หลัก

- 🔄 **รีบูทอัตโนมัติ**: รีบูทเร้าเตอร์ทุกๆ 10 ไอดี
- 🔐 **SSH ไม่ต้องถาม Password**: ใช้การตั้งค่าในไฟล์ config
- 📡 **ตรวจสอบ IP**: ตรวจสอบการเปลี่ยนแปลง IP หลังรีบูท
- 🔔 **แจ้งเตือน**: ส่งการแจ้งเตือนผ่าน Discord/Telegram
- 🛡️ **Retry อัตโนมัติ**: ลองใหม่อัตโนมัติหากเชื่อมต่อไม่สำเร็จ
- 📝 **Log ระบบ**: บันทึกการทำงานในไฟล์ log

## 📁 ไฟล์ที่สำคัญ

- `router_reboot_system.py`: ระบบหลัก Router Reboot
- `router_config.json`: การตั้งค่าเร้าเตอร์
- `integrated_system.py`: ระบบรวมกับระบบเดิม
- `ok_with_router_reboot.py`: ระบบเดิมที่รวม Router Reboot แล้ว
- `router_reboot.log`: Log การทำงาน
- `requirements.txt`: Dependencies

## 🔧 การแก้ไขปัญหา

### 1. ไม่สามารถเชื่อมต่อ SSH
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

## 📈 การติดตามสถานะ

ระบบจะแสดงสถานะดังนี้:
- 📊 จำนวนไอดีที่เจนแล้ว
- 🔄 จำนวนครั้งที่รีบูท
- 📡 IP ปัจจุบัน
- 🌐 สถานะการเชื่อมต่ออินเทอร์เน็ต
- 🔌 สถานะการเชื่อมต่อ SSH

## ⚠️ คำเตือน

1. **ความปลอดภัย**: เก็บ password ไว้ในไฟล์ config อย่างปลอดภัย
2. **การทดสอบ**: ทดสอบระบบในสภาพแวดล้อมที่ปลอดภัยก่อน
3. **การสำรองข้อมูล**: สำรองข้อมูลสำคัญก่อนใช้งาน
4. **การตรวจสอบ**: ตรวจสอบ log file เป็นประจำ

## 🆘 การสนับสนุน

หากมีปัญหา:
1. ตรวจสอบ log file `router_reboot.log`
2. ตรวจสอบการตั้งค่าใน `router_config.json`
3. ทดสอบการเชื่อมต่อ SSH ด้วยตนเอง
4. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต

## 🎉 การเริ่มต้นใช้งาน

1. แก้ไขไฟล์ `router_config.json` ให้ถูกต้อง
2. เปิดใช้งาน virtual environment
3. รันระบบตามต้องการ
4. ตรวจสอบ log และสถานะการทำงาน

---

**หมายเหตุ**: ระบบนี้ถูกออกแบบมาเพื่อใช้งานกับเร้าเตอร์ GEL.iNet GL-XE300C4 โดยเฉพาะ แต่สามารถปรับแต่งให้ใช้งานกับเร้าเตอร์อื่นๆ ได้