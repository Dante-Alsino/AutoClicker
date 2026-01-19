
import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists("build"):
    shutil.rmtree("build")
if os.path.exists("dist"):
    shutil.rmtree("dist")

# Assets
icon_path = os.path.join("assets", "logo.ico") 
splash_path = os.path.join("assets", "splash.png")

print("Building AutoClicker...")

PyInstaller.__main__.run([
    'main.py',
    '--name=AutoClicker',
    '--onefile',
    '--noconsole',
    '--clean',
    f'--splash={splash_path}',
    f'--icon={icon_path}',
    f'--add-data=assets;assets',
    '--collect-all=customtkinter', # Sometimes needed for ctk
])

print("Build Complete. Check 'dist' folder.")
