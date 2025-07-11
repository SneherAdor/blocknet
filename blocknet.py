import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import ctypes
import sys
import os
import threading
import pystray
import webbrowser
from PIL import Image, ImageDraw, ImageTk

# --- Utility Functions ---

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", f"Command failed:\n{command}")

def open_github(event=None):
    webbrowser.open_new("https://github.com/SneherAdor/blocknet")

# --- Firewall Functions ---

def enable_chatgpt_mode():
    if not is_admin():
        messagebox.showwarning("Permission Denied", "❌ Please run this app as Administrator to enable firewall rules.")
        return

    run_command('netsh advfirewall set privateprofile state on')
    run_command('netsh advfirewall set publicprofile state on')
    run_command('netsh advfirewall set domainprofile firewallpolicy blockinbound,blockoutbound')
    run_command('netsh advfirewall set privateprofile firewallpolicy blockinbound,blockoutbound')
    run_command('netsh advfirewall set publicprofile firewallpolicy blockinbound,blockoutbound')

    run_command('netsh advfirewall firewall add rule name="Allow ChatGPT 1" dir=out action=allow remoteip=104.18.32.47 protocol=any enable=yes profile=any')
    run_command('netsh advfirewall firewall add rule name="Allow ChatGPT 2" dir=out action=allow remoteip=172.64.155.209 protocol=any enable=yes profile=any')
    run_command('netsh advfirewall firewall add rule name="Allow DNS" dir=out action=allow protocol=UDP localport=53 remoteport=53 enable=yes profile=any')

    run_command('netsh interface ipv6 set teredo disabled')
    run_command('netsh interface ipv6 6to4 set state disabled')
    run_command('netsh interface ipv6 isatap set state disabled')

    messagebox.showinfo("Success", "✅ BlockNet now active!")

def disable_chatgpt_mode():
    if not is_admin():
        messagebox.showwarning("Permission Denied", "❌ Please run this app as Administrator to restore internet access.")
        return

    run_command('netsh advfirewall firewall delete rule name="Allow ChatGPT 1"')
    run_command('netsh advfirewall firewall delete rule name="Allow ChatGPT 2"')
    run_command('netsh advfirewall firewall delete rule name="Allow DNS"')

    run_command('netsh advfirewall set domainprofile firewallpolicy blockinbound,allowoutbound')
    run_command('netsh advfirewall set privateprofile firewallpolicy blockinbound,allowoutbound')
    run_command('netsh advfirewall set publicprofile firewallpolicy blockinbound,allowoutbound')

    run_command('netsh advfirewall set privateprofile state off')
    run_command('netsh advfirewall set publicprofile state off')

    run_command('netsh interface ipv6 set teredo default')
    run_command('netsh interface ipv6 6to4 set state enabled')
    run_command('netsh interface ipv6 isatap set state enabled')

    messagebox.showinfo("Restored", "🌐 Full internet access has been restored.")

# --- System Tray Functions ---

def create_image():
    # Use your custom icon or create a minimal one
    icon_path = "icon.ico"
    if os.path.exists(icon_path):
        return Image.open(icon_path)
    # Fallback: simple shape for the icon
    image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
    ImageDraw.Draw(image).polygon([(19,6), (45,6), (54,26), (32,58), (10,26)], fill=(0, 122, 204, 255))

    return image

def on_quit(icon, item):
    icon.stop()
    root.quit()

def show_window(icon, item):
    root.after(0, root.deiconify)

def hide_window():
    root.withdraw()

def setup_tray():
    menu = pystray.Menu(
        pystray.MenuItem('Show', show_window),
        pystray.MenuItem('Block Internet Access', lambda: enable_chatgpt_mode()),
        pystray.MenuItem('Restore Internet Access', lambda: disable_chatgpt_mode()),
        pystray.MenuItem('Exit', on_quit)
    )
    icon = pystray.Icon("BlockNet", create_image(), "Block Net — Internet Access Controller", menu)
    icon.run()

def minimize_to_tray(event=None):
    hide_window()
    threading.Thread(target=setup_tray, daemon=True).start()

# --- GUI Setup ---

root = tk.Tk()
root.title("Block Net — Internet Access Controller")
root.geometry("460x300")
root.resizable(False, False)

# Use your custom icon
if os.path.exists('icon.ico'):
    root.iconbitmap('icon.ico')

style = ttk.Style(root)
style.theme_use('clam')

default_font = ("Segoe UI", 11)
header_font = ("Segoe UI", 14, "bold")

container = ttk.Frame(root, padding=20)
container.pack(fill='both', expand=True)

title_lbl = ttk.Label(container, text="Block Net — Internet Access Controller", font=header_font)
title_lbl.grid(row=0, column=0, columnspan=2, pady=(0,15))

enable_btn = tk.Button(container,
    text="❌ Block Internet Access", font=default_font,
    width=30, height=2, fg="white", bg="#dc3545",
    activebackground="#c82333", relief="flat", cursor="hand2",
    command=enable_chatgpt_mode)
enable_btn.default_bg = "#dc3545"
enable_btn.hover_bg = "#c82333"
enable_btn.grid(row=1, column=0, columnspan=2, pady=(0,12))

disable_btn = tk.Button(container,
    text="✅ Restore Internet Access", font=default_font,
    width=30, height=2, fg="white", bg="#28a745",
    activebackground="#218838", relief="flat", cursor="hand2",
    command=disable_chatgpt_mode)
disable_btn.default_bg = "#28a745"
disable_btn.hover_bg = "#218838"
disable_btn.grid(row=2, column=0, columnspan=2)

info_lbl = ttk.Label(
    container,
    text="⚠️ Please run as Administrator!\nOnly chatgpt.com will be accessible while blocking internet access.",
    foreground="#b22222",
    font=("Segoe UI", 9, "italic"),
    justify="center"
)
info_lbl.grid(row=3, column=0, columnspan=2, pady=(20,0))

# GitHub footer link with icon
github_lbl = ttk.Label(
    container,
    text="GitHub",
    foreground="#666666",  # subtle gray
    cursor="hand2",
    font=("Segoe UI", 9, "underline")
)
github_lbl.grid(row=4, column=0, columnspan=2, pady=(10, 0))
github_lbl.bind("<Button-1>", open_github)

container.columnconfigure(0, weight=1)
container.columnconfigure(1, weight=1)

# Hover effect
def on_enter(e, btn): btn['background'] = btn.hover_bg
def on_leave(e, btn): btn['background'] = btn.default_bg
enable_btn.bind("<Enter>", lambda e: on_enter(e, enable_btn))
enable_btn.bind("<Leave>", lambda e: on_leave(e, enable_btn))
disable_btn.bind("<Enter>", lambda e: on_enter(e, disable_btn))
disable_btn.bind("<Leave>", lambda e: on_leave(e, disable_btn))

# Handle minimize
root.protocol("WM_DELETE_WINDOW", minimize_to_tray)
root.bind("<Unmap>", lambda event: minimize_to_tray() if root.state() == "iconic" else None)

root.mainloop()
