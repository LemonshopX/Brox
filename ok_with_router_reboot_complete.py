#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ระบบรวม Router Reboot กับโค้ดเดิม 1176 บรรทัด
สำหรับเร้าเตอร์ GEL.iNet GL-XE300C4
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
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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

# --- ระบบ Router Reboot ---
class RouterRebootSystem:
    def __init__(self, config_file="router_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.ssh_client = None
        self.is_monitoring = False
        
    def load_config(self):
        """โหลดการตั้งค่าเร้าเตอร์"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ ไม่สามารถโหลด router config ได้: {e}")
            return None
    
    def connect_ssh(self):
        """เชื่อมต่อ SSH กับเร้าเตอร์"""
        try:
            if not self.config:
                return False
                
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            router_config = self.config['router']
            self.ssh_client.connect(
                hostname=router_config['host'],
                port=router_config['port'],
                username=router_config['username'],
                password=router_config['password'],
                timeout=self.config['reboot_settings']['connection_timeout']
            )
            return True
            
        except Exception as e:
            print(f"❌ ไม่สามารถเชื่อมต่อ SSH ได้: {e}")
            return False
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ"""
        return self.connect_ssh()
    
    def reboot_router(self):
        """รีบูทเร้าเตอร์"""
        try:
            if not self.ssh_client:
                if not self.connect_ssh():
                    return False
            
            # คำสั่งรีบูทสำหรับ GEL.iNet GL-XE300C4
            reboot_command = "reboot"
            
            stdin, stdout, stderr = self.ssh_client.exec_command(reboot_command)
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
                print("✅ รีบูทเร้าเตอร์สำเร็จ!")
                return True
            else:
                print(f"❌ รีบูทไม่สำเร็จ: {stderr.read().decode()}")
                return False
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการรีบูท: {e}")
            return False
        finally:
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
    
    def stop_monitoring(self):
        """หยุดการติดตาม"""
        self.is_monitoring = False
        if self.ssh_client:
            self.ssh_client.close()

# --- ระบบหลัก ---
class CompleteSystem:
    def __init__(self):
        self.router_system = None
        self.account_counter = 0
        self.reboot_counter = 0
        self.is_running = False
        
    def start_router_system(self):
        """เริ่มระบบ Router Reboot"""
        try:
            self.router_system = RouterRebootSystem()
            if self.router_system.test_connection():
                print("✅ ระบบ Router Reboot พร้อมใช้งาน!")
                return True
            else:
                print("❌ ไม่สามารถเชื่อมต่อกับเร้าเตอร์ได้")
                return False
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def check_and_reboot(self):
        """ตรวจสอบและรีบูทเร้าเตอร์"""
        try:
            if not self.router_system:
                return
            
            config = self.router_system.load_config()
            if not config:
                return
            
            reboot_every = config['reboot_settings']['reboot_every_n_accounts']
            
            if self.account_counter > 0 and self.account_counter % reboot_every == 0:
                print(f"🔄 ถึงเวลารีบูท! (ไอดี #{self.account_counter})")
                self.reboot_counter += 1
                
                if self.router_system.reboot_router():
                    print(f"✅ รีบูทเร้าเตอร์สำเร็จ! (ครั้งที่ {self.reboot_counter})")
                    
                    # รอให้เร้าเตอร์บูทเสร็จ
                    wait_time = config['reboot_settings']['wait_after_reboot']
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
        return

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
        return None, True

    email_file = "email.txt"
    original_email_to_try = None
    remaining_emails = []

    # --- 1. อ่านและเตรียมอีเมลจากไฟล์ ---
    try:
        if not os.path.exists(email_file) or os.path.getsize(email_file) == 0:
            print(f"[{username}] ...'email.txt' not found or is empty. Skipping email add.")
            return None, True
        
        with open(email_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines:
            print(f"[{username}] ...No emails left in email.txt. Skipping email add.")
            return None, True

        original_email_to_try = lines[0].strip()
        remaining_emails = lines[1:]

    except Exception as e:
        print(f"[{username}] ...⚠️ Error reading email.txt: {e}")
        return None, False

    # --- 2. เริ่มกระบวนการเพิ่มอีเมล ---
    max_retries = 3
    for attempt in range(max_retries + 1):
        email_to_use = ""
        if attempt == 0:
            email_to_use = original_email_to_try
        else:
            email_prefix = generate_random_email_prefix()
            email_to_use = f"{email_prefix}@gml.com"
        
        print(f"[{username}] ...Attempt #{attempt + 1}: Trying to add email: {email_to_use}")

        try:
            if "/account" not in driver.current_url:
                driver.get("https://www.roblox.com/my/account#!/info")
            
            add_email_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add Email')]")))
            add_email_button.click()
            time.sleep(1)

            email_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "emailAddress")))
            email_input.send_keys(email_to_use)
            time.sleep(1)

            modal_add_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'modal-content')]//button[contains(text(), 'Add Email')]")))
            modal_add_button.click()
            time.sleep(2)
            
            try:
                error_msg = driver.find_element(By.CSS_SELECTOR, ".modal-body .text-error")
                if error_msg.is_displayed():
                    raise Exception(f"Invalid email error detected: {error_msg.text}")
            except NoSuchElementException:
                pass

            ok_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'modal-content')]//button[text()='OK']")))
            ok_button.click()
            
            print(f"[{username}] ...Successfully submitted email: {email_to_use}")
            
            try:
                with open(email_file, "w", encoding="utf-8") as f:
                    f.writelines(remaining_emails)
                print(f"INFO: Removed '{original_email_to_try}' from email.txt.")
            except Exception as e:
                print(f"⚠️ Could not update email.txt: {e}")
            
            log_id_email(username, email_to_use)
            return email_to_use, True

        except Exception as e:
            print(f"[{username}] ...⚠️ Attempt #{attempt + 1} failed. Reason: {e}")
            if attempt < max_retries:
                print(f"[{username}] ...Retrying with a new email...")
                try:
                    cancel_button = driver.find_element(By.XPATH, "//div[contains(@class, 'modal-content')]//button[contains(text(), 'Cancel')]")
                    cancel_button.click()
                except:
                    driver.refresh()
                time.sleep(2)
            else:
                print(f"[{username}] ...Failed to add any email after {max_retries + 1} total attempts.")
                break

    print(f"[{username}] ...Refreshing page and moving to the next function.")
    driver.refresh()
    time.sleep(3)
    return None, False

def generate_random_email_prefix(length=10):
    """สร้างชื่ออีเมลแบบสุ่ม a-z, 0-9"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def log_id_email(username, email):
    """บันทึก username และ email ลงไฟล์ id_email.txt"""
    try:
        with open("id_email.txt", "a", encoding="utf-8") as f:
            f.write(f"{username}:{email}\n")
        print(f"INFO: Logged {username}:{email} to id_email.txt")
    except Exception as e:
        print(f"⚠️ Could not log to id_email.txt: {e}")

def load_config():
    """โหลดการตั้งค่าจากไฟล์ config"""
    config = {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Config file '{CONFIG_FILE}' not found. Creating default config.")
        create_default_config()
        return load_config()
    except Exception as e:
        print(f"Error loading config: {e}")
    
    return config

def create_default_config():
    """สร้างไฟล์ config เริ่มต้น"""
    default_config = """# Roblox Account Registration Configuration
# Discord Webhook URL (optional)
Discord_Webhook=

# Registration Settings
Username_Prefix=user
Password_Length=12
Use_Random_Suffix=true
Suffix_Length=2

# Email Settings
Add_Email=false
Email_Retry_Count=3

# Post-Login Actions
Change_Display_Name=false
Update_About_Me=false
Update_Social_Links=false
Purchase_Random_Item=false

# Browser Settings
Headless_Mode=false
Implicit_Wait=10
Page_Load_Timeout=30

# Router Reboot Settings
Enable_Router_Reboot=true
Reboot_Every_N_Accounts=10
Wait_After_Reboot=60
"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(default_config)

def generate_password():
    """สร้างรหัสผ่านแบบสุ่ม"""
    length = int(config.get('Password_Length', 12))
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def log_success(username, password, cookies):
    """บันทึกข้อมูลบัญชีที่สร้างสำเร็จ"""
    try:
        with open(SUCCESS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}\n")
        
        # ส่งไปยัง Discord
        webhook_url = config.get('Discord_Webhook', '')
        if webhook_url:
            embed_data = {
                "title": "✅ Account Created Successfully",
                "description": f"**Username:** {username}\n**Password:** {password}",
                "color": 0x00ff00,
                "timestamp": datetime.now().isoformat()
            }
            send_to_discord(webhook_url, embed_data)
            
    except Exception as e:
        print(f"Error logging success: {e}")

def log_failure(username, password, cookies):
    """บันทึกข้อมูลบัญชีที่สร้างไม่สำเร็จ"""
    try:
        with open("account_failed.txt", "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}\n")
    except Exception as e:
        print(f"Error logging failure: {e}")

def perform_post_login_actions(driver, username, password, config):
    """ทำการกระทำต่างๆ หลังล็อกอิน"""
    try:
        if config.get('Change_Display_Name', 'false').lower() == 'true':
            change_display_name(driver, username)
        
        if config.get('Update_About_Me', 'false').lower() == 'true':
            update_about_me(driver, username)
        
        if config.get('Update_Social_Links', 'false').lower() == 'true':
            update_social_links(driver, username)
        
        if config.get('Purchase_Random_Item', 'false').lower() == 'true':
            purchase_random_item(driver, username, config)
            
    except Exception as e:
        print(f"Error in post-login actions: {e}")

def change_display_name(driver, username):
    """เปลี่ยนชื่อแสดงผล"""
    try:
        driver.get("https://www.roblox.com/my/account#!/info")
        time.sleep(2)
        
        display_name = random.choice(DISPLAY_NAMES)
        
        edit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Edit')]"))
        )
        edit_button.click()
        
        display_name_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "displayName"))
        )
        display_name_input.clear()
        display_name_input.send_keys(display_name)
        
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()
        
        print(f"[{username}] Changed display name to: {display_name}")
        
    except Exception as e:
        print(f"Error changing display name: {e}")

def update_about_me(driver, username):
    """อัปเดตข้อมูล About Me"""
    try:
        driver.get("https://www.roblox.com/my/account#!/info")
        time.sleep(2)
        
        about_me_text = random.choice(ABOUT_ME_TEXTS)
        
        about_me_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "aboutMe"))
        )
        about_me_input.clear()
        about_me_input.send_keys(about_me_text)
        
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()
        
        print(f"[{username}] Updated About Me: {about_me_text}")
        
    except Exception as e:
        print(f"Error updating About Me: {e}")

def update_social_links(driver, username):
    """อัปเดตลิงก์โซเชียล"""
    try:
        driver.get("https://www.roblox.com/my/account#!/info")
        time.sleep(2)
        
        social_links = {
            "YouTube": "https://www.youtube.com/@gaminglab",
            "Twitter": "https://twitter.com/gaminglab",
            "Instagram": "https://www.instagram.com/gaminglab"
        }
        
        for platform, url in social_links.items():
            try:
                input_field = driver.find_element(By.XPATH, f"//input[@placeholder='{platform} URL']")
                input_field.clear()
                input_field.send_keys(url)
            except:
                continue
        
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()
        
        print(f"[{username}] Updated social links")
        
    except Exception as e:
        print(f"Error updating social links: {e}")

def purchase_random_item(driver, username, config):
    """ซื้อไอเทมแบบสุ่ม"""
    try:
        # ไปที่หน้า Catalog
        driver.get("https://www.roblox.com/catalog")
        time.sleep(3)
        
        # คลิกไอเทมแรกที่เจอ
        item_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'catalog-item')]"))
        )
        item_link.click()
        time.sleep(2)
        
        # คลิกปุ่ม Buy
        buy_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Buy')]"))
        )
        buy_button.click()
        
        print(f"[{username}] Purchased random item")
        
    except Exception as e:
        print(f"Error purchasing item: {e}")

def create_roblox_account(username, password, config):
    """สร้างบัญชี Roblox"""
    driver = None
    try:
        # ตั้งค่า Chrome
        chrome_options = Options()
        if config.get('Headless_Mode', 'false').lower() == 'true':
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.implicitly_wait(int(config.get('Implicit_Wait', 10)))
        driver.set_page_load_timeout(int(config.get('Page_Load_Timeout', 30)))
        
        # ไปที่หน้า Register
        driver.get("https://www.roblox.com/signup")
        time.sleep(3)
        
        # กรอกข้อมูล
        username_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "signup-username"))
        )
        username_input.send_keys(username)
        
        password_input = driver.find_element(By.ID, "signup-password")
        password_input.send_keys(password)
        
        # เลือกวันเกิด
        month_select = driver.find_element(By.ID, "MonthDropdown")
        month_select.click()
        month_option = driver.find_element(By.XPATH, "//option[@value='1']")
        month_option.click()
        
        day_select = driver.find_element(By.ID, "DayDropdown")
        day_select.click()
        day_option = driver.find_element(By.XPATH, "//option[@value='1']")
        day_option.click()
        
        year_select = driver.find_element(By.ID, "YearDropdown")
        year_select.click()
        year_option = driver.find_element(By.XPATH, "//option[@value='1990']")
        year_option.click()
        
        # คลิกปุ่ม Sign Up
        signup_button = driver.find_element(By.ID, "signup-button")
        signup_button.click()
        
        # รอการสร้างบัญชี
        time.sleep(5)
        
        # ตรวจสอบว่าสำเร็จหรือไม่
        if "my/account" in driver.current_url or "home" in driver.current_url:
            print(f"✅ สร้างบัญชี {username} สำเร็จ!")
            
            # เพิ่มอีเมล
            add_email_to_account(driver, username)
            
            # ทำการกระทำหลังล็อกอิน
            perform_post_login_actions(driver, username, password, config)
            
            # บันทึกข้อมูล
            cookies = driver.get_cookies()
            log_success(username, password, cookies)
            
            return True
        else:
            print(f"❌ สร้างบัญชี {username} ไม่สำเร็จ")
            cookies = driver.get_cookies()
            log_failure(username, password, cookies)
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        if driver:
            cookies = driver.get_cookies()
            log_failure(username, password, cookies)
        return False
    finally:
        if driver:
            driver.quit()

def run_registration_mode(config):
    """รันโหมดสร้างบัญชี"""
    print("🚀 เริ่มโหมดสร้างบัญชี...")
    
    # เริ่มระบบ Router Reboot
    complete_system = CompleteSystem()
    if config.get('Enable_Router_Reboot', 'true').lower() == 'true':
        if complete_system.start_router_system():
            print("✅ ระบบ Router Reboot พร้อมใช้งาน!")
        else:
            print("⚠️  ระบบ Router Reboot ไม่พร้อมใช้งาน")
    
    try:
        while True:
            # สร้าง username
            prefix = config.get('Username_Prefix', 'user')
            suffix_length = int(config.get('Suffix_Length', 2))
            
            if config.get('Use_Random_Suffix', 'true').lower() == 'true':
                suffix = generate_random_suffix(suffix_length)
                username = f"{prefix}{suffix}"
            else:
                username = f"{prefix}{complete_system.account_counter + 1}"
            
            # สร้าง password
            password = generate_password()
            
            print(f"🔄 กำลังสร้างบัญชี: {username}")
            
            # สร้างบัญชี
            if create_roblox_account(username, password, config):
                complete_system.account_counter += 1
                print(f"✅ สร้างบัญชีสำเร็จ! (จำนวน: {complete_system.account_counter})")
                
                # ตรวจสอบการรีบูท
                complete_system.check_and_reboot()
            else:
                print(f"❌ สร้างบัญชีไม่สำเร็จ: {username}")
            
            # รอสักครู่
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n⏹️  หยุดการทำงาน...")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 60)
    print("🚀 ระบบสร้างบัญชี Roblox + Router Reboot")
    print("สำหรับเร้าเตอร์ GEL.iNet GL-XE300C4")
    print("=" * 60)
    
    # โหลดการตั้งค่า
    global config
    config = load_config()
    
    # รันโหมดสร้างบัญชี
    run_registration_mode(config)

if __name__ == "__main__":
    main()