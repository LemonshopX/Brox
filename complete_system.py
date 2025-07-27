#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ระบบสมบูรณ์ Router Reboot + ระบบเดิม
สำหรับเร้าเตอร์ GEL.iNet GL-XE300C4
"""

import sys
import os
import time
import json
import threading
from datetime import datetime
from router_reboot_system import RouterRebootSystem

# Import ระบบเดิม
try:
    from ok import *
except ImportError:
    print("⚠️  ไม่พบไฟล์ ok.py กรุณาตรวจสอบ")
    sys.exit(1)

class CompleteSystem:
    def __init__(self):
        self.router_system = None
        self.is_running = False
        self.account_counter = 0
        self.reboot_counter = 0
        self.original_system = None
        
    def load_config(self):
        """โหลดการตั้งค่า"""
        try:
            with open("router_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ ไม่สามารถโหลด config ได้: {e}")
            return None
    
    def start_router_system(self):
        """เริ่มระบบ Router Reboot"""
        print("🔧 เริ่มระบบ Router Reboot...")
        
        try:
            self.router_system = RouterRebootSystem()
            
            # ทดสอบการเชื่อมต่อ
            if not self.router_system.test_connection():
                print("❌ ไม่สามารถเชื่อมต่อกับเร้าเตอร์ได้")
                return False
            
            print("✅ ระบบ Router Reboot พร้อมใช้งาน!")
            return True
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def start_original_system(self):
        """เริ่มระบบเดิม"""
        print("🚀 เริ่มระบบเดิม...")
        
        try:
            # เริ่มระบบเดิมใน thread แยก
            self.original_system = threading.Thread(target=self.run_original_system)
            self.original_system.daemon = True
            self.original_system.start()
            
            print("✅ ระบบเดิมเริ่มทำงานแล้ว!")
            return True
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def run_original_system(self):
        """รันระบบเดิม"""
        try:
            # เรียกใช้ฟังก์ชันหลักของระบบเดิม
            # หมายเหตุ: ต้องปรับแต่งตามโครงสร้างของระบบเดิม
            print("🔄 ระบบเดิมกำลังทำงาน...")
            
            # จำลองการทำงานของระบบเดิม
            while self.is_running:
                # เพิ่มเคาน์เตอร์ไอดี
                self.account_counter += 1
                current_time = datetime.now().strftime("%H:%M:%S")
                
                print(f"[{current_time}] 🔄 ระบบเดิม: กำลังเจนไอดี #{self.account_counter}")
                
                # ตรวจสอบว่าต้องรีบูทหรือไม่
                config = self.load_config()
                if config and self.account_counter % config['reboot_settings']['reboot_every_n_accounts'] == 0:
                    print(f"🔄 ถึงเวลารีบูท! (ไอดี #{self.account_counter})")
                    self.reboot_router()
                
                # รอ 3 วินาที
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในระบบเดิม: {e}")
    
    def reboot_router(self):
        """รีบูทเร้าเตอร์"""
        try:
            self.reboot_counter += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            
            print(f"[{current_time}] 🔄 กำลังรีบูทเร้าเตอร์... (ครั้งที่ {self.reboot_counter})")
            
            if self.router_system and self.router_system.reboot_router():
                print(f"✅ รีบูทเร้าเตอร์สำเร็จ! (ครั้งที่ {self.reboot_counter})")
                
                # รอให้เร้าเตอร์บูทเสร็จ
                config = self.load_config()
                wait_time = config['reboot_settings']['wait_after_reboot'] if config else 60
                print(f"⏳ รอ {wait_time} วินาทีให้เร้าเตอร์บูทเสร็จ...")
                time.sleep(wait_time)
                
                # ทดสอบการเชื่อมต่อใหม่
                if self.router_system.test_connection():
                    print("✅ เร้าเตอร์พร้อมใช้งานแล้ว!")
                else:
                    print("⚠️  เร้าเตอร์ยังไม่พร้อมใช้งาน")
                    
            else:
                print("❌ ไม่สามารถรีบูทเร้าเตอร์ได้")
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการรีบูท: {e}")
    
    def start_system(self):
        """เริ่มระบบทั้งหมด"""
        print("🚀 เริ่มระบบสมบูรณ์...")
        
        config = self.load_config()
        if not config:
            return False
        
        # เริ่มระบบ Router Reboot
        if not self.start_router_system():
            return False
        
        # เริ่มระบบเดิม
        if not self.start_original_system():
            return False
        
        self.is_running = True
        print("✅ ระบบสมบูรณ์เริ่มทำงานแล้ว!")
        print(f"🔄 จะรีบูททุก {config['reboot_settings']['reboot_every_n_accounts']} ไอดี")
        print("⏹️  กด Ctrl+C เพื่อหยุดระบบ")
        print()
        
        return True
    
    def stop_system(self):
        """หยุดระบบ"""
        self.is_running = False
        print("\n⏹️  หยุดระบบ...")
        
        if self.router_system:
            self.router_system.stop_monitoring()
        
        print("✅ หยุดระบบแล้ว!")
    
    def run(self):
        """รันระบบ"""
        if not self.start_system():
            return
        
        try:
            # รอให้ผู้ใช้หยุดระบบ
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_system()

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 60)
    print("🚀 ระบบสมบูรณ์ Router Reboot + ระบบเดิม")
    print("สำหรับเร้าเตอร์ GEL.iNet GL-XE300C4")
    print("=" * 60)
    
    # ตรวจสอบไฟล์ config
    if not os.path.exists("router_config.json"):
        print("❌ ไม่พบไฟล์ router_config.json")
        print("กรุณาสร้างไฟล์ config ก่อน")
        return
    
    # แสดงการตั้งค่า
    try:
        with open("router_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        print(f"📋 เร้าเตอร์: {config['router']['host']}")
        print(f"👤 Username: {config['router']['username']}")
        print(f"🔄 รีบูททุก: {config['reboot_settings']['reboot_every_n_accounts']} ไอดี")
        print(f"⏳ รอหลังรีบูท: {config['reboot_settings']['wait_after_reboot']} วินาที")
        print()
        
    except Exception as e:
        print(f"❌ ไม่สามารถอ่านไฟล์ config ได้: {e}")
        return
    
    # เริ่มระบบ
    complete_system = CompleteSystem()
    complete_system.run()

if __name__ == "__main__":
    main()