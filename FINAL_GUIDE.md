# 🚀 คู่มือการใช้งานระบบ Router Reboot + โค้ดเดิม 1176 บรรทัด

## 📋 สรุประบบ

ระบบ SSH Reboot เร้าเตอร์ GEL.iNet GL-XE300C4 สำหรับรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password และให้รันต่อเนื่องกันเลย พร้อมรวมกับโค้ดเดิม 1176 บรรทัดของคุณ

## 🎯 คุณสมบัติหลัก

### ✅ ระบบ Router Reboot
- 🔄 **รีบูทเร้าเตอร์อัตโนมัติ** ทุกๆ 10 ไอดี
- 🔐 **เชื่อมต่อ SSH โดยไม่ต้องถาม Password**
- 📊 **ติดตามสถานะการทำงานแบบ Real-time**
- 🔔 **แจ้งเตือนผ่าน Discord/Telegram**
- 📡 **ตรวจสอบการเปลี่ยนแปลง IP**
- 🛡️ **ระบบ Retry อัตโนมัติ**

### ✅ ระบบสร้างบัญชี Roblox
- 🤖 **สร้างบัญชีอัตโนมัติ**
- 📧 **เพิ่มอีเมลอัตโนมัติ**
- 👤 **เปลี่ยนชื่อแสดงผล**
- 📝 **อัปเดตข้อมูล About Me**
- 🔗 **อัปเดตลิงก์โซเชียล**
- 🛒 **ซื้อไอเทมแบบสุ่ม**

## ⚙️ การตั้งค่า

### 1. ตั้งค่าเร้าเตอร์ (`router_config.json`)
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

### 2. ตั้งค่าระบบสร้างบัญชี (`config_register.txt`)
```ini
# Discord Webhook URL (optional)
Discord_Webhook=

# Registration Settings
Username_Prefix=user
Password_Length=12
Use_Random_Suffix=true
Suffix_Length=2

# Email Settings
Add_Email=false
Email_Retry_Count=3

# Post-Login Actions
Change_Display_Name=false
Update_About_Me=false
Update_Social_Links=false
Purchase_Random_Item=false

# Browser Settings
Headless_Mode=false
Implicit_Wait=10
Page_Load_Timeout=30

# Router Reboot Settings
Enable_Router_Reboot=true
Reboot_Every_N_Accounts=10
Wait_After_Reboot=60
```

## 🚀 การใช้งาน

### 1. เปิดใช้งาน Virtual Environment
```bash
source venv/bin/activate
```

### 2. ทดสอบระบบ Router Reboot
```bash
python test_router_reboot.py
```

### 3. รันระบบสมบูรณ์
```bash
python ok_with_router_reboot_complete.py
```

## 📁 ไฟล์สำคัญ

| ไฟล์ | คำอธิบาย |
|------|----------|
| `ok_with_router_reboot_complete.py` | **ระบบหลัก** - โค้ดเดิม 1176 บรรทัด + Router Reboot |
| `router_config.json` | การตั้งค่าเร้าเตอร์ |
| `config_register.txt` | การตั้งค่าระบบสร้างบัญชี |
| `router_reboot_system.py` | ระบบ Router Reboot แยก |
| `test_router_reboot.py` | ทดสอบระบบ |
| `run_auto_router_reboot.py` | รันระบบอัตโนมัติ |
| `complete_system.py` | ระบบสมบูรณ์ |
| `QUICK_START.md` | คู่มือการใช้งานแบบรวดเร็ว |
| `SETUP_GUIDE.md` | คู่มือการติดตั้ง |
| `README.md` | คู่มือการใช้งาน |

## 🔧 ฟีเจอร์หลัก

### 🔄 ระบบ Router Reboot
- **รีบูทอัตโนมัติ**: รีบูทเร้าเตอร์ทุกๆ 10 ไอดี
- **SSH ไม่ต้องถาม Password**: ใช้การตั้งค่าในไฟล์ config
- **ตรวจสอบ IP**: ตรวจสอบการเปลี่ยนแปลง IP หลังรีบูท
- **แจ้งเตือน**: ส่งการแจ้งเตือนผ่าน Discord/Telegram
- **Retry อัตโนมัติ**: ลองใหม่อัตโนมัติหากเชื่อมต่อไม่สำเร็จ
- **Log ระบบ**: บันทึกการทำงานในไฟล์ log

### 🤖 ระบบสร้างบัญชี Roblox
- **สร้างบัญชีอัตโนมัติ**: สร้างบัญชี Roblox แบบอัตโนมัติ
- **เพิ่มอีเมล**: เพิ่มอีเมลอัตโนมัติพร้อมระบบ Retry
- **เปลี่ยนชื่อแสดงผล**: เปลี่ยนชื่อแสดงผลแบบสุ่ม
- **อัปเดตข้อมูล**: อัปเดตข้อมูล About Me และ Social Links
- **ซื้อไอเทม**: ซื้อไอเทมแบบสุ่ม
- **บันทึกข้อมูล**: บันทึกข้อมูลบัญชีที่สร้างสำเร็จ

## 📊 การติดตามสถานะ

ระบบจะแสดงสถานะดังนี้:
- 📊 **จำนวนไอดีที่เจนแล้ว**
- 🔄 **จำนวนครั้งที่รีบูท**
- 📡 **IP ปัจจุบัน**
- 🌐 **สถานะการเชื่อมต่ออินเทอร์เน็ต**
- 🔌 **สถานะการเชื่อมต่อ SSH**
- ✅ **สถานะการสร้างบัญชี**

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

### ❌ ไม่สามารถสร้างบัญชีได้
1. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
2. ตรวจสอบการตั้งค่า Browser
3. ตรวจสอบการตั้งค่า Roblox

### ❌ ระบบหยุดทำงาน
1. ตรวจสอบ Log ใน `router_reboot.log`
2. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
3. ตรวจสอบสถานะเร้าเตอร์

## 📈 การปรับแต่ง

### เปลี่ยนจำนวนไอดีก่อนรีบูท
แก้ไขใน `router_config.json`:
```json
"reboot_every_n_accounts": 10
```

### เปลี่ยนเวลารอหลังรีบูท
แก้ไขใน `router_config.json`:
```json
"wait_after_reboot": 60
```

### เปิด/ปิดระบบ Router Reboot
แก้ไขใน `config_register.txt`:
```ini
Enable_Router_Reboot=true
```

### เปลี่ยนการตั้งค่าบราวเซอร์
แก้ไขใน `config_register.txt`:
```ini
Headless_Mode=false
Implicit_Wait=10
Page_Load_Timeout=30
```

## 🔄 การอัปเดต

ระบบจะอัปเดตอัตโนมัติเมื่อ:
- เปลี่ยนการตั้งค่าใน `router_config.json`
- เปลี่ยนการตั้งค่าใน `config_register.txt`
- รีสตาร์ทระบบ
- เกิดข้อผิดพลาดและ Retry

## ⚠️ คำเตือน

1. **ความปลอดภัย**: เก็บ password ไว้ในไฟล์ config อย่างปลอดภัย
2. **การทดสอบ**: ทดสอบระบบในสภาพแวดล้อมที่ปลอดภัยก่อน
3. **การสำรองข้อมูล**: สำรองข้อมูลสำคัญก่อนใช้งาน
4. **การตรวจสอบ**: ตรวจสอบ log file เป็นประจำ

## 🆘 การสนับสนุน

หากมีปัญหา:
1. ตรวจสอบ log file `router_reboot.log`
2. ตรวจสอบการตั้งค่าใน `router_config.json`
3. ตรวจสอบการตั้งค่าใน `config_register.txt`
4. ทดสอบการเชื่อมต่อ SSH ด้วยตนเอง
5. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต

## 🎉 การเริ่มต้นใช้งาน

1. แก้ไขไฟล์ `router_config.json` ให้ถูกต้อง
2. แก้ไขไฟล์ `config_register.txt` ตามต้องการ
3. เปิดใช้งาน virtual environment
4. รันระบบ: `python ok_with_router_reboot_complete.py`
5. ตรวจสอบ log และสถานะการทำงาน

---

**หมายเหตุ**: ระบบนี้ออกแบบมาเฉพาะสำหรับเร้าเตอร์ GEL.iNet GL-XE300C4 และรวมกับโค้ดเดิม 1176 บรรทัดของคุณ กรุณาตรวจสอบความเข้ากันได้ก่อนใช้งาน