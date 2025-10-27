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
try:
    from router_reboot_system import RouterRebootSystem
    ROUTER_SYSTEM_AVAILABLE = True
except ImportError:
    ROUTER_SYSTEM_AVAILABLE = False
    print("⚠️ Router Reboot System not available")

# --- การตั้งค่าไฟล์ ---
CONFIG_FILE = "config_register.txt"
ACCOUNTS_FILE = "accounts.txt"
COOKIE_FILE = "cookie_join.txt"
SUCCESS_FILE = "account_ok.txt"
DISPLAY_NAMES_FILE = "DISPLAY_NAMES.txt"
ABOUT_ME_FILE = "ABOUT_ME_TEXTS.txt"

# Global Router System
router_system = None
account_counter = 0

def initialize_router_system():
    """เริ่มต้นระบบ Router Reboot"""
    global router_system
    if not ROUTER_SYSTEM_AVAILABLE:
        print("⚠️ Router Reboot System not available")
        return False
    
    try:
        print("🔧 Initializing Router Reboot System...")
        router_system = RouterRebootSystem()
        
        # ทดสอบการเชื่อมต่อ
        if router_system.connect_ssh():
            print("✅ Router connection successful!")
            router_system.disconnect_ssh()
            return True
        else:
            print("❌ Router connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing Router Reboot System: {e}")
        return False

def account_generated_callback():
    """Callback เมื่อมีการเจนอีเมลสำเร็จ"""
    global router_system, account_counter
    account_counter += 1
    print(f"📊 Account generated: {account_counter}")
    
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
    
    # ตรวจสอบว่ามีอีเมลในไฟล์หรือไม่
    if AVAILABLE_EMAILS:
        original_email_to_try = random.choice(AVAILABLE_EMAILS)
        print(f"[{username}] Using email from file: {original_email_to_try}")
    else:
        print(f"[{username}] No emails in file, generating random email...")
        original_email_to_try = f"{generate_random_email_prefix()}@gmail.com"

    # ลอง 3 ครั้ง
    for attempt in range(3):
        email_to_try = original_email_to_try
        if attempt > 0:
            # สร้างอีเมลใหม่สำหรับการลองครั้งที่ 2 และ 3
            email_to_try = f"{generate_random_email_prefix()}@gmail.com"
            print(f"[{username}] Attempt {attempt + 1}: Using new email: {email_to_try}")

        try:
            print(f"[{username}] Adding email: {email_to_try}")
            
            # ไปที่หน้า Account Settings
            driver.get("https://www.roblox.com/my/account")
            time.sleep(3)
            
            # หาและคลิกปุ่ม Add Email
            try:
                add_email_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Email')]"))
                )
                driver.execute_script("arguments[0].click();", add_email_button)
                time.sleep(2)
            except:
                print(f"[{username}] Could not find 'Add Email' button")
                continue

            # กรอกอีเมล
            try:
                email_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "emailAddress"))
                )
                email_input.clear()
                email_input.send_keys(email_to_try)
                time.sleep(1)
            except:
                print(f"[{username}] Could not find email input field")
                continue

            # คลิกปุ่ม Add
            try:
                add_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add')]"))
                )
                driver.execute_script("arguments[0].click();", add_button)
                time.sleep(2)
            except:
                print(f"[{username}] Could not find 'Add' button")
                continue

            # รอแคปช่า
            if wait_for_extension_to_solve(driver, context="Add Email"):
                print(f"[{username}] Email added successfully: {email_to_try}")
                log_id_email(username, email_to_try)
                return email_to_try, True
            else:
                print(f"[{username}] CAPTCHA solve failed for email addition")
                continue

        except Exception as e:
            print(f"[{username}] Error adding email (attempt {attempt + 1}): {e}")
            continue

    print(f"[{username}] Failed to add email after 3 attempts")
    return None, False

def log_success(username, password, cookies):
    """บันทึกข้อมูลเมื่อสร้างบัญชีสำเร็จ"""
    try:
        roblo_security_cookie = ""
        for cookie in cookies:
            if cookie['name'] == '.ROBLOSECURITY':
                roblo_security_cookie = cookie['value']
                break
        if roblo_security_cookie:
            with open(SUCCESS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{username}:{password}:{roblo_security_cookie}\n")
            
            # เรียกใช้ Router Reboot System
            account_generated_callback()
            
            return True
        return False
    except Exception as e:
        print(f"❌ Error logging success: {e}")
        return False

def log_failure(username, password, cookies):
    """บันทึกข้อมูลเมื่อสร้างบัญชีไม่สำเร็จ"""
    try:
        with open("account_failed.txt", "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}\n")
        print(f"❌ Account creation failed: {username}")
    except Exception as e:
        print(f"❌ Error logging failure: {e}")

# ฟังก์ชันอื่นๆ จาก ok.py จะถูก import มาใช้
# ... (ฟังก์ชันอื่นๆ ทั้งหมด) ...

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 Integrated Router Reboot System")
    print("=" * 50)
    
    # เริ่มต้นระบบ Router Reboot
    if initialize_router_system():
        print("✅ Router Reboot System initialized successfully")
    else:
        print("⚠️ Router Reboot System initialization failed. Continuing without router reboot...")
    
    # โหลดการตั้งค่า
    try:
        config = load_config()
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return
    
    # รันระบบตามโหมดที่กำหนด
    try:
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
        if router_system:
            router_system.stop_monitoring()

if __name__ == "__main__":
    main()