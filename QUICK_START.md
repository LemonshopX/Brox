# 🚀 คู่มือการใช้งานระบบ Router Reboot แบบรวดเร็ว

## 📋 สรุประบบ
ระบบ SSH Reboot เร้าเตอร์ GEL.iNet GL-XE300C4 สำหรับรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password และให้รันต่อเนื่องกันเลย

## ⚡ การใช้งานแบบรวดเร็ว

### 1. ตั้งค่าเร้าเตอร์
แก้ไขไฟล์ `router_config.json`:
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
        "wait_after_reboot": 60,       // รอหลังรีบูท (วินาที)
        "max_retries": 3,              // จำนวนครั้งลองใหม่
        "connection_timeout": 30        // Timeout การเชื่อมต่อ
    }
}
```

### 2. ทดสอบระบบ
```bash
# เปิดใช้งาน Virtual Environment
source venv/bin/activate

# ทดสอบการเชื่อมต่อ
python test_router_reboot.py
```

### 3. รันระบบอัตโนมัติ
```bash
# รันระบบอัตโนมัติ (จำลองการเจนไอดี)
python run_auto_router_reboot.py

# รันระบบสมบูรณ์ (รวมกับระบบเดิม)
python complete_system.py
```

## 🔧 ไฟล์สำคัญ

| ไฟล์ | คำอธิบาย |
|------|----------|
| `router_config.json` | การตั้งค่าเร้าเตอร์ |
| `router_reboot_system.py` | ระบบหลัก Router Reboot |
| `test_router_reboot.py` | ทดสอบระบบ |
| `run_auto_router_reboot.py` | รันระบบอัตโนมัติ |
| `complete_system.py` | ระบบสมบูรณ์ |
| `ok_with_router_reboot.py` | ระบบเดิม + Router Reboot |

## 🎯 คุณสมบัติหลัก

### ✅ ระบบ Router Reboot
- 🔄 รีบูทเร้าเตอร์อัตโนมัติทุกๆ 10 ไอดี
- 🔐 เชื่อมต่อ SSH โดยไม่ต้องถาม Password
- 📊 ติดตามสถานะการทำงานแบบ Real-time
- 🔔 แจ้งเตือนผ่าน Discord/Telegram
- 📡 ตรวจสอบการเปลี่ยนแปลง IP
- 🛡️ ระบบ Retry อัตโนมัติ

### ✅ ระบบความปลอดภัย
- 🔒 การเชื่อมต่อ SSH แบบปลอดภัย
- ⏱️ Timeout การเชื่อมต่อ
- 🔄 Retry อัตโนมัติเมื่อล้มเหลว
- 📝 บันทึก Log การทำงาน

## 🚨 การแก้ไขปัญหา

### ❌ ไม่สามารถเชื่อมต่อ SSH ได้
1. ตรวจสอบ IP ของเร้าเตอร์
2. ตรวจสอบ Username/Password
3. ตรวจสอบ SSH Port
4. ตรวจสอบการเปิดใช้งาน SSH บนเร้าเตอร์

### ❌ ไม่สามารถรีบูทเร้าเตอร์ได้
1. ตรวจสอบสิทธิ์การรีบูท
2. ตรวจสอบคำสั่งรีบูทของเร้าเตอร์
3. ตรวจสอบการตั้งค่าใน config

### ❌ ระบบหยุดทำงาน
1. ตรวจสอบ Log ใน `router_reboot.log`
2. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
3. ตรวจสอบสถานะเร้าเตอร์

## 📞 การสนับสนุน

หากมีปัญหา กรุณาตรวจสอบ:
1. ไฟล์ Log: `router_reboot.log`
2. การตั้งค่า: `router_config.json`
3. การเชื่อมต่อเร้าเตอร์

## 🔄 การอัปเดต

ระบบจะอัปเดตอัตโนมัติเมื่อ:
- เปลี่ยนการตั้งค่าใน `router_config.json`
- รีสตาร์ทระบบ
- เกิดข้อผิดพลาดและ Retry

---

**หมายเหตุ**: ระบบนี้ออกแบบมาเฉพาะสำหรับเร้าเตอร์ GEL.iNet GL-XE300C4 กรุณาตรวจสอบความเข้ากันได้ก่อนใช้งาน