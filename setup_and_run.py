#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์สำหรับติดตั้งและรันระบบ Router Reboot
สำหรับรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password
และให้รันต่อเนื่องกันเลย
"""

import os
import sys
import subprocess
import time

def install_dependencies():
    """ติดตั้ง dependencies ที่จำเป็น"""
    print("📦 Installing dependencies...")
    
    dependencies = [
        "paramiko>=2.8.1",
        "requests>=2.28.0",
        "selenium>=4.0.0",
        "beautifulsoup4>=4.11.0",
        "pyautogui>=0.9.53",
        "webdriver-manager>=3.8.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True

def check_config_files():
    """ตรวจสอบไฟล์ config ที่จำเป็น"""
    print("🔍 Checking configuration files...")
    
    required_files = [
        "router_config.json",
        "config_register.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ Missing files: {', '.join(missing_files)}")
        print("Please create these files before running the system")
        return False
    
    print("✅ All configuration files found")
    return True

def setup_router_config():
    """ตั้งค่า router config"""
    print("🔧 Setting up router configuration...")
    
    if not os.path.exists("router_config.json"):
        print("Creating router_config.json...")
        config = {
            "router": {
                "host": "192.168.1.1",
                "port": 22,
                "username": "root",
                "password": "your_password_here",
                "key_file": None
            },
            "reboot_settings": {
                "reboot_every_n_accounts": 10,
                "wait_after_reboot": 60,
                "max_retries": 3,
                "connection_timeout": 30
            },
            "notification": {
                "discord_webhook": "",
                "telegram_bot_token": "",
                "telegram_chat_id": ""
            }
        }
        
        import json
        with open("router_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print("✅ router_config.json created")
        print("⚠️ Please edit router_config.json with your router settings")
        return False
    
    return True

def test_router_connection():
    """ทดสอบการเชื่อมต่อเร้าเตอร์"""
    print("🔧 Testing router connection...")
    
    try:
        from test_router_reboot import test_router_connection
        if test_router_connection():
            print("✅ Router connection test passed")
            return True
        else:
            print("❌ Router connection test failed")
            return False
    except Exception as e:
        print(f"❌ Error testing router connection: {e}")
        return False

def run_system():
    """รันระบบ"""
    print("🚀 Starting integrated system...")
    
    try:
        # รันระบบรวม
        from ok_with_router_integration import main
        main()
    except KeyboardInterrupt:
        print("\n⏹️ System stopped by user")
    except Exception as e:
        print(f"❌ Error running system: {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 Router Reboot System Setup")
    print("=" * 50)
    
    # 1. ติดตั้ง dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # 2. ตรวจสอบไฟล์ config
    if not check_config_files():
        print("❌ Configuration files missing")
        return
    
    # 3. ตั้งค่า router config
    if not setup_router_config():
        print("⚠️ Please configure router settings and run again")
        return
    
    # 4. ทดสอบการเชื่อมต่อเร้าเตอร์
    print("\n" + "=" * 50)
    response = input("Do you want to test router connection? (y/n): ").lower()
    
    if response == 'y':
        if not test_router_connection():
            print("❌ Router connection test failed")
            print("Please check your router configuration")
            return
    
    # 5. รันระบบ
    print("\n" + "=" * 50)
    response = input("Do you want to start the system? (y/n): ").lower()
    
    if response == 'y':
        run_system()
    else:
        print("System not started")

if __name__ == "__main__":
    main()