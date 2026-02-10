"""
Final production build script for SuperDiagnosticTool
Run: python build.py
"""

import subprocess
import sys
import os
import shutil

def run_command(cmd):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    print("=" * 60)
    print("SuperDiagnosticTool - Production Build")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("[1/4] Checking dependencies...")
    success, _ = run_command("pip show pyinstaller")
    if not success:
        print("Installing PyInstaller...")
        run_command("pip install pyinstaller")
    
    # Build
    print("[2/4] Building executable...")
    cmd = [
        f'"{sys.executable}"', "-m", "PyInstaller",
        "--onefile",
        "--noconfirm",
        "--name", "SuperDiagnosticTool",
        "--icon", "icon.ico",
        "--hidden-import=google.generativeai",
        "--hidden-import=psutil",
        "--collect-all", "rich",
        "--console",
        "--clean",
        "super_diagnose_v2.py"
    ]
    
    success, output = run_command(" ".join(cmd))
    if not success:
        print(f"ERROR: {output}")
        return False
    
    # Cleanup
    print("[3/4] Cleaning up...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("SuperDiagnosticTool.spec"):
        os.remove("SuperDiagnosticTool.spec")
    
    print("[4/4] Done!")
    print()
    print("=" * 60)
    print("SUCCESS! EXE created: dist\\SuperDiagnosticTool.exe")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
