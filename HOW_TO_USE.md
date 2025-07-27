# วิธีใช้งานระบบ SSH Reboot เร้าเตอร์ GL.iNet GL-XE300C4

## 🚀 เริ่มใช้งานเร็วๆ (5 ขั้นตอน)

### 1. ติดตั้ง Dependencies
```bash
python3 install_requirements.py
```

### 2. เปิด SSH ในเร้าเตอร์
- เข้า `http://192.168.8.1`
- ไปที่ **System** → **Administration** 
- เปิด **SSH Access**

### 3. รันโปรแกรม
```bash
python3 ok.py
```

### 4. Setup SSH ครั้งแรก
- เลือก `s` เพื่อ Setup SSH
- ใส่รหัสผ่านเร้าเตอร์ (ลอง: เว้นว่าง หรือ `goodlife`)

### 5. ทดสอบการเชื่อมต่อ
- เลือก `t` เพื่อทดสอบ SSH
- ถ้าเห็น ✅ แสดงว่าพร้อมใช้งาน!

## 📋 เมนูการใช้งาน

```
==========================================
Please select an operation mode:
  1: Register from file          ← สมัครจากไฟล์ accounts.txt
  2: Log in & Update Cookie      ← อัปเดต Cookie จากไฟล์ cookie_join.txt  
  3: Interactive Register        ← สมัครแบบโต้ตอบ
  s: Setup SSH Router Auth       ← ตั้งค่า SSH ครั้งแรก
  t: Test Router SSH Connection  ← ทดสอบการเชื่อมต่อ SSH
  q: Exit program               ← ออกจากโปรแกรม
==========================================
```

## ⚙️ การตั้งค่าในไฟล์ config_register.txt

เพิ่มบรรทัดเหล่านี้:
```
ROUTER_SSH_HOST=192.168.8.1      # IP เร้าเตอร์ 
ROUTER_SSH_PORT=22               # Port SSH
ROUTER_SSH_USERNAME=root         # Username SSH
ROUTER_REBOOT_ENABLED=True       # เปิด/ปิด การรีบูต
ROUTER_REBOOT_INTERVAL=10        # รีบูตทุกกี่ไอดี
```

## 🔄 การทำงานอัตโนมัติ

ระบบจะ:
1. นับไอดีที่สมัครสำเร็จ
2. ครับ 10 ไอดี → รีบูตเร้าเตอร์ → รอ IP ใหม่
3. ดำเนินการต่อด้วย IP ใหม่
4. ทำซ้ำไปเรื่อยๆ

## 🛠️ แก้ปัญหาด่วน

**SSH Connection Failed:**
```bash
ping 192.168.8.1          # ตรวจสอบเร้าเตอร์
ssh root@192.168.8.1      # ทดสอบ SSH ด้วยมือ
```

**เปลี่ยนจำนวนไอดีก่อนรีบูต:**
แก้ `ROUTER_REBOOT_INTERVAL=5` (รีบูตทุก 5 ไอดี)

**ปิดการรีบูต:**
แก้ `ROUTER_REBOOT_ENABLED=False`

---

🎯 **พร้อมใช้แล้ว!** เลือกโหมด 1, 2, หรือ 3 เพื่อเริ่มสมัครไอดี ระบบจะรีบูตเร้าเตอร์อัตโนมัติทุกๆ 10 ไอดี!