#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบระบบ Router Reboot
สำหรับทดสอบการเชื่อมต่อและรีบูทเร้าเตอร์
"""

import sys
import time
from router_reboot_system import RouterRebootSystem

def test_router_connection():
    """ทดสอบการเชื่อมต่อเร้าเตอร์"""
    print("🔧 Testing Router Connection...")
    
    try:
        router = RouterRebootSystem()
        
        # ทดสอบการเชื่อมต่อ SSH
        print("📡 Connecting to router...")
        if router.connect_ssh():
            print("✅ SSH connection successful!")
            
            # ทดสอบการรันคำสั่ง
            print("🔍 Testing command execution...")
            result = router.execute_command("uname -a")
            if result:
                print(f"✅ Command executed successfully: {result}")
            else:
                print("❌ Command execution failed")
            
            # ทดสอบการตรวจสอบ IP
            print("🌐 Checking current IP...")
            current_ip = router.get_current_ip()
            if current_ip:
                print(f"✅ Current IP: {current_ip}")
            else:
                print("❌ Failed to get current IP")
            
            router.disconnect_ssh()
            return True
        else:
            print("❌ SSH connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_router_reboot():
    """ทดสอบการรีบูทเร้าเตอร์"""
    print("\n🔄 Testing Router Reboot...")
    
    try:
        router = RouterRebootSystem()
        
        # ตรวจสอบ IP ก่อนรีบูท
        print("🌐 Current IP before reboot:")
        ip_before = router.get_current_ip()
        print(f"   {ip_before}")
        
        # รีบูทเร้าเตอร์
        print("🔄 Rebooting router...")
        if router.reboot_router():
            print("✅ Router reboot command sent successfully!")
            
            # รอให้เร้าเตอร์บูทขึ้นมาใหม่
            print("⏳ Waiting for router to come back online...")
            time.sleep(60)  # รอ 60 วินาที
            
            # ตรวจสอบ IP หลังรีบูท
            print("🌐 Checking IP after reboot:")
            ip_after = router.get_current_ip()
            print(f"   {ip_after}")
            
            if ip_before != ip_after:
                print("✅ IP changed successfully!")
            else:
                print("⚠️ IP did not change")
                
        else:
            print("❌ Router reboot failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during reboot test: {e}")
        return False

def test_account_counter():
    """ทดสอบการนับจำนวนอีเมล"""
    print("\n📊 Testing Account Counter...")
    
    try:
        router = RouterRebootSystem()
        
        # ทดสอบการนับ 10 ครั้ง
        for i in range(1, 11):
            print(f"📝 Account {i} generated")
            router.account_generated()
            time.sleep(1)
            
        print("✅ Account counter test completed!")
        
    except Exception as e:
        print(f"❌ Error during account counter test: {e}")

def main():
    """ฟังก์ชันหลักสำหรับทดสอบ"""
    print("🚀 Router Reboot System Test")
    print("=" * 50)
    
    # ทดสอบการเชื่อมต่อ
    if test_router_connection():
        print("\n✅ Connection test passed!")
    else:
        print("\n❌ Connection test failed!")
        print("Please check your router configuration in router_config.json")
        return
    
    # ทดสอบการนับจำนวนอีเมล
    test_account_counter()
    
    # ถามว่าต้องการทดสอบการรีบูทหรือไม่
    print("\n" + "=" * 50)
    response = input("Do you want to test router reboot? (y/n): ").lower()
    
    if response == 'y':
        test_router_reboot()
    else:
        print("Skipping reboot test")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()