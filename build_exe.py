"""
Build script to create EXE file from ai_diagnostic.py
Run: python build_exe.py
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    print("=" * 60)
    print("Building Windows Diagnostic Tool (v1.0)")
    print("=" * 60)
    print()
    
    # Check if PyInstaller is installed
    print("[1/4] Checking PyInstaller...")
    success, output = run_command("pip show pyinstaller")
    if not success:
        print("Installing PyInstaller...")
        success, output = run_command("pip install pyinstaller")
        if not success:
            print(f"ERROR: Failed to install PyInstaller: {output}")
            return False
    
    print("[2/4] Building EXE file...")
    
    # PyInstaller command
    # PyInstaller command
    cmd = [
        f'"{sys.executable}"', "-m", "PyInstaller",
        "--onefile",
        "--noconfirm",
        "--name", "SuperDiagnosticTool",
        "--hidden-import=google.generativeai",
        "--hidden-import=psutil",
        "--hidden-import=rich",
        "--console",
        "--clean",
        "super_diagnose_v2.py"
    ]
    
    success, output = run_command(" ".join(cmd))
    if not success:
        print(f"ERROR: Build failed: {output}")
        return False
    
    print("[3/4] Cleaning up build files...")
    # Clean up build directory and spec file
    import shutil
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("SuperDiagnosticTool.spec"):
        os.remove("SuperDiagnosticTool.spec")
    
    print("[4/4] Done!")
    print()
    print("=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print()
    print("Your EXE file is located in: dist\\SuperDiagnosticTool.exe")
    print()
    print("You can now:")
    print("  1. Copy dist\\SuperDiagnosticTool.exe to any folder")
    print("  2. Run it directly (no Python needed!)")
    print("  3. Share it with others")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

