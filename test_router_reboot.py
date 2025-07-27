#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบระบบ Router Reboot
สำหรับเร้าเตอร์ GEL.iNet GL-XE300C4
"""

import sys
import os
import time
import json
from router_reboot_system import RouterRebootSystem

def test_router_connection():
    """ทดสอบการเชื่อมต่อกับเร้าเตอร์"""
    print("🔍 ทดสอบการเชื่อมต่อกับเร้าเตอร์...")
    
    try:
        router = RouterRebootSystem()
        
        # ทดสอบการเชื่อมต่อ
        if router.test_connection():
            print("✅ เชื่อมต่อกับเร้าเตอร์สำเร็จ!")
            return True
        else:
            print("❌ ไม่สามารถเชื่อมต่อกับเร้าเตอร์ได้")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def test_router_reboot():
    """ทดสอบการรีบูทเร้าเตอร์"""
    print("🔄 ทดสอบการรีบูทเร้าเตอร์...")
    
    try:
        router = RouterRebootSystem()
        
        # ทดสอบการรีบูท
        if router.reboot_router():
            print("✅ รีบูทเร้าเตอร์สำเร็จ!")
            return True
        else:
            print("❌ ไม่สามารถรีบูทเร้าเตอร์ได้")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def test_integrated_system():
    """ทดสอบระบบรวม"""
    print("🚀 ทดสอบระบบรวม...")
    
    try:
        from integrated_system import IntegratedSystem
        
        system = IntegratedSystem()
        
        # เริ่มระบบ
        if system.start_router_system():
            print("✅ ระบบรวมทำงานได้ปกติ!")
            
            # หยุดระบบ
            system.stop_router_system()
            return True
        else:
            print("❌ ระบบรวมไม่สามารถทำงานได้")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 50)
    print("🧪 ทดสอบระบบ Router Reboot")
    print("=" * 50)
    
    # ตรวจสอบไฟล์ config
    if not os.path.exists("router_config.json"):
        print("❌ ไม่พบไฟล์ router_config.json")
        print("กรุณาสร้างไฟล์ config ก่อน")
        return
    
    # อ่าน config
    try:
        with open("router_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        print(f"📋 ตั้งค่าเร้าเตอร์: {config['router']['host']}")
        print(f"👤 Username: {config['router']['username']}")
        print(f"🔄 รีบูททุก: {config['reboot_settings']['reboot_every_n_accounts']} ไอดี")
        print()
        
    except Exception as e:
        print(f"❌ ไม่สามารถอ่านไฟล์ config ได้: {e}")
        return
    
    # ทดสอบการเชื่อมต่อ
    if test_router_connection():
        print()
        
        # ถามผู้ใช้ว่าต้องการทดสอบรีบูทหรือไม่
        response = input("🤔 ต้องการทดสอบการรีบูทเร้าเตอร์หรือไม่? (y/n): ")
        if response.lower() == 'y':
            test_router_reboot()
        
        print()
        
        # ทดสอบระบบรวม
        test_integrated_system()
        
    else:
        print("❌ ไม่สามารถทดสอบระบบอื่นได้เนื่องจากไม่สามารถเชื่อมต่อกับเร้าเตอร์ได้")
        print("กรุณาตรวจสอบการตั้งค่าใน router_config.json")

if __name__ == "__main__":
    main()