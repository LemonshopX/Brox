#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ระบบ SSH Reboot เร้าเตอร์ GEL.iNet GL-XE300C4
สำหรับรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password
และให้รันต่อเนื่องกันเลย
"""

import paramiko
import time
import threading
import logging
import json
import os
from datetime import datetime
import subprocess
import sys

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('router_reboot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RouterRebootSystem:
    def __init__(self, config_file="router_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.ssh_client = None
        self.reboot_count = 0
        self.account_count = 0
        self.lock = threading.Lock()
        
    def load_config(self):
        """โหลดการตั้งค่าจากไฟล์ config"""
        default_config = {
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
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with default config
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in config[key]:
                                    config[key][sub_key] = sub_value
                    return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            # สร้างไฟล์ config ใหม่
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            logger.info(f"Created new config file: {self.config_file}")
            logger.info("Please edit the config file with your router settings")
            return default_config
    
    def connect_ssh(self):
        """เชื่อมต่อ SSH กับเร้าเตอร์"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            router_config = self.config["router"]
            reboot_config = self.config["reboot_settings"]
            
            if router_config.get("key_file"):
                # ใช้ SSH key
                self.ssh_client.connect(
                    hostname=router_config["host"],
                    port=router_config["port"],
                    username=router_config["username"],
                    key_filename=router_config["key_file"],
                    timeout=reboot_config["connection_timeout"]
                )
            else:
                # ใช้ password
                self.ssh_client.connect(
                    hostname=router_config["host"],
                    port=router_config["port"],
                    username=router_config["username"],
                    password=router_config["password"],
                    timeout=reboot_config["connection_timeout"]
                )
            
            logger.info(f"✅ SSH Connected to {router_config['host']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ SSH Connection failed: {e}")
            return False
    
    def disconnect_ssh(self):
        """ตัดการเชื่อมต่อ SSH"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            logger.info("🔌 SSH Disconnected")
    
    def execute_command(self, command, timeout=30):
        """รันคำสั่งบนเร้าเตอร์"""
        try:
            if not self.ssh_client:
                if not self.connect_ssh():
                    return False, "SSH connection failed"
            
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            
            # รอให้คำสั่งเสร็จสิ้น
            exit_status = stdout.channel.recv_exit_status()
            
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            if exit_status == 0:
                logger.info(f"✅ Command executed: {command}")
                return True, output
            else:
                logger.error(f"❌ Command failed: {command}, Error: {error}")
                return False, error
                
        except Exception as e:
            logger.error(f"❌ Command execution error: {e}")
            return False, str(e)
    
    def reboot_router(self):
        """รีบูทเร้าเตอร์"""
        logger.info("🔄 Starting router reboot...")
        
        # คำสั่งรีบูทสำหรับ GEL.iNet GL-XE300C4
        reboot_commands = [
            "reboot",  # คำสั่งมาตรฐาน
            "sync && reboot",  # บันทึกข้อมูลก่อนรีบูท
            "/sbin/reboot",  # path เต็ม
            "killall -9 init && reboot"  # force reboot
        ]
        
        for command in reboot_commands:
            success, output = self.execute_command(command, timeout=60)
            if success:
                logger.info(f"✅ Router reboot command sent: {command}")
                break
        else:
            logger.error("❌ All reboot commands failed")
            return False
        
        # รอให้เร้าเตอร์รีบูทเสร็จ
        wait_time = self.config["reboot_settings"]["wait_after_reboot"]
        logger.info(f"⏳ Waiting {wait_time} seconds for router to reboot...")
        time.sleep(wait_time)
        
        # ลองเชื่อมต่อใหม่
        retry_count = 0
        max_retries = self.config["reboot_settings"]["max_retries"]
        
        while retry_count < max_retries:
            logger.info(f"🔄 Attempting to reconnect... (Attempt {retry_count + 1}/{max_retries})")
            
            # ตัดการเชื่อมต่อเก่า
            self.disconnect_ssh()
            time.sleep(5)
            
            # ลองเชื่อมต่อใหม่
            if self.connect_ssh():
                logger.info("✅ Router reboot completed successfully")
                self.reboot_count += 1
                return True
            
            retry_count += 1
            time.sleep(10)
        
        logger.error("❌ Failed to reconnect after reboot")
        return False
    
    def check_internet_connection(self):
        """ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต"""
        try:
            # ทดสอบ ping Google DNS
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "5", "8.8.8.8"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def get_current_ip(self):
        """ดึง IP ปัจจุบัน"""
        try:
            # ใช้ curl เพื่อดึง IP จาก external service
            result = subprocess.run(
                ["curl", "-s", "--max-time", "10", "https://api.ipify.org"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except:
            return None
    
    def send_notification(self, message):
        """ส่งการแจ้งเตือน"""
        try:
            # Discord Webhook
            if self.config["notification"]["discord_webhook"]:
                import requests
                payload = {
                    "content": f"🔄 Router Reboot System: {message}",
                    "username": "Router Reboot Bot"
                }
                requests.post(self.config["notification"]["discord_webhook"], json=payload)
            
            # Telegram Bot
            if (self.config["notification"]["telegram_bot_token"] and 
                self.config["notification"]["telegram_chat_id"]):
                import requests
                url = f"https://api.telegram.org/bot{self.config['notification']['telegram_bot_token']}/sendMessage"
                payload = {
                    "chat_id": self.config["notification"]["telegram_chat_id"],
                    "text": f"🔄 Router Reboot System: {message}"
                }
                requests.post(url, json=payload)
                
        except Exception as e:
            logger.error(f"❌ Notification error: {e}")
    
    def account_generated(self):
        """เรียกเมื่อมีการเจนอีเมลสำเร็จ"""
        with self.lock:
            self.account_count += 1
            logger.info(f"📊 Account generated: {self.account_count}")
            
            # ตรวจสอบว่าควรรีบูทหรือไม่
            if self.account_count % self.config["reboot_settings"]["reboot_every_n_accounts"] == 0:
                logger.info(f"🔄 Time to reboot router after {self.account_count} accounts")
                
                # บันทึก IP ก่อนรีบูท
                old_ip = self.get_current_ip()
                logger.info(f"📡 Current IP: {old_ip}")
                
                # รีบูทเร้าเตอร์
                if self.reboot_router():
                    # รอให้อินเทอร์เน็ตกลับมา
                    logger.info("⏳ Waiting for internet connection...")
                    for i in range(30):  # รอสูงสุด 5 นาที
                        if self.check_internet_connection():
                            break
                        time.sleep(10)
                    
                    # ตรวจสอบ IP ใหม่
                    new_ip = self.get_current_ip()
                    logger.info(f"📡 New IP: {new_ip}")
                    
                    if new_ip and new_ip != old_ip:
                        message = f"✅ IP changed successfully! Old: {old_ip} → New: {new_ip}"
                        logger.info(message)
                        self.send_notification(message)
                    else:
                        message = f"⚠️ IP may not have changed. Old: {old_ip} → New: {new_ip}"
                        logger.warning(message)
                        self.send_notification(message)
                else:
                    message = f"❌ Router reboot failed after {self.account_count} accounts"
                    logger.error(message)
                    self.send_notification(message)
    
    def start_monitoring(self):
        """เริ่มการติดตาม"""
        logger.info("🚀 Starting Router Reboot System...")
        logger.info(f"📊 Will reboot every {self.config['reboot_settings']['reboot_every_n_accounts']} accounts")
        
        # ทดสอบการเชื่อมต่อ SSH
        if not self.connect_ssh():
            logger.error("❌ Cannot connect to router. Please check your configuration.")
            return False
        
        self.send_notification("🚀 Router Reboot System started successfully")
        return True
    
    def stop_monitoring(self):
        """หยุดการติดตาม"""
        logger.info("🛑 Stopping Router Reboot System...")
        self.disconnect_ssh()
        self.send_notification("🛑 Router Reboot System stopped")
    
    def get_status(self):
        """ดึงสถานะปัจจุบัน"""
        return {
            "account_count": self.account_count,
            "reboot_count": self.reboot_count,
            "current_ip": self.get_current_ip(),
            "internet_connected": self.check_internet_connection(),
            "ssh_connected": self.ssh_client is not None
        }

# ฟังก์ชันสำหรับใช้งานกับระบบเดิม
def integrate_with_existing_system():
    """ฟังก์ชันสำหรับใช้งานกับระบบเดิม"""
    router_system = RouterRebootSystem()
    
    if not router_system.start_monitoring():
        return None
    
    return router_system

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    print("🔄 Router Reboot System for GEL.iNet GL-XE300C4")
    print("=" * 50)
    
    router_system = RouterRebootSystem()
    
    # เริ่มการติดตาม
    if not router_system.start_monitoring():
        print("❌ Failed to start monitoring")
        sys.exit(1)
    
    try:
        print("✅ System started successfully")
        print("📊 Press Ctrl+C to stop")
        
        # จำลองการเจนอีเมล (สำหรับทดสอบ)
        while True:
            time.sleep(5)
            # จำลองการเจนอีเมลสำเร็จ
            router_system.account_generated()
            
            # แสดงสถานะ
            status = router_system.get_status()
            print(f"📊 Status: {status['account_count']} accounts, {status['reboot_count']} reboots, IP: {status['current_ip']}")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
        router_system.stop_monitoring()
        print("✅ System stopped")