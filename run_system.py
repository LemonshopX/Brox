#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์สำหรับรันระบบ Router Reboot แบบง่าย
สำหรับรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password
และให้รันต่อเนื่องกันเลย
"""

import os
import sys
import time

def check_files():
    """ตรวจสอบไฟล์ที่จำเป็น"""
    required_files = [
        "router_config.json",
        "router_reboot_system.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 Router Reboot System")
    print("=" * 50)
    
    # ตรวจสอบไฟล์
    if not check_files():
        print("Please run setup_and_run.py first")
        return
    
    # เลือกโหมดการทำงาน
    print("\nเลือกโหมดการทำงาน:")
    print("1. ทดสอบการเชื่อมต่อเร้าเตอร์")
    print("2. รันระบบ Router Reboot อย่างเดียว")
    print("3. รันระบบรวมกับระบบเดิม")
    print("4. รันระบบรวมแบบอื่น")
    
    choice = input("\nเลือก (1-4): ").strip()
    
    try:
        if choice == "1":
            print("\n🔧 Testing router connection...")
            from test_router_reboot import test_router_connection
            test_router_connection()
            
        elif choice == "2":
            print("\n🔄 Running router reboot system...")
            from router_reboot_system import RouterRebootSystem
            router = RouterRebootSystem()
            router.start_monitoring()
            
        elif choice == "3":
            print("\n🤖 Running integrated system...")
            from ok_with_router_integration import main
            main()
            
        elif choice == "4":
            print("\n🔄 Running alternative integrated system...")
            from ok_with_router_reboot import main
            main()
            
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n⏹️ System stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()