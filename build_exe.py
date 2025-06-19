#!/usr/bin/env python3
"""
Build script for Ice Cream Database Generator
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess

def check_icon():
    """Check if the ice-cream.ico file exists"""
    if os.path.exists("ice-cream.ico"):
        print("✅ Icon found: ice-cream.ico")
        return True
    else:
        print("⚠️  Icon not found: ice-cream.ico")
        print("ℹ️  Please ensure ice-cream.ico is in the current directory")
        return False

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check for icon file
    has_icon = check_icon()
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create a single executable file
        "--windowed",                   # Hide console window (for GUI apps)
        "--name", "IceCreamDBGenerator", # Name of the executable
        "--distpath", "dist",           # Output directory
        "--workpath", "build",          # Temporary build directory
        "--clean",                      # Clean build directory before building
    ]
    
    # Add icon if available
    if has_icon:
        cmd.extend(["--icon", "ice-cream.ico"])
    
    # Add the main script
    cmd.append("ice_cream_data.py")
    
    print("🔨 Building executable with command:")
    print(" ".join(cmd))
    print()
    
    try:
        subprocess.check_call(cmd)
        print("\n✅ Build completed successfully!")
        print("📁 Executable location: dist/IceCreamDBGenerator.exe")
        print("\n📋 To distribute, copy the following files:")
        print("   - dist/IceCreamDBGenerator.exe")
        print("   - Any required ODBC drivers on target machines")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🍦 Ice Cream Database Generator - Build Script")
    print("=" * 50)
    
    if not os.path.exists("ice_cream_data.py"):
        print("❌ ice_cream_data.py not found in current directory")
        sys.exit(1)
    
    success = build_executable()
    
    if success:
        print("\n🎉 Build process completed!")
        print("\n💡 Usage instructions:")
        print("   1. Copy dist/IceCreamDBGenerator.exe to target machine")
        print("   2. Ensure ODBC drivers are installed on target machine")
        print("   3. Run the executable")
    else:
        print("\n❌ Build process failed")
        sys.exit(1) 