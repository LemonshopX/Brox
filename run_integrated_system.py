#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ไฟล์สำหรับรันระบบรวม Router Reboot กับระบบเดิม
สำหรับรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password
และให้รันต่อเนื่องกันเลย
"""

import sys
import os
import time
import threading
from router_reboot_system import RouterRebootSystem

# Import ระบบเดิม
from ok import *

class IntegratedSystem:
    def __init__(self):
        self.router_system = None
        self.is_running = False
        self.account_counter = 0
        
    def initialize_router_system(self):
        """เริ่มต้นระบบ Router Reboot"""
        try:
            print("🔧 Initializing Router Reboot System...")
            self.router_system = RouterRebootSystem()
            
            # ทดสอบการเชื่อมต่อ
            if self.router_system.connect_ssh():
                print("✅ Router connection successful!")
                self.router_system.disconnect_ssh()
                return True
            else:
                print("❌ Router connection failed!")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing Router Reboot System: {e}")
            return False
    
    def account_generated_callback(self):
        """Callback เมื่อมีการเจนอีเมลสำเร็จ"""
        self.account_counter += 1
        print(f"📊 Account generated: {self.account_counter}")
        
        if self.router_system:
            self.router_system.account_generated()
    
    def run_registration_with_reboot(self, config):
        """รันระบบเจนอีเมลพร้อม Router Reboot"""
        print("🚀 Starting Integrated System with Router Reboot...")
        
        # เริ่มต้นระบบ Router Reboot
        if not self.initialize_router_system():
            print("⚠️ Router system initialization failed. Continuing without router reboot...")
        
        self.is_running = True
        
        try:
            # เรียกใช้ฟังก์ชันเดิมจาก ok.py
            if config.get('mode') == 'register':
                print("📝 Running in registration mode...")
                run_registration_mode(config)
            elif config.get('mode') == 'login':
                print("🔐 Running in login mode...")
                run_login_and_update_cookie_mode(config)
            elif config.get('mode') == 'interactive':
                print("🎯 Running in interactive mode...")
                run_interactive_registration_mode(config)
            else:
                print("❌ Invalid mode specified in config")
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopping system...")
        except Exception as e:
            print(f"❌ Error in integrated system: {e}")
        finally:
            self.is_running = False
            if self.router_system:
                self.router_system.stop_monitoring()

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 Integrated Router Reboot System")
    print("=" * 50)
    
    # โหลดการตั้งค่า
    try:
        config = load_config()
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return
    
    # สร้างระบบรวม
    integrated_system = IntegratedSystem()
    
    # รันระบบ
    integrated_system.run_registration_with_reboot(config)

if __name__ == "__main__":
    main()