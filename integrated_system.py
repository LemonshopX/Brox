#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ระบบรวม Router Reboot กับระบบเดิม
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
        
    def start_router_system(self):
        """เริ่มระบบ Router Reboot"""
        try:
            self.router_system = RouterRebootSystem()
            if self.router_system.start_monitoring():
                print("✅ Router Reboot System started successfully")
                return True
            else:
                print("❌ Failed to start Router Reboot System")
                return False
        except Exception as e:
            print(f"❌ Error starting Router Reboot System: {e}")
            return False
    
    def stop_router_system(self):
        """หยุดระบบ Router Reboot"""
        if self.router_system:
            self.router_system.stop_monitoring()
            print("✅ Router Reboot System stopped")
    
    def account_generated_callback(self):
        """Callback เมื่อมีการเจนอีเมลสำเร็จ"""
        if self.router_system:
            self.router_system.account_generated()
    
    def run_with_router_reboot(self, config):
        """รันระบบเดิมพร้อมกับ Router Reboot"""
        print("🚀 Starting Integrated System with Router Reboot...")
        
        # เริ่มระบบ Router Reboot
        if not self.start_router_system():
            print("⚠️ Continuing without Router Reboot System")
        
        self.is_running = True
        
        try:
            # เรียกฟังก์ชันเดิมจาก ok.py
            if config.get('mode') == 'register':
                run_registration_mode(config)
            elif config.get('mode') == 'login':
                run_login_and_update_cookie_mode(config)
            elif config.get('mode') == 'interactive':
                run_interactive_registration_mode(config)
            else:
                print("❌ Invalid mode specified")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping integrated system...")
        except Exception as e:
            print(f"❌ Error in integrated system: {e}")
        finally:
            self.is_running = False
            self.stop_router_system()

# ฟังก์ชันสำหรับแก้ไขระบบเดิมเพื่อรองรับ Router Reboot
def modify_existing_functions():
    """แก้ไขฟังก์ชันเดิมเพื่อรองรับ Router Reboot"""
    
    # สร้าง global variable สำหรับ integrated system
    global integrated_system
    integrated_system = IntegratedSystem()
    
    # แก้ไขฟังก์ชัน log_success เพื่อเรียก Router Reboot
    original_log_success = log_success
    
    def new_log_success(username, password, cookies):
        """ฟังก์ชัน log_success ที่แก้ไขแล้ว"""
        # เรียกฟังก์ชันเดิม
        original_log_success(username, password, cookies)
        
        # เรียก Router Reboot callback
        if 'integrated_system' in globals() and integrated_system.is_running:
            integrated_system.account_generated_callback()
    
    # แทนที่ฟังก์ชันเดิม
    globals()['log_success'] = new_log_success
    
    return integrated_system

def main():
    """ฟังก์ชันหลัก"""
    print("🔄 Integrated Router Reboot System")
    print("=" * 50)
    
    # โหลด config
    config = load_config()
    
    # แก้ไขฟังก์ชันเดิม
    integrated_system = modify_existing_functions()
    
    # รันระบบ
    integrated_system.run_with_router_reboot(config)

if __name__ == "__main__":
    main()