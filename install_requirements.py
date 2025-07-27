#!/usr/bin/env python3
"""
Installation script for SSH Router Reboot System
For GL.iNet GL-XE300C4 Router IP Renewal
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    print("🔧 Installing required packages for SSH Router Reboot System...")
    print("=" * 60)
    
    required_packages = [
        "paramiko",  # For SSH connections
        "requests",  # For IP checking
    ]
    
    failed_packages = []
    
    for package in required_packages:
        print(f"📦 Installing {package}...")
        if not install_package(package):
            failed_packages.append(package)
    
    print("\n" + "=" * 60)
    if failed_packages:
        print(f"❌ Failed to install: {', '.join(failed_packages)}")
        print("Please install them manually using:")
        for package in failed_packages:
            print(f"   pip install {package}")
        return False
    else:
        print("✅ All packages installed successfully!")
        
    print("\n🔑 SSH Key Setup Instructions:")
    print("1. The system will automatically generate SSH keys if needed")
    print("2. Default router IP: 192.168.8.1")
    print("3. Default username: root")
    print("4. Default password: (empty) or 'goodlife'")
    print("5. Make sure your GL.iNet router SSH is enabled:")
    print("   - Go to router admin panel")
    print("   - System > Administration")
    print("   - Enable SSH Access")
    
    print("\n📋 Configuration File Settings:")
    print("Add these lines to your config_register.txt:")
    print("ROUTER_SSH_HOST=192.168.8.1")
    print("ROUTER_SSH_PORT=22") 
    print("ROUTER_SSH_USERNAME=root")
    print("ROUTER_REBOOT_ENABLED=True")
    print("ROUTER_REBOOT_INTERVAL=10")
    
    print("\n🚀 System is ready! Run your main script to start using SSH router reboot.")
    return True

if __name__ == "__main__":
    main()