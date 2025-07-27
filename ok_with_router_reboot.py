#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ระบบรวม Router Reboot กับระบบเดิม
สำหรับรีไอพีทุกๆการเจนรหัส 10 ไอดี โดยไม่ต้องถาม Password
และให้รันต่อเนื่องกันเลย
"""

import time
import string
import requests
import imaplib
import email
from bs4 import BeautifulSoup
import json
import os
import pyautogui
import sys
import random
import calendar
import re
import paramiko
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import Router Reboot System
from router_reboot_system import RouterRebootSystem

# --- การตั้งค่าไฟล์ ---
CONFIG_FILE = "config_register.txt"
ACCOUNTS_FILE = "accounts.txt"
COOKIE_FILE = "cookie_join.txt"
SUCCESS_FILE = "account_ok.txt"
DISPLAY_NAMES_FILE = "DISPLAY_NAMES.txt"
ABOUT_ME_FILE = "ABOUT_ME_TEXTS.txt"

# --- [ใหม่] ลิสต์ชื่อสำหรับสุ่ม ---
DISPLAY_NAMES = [
    "SupraMK4", "GTR_R34", "RX7_SpiritR", "LancerEvoIX", "ImprezaWRX",
    "MonkeyDLuffy", "RoronoaZoro", "SaitamaSensei", "GojoSatoru", "LeviAckerman",
    "UzumakiNaruto", "SonGokuKakarot", "LightYagami", "ErenYeager", "TakumiFujiwara",
    "InitialD_Rider", "WanganGhost", "AkumaNoZetto", "VinsmokeSanji"
]
ABOUT_ME_TEXTS = [
    "Gaminglab On Top", "I love Thailand!", "Thailand is a beautiful country.",
    "ผมรักประเทศไทย", "ประเทศไทยสวยงามมาก", "Made in Thailand"
]

# Global Router Reboot System
router_system = None

def initialize_router_system():
    """เริ่มต้นระบบ Router Reboot"""
    global router_system
    try:
        router_system = RouterRebootSystem()
        if router_system.start_monitoring():
            print("✅ Router Reboot System initialized successfully")
            return True
        else:
            print("❌ Failed to initialize Router Reboot System")
            return False
    except Exception as e:
        print(f"❌ Error initializing Router Reboot System: {e}")
        return False

def account_generated_callback():
    """Callback เมื่อมีการเจนอีเมลสำเร็จ"""
    global router_system
    if router_system:
        router_system.account_generated()

# --- [ใหม่] ฟังก์ชันสำหรับอ่านอีเมล ---
def generate_random_string(length=8):
    """สร้างตัวอักษรและตัวเลขต่อท้ายแบบสุ่ม"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_random_suffix(length=2):
    """สร้างตัวอักษรต่อท้ายแบบสุ่ม a-z, A-Z"""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def send_to_discord(webhook_url, embed_data):
    """ส่งข้อมูลแบบ Embed ไปยัง Discord Webhook"""
    if not webhook_url:
        return # ถ้าไม่ได้ตั้งค่า webhook URL ไว้ ก็ไม่ต้องทำอะไร

    headers = {"Content-Type": "application/json"}
    payload = {"embeds": [embed_data]}

    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code not in [200, 204]:
            print(f"⚠️ Discord Webhook Error: Received status code {response.status_code}")
    except Exception as e:
        print(f"⚠️ Failed to send message to Discord: {e}")

def load_list_from_file(filename, default_values=None):
    """อ่านข้อมูลจากไฟล์ txt บรรทัดละ 1 รายการ"""
    if default_values is None:
        default_values = []
    if not os.path.exists(filename):
        print(f"File '{filename}' not found. Creating a sample file.")
        with open(filename, "w", encoding="utf-8") as f:
            for value in default_values:
                f.write(f"{value}\n")
        return default_values
    
    with open(filename, "r", encoding="utf-8") as f:
        # อ่านไฟล์, ตัดช่องว่าง, และกรองบรรทัดที่ว่างเปล่าออก
        lines = [line.strip() for line in f if line.strip()]
        return lines

# --- [ใหม่] โหลดข้อมูลจากไฟล์มาเก็บในตัวแปร ---
DISPLAY_NAMES = load_list_from_file(DISPLAY_NAMES_FILE, default_values=["SupraMK4","Sanji","UzumakiNaruto", "SonGokuKakarot"])
ABOUT_ME_TEXTS = load_list_from_file(ABOUT_ME_FILE, default_values=["Gaminglab On Top", "I love Thailand!"])
AVAILABLE_EMAILS = load_list_from_file("email.txt", default_values=[])
print(f"--- Found {len(AVAILABLE_EMAILS)} emails in email.txt ---")

def add_email_to_account(driver, username):
    """
    ฟังก์ชันสำหรับเพิ่มอีเมล พร้อมระบบลองใหม่ 3 ครั้งด้วยอีเมลใหม่ที่สุ่มขึ้น
    """
    if config.get('Add_Email', 'false').lower() != 'true':
        return None, True # ถ้าปิดฟังก์ชันนี้ ให้ถือว่าสำเร็จ

    email_file = "email.txt"
    original_email_to_try = None

# ... (โค้ดเดิมทั้งหมดจาก ok.py) ...

def log_success(username, password, cookies):
    """บันทึกข้อมูลเมื่อสร้างบัญชีสำเร็จ"""
    try:
        with open(SUCCESS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}\n")
        
        # ส่งไปยัง Discord Webhook ถ้ามีการตั้งค่า
        webhook_url = config.get('Discord_Webhook_URL', '')
        if webhook_url:
            embed_data = {
                "title": "✅ Account Created Successfully",
                "description": f"**Username:** {username}\n**Password:** {password}",
                "color": 0x00ff00,
                "timestamp": datetime.now().isoformat()
            }
            send_to_discord(webhook_url, embed_data)
        
        print(f"✅ Successfully created account: {username}")
        
        # เรียก Router Reboot callback
        account_generated_callback()
        
    except Exception as e:
        print(f"❌ Error logging success: {e}")

def log_failure(username, password, cookies):
    """บันทึกข้อมูลเมื่อสร้างบัญชีไม่สำเร็จ"""
    try:
        with open("account_failed.txt", "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}\n")
        
        print(f"❌ Failed to create account: {username}")
        
    except Exception as e:
        print(f"❌ Error logging failure: {e}")

# ... (ฟังก์ชันอื่นๆ ทั้งหมดจาก ok.py) ...

def main():
    """ฟังก์ชันหลัก"""
    print("🔄 Starting Integrated System with Router Reboot...")
    
    # เริ่มต้นระบบ Router Reboot
    if not initialize_router_system():
        print("⚠️ Continuing without Router Reboot System")
    
    # โหลด config
    config = load_config()
    
    try:
        # รันระบบตาม mode ที่เลือก
        if config.get('mode') == 'register':
            run_registration_mode(config)
        elif config.get('mode') == 'login':
            run_login_and_update_cookie_mode(config)
        elif config.get('mode') == 'interactive':
            run_interactive_registration_mode(config)
        else:
            print("❌ Invalid mode specified")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
    except Exception as e:
        print(f"❌ Error in system: {e}")
    finally:
        # หยุดระบบ Router Reboot
        if router_system:
            router_system.stop_monitoring()
            print("✅ Router Reboot System stopped")

if __name__ == "__main__":
    main()