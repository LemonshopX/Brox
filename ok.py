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
#import undetected_chromedriver as uc
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

# --- Router SSH Configuration (will be updated from config file) ---
ROUTER_SSH_HOST = "192.168.8.1"  # Default GL.iNet router IP
ROUTER_SSH_PORT = 22
ROUTER_SSH_USERNAME = "root"  # Default GL.iNet username
ROUTER_SSH_PRIVATE_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")  # Path to SSH private key
ROUTER_REBOOT_COUNTER = 0  # Global counter for tracking when to reboot
ROUTER_REBOOT_ENABLED = True  # Whether router reboot is enabled
ROUTER_REBOOT_INTERVAL = 10  # How many accounts before reboot

def setup_ssh_key_if_needed():
    """Setup SSH key authentication for passwordless access to router"""
    print("🔑 Setting up SSH key authentication...")
    
    # Check if SSH key exists
    if not os.path.exists(ROUTER_SSH_PRIVATE_KEY_PATH):
        print("📝 SSH private key not found. Generating new SSH key pair...")
        try:
            # Generate SSH key pair
            os.system(f'ssh-keygen -t rsa -b 2048 -f {ROUTER_SSH_PRIVATE_KEY_PATH} -N ""')
            print(f"✅ SSH key pair generated at {ROUTER_SSH_PRIVATE_KEY_PATH}")
        except Exception as e:
            print(f"❌ Failed to generate SSH key: {e}")
            return False
    
    # Copy public key to router
    public_key_path = f"{ROUTER_SSH_PRIVATE_KEY_PATH}.pub"
    if os.path.exists(public_key_path):
        print("📤 Copying public key to router...")
        try:
            # Read public key
            with open(public_key_path, 'r') as f:
                public_key = f.read().strip()
            
            # Connect to router and add public key
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Try to connect with password first time to setup key
            print("🔐 Please enter router password for initial setup:")
            password = input("Router password (default is usually empty or 'goodlife'): ").strip()
            if not password:
                password = "goodlife"  # Common default for GL.iNet
                
            ssh.connect(ROUTER_SSH_HOST, port=ROUTER_SSH_PORT, username=ROUTER_SSH_USERNAME, password=password)
            
            # Create .ssh directory and authorized_keys
            ssh.exec_command("mkdir -p ~/.ssh")
            ssh.exec_command("chmod 700 ~/.ssh")
            ssh.exec_command(f"echo '{public_key}' >> ~/.ssh/authorized_keys")
            ssh.exec_command("chmod 600 ~/.ssh/authorized_keys")
            
            ssh.close()
            print("✅ SSH key authentication setup completed!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup SSH key authentication: {e}")
            print("💡 You may need to setup the router manually or check the IP address")
            return False
    
    return True

def reboot_router_via_ssh():
    """Reboot GL.iNet router via SSH to get new IP address"""
    global ROUTER_REBOOT_COUNTER
    
    print(f"🔄 Initiating router reboot via SSH (Host: {ROUTER_SSH_HOST})...")
    
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect using private key
        private_key = paramiko.RSAKey.from_private_key_file(ROUTER_SSH_PRIVATE_KEY_PATH)
        ssh.connect(
            hostname=ROUTER_SSH_HOST,
            port=ROUTER_SSH_PORT,
            username=ROUTER_SSH_USERNAME,
            pkey=private_key,
            timeout=10
        )
        
        print("✅ SSH connection established successfully")
        
        # Execute reboot command
        stdin, stdout, stderr = ssh.exec_command("reboot")
        
        # Wait a moment for command to execute
        time.sleep(2)
        
        ssh.close()
        print("🚀 Router reboot command sent successfully!")
        
        # Wait for router to reboot and come back online
        print("⏳ Waiting for router to reboot (60 seconds)...")
        time.sleep(60)
        
        # Wait for router to be accessible again
        print("🔍 Checking if router is back online...")
        max_wait_attempts = 30  # 30 attempts * 2 seconds = 60 seconds max wait
        for attempt in range(max_wait_attempts):
            try:
                test_ssh = paramiko.SSHClient()
                test_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                test_ssh.connect(
                    hostname=ROUTER_SSH_HOST,
                    port=ROUTER_SSH_PORT,
                    username=ROUTER_SSH_USERNAME,
                    pkey=private_key,
                    timeout=5
                )
                test_ssh.close()
                print("✅ Router is back online and accessible!")
                break
            except:
                print(f"⏳ Attempt {attempt + 1}/{max_wait_attempts} - Router not ready yet...")
                time.sleep(2)
        else:
            print("⚠️ Router may not be fully ready yet, continuing anyway...")
        
        # Check new IP address
        print("🌐 Checking new IP address...")
        try:
            response = requests.get("http://httpbin.org/ip", timeout=10)
            if response.status_code == 200:
                new_ip = response.json().get('origin', 'Unknown')
                print(f"🎯 New IP Address: {new_ip}")
            else:
                print("⚠️ Could not verify new IP address")
        except:
            print("⚠️ Could not check IP address")
        
        ROUTER_REBOOT_COUNTER = 0  # Reset counter
        return True
        
    except paramiko.AuthenticationException:
        print("❌ SSH authentication failed! Please run setup_ssh_key_if_needed() first")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Router reboot failed: {e}")
        return False

def update_router_config_from_file(config):
    """Update router configuration from config file"""
    global ROUTER_SSH_HOST, ROUTER_SSH_PORT, ROUTER_SSH_USERNAME, ROUTER_REBOOT_ENABLED, ROUTER_REBOOT_INTERVAL
    
    ROUTER_SSH_HOST = config.get('ROUTER_SSH_HOST', '192.168.8.1')
    ROUTER_SSH_PORT = int(config.get('ROUTER_SSH_PORT', 22))
    ROUTER_SSH_USERNAME = config.get('ROUTER_SSH_USERNAME', 'root')
    ROUTER_REBOOT_ENABLED = config.get('ROUTER_REBOOT_ENABLED', 'True').lower() == 'true'
    ROUTER_REBOOT_INTERVAL = int(config.get('ROUTER_REBOOT_INTERVAL', 10))
    
    print(f"🔧 Router Config: {ROUTER_SSH_HOST}:{ROUTER_SSH_PORT} (Reboot every {ROUTER_REBOOT_INTERVAL} accounts)")

def check_and_reboot_if_needed():
    """Check if router reboot is needed (based on config interval) and execute if necessary"""
    global ROUTER_REBOOT_COUNTER
    
    if not ROUTER_REBOOT_ENABLED:
        return True
    
    ROUTER_REBOOT_COUNTER += 1
    print(f"📊 Account counter: {ROUTER_REBOOT_COUNTER}/{ROUTER_REBOOT_INTERVAL}")
    
    if ROUTER_REBOOT_COUNTER >= ROUTER_REBOOT_INTERVAL:
        print(f"🔄 Reached {ROUTER_REBOOT_INTERVAL} accounts! Time to reboot router for new IP...")
        success = reboot_router_via_ssh()
        if success:
            print("✅ Router reboot completed successfully!")
        else:
            print("❌ Router reboot failed, continuing with current IP...")
        return success
    
    return True

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


# ... (ฟังก์ชันอื่นๆ ทั้งหมดที่เราเคยทำกันมา เช่น load_config, generate_password, perform_post_login_actions ฯลฯ ควรอยู่ที่นี่) ...
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
    remaining_emails = []

    # --- 1. อ่านและเตรียมอีเมลจากไฟล์ ---
    try:
        if not os.path.exists(email_file) or os.path.getsize(email_file) == 0:
            print(f"[{username}] ...'email.txt' not found or is empty. Skipping email add.")
            return None, True # ข้ามไป ถือว่าไม่ล้มเหลว
        
        with open(email_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines:
            print(f"[{username}] ...No emails left in email.txt. Skipping email add.")
            return None, True # ข้ามไป ถือว่าไม่ล้มเหลว

        original_email_to_try = lines[0].strip()
        remaining_emails = lines[1:]

    except Exception as e:
        print(f"[{username}] ...⚠️ Error reading email.txt: {e}")
        return None, False

    # --- 2. เริ่มกระบวนการเพิ่มอีเมล ---
    max_retries = 3
    for attempt in range(max_retries + 1): # +1 คือครั้งแรกที่ใช้ original_email
        email_to_use = ""
        if attempt == 0:
            email_to_use = original_email_to_try
        else:
            # สร้างอีเมลใหม่สำหรับการลองครั้งถัดไป
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
            
            # ตรวจสอบว่ามี Error message หรือไม่
            try:
                error_msg = driver.find_element(By.CSS_SELECTOR, ".modal-body .text-error")
                if error_msg.is_displayed():
                    raise Exception(f"Invalid email error detected: {error_msg.text}")
            except NoSuchElementException:
                pass # ไม่เจอ error ถือว่าผ่าน

            ok_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'modal-content')]//button[text()='OK']")))
            ok_button.click()
            
            # --- ถ้าสำเร็จ ---
            print(f"[{username}] ...Successfully submitted email: {email_to_use}")
            
            # ลบอีเมล (ตัวแรก) ออกจากไฟล์ email.txt
            try:
                with open(email_file, "w", encoding="utf-8") as f:
                    f.writelines(remaining_emails)
                print(f"INFO: Removed '{original_email_to_try}' from email.txt.")
            except Exception as e:
                print(f"⚠️ Could not update email.txt: {e}")
            
            # บันทึกอีเมลที่ใช้ได้ผลจริงๆ ลงไฟล์ id_email.txt
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
                # หากลองครบทุกครั้งแล้วยังไม่สำเร็จ
                print(f"[{username}] ...Failed to add any email after {max_retries + 1} total attempts.")
                break # ออกจาก Loop

    # หากจบ Loop แล้วยังไม่สำเร็จ ให้รีเฟรชหน้าแล้วไปต่อ
    print(f"[{username}] ...Refreshing page and moving to the next function.")
    driver.refresh()
    time.sleep(3)
    return None, False

def generate_random_email_prefix(length=10):
    """สร้างชื่ออีเมลแบบสุ่ม a-z, 0-9"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
def log_id_email(username, email):
    """บันทึก id และ email ที่คู่กันลงใน id_email.txt"""
    try:
        with open("id_email.txt", "a", encoding="utf-8") as f:
            f.write(f"{username}:{email}\n")
        print(f"INFO: Successfully logged '{username}:{email}' to id_email.txt.")
    except Exception as e:
        print(f"⚠️ Could not write to id_email.txt: {e}")
def load_config():
    """โหลดการตั้งค่าจากไฟล์ config และรองรับหลาย URL"""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write("CHROME_PATH=C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\n")
            f.write("GROUP_URLS=https://www.roblox.com/groups/group1\n")
            f.write("GAME_URLS=https://www.roblox.com/games/game1\n")
            f.write("EXTENSION_PATH=C:\\path\\to\\your\\extension_folder\n")
            f.write("ITEM_URLS=https://www.roblox.com/catalog/item1,https://www.roblox.com/catalog/item2\n") # เพิ่มตัวอย่าง
            f.write("RESTART_BUTTON_IMAGE_PATH=C:\\path\\to\\your\\restart_button.png\n") 
            f.write("Change_Display_name=True\n") # เพิ่มตัวอย่าง
            f.write("Change_About_me=True\n")            
            f.write("Add_Email=True\n")
            f.write("Purchase_Random_Item=True\n") 
            f.write("Notifly_FavMap=True\n") 
            f.write("Join_Group=True\n")
            f.write("DISCORD_WEBHOOK_URL=\n")
            f.write("# Router SSH Configuration for GL.iNet GL-XE300C4\n")
            f.write("ROUTER_SSH_HOST=192.168.8.1\n")
            f.write("ROUTER_SSH_PORT=22\n")
            f.write("ROUTER_SSH_USERNAME=root\n")
            f.write("ROUTER_REBOOT_ENABLED=True\n")
            f.write("ROUTER_REBOOT_INTERVAL=10\n")



        print(f"❌ ไม่พบไฟล์ '{CONFIG_FILE}', ได้สร้างไฟล์ตัวอย่างขึ้นมา กรุณาแก้ไขข้อมูลให้ถูกต้องแล้วรันใหม่อีกครั้ง")
        return None

    config = {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key] = value

    # แปลง URL ที่เป็น string ให้เป็น list
    config['GROUP_URLS'] = [url.strip() for url in config.get('GROUP_URLS', '').split(',') if url.strip()]
    config['GAME_URLS'] = [url.strip() for url in config.get('GAME_URLS', '').split(',') if url.strip()]
    config['ITEM_URLS'] = [url.strip() for url in config.get('ITEM_URLS', '').split(',') if url.strip()] # เพิ่มการอ่าน ITEM_URLS
    
    # เพิ่ม ITEM_URLS ใน key ที่จำเป็น
    required_keys = ["CHROME_PATH", "GROUP_URLS", "GAME_URLS", "EXTENSION_PATH", "ITEM_URLS","RESTART_BUTTON_IMAGE_PATH","DISCORD_WEBHOOK_URL","Change_Display_name","Change_About_me","Purchase_Random_Item","Notifly_FavMap","Join_Group"]
    if not all(key in config and config[key] for key in required_keys):
        print(f"❌ ไฟล์ '{CONFIG_FILE}' ขาดการตั้งค่าที่จำเป็น กรุณาตรวจสอบให้มีครบทั้ง {required_keys}")
        return None
    return config

def generate_password():
    # ... (ฟังก์ชันนี้เหมือนเดิม) ...
    return f"gml_{random.randint(10000, 99999)}"

def log_success(username, password, cookies):
    # ... (ฟังก์ชันนี้เหมือนเดิม) ...
    roblo_security_cookie = ""
    for cookie in cookies:
        if cookie['name'] == '.ROBLOSECURITY':
            roblo_security_cookie = cookie['value']
            break
    if roblo_security_cookie:
        with open(SUCCESS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{username}:{password}:{roblo_security_cookie}\n")
        return True
    return False

# --- [ใหม่] ฟังก์ชันสำหรับเปลี่ยน Display Name ---

def perform_post_login_actions(driver, username,password, config):
    """ฟังก์ชันสำหรับทำงานหลังล็อกอิน (เปลี่ยนชื่อ, แก้ไขโซเชียล, จอยกลุ่ม, ไลค์เกม)"""
    print(f"[{username}] Starting post-login actions...")

    # 1. เปลี่ยน Display Name
    if config['Change_Display_name'] == "True":
        change_display_name(driver, username)
        # 2. แก้ไข Social Links
    if config['Add_Email'] == "True":
        add_email_to_account(driver, username)            # 2. แก้ไข Social Links
        update_social_links(driver, username)
    if config['Change_About_me'] == "True":
        update_about_me(driver, username)
    # 3. วนลูปเข้ากลุ่มทั้งหมด
    if config['Purchase_Random_Item'] == "True":
        purchase_random_item(driver, username, config)
        # 4. วนลูปกดถูกใจ/ดาว/กระดิ่ง ทั้งหมด
    if config['Notifly_FavMap'] == "True":
        for i, game_url in enumerate(config['GAME_URLS'], 1):
            try:
                print(f"[{username}] ...Processing game {i}/{len(config['GAME_URLS'])}")
                driver.get(game_url)
                time.sleep(2)
                try:
                    fav_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "game-favorite-icon")))
                    driver.execute_script("arguments[0].click();", fav_button)
                    print(f"[{username}] ...Favorite action successful.")
                    time.sleep(1)
                except Exception:
                    print(f"[{username}] ...⚠️ Could not perform Favorite action.")
                try:
                    follow_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "game-follow-icon")))
                    driver.execute_script("arguments[0].click();", follow_button)
                    print(f"[{username}] ...Follow action successful.")
                    time.sleep(1)
                except Exception:
                    print(f"[{username}] ...⚠️ Could not perform Follow action.")
                try:
                    like_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.upvote")))
                    driver.execute_script("arguments[0].click();", like_button)
                    print(f"[{username}] ...Like action successful.")
                    time.sleep(1)
                except Exception:
                    print(f"[{username}] ...⚠️ Could not perform Like action.")
            except Exception as e:
                print(f"[{username}] ...⚠️ An error occurred with game: {game_url} | {e}")
    if config['Join_Group'] == "True":
        for i, group_url in enumerate(config['GROUP_URLS'], 1):
            print(f"[{username}] --- Processing Group {i}/{len(config['GROUP_URLS'])} ---")
            
            max_group_retries = 3
            is_group_successful = False
            
            for attempt in range(max_group_retries):
                print(f"[{username}] ...Group join attempt #{attempt + 1}/{max_group_retries} for URL: {group_url}")
                try:
                    driver.get(group_url)
                    join_button_xpath = "//button[contains(., 'Join')]"
                    
                    # 1. ลองหาปุ่ม Join ก่อน
                    try:
                        join_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, join_button_xpath))
                        )
                    except TimeoutException:
                        # ถ้าหาปุ่มไม่เจอใน 10 วิ แสดงว่าอยู่ในกลุ่มแล้ว
                        print(f"[{username}] ...'Join' button not found. Assuming already in group.")
                        is_group_successful = True
                        break # ออกจาก Loop ของกลุ่มนี้ ไปทำกลุ่มต่อไป

                    # 2. ถ้าเจอ ให้คลิกและรอแคปช่า
                    driver.execute_script("arguments[0].click();", join_button)
                    print(f"[{username}] ...'Join' button clicked. Checking for CAPTCHA...")


                    if not wait_for_extension_to_solve(driver, context="Group Join"):
                        # ถ้าแก้แคปช่าไม่สำเร็จ ให้ลองใหม่ในรอบถัดไป
                        print(f"[{username}] ...CAPTCHA solve failed on attempt #{attempt + 1}. Retrying group...")
                        continue # ไปยัง attempt ถัดไปของ Loop นี้

                    # 3. ตรวจสอบหลังแก้แคปช่า ว่าปุ่ม Join หายไปจริงหรือไม่
                    time.sleep(3) # รอให้หน้าเว็บอัปเดต
                    try:
                        driver.find_element(By.XPATH, join_button_xpath)
                        # ถ้ายังเจอปุ่มอยู่ แสดงว่าจอยไม่สำเร็จ (เช่น Unable to join)
                        print(f"[{username}] ...⚠️ Join failed after CAPTCHA (button still visible). Retrying group...")
                        continue # ไปยัง attempt ถัดไปของ Loop นี้
                    except NoSuchElementException:
                        # ถ้าหาปุ่มไม่เจอ แสดงว่าจอยสำเร็จ
                        print(f"[{username}] ...Successfully joined group.")
                        is_group_successful = True
                        break # ออกจาก Loop ของกลุ่มนี้ ไปทำกลุ่มต่อไป

                except Exception as e:
                    print(f"[{username}] ...An unexpected error occurred during group join attempt: {e}")
                    # หากเกิด Error ที่ไม่คาดคิด ให้ลองใหม่ในรอบถัดไป
                    continue
            if not is_group_successful:
                # หากลองครบ 3 ครั้งแล้วยังจอยกลุ่มนี้ไม่ได้
                print(f"FATAL: [{username}] Failed to join group {group_url} after {max_group_retries} attempts.")
                return # ออกจากฟังก์ชันทั้งหมดสำหรับบัญชีนี้
            # --- ตรวจสอบผลลัพธ์ของกลุ่มนี้ ---


# --- ส่วนที่เหลือของโค้ด (create_roblox_account, login_with_credentials, run modes, main) ---
# --- ไม่มีการเปลี่ยนแปลง สามารถใช้ของเดิมได้เลย ---
def log_failure(username, password, cookies):
    """บันทึกข้อมูลบัญชีที่ล้มเหลวลงใน account_fail.txt"""
    roblo_security_cookie = ""
    if cookies:
        for cookie in cookies:
            if cookie['name'] == '.ROBLOSECURITY':
                roblo_security_cookie = cookie['value']
                break
    else:
        roblo_security_cookie = "NO_COOKIE_OBTAINED"

    with open("account_fail.txt", "a", encoding="utf-8") as f:
        f.write(f"{username}:{password}:{roblo_security_cookie}\n")
    return True
def purchase_random_item(driver, username, config):
    """ฟังก์ชันสำหรับสุ่มซื้อไอเทมฟรี 1 ชิ้นจากลิสต์ใน config"""
    # ตรวจสอบว่ามีลิสต์ไอเทมใน config หรือไม่
    item_urls = config.get('ITEM_URLS')
    if not item_urls:
        print(f"[{username}] ...No item URLs found in config. Skipping purchase.")
        return

    print(f"[{username}] ...Attempting to purchase a random item...")
    try:
        # 1. สุ่มเลือกไอเทม 1 ชิ้นจากลิสต์
        item_to_buy_url = random.choice(item_urls)
        print(f"[{username}] ...Selected item: {item_to_buy_url}")
        driver.get(item_to_buy_url)
        time.sleep(5) # รอหน้าโหลด

        # 2. ค้นหาและคลิกปุ่ม "Buy"
        # ใช้ Selector ที่รวม class หลายๆ ตัวเพื่อความแม่นยำ
        buy_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.shopping-cart-buy-button.btn-growth-lg"))
        )
        buy_button.click()
        print(f"[{username}] ...Clicked 'Buy' button.")
        time.sleep(1.5)

        # 3. รอให้หน้าต่างยืนยันปรากฏขึ้นมา แล้วคลิกปุ่ม "Get Now"
        get_now_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.modal-button.btn-primary-md"))
        )
        get_now_button.click()
        print(f"[{username}] ...Clicked 'Get Now' button.")
        time.sleep(2) # รอให้หน้าต่างปิดไป
        
        print(f"[{username}] ...Successfully purchased item.")

    except Exception as e:
        print(f"[{username}] ...⚠️ Could not purchase item. (Already owned? Not for sale? Error: {e})")
def create_roblox_account(username, password, config):
    """ฟังก์ชันสำหรับสมัครบัญชี พร้อมระบบสุ่มชื่อใหม่เมื่อซ้ำ"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
    chrome_options.binary_location = config['CHROME_PATH']
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if config.get('EXTENSION_PATH'):
        try:
            chrome_options.add_argument(f"--load-extension={config['EXTENSION_PATH']}")
            print(f"[{username}] Loading extension from: {config['EXTENSION_PATH']}")
        except Exception as e:
            print(f"⚠️ Could not load extension: {e}")

    driver = None
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        #driver = uc.Chrome(options=chrome_options)
    except Exception as e:
        return {"status": "driver_error", "message": f"Could not start ChromeDriver: {e}"}


    
    # --- [ใหม่] ใช้ current_username เพื่อให้สามารถเปลี่ยนชื่อได้ ---
    current_username = username 
    try: 
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                print(f"[{current_username}] Registration attempt #{attempt + 1}/{max_attempts}...")
                driver.get("https://www.roblox.com/")
                
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "signup-username")))
                
                # --- ส่วนกรอกข้อมูลวันเกิด ---
                year = random.randint(1997, 2009)
                month = random.choice(list(calendar.month_name)[1:])
                day = random.randint(10, 28)
                month_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "MonthDropdown")))
                month_dropdown.send_keys(month)
                time.sleep(1)
                day_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "DayDropdown")))
                day_dropdown.send_keys(str(day))
                time.sleep(1)
                year_dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "YearDropdown")))
                year_dropdown.send_keys(str(year))
                
                # --- [ใหม่] กรอกชื่อที่อาจมีการเปลี่ยนแปลง และรหัสผ่าน ---
                username_field = driver.find_element(By.ID, "signup-username")
                username_field.clear()
                username_field.send_keys(current_username)
                driver.find_element(By.ID, "signup-password").send_keys(password)

                try:
                    signup_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "signup-button")))
                    driver.execute_script("arguments[0].click();", signup_button)
                    print(f"[{current_username}] Sign up button clicked, checking for CAPTCHA...")
                except TimeoutException:
                    # --- [ใหม่] ตรรกะการสุ่มชื่อใหม่ ---
                    new_suffix = generate_random_suffix()
                    new_username = f"{username}_{new_suffix}"
                    print(f"[{username}] Username might be taken. Retrying with new name: {new_username}")
                    current_username = new_username # อัปเดตชื่อที่จะใช้ในรอบถัดไป
                    username = new_username
                    continue # ข้ามไปลองใหม่ในรอบถัดไป
                
                if not wait_for_extension_to_solve(driver, context="Registration"):
                    raise Exception("Extension failed to solve CAPTCHA.")

                # ถ้าสำเร็จ จะออกจาก loop และไปที่ return ด้านล่าง
                start_time = time.time()
                is_successful = False
                while time.time() - start_time < 60:
                    if "home" in driver.current_url:
                        is_successful = True
                        break
                    try:
                        try_again_button = driver.find_element(By.XPATH, "//button[text()='Try again']")
                        try_again_button.click()
                        time.sleep(5)
                    except NoSuchElementException: pass
                    time.sleep(2)

                if is_successful:
                    print(f"✅ [{username}] Registration successful!")
                    perform_post_login_actions(driver, username, password, config)
                    cookies = driver.get_cookies()
                    return {"status": "success", "username": username, "password": password, "cookies": cookies}
                else:
                    # ถ้าหมดเวลา 60 วินาที ให้โยน Exception เพื่อไปที่ except ด้านล่าง
                    raise Exception("Final verification timed out after 60 seconds.")
                # --- สิ้นสุดส่วนที่แก้ไข ---

            except Exception as e:
                print(f"[{username}] ERROR on attempt #{attempt + 1}: {e}")
                if attempt < max_attempts - 1:
                    print(f"[{username}] ...Retrying...")
                    # ไม่ต้อง refresh เพราะ Loop จะ get URL ใหม่ให้เอง
                else:
                    print(f"[{username}] Failed to register after {max_attempts} attempts.")
                    return {"status": "error", "message": f"Failed after {max_attempts} attempts."}
        
    finally:
        # --- 3. บล็อกนี้จะทำงานเป็นอย่างสุดท้าย "เสมอ" ---
        # ไม่ว่าโปรแกรมจะคืนค่า return จากจุดไหนใน try บล็อกก็ตาม
        print(f"[{username}] --- Closing browser ---")
        if driver:
            driver.quit()
    #finally:
      #  if driver:
       #     driver.quit()
def click_image_on_screen(config, confidence=0.90):
    """ค้นหารูปภาพบนหน้าจอและคลิกตรงกลาง โดยอ่าน Path จาก config"""
    try:
        # --- ส่วนที่แก้ไข: ดึง Path ของรูปภาพจาก config ---
        image_file = config['RESTART_BUTTON_IMAGE_PATH']
        # --- สิ้นสุดส่วนที่แก้ไข ---
        
        location = pyautogui.locateCenterOnScreen(image_file, confidence=confidence)
        if location:
            print(f"    [PyAutoGUI] Image '{image_file}' found at {location}. Clicking...")
            pyautogui.click(location)
            return True
        else:
            #print(f"    [PyAutoGUI] Image '{image_file}' not found on screen.")
            return False
    except Exception as e:
        print(f"    [PyAutoGUI] An error occurred: {e}")
        return False
def wait_for_extension_to_solve(driver, context="Unknown"):
    """
    รอให้ Extension แก้ CAPTCHA (เวอร์ชันค้นหาเชิงลึก และกดปุ่ม Try again)
    """
    for attempt in range(4):
        print(f"    [CAPTCHA] Attempt #{attempt + 1}/4 (Context: {context})...")
        
        captcha_iframe = None
        try:
            print("    [DEBUG] Searching for CAPTCHA in main document...")
            captcha_iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='arkoselabs']"))
            )
        except TimeoutException:
        # --- ตรรกะการค้นหาเชิงลึก (เหมือนเดิม) ---
            #print("    [DEBUG] Not in main document. Searching inside other iframes...")
            try:
                    parent_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                    for p_iframe in parent_iframes:
                        try:
                            driver.switch_to.frame(p_iframe)
                            captcha_iframe = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='arkoselabs']"))
                            )
                            if captcha_iframe:
                                # ถ้าเจอ ให้หยุดค้นหา (ตอนนี้เรายังอยู่ใน iframe ตัวแม่)
                                break
                        except TimeoutException:
                            driver.switch_to.default_content()
            except Exception:
                    driver.switch_to.default_content()
            
        if captcha_iframe:
            print("    [CAPTCHA] Detected. Waiting for extension to solve...")
            try:
                # รอจนกว่า iframe นั้นจะหายไป
                WebDriverWait(driver, 40).until(EC.staleness_of(captcha_iframe))
                print("    [CAPTCHA] Solved successfully by extension.")
                driver.switch_to.default_content()
                return True
            except TimeoutException:
                # ถ้าไม่หายไปใน 20 วิ แสดงว่า Extension แก้ไม่สำเร็จ
                if attempt < 3:
                    # --- ส่วนที่แก้ไข: เปลี่ยนเป็นค้นหาและคลิกปุ่ม 'Try again' ---
                    try:
                        # 3a. สลับเข้าไปในกรอบของแคปช่าก่อน
                        if click_image_on_screen(config):
                        # --- สิ้นสุดส่วนที่แก้ไข ---
                            print("    [CAPTCHA] ...Attempting to click 'Try again'.")
                            print("    [PyAutoGUI] Click successful. Waiting for CAPTCHA to reload...")
                            time.sleep(2)
                        else:
                           print("    [CAPTCHA] Solved successfully by extension.")
                           return True
                            #time.sleep(1)
                    except Exception:
                        print("Nope")
                        time.sleep(5)
                    finally:
                        # **สำคัญ:** กลับมาที่หน้าหลักเสมอไม่ว่าจะเกิดอะไรขึ้น
                        driver.switch_to.default_content()
                    # --- สิ้นสุดส่วนที่แก้ไข ---
                else:
                     driver.switch_to.default_content()
        else:
            print("    [CAPTCHA] No CAPTCHA detected after deep search. Continuing.")
            return True

    print(f"    [CAPTCHA] ❌ Failed to solve CAPTCHA after 4 attempts.")
    return False
def login_with_credentials(driver, username, password, config):
    """ฟังก์ชันสำหรับล็อกอิน พร้อมระบบ Retry หากแก้แคปช่าไม่สำเร็จ"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"[{username}] Login attempt #{attempt + 1}/{max_attempts}...")
            # ไปที่หน้าเว็บทุกครั้งที่เริ่มลองใหม่
            driver.get("https://www.roblox.com/login")
            
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))
            driver.find_element(By.ID, "login-username").send_keys(username)
            driver.find_element(By.ID, "login-password").send_keys(password)
            driver.find_element(By.ID, "login-button").click()
            print(f"[{username}] Attempting login, checking for CAPTCHA...")

            if not wait_for_extension_to_solve(driver, context="Login"):
                # ถ้าแก้ไม่สำเร็จ ให้โยน Exception เพื่อเริ่มลองใหม่
                raise Exception("Extension failed to solve CAPTCHA.")
            
            WebDriverWait(driver, 60).until_not(EC.url_contains("login"))
            if "home" in driver.current_url or "discover" in driver.current_url:
                print(f"✅ [{username}] Login successful.")
                return True # คืนค่า True เมื่อสำเร็จ
            else:
                # ถ้ายังล็อกอินไม่สำเร็จหลังแก้แคปช่า
                raise Exception("Login failed after CAPTCHA or due to 2-Step Verification.")

        except Exception as e:
            print(f"[{username}] ERROR on attempt #{attempt + 1}: {e}")
            if attempt < max_attempts - 1:
                print(f"[{username}] ...Retrying...")
            else:
                print(f"❌ [{username}] Login failed after {max_attempts} attempts.")
                return False # คืนค่า False เมื่อลองครบทุกครั้งแล้วยังไม่สำเร็จ
def run_registration_mode(config):
    """โหมดที่ 1: สมัครบัญชีใหม่ และลบไอดีที่ทำแล้วออกจากไฟล์"""
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"❌ '{ACCOUNTS_FILE}' not found. Please create it and add usernames.")
        return
        
    # อ่านข้อมูลทั้งหมดเก็บในหน่วยความจำก่อน
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        usernames_to_register = [line.strip() for line in f if line.strip()]

    total_accounts_initial = len(usernames_to_register)
    if total_accounts_initial == 0:
        print("--- [Mode 1] No accounts found in accounts.txt. Nothing to do. ---")
        return

    ok_count = 0
    fail_count = 0
    webhook_url = config.get("DISCORD_WEBHOOK_URL")

    print(f"--- [Mode 1] Starting registration process for {total_accounts_initial} accounts ---")
    
    # --- [ใหม่] ใช้ while loop เพื่อให้สามารถลบไอดีออกจากลิสต์ได้ ---
    processed_count = 0
    while usernames_to_register:
        # ดึงชื่อแรกออกจากลิสต์มาทำงาน
        username = usernames_to_register.pop(0) 
        password = generate_password()
        processed_count += 1
        
        print(f"\n▶️ Processing account {processed_count}/{total_accounts_initial}: {username}")
        
        result = create_roblox_account(username, password, config)
        
        # --- ส่วนจัดการ Webhook และนับคะแนน (เหมือนที่คุณส่งมา) ---
        if result.get('status') == 'success':
            ok_count += 1
            if log_success(result['username'], result['password'], result['cookies']):
                print(f"✔️ Successfully saved result for {result['username']} to {SUCCESS_FILE}")
                
                # --- [ใหม่] เช็คและรีบูตเร้าเตอร์ทุก N ไอดี ---
                check_and_reboot_if_needed()
                
                success_embed = {
                    "title": f"✅ Registration Successful ({processed_count}/{total_accounts_initial})",
                    "color": 3066993,
                    "fields": [
                        {"name": "Username", "value": f"```{result['username']}```", "inline": True},
                        {"name": "Password", "value": "```**********```", "inline": True},
                        {"name": "---", "value": "**Post-Login Actions Status:**", "inline": False},
                        {"name": "Display Name", "value": "✅ Done" if config.get('Change_Display_name', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        {"name": "About Me", "value": "✅ Done" if config.get('Change_About_me', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        {"name": "Purchase Item", "value": "✅ Done" if config.get('Purchase_Random_Item', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        {"name": "Notify/Fav Game", "value": "✅ Done" if config.get('Notifly_FavMap', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        {"name": "Join Group", "value": "✅ Done" if config.get('Join_Group', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                    ]
                }
                send_to_discord(webhook_url, success_embed)
        else:
            fail_count += 1
            error_message = result.get('message', 'Unknown Error')
            print(f"❌ Failed for {username}: {error_message}")
            fail_embed = {
                "title": f"❌ Registration Failed ({processed_count}/{total_accounts_initial})",
                "color": 15158332,
                "fields": [{"name": "Username", "value": f"```{username}```"}, {"name": "Reason", "value": f"```{error_message}```"}]
            }
            send_to_discord(webhook_url, fail_embed)
        
        # --- [ใหม่] เขียนไฟล์ accounts.txt ใหม่ด้วยรายชื่อที่เหลืออยู่ ---
        try:
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                for name in usernames_to_register:
                    f.write(f"{name}\n")
            print(f"INFO: Updated '{ACCOUNTS_FILE}'. {len(usernames_to_register)} accounts remaining.")
        except Exception as e:
            print(f"⚠️ Could not update '{ACCOUNTS_FILE}': {e}")
            
        print("--- Pausing for 5 seconds before next item ---")
        time.sleep(5)
    
    # --- ส่วนสรุปผลตอนท้าย (เหมือนที่คุณส่งมา) ---
    summary_embed = {"title": "📊 Registration Summary", "color": 3447003,
                     "fields": [{"name": "Total Processed", "value": str(processed_count)}, {"name": "✅ Success", "value": str(ok_count)}, {"name": "❌ Failed", "value": str(fail_count)}]}
    send_to_discord(webhook_url, summary_embed)
    print("\n" + "="*20)
    print("      MODE 1 SUMMARY")
    print("="*20)
    print(f"  Total Accounts Processed: {processed_count}/{total_accounts_initial}")
    print(f"  ✅ Success: {ok_count}")
    print(f"  ❌ Failed/Skipped: {fail_count}")
    print("="*20)
    print("\n--- [Mode 1] Registration process finished ---")
    
def change_display_name(driver, username):
    time.sleep(3)
    """ฟังก์ชันสำหรับเปลี่ยน Display Name พร้อมระบบลองใหม่หากชื่อซ้ำ"""
    print(f"[{username}] ...Attempting to change display name...")
    try:
        # 1. ไปที่หน้าตั้งค่าและคลิกปุ่มแก้ไข
        driver.get("https://www.roblox.com/my/account#!/info")
        edit_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='setting-text-field-edit-btn']"))
        )
        edit_button.click()
        time.sleep(2)

        # 2. ค้นหาช่องกรอกข้อมูลเพียงครั้งเดียว
        display_name_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[focus-me='true']"))
        )

        is_successful = False
        # --- ส่วนที่แก้ไข: เพิ่ม Loop สำหรับลองใหม่ 3 ครั้ง ---
        for attempt in range(3):
            # 3. สุ่มชื่อและกรอกข้อมูล
            new_name = random.choice(DISPLAY_NAMES)
            print(f"[{username}] ...Attempt #{attempt + 1}: Trying new display name: {new_name}")
            
            display_name_input.click()
            time.sleep(1)
            display_name_input.clear()
            time.sleep(1)
            display_name_input.send_keys(new_name)
            time.sleep(2)

            try:
                # 4. พยายามค้นหาและคลิกปุ่ม Save
                # หากชื่อซ้ำ ปุ่ม Save มักจะกดไม่ได้ (disabled) ทำให้ WebDriverWait Timeout
                save_button_xpath = "//div[contains(@class, 'modal-content')]//button[contains(., 'Save')]"
                save_button = WebDriverWait(driver, 5).until( # ลดเวลารอลงเหลือ 5 วินาที
                    EC.element_to_be_clickable((By.XPATH, save_button_xpath))
                )
                save_button.click()
                time.sleep(2)
                
                print(f"[{username}] ...Display name change submitted successfully.")
                is_successful = True
                break # หากสำเร็จ ให้ออกจาก Loop

            except TimeoutException:
                # หากรอ 5 วิแล้วปุ่มยังกดไม่ได้ ให้ถือว่าชื่อซ้ำและลองใหม่
                print(f"[{username}] ...Attempt #{attempt + 1} failed, 'Save' button not clickable. Retrying...")
                # การวน Loop รอบถัดไปจะเกิดขึ้นโดยอัตโนมัติ
        
        if not is_successful:
            print(f"[{username}] ...Failed to change display name after 3 attempts. Closing modal.")
            # หากลองครบ 3 ครั้งแล้วยังไม่สำเร็จ ให้หากดปุ่ม Cancel หรือกากบาทเพื่อปิดหน้าต่าง
            try:
                # ลองหากากบาท (X) เพื่อปิด
                close_modal_button = driver.find_element(By.CSS_SELECTOR, ".modal-header .modal-close")
                close_modal_button.click()
            except:
                # ถ้าไม่เจอ ให้กดปุ่ม Cancel แทน
                cancel_button_xpath = "//div[contains(@class, 'modal-content')]//button[contains(., 'Cancel')]"
                driver.find_element(By.XPATH, cancel_button_xpath).click()
        # --- สิ้นสุดส่วนที่แก้ไข ---

    except Exception as e:
        print(f"[{username}] ...⚠️ A critical error occurred in the change name process: {e}")

def update_about_me(driver, username):
    print(f"[{username}] ...Attempting to update 'About Me' section...")
    try:
        driver.get("https://www.roblox.com/users/profile")
        time.sleep(2)
        # หน้านี้เปิดอยู่แล้ว ไม่ต้องไปไหน
        # 2. ค้นหาช่อง Textarea ด้วย ID และรอจนกว่าจะมองเห็น
        description_textarea = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "descriptionTextBox"))
        )
        
        # 3. สุ่มข้อความ, คลิก, ล้างของเก่า, แล้วพิมพ์ของใหม่
        about_text = random.choice(ABOUT_ME_TEXTS)
        print(f"[{username}] ...Trying new about text: '{about_text}'")
        
        description_textarea.click()
        time.sleep(1)
        description_textarea.clear()
        time.sleep(1)
        description_textarea.send_keys(about_text)
        time.sleep(1)

        # 4. ค้นหาปุ่ม Save ด้วย ID และคลิก
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "SaveInfoSettings"))
        )
        save_button.click()
        time.sleep(2) # รอให้ระบบบันทึก
        
        print(f"[{username}] ...'About Me' section saved successfully.")

    except Exception as e:
        print(f"[{username}] ...⚠️ Could not update 'About Me' section. Error: {e}")

def update_social_links(driver, username):
    """ฟังก์ชันสำหรับแก้ไข Social Links พร้อมการเลื่อนหน้าจอที่แม่นยำขึ้น"""
    print(f"[{username}] ...Attempting to update social links...")
    try:
        time.sleep(3)
        # --- ส่วนที่แก้ไข: เปลี่ยนวิธีการเลื่อนหน้าจอ ---
        # 1. ค้นหาช่องกรอก Facebook เพื่อใช้เป็นจุดอ้างอิงในการเลื่อน
        facebook_input_selector = "input[placeholder*='facebook.com']"
        facebook_input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, facebook_input_selector))
        )
        
        # 2. สั่งให้เลื่อนหน้าจอไปที่ตำแหน่งของช่องกรอกนั้น แล้วจัดให้อยู่กลางหน้าจอ
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", facebook_input_element)
        print(f"[{username}] ...Scrolled to social links section.")
        time.sleep(1)
        # --- สิ้นสุดส่วนที่แก้ไข ---

        # สร้างฟังก์ชันย่อยเพื่อลดความซ้ำซ้อน (เหมือนเดิม)
        def fill_social_input(placeholder_text, value_to_type):
            try:
                input_selector = f"input[placeholder*='{placeholder_text}']"
                social_input = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, input_selector))
                )
                social_input.click(); time.sleep(1)
                social_input.clear() # เพิ่มการล้างข้อมูลเก่าก่อนพิมพ์
                social_input.send_keys(value_to_type); time.sleep(1)
                print(f"[{username}] ...Filled '{placeholder_text}'")
            except Exception:
                print(f"[{username}] ...⚠️ Could not find or fill input for '{placeholder_text}'")
        
        # กรอกข้อมูลแต่ละช่อง (เหมือนเดิม)
        fill_social_input("facebook.com", f"www.facebook.com/{username}")
        #fill_social_input("@Roblox", f"https://x.com/{username}")
        fill_social_input("@Roblox", f"")
        fill_social_input("youtube.com", f"https://www.youtube.com/{username}") # ใช้ URL เต็มเพื่อให้สมจริง
        fill_social_input("twitch.tv", f"www.twitch.tv/{username}")
        fill_social_input("guilded.gg", f"")

        # กดปุ่ม Save (เหมือนเดิม)
        try:
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "save-social-settings"))
            )
            driver.execute_script("arguments[0].click();", save_button)
            time.sleep(1)
            print(f"[{username}] ...Clicked 'Save' for social links.")
        except Exception:
            print(f"[{username}] ...⚠️ Could not click the 'Save' button for social links.")

    except Exception as e:
        print(f"[{username}] ...⚠️ A critical error occurred in the update social links process: {e}")
def run_login_and_update_cookie_mode(config):
    """โหมดที่ 2: ล็อกอินด้วย id:pass, ทำงาน, แล้วอัปเดตคุกกี้"""
    if not os.path.exists(COOKIE_FILE):
        print(f"❌ '{COOKIE_FILE}' not found. Please create it and add id:pass data.")
        return

    accounts_data = []
    with open(COOKIE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                parts = line.strip().split(":", 2)
                username, password = parts[0], parts[1]
                old_cookie = parts[2] if len(parts) > 2 else ""
                accounts_data.append({"username": username, "password": password, "cookie": old_cookie})

    total_accounts = len(accounts_data)
    # --- [เพิ่มใหม่] ตั้งค่าตัวนับ ---
    ok_count = 0
    fail_count = 0
    webhook_url = config.get("DISCORD_WEBHOOK_URL")
    print(f"--- [Mode 2] Processing {total_accounts} accounts ---")
    
    for i, account in enumerate(accounts_data, 1):
        username, password = account['username'], account['password']
        # --- [เพิ่มใหม่] เพิ่มตัวบอกลำดับ ---
        print(f"\n▶️ Processing account {i}/{total_accounts}: {username}")
        
        driver = None
        is_successful_run = False # --- [เพิ่มใหม่] ตัวแปรตรวจสอบความสำเร็จ
        try:
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.binary_location = config['CHROME_PATH']
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            if config.get('EXTENSION_PATH'):
                try:
                    chrome_options.add_argument(f"--load-extension={config['EXTENSION_PATH']}")
                    print(f"[{username}] Loading extension from: {config['EXTENSION_PATH']}")
                except Exception as e:
                    print(f"⚠️ Could not load extension: {e}")
            
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            #driver = uc.Chrome(options=chrome_options)           
            # --- [เพิ่มใหม่] ปิดแท็บส่วนเกินที่ Extension อาจเปิดขึ้นมา ---
            
            # --- [แก้ไข] ส่ง config เข้าไปในฟังก์ชันด้วย ---
            if login_with_credentials(driver, username, password, config):
                perform_post_login_actions(driver, username, password, config)
                
                new_cookies = driver.get_cookies()
                new_roblo_security = ""
                for cookie in new_cookies:
                    if cookie['name'] == '.ROBLOSECURITY':
                        new_roblo_security = cookie['value']
                        break
                if new_roblo_security:
                    accounts_data[i-1]['cookie'] = new_roblo_security # แก้ไข index ให้ถูกต้อง
                    print(f"✔️ [{username}] New cookie obtained.")
                    is_successful_run = True # --- [เพิ่มใหม่] ตั้งค่าว่าสำเร็จ
                else:
                    print(f"⚠️ [{username}] Could not find new cookie after actions.")
            # ถ้า login ไม่สำเร็จ จะไม่เข้า if นี้ และ is_successful_run จะเป็น False
        
        except Exception as e:
            print(f"❌ A critical error occurred with account {username}: {e}")
        finally:
            # --- [เพิ่มใหม่] นับคะแนนตามผลลัพธ์ ---
            if is_successful_run:
                ok_count += 1
                if log_success(username, password, new_cookies):
                    print(f"✔️ Successfully saved result for {username} to {SUCCESS_FILE}")
                    
                    # --- [ใหม่] เช็คและรีบูตเร้าเตอร์ทุก N ไอดี ---
                    check_and_reboot_if_needed()

                    # --- [ใหม่] ส่ง Webhook เมื่อสำเร็จ ---
                    success_embed = {
                        "title": f"✅ Registration Successful ({i}/{total_accounts})",
                        "color": 3066993, # สีเขียว
                        "fields": [
                            {"name": "Username", "value": f"```{username}```", "inline": True},
                            {"name": "Password", "value": "```**********```", "inline": True},
                            {"name": "---", "value": "**Post-Login Actions Status:**", "inline": False}, # ตัวแบ่งเพื่อความชัดเจน
                            {"name": "Display Name", "value": "✅ Done" if config.get('Change_Display_name', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                            {"name": "About Me", "value": "✅ Done" if config.get('Change_About_me', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                            {"name": "Purchase Item", "value": "✅ Done" if config.get('Purchase_Random_Item', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                            {"name": "Notify/Fav Game", "value": "✅ Done" if config.get('Notifly_FavMap', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                            {"name": "Join Group", "value": "✅ Done" if config.get('Join_Group', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        ]
                    }
                    send_to_discord(webhook_url, success_embed)
                else: # หากล้มเหลว
                    fail_count += 1
                    #print(f"❌ Failed for {username}: {result['message']}")
                    # --- [ใหม่] ส่ง Webhook เมื่อล้มเหลว ---
                    fail_embed = {
                        "title": f"❌ Registration Failed ({i}/{total_accounts})",
                        "color": 15158332, # สีแดง
                        "fields": [
                            {"name": "Username", "value": f"```{username}```"},
                            {"name": "Password", "value": "```**********```", "inline": True},
                            {"name": "---", "value": "**Post-Login Actions Status:**", "inline": False}, # ตัวแบ่งเพื่อความชัดเจน
                            {"name": "Display Name", "value": "✅ Done" if config.get('Change_Display_name', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                            {"name": "About Me", "value": "✅ Done" if config.get('Change_About_me', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                            {"name": "Purchase Item", "value": "✅ Done" if config.get('Purchase_Random_Item', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                            {"name": "Notify/Fav Game", "value": "✅ Done" if config.get('Notifly_FavMap', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                            {"name": "Join Group", "value": "✅ Done" if config.get('Join_Group', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        ]
                    }
                    send_to_discord(webhook_url, fail_embed)

            if driver:
                driver.quit()
        print("--- Pausing for 5 seconds before next item ---")
        time.sleep(5)
    
    try:
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            for acc in accounts_data:
                f.write(f"{acc['username']}:{acc['password']}:{acc['cookie']}\n")
        print(f"\n✅ Successfully updated '{COOKIE_FILE}' with new cookies.")
    except Exception as e:
        print(f"\n❌ Could not write to '{COOKIE_FILE}': {e}")
    
    # --- [เพิ่มใหม่] แสดงสรุปผล ---
    print("\n" + "="*20)
    print("      MODE 2 SUMMARY")
    print("="*20)
    print(f"  Total Accounts Processed: {total_accounts}")
    print(f"  ✅ Success: {ok_count}")
    print(f"  ❌ Failed: {fail_count}")
    print("="*20)
    print("\n--- [Mode 2] Process finished ---")
def run_interactive_registration_mode(config):
    """โหมดที่ 3: สมัครบัญชีแบบโต้ตอบ รับชื่อนำหน้าและจำนวน"""
    print("\n--- [Mode 3] Interactive Registration ---")
    
    prefix = input("Please enter the username prefix (e.g., keyboard_): ").strip()
    if not prefix:
        print("❌ Prefix cannot be empty. Exiting mode.")
        return

    quantity = 0
    while True:
        try:
            quantity_str = input("How many accounts to create? (Max 100): ").strip()
            quantity = int(quantity_str)
            if 1 <= quantity <= 100: break
            else: print("❌ Please enter a number between 1 and 100.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            
    print("Generating unique numbers...")
    possible_numbers = list(range(1000, 10000))
    random.shuffle(possible_numbers)
    numbers_to_use = possible_numbers[:quantity]
    
    total_accounts = len(numbers_to_use)
    # --- [ใหม่] ตั้งค่าตัวนับ ---
    ok_count = 0
    fail_count = 0
    webhook_url = config.get("DISCORD_WEBHOOK_URL")
    print(f"--- Starting interactive registration for {total_accounts} accounts with prefix '{prefix}' ---")

    for i, number in enumerate(numbers_to_use, 1):
        username = f"{prefix}{number}"
        password = generate_password()
        # --- [ใหม่] เพิ่มตัวบอกลำดับ ---
        print(f"\n▶️ Processing account {i}/{total_accounts}: {username} | Password: {password}")
        
        result = create_roblox_account(username, password, config)
        
        if result['status'] == 'success':
            ok_count += 1
            if log_success(result['username'], result['password'], result['cookies']):
                print(f"✔️ Successfully saved result for {result['username']} to {SUCCESS_FILE}")
                
                # --- [ใหม่] เช็คและรีบูตเร้าเตอร์ทุก N ไอดี ---
                check_and_reboot_if_needed()
                
                # --- [ใหม่] ส่ง Webhook เมื่อสำเร็จ ---
                success_embed = {
                    "title": f"✅ Registration Successful ({i}/{total_accounts})",
                    "color": 3066993, # สีเขียว
                    "fields": [
                        {"name": "Username", "value": f"```{result['username']}```", "inline": True},
                        {"name": "Password", "value": "```**********```", "inline": True},
                        {"name": "---", "value": "**Post-Login Actions Status:**", "inline": False}, # ตัวแบ่งเพื่อความชัดเจน
                        {"name": "Display Name", "value": "✅ Done" if config.get('Change_Display_name', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        {"name": "About Me", "value": "✅ Done" if config.get('Change_About_me', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        {"name": "Purchase Item", "value": "✅ Done" if config.get('Purchase_Random_Item', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        {"name": "Notify/Fav Game", "value": "✅ Done" if config.get('Notifly_FavMap', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                        {"name": "Join Group", "value": "✅ Done" if config.get('Join_Group', 'False').lower() == 'true' else "❌ Skipped", "inline": True},
                     ]
                }
                send_to_discord(webhook_url, success_embed)
            else:
                # ...
                pass
        else: # หากล้มเหลว
            fail_count += 1
            print(f"❌ Failed for {username}: {result['message']}")
            # --- [ใหม่] ส่ง Webhook เมื่อล้มเหลว ---
            fail_embed = {
                "title": f"❌ Registration Failed ({i}/{total_accounts})",
                "color": 15158332, # สีแดง
                "fields": [
                    {"name": "Username", "value": f"```{username}```"},
                    {"name": "Reason", "value": f"```{result['message']}```"}
                ]
            }
            send_to_discord(webhook_url, fail_embed)

        if result['status'] == 'limit_reached':
            print(f"🛑 {result['message']}. Halting all operations.")
            break
        
        print("--- Pausing for 5 seconds before next item ---")
        time.sleep(5)
        
    # --- [ใหม่] ส่ง Webhook สรุปผล ---
    summary_embed = {
        "title": "📊 Registration Summary",
        "description": "The registration process has finished.",
        "color": 3447003, # สีฟ้า
        "fields": [
            {"name": "Total Processed", "value": str(i), "inline": True},
            {"name": "✅ Success", "value": str(ok_count), "inline": True},
            {"name": "❌ Failed", "value": str(fail_count), "inline": True}
        ]
    }
    send_to_discord(webhook_url, summary_embed)
        
    # --- [ใหม่] แสดงสรุปผล ---
    print("\n" + "="*20)
    print("      MODE 3 SUMMARY")
    print("="*20)
    print(f"  Total Accounts Processed: {i}/{total_accounts}")
    print(f"  ✅ Success: {ok_count}")
    print(f"  ❌ Failed/Skipped: {fail_count}")
    print("="*20)
    print("\n--- [Mode 3] Interactive registration process finished ---")
if __name__ == "__main__":
    config = load_config()
    if not config:
        exit()
        
    # --- [ใหม่] Update Router Configuration ---
    update_router_config_from_file(config)
    
    # --- [ใหม่] SSH Router Setup Check ---
    print("\n🔧 SSH Router Reboot System for GL.iNet GL-XE300C4")
    print(f"This system will automatically reboot your router every {ROUTER_REBOOT_INTERVAL} successful accounts to get new IP addresses.")
    
    if ROUTER_REBOOT_ENABLED:
        if not os.path.exists(ROUTER_SSH_PRIVATE_KEY_PATH):
            print(f"\n🔑 SSH key not found at {ROUTER_SSH_PRIVATE_KEY_PATH}")
            setup_choice = input("Would you like to setup SSH key authentication now? (y/n): ").strip().lower()
            if setup_choice == 'y':
                if setup_ssh_key_if_needed():
                    print("✅ SSH setup completed! Router reboot will work automatically.")
                else:
                    print("❌ SSH setup failed. Router reboot may not work.")
            else:
                print("⚠️ Skipping SSH setup. You can run setup later by selecting option 's' from main menu.")
        else:
            print("✅ SSH key found. Router reboot system is ready!")
    else:
        print("⚠️ Router reboot is disabled in config. Set ROUTER_REBOOT_ENABLED=True to enable.")
    
    while True:
        print("\n" + "="*40)
        print("Please select an operation mode:")
        print("  1: Register from file")
        print("  2: Log in & Update Cookie")
        print("  3: Interactive Register")
        print("  s: Setup SSH Router Authentication")
        print("  t: Test Router SSH Connection")
        print("  q: Exit program")
        print("="*40)
        
        choice = input("Select mode (1/2/3/s/t/q): ").strip()
        
        if choice == '1':
            run_registration_mode(config)
            break
        elif choice == '2':
            run_login_and_update_cookie_mode(config)
            break
        elif choice == '3':
            run_interactive_registration_mode(config) 
            break
        elif choice.lower() == 's':
            print("\n🔧 Setting up SSH Router Authentication...")
            if setup_ssh_key_if_needed():
                print("✅ SSH setup completed successfully!")
            else:
                print("❌ SSH setup failed!")
        elif choice.lower() == 't':
            print("\n🧪 Testing SSH connection to router...")
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                private_key = paramiko.RSAKey.from_private_key_file(ROUTER_SSH_PRIVATE_KEY_PATH)
                ssh.connect(
                    hostname=ROUTER_SSH_HOST,
                    port=ROUTER_SSH_PORT,
                    username=ROUTER_SSH_USERNAME,
                    pkey=private_key,
                    timeout=10
                )
                stdin, stdout, stderr = ssh.exec_command("uptime")
                uptime_output = stdout.read().decode().strip()
                ssh.close()
                print(f"✅ SSH connection successful!")
                print(f"📊 Router uptime: {uptime_output}")
            except Exception as e:
                print(f"❌ SSH connection failed: {e}")
                print("💡 Please run 'Setup SSH Router Authentication' first")
        elif choice.lower() == 'q':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

    input("\nProcess finished. Press Enter to exit...")