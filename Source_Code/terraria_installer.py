import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
import os
import sys
import time
import shutil
import zipfile
from pathlib import Path
import winreg
import threading
import urllib.request
import json  # Нужно для чтения конфига

class TerrariaInstaller:
    # --- ССЫЛКИ НА ФАЙЛЫ ---
    
    # 1. Ссылка на конфиг установщика (ЭТО ГЛАВНАЯ ССЫЛКА, КОТОРУЮ НУЖНО ВСТАВИТЬ)
    # Вставь сюда свою RAW ссылку с GitHub:
    URL_APP_CONFIG = "https://raw.githubusercontent.com/TheFleece/calamity-coop-perfect-setup/refs/heads/main/app_config.json"
    
    # 2. Ссылки на файлы релиза (оставляем как есть, они ведут на Latest Release)
    URL_JSON_MODS = "https://github.com/TheFleece/calamity-coop-perfect-setup/releases/latest/download/enabled.json"
    URL_ZIP_CONFIGS = "https://github.com/TheFleece/calamity-coop-perfect-setup/releases/latest/download/ModConfigs.zip"

    # Ссылка по умолчанию (на случай, если GitHub недоступен)
    DEFAULT_STEAM_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id=3663184214"

    def __init__(self, root):
        self.root = root
        self.root.title("Terraria & tModLoader Установщик [Smart]")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        self.dialog_result = None
        self.steam_path = self.get_steam_path()
        self.docs_path = os.path.join(os.path.expanduser("~"), "Documents", "My Games", "Terraria", "tModLoader")
        
        self.terraria_installed = False
        self.tmodloader_installed = False
        
        self.setup_ui()
        self.check_installations(log_to_ui=False)
        
    def get_steam_path(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
            steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
            winreg.CloseKey(key)
            return steam_path
        except:
            return "C:\\Program Files (x86)\\Steam"

    def setup_ui(self):
        try:
            if hasattr(sys, '_MEIPASS'):
                banner_path = os.path.join(sys._MEIPASS, 'banner.jpg')
            else:
                banner_path = 'banner.jpg'
            
            if os.path.exists(banner_path):
                from PIL import Image, ImageTk
                img = Image.open(banner_path)
                img = img.resize((700, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(self.root, image=photo)
                lbl.image = photo
                lbl.pack(pady=10)
        except:
            tk.Label(self.root, text="🎮 Terraria Installer 🎮", font=("Arial", 16, "bold")).pack(pady=20)
        
        frame = ttk.LabelFrame(self.root, text="Статус", padding=10)
        frame.pack(padx=20, pady=5, fill="x")
        self.lbl_terraria = tk.Label(frame, text="Checking...", anchor="w")
        self.lbl_terraria.pack(fill="x")
        self.lbl_tmod = tk.Label(frame, text="Checking...", anchor="w")
        self.lbl_tmod.pack(fill="x")
        
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(padx=20, pady=10, fill="x")
        
        log_frame = ttk.LabelFrame(self.root, text="Лог", padding=10)
        log_frame.pack(padx=20, pady=5, fill="both", expand=True)
        self.txt_log = tk.Text(log_frame, height=8, state="disabled", font=("Consolas", 9))
        self.txt_log.pack(side="left", fill="both", expand=True)
        
        self.btn_run = tk.Button(self.root, text="🚀 Начать установку", command=self.start_thread,
                                 font=("Arial", 12, "bold"), bg="#0066cc", fg="white", height=2)
        self.btn_run.pack(padx=20, pady=10, fill="x")

    def safe_log(self, text):
        self.root.after(0, lambda: self._log_internal(text))

    def _log_internal(self, text):
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", f"[{time.strftime('%H:%M:%S')}] {text}\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    def safe_update_label(self, label, text, color):
        self.root.after(0, lambda: label.config(text=text, fg=color))

    def safe_ask_question(self, title, message):
        self.dialog_result = None
        self.root.after(0, lambda: self._show_dialog(title, message))
        while self.dialog_result is None:
            time.sleep(0.1)
            if not self.root.winfo_exists(): return 'no'
        return self.dialog_result

    def _show_dialog(self, title, message):
        self.dialog_result = messagebox.askquestion(title, message)

    def get_online_config_url(self):
        """Скачивает конфиг с GitHub и возвращает актуальную ссылку на коллекцию"""
        try:
            self.safe_log("🌍 Получение актуальной ссылки на коллекцию...")
            with urllib.request.urlopen(self.URL_APP_CONFIG) as response:
                data = json.loads(response.read().decode())
                url = data.get("steam_collection_url")
                if url:
                    self.safe_log("✅ Ссылка успешно обновлена из облака!")
                    return url
        except Exception as e:
            self.safe_log(f"⚠️ Не удалось получить ссылку с GitHub: {e}")
            self.safe_log("Использую стандартную ссылку.")
        
        return self.DEFAULT_STEAM_URL

    def launch_game_direct(self, app_id, exe_name=None):
        try:
            if exe_name and self.steam_path:
                possible_path = os.path.join(self.steam_path, "steamapps", "common", "tModLoader", exe_name)
                if os.path.exists(possible_path):
                    subprocess.Popen([possible_path], cwd=os.path.dirname(possible_path))
                    return True
            os.startfile(f'steam://rungameid/{app_id}')
            return True
        except: return False

    def download_file(self, url, dest_path):
        try:
            self.safe_log(f"☁️ Скачивание: {os.path.basename(dest_path)}...")
            with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            return True
        except Exception as e:
            self.safe_log(f"❌ Ошибка скачивания: {e}")
            return False

    def check_installations(self, log_to_ui=True):
        t_ok = False
        tm_ok = False
        if self.steam_path:
            if os.path.exists(os.path.join(self.steam_path, "steamapps", "appmanifest_105600.acf")):
                t_ok = True
                self.safe_update_label(self.lbl_terraria, "✅ Terraria: Установлена", "green")
            else:
                self.safe_update_label(self.lbl_terraria, "❌ Terraria: Не установлена", "red")

            if os.path.exists(os.path.join(self.steam_path, "steamapps", "appmanifest_1281930.acf")):
                tm_ok = True
                self.safe_update_label(self.lbl_tmod, "✅ tModLoader: Установлен", "green")
            else:
                self.safe_update_label(self.lbl_tmod, "❌ tModLoader: Не установлен", "red")
        
        self.terraria_installed = t_ok
        self.tmodloader_installed = tm_ok
        return t_ok, tm_ok

    def start_thread(self):
        self.btn_run.config(state="disabled", text="Работаю...")
        self.progress.start(10)
        threading.Thread(target=self.installation_logic, daemon=True).start()

    def installation_logic(self):
        try:
            self.safe_log("--- ЗАПУСК ---")
            self.check_installations(log_to_ui=True)
            time.sleep(1)

            # 1. Игры
            if not self.terraria_installed:
                os.startfile('steam://install/105600')
                if self.safe_ask_question("Terraria", "Нажмите Да, когда Terraria установится.") != 'yes': raise Exception("Отмена")
            
            if not self.tmodloader_installed:
                os.startfile('steam://install/1281930')
                if self.safe_ask_question("tModLoader", "Нажмите Да, когда tModLoader установится.") != 'yes': raise Exception("Отмена")

            # 2. Моды (ДИНАМИЧЕСКАЯ ССЫЛКА)
            collection_url = self.get_online_config_url() # Получаем ссылку с GitHub
            self.root.after(0, lambda: webbrowser.open(collection_url))
            
            if self.safe_ask_question("Моды", "Подпишитесь на все моды в браузере.\nЗатем нажмите Да.") != 'yes': raise Exception("Отмена")

            # 3. Инициализация
            self.safe_log("Инициализация папок...")
            self.root.after(0, lambda: self.launch_game_direct(1281930, "tModLoader.exe"))
            if self.safe_ask_question("Первый запуск", "Дождитесь меню, закройте игру и нажмите Да.") != 'yes': raise Exception("Отмена")

            # 4. Скачивание конфигов
            mods_dir = os.path.join(self.docs_path, "Mods")
            configs_dir = os.path.join(self.docs_path, "ModConfigs")
            Path(mods_dir).mkdir(parents=True, exist_ok=True)
            Path(configs_dir).mkdir(parents=True, exist_ok=True)

            self.download_file(self.URL_JSON_MODS, os.path.join(mods_dir, "enabled.json"))
            
            temp_zip = os.path.join(self.docs_path, "temp_configs.zip")
            if self.download_file(self.URL_ZIP_CONFIGS, temp_zip):
                try:
                    with zipfile.ZipFile(temp_zip, 'r') as z: z.extractall(configs_dir)
                    self.safe_log("✅ Конфиги распакованы")
                except: pass
                if os.path.exists(temp_zip): os.remove(temp_zip)

            # 5. Финал
            self.safe_log("✨ ГОТОВО! ✨")
            self.root.after(0, lambda: messagebox.showinfo("Успех", "Приятной игры!"))
            self.root.after(0, lambda: self.launch_game_direct(1281930, "tModLoader.exe"))
            self.root.after(0, lambda: self.finish_ui(True))

        except Exception as e:
            self.safe_log(f"❌: {e}")
            self.root.after(0, lambda: self.finish_ui(False))

    def finish_ui(self, success):
        self.progress.stop()
        state = "normal"
        self.btn_run.config(text="Готово (Выход)" if success else "Ошибка (Повторить)", 
                            bg="green" if success else "red", command=self.root.quit if success else self.start_thread, state=state)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        if hasattr(sys, '_MEIPASS'):
            root.iconbitmap(os.path.join(sys._MEIPASS, 'icon.ico'))
        else:
            root.iconbitmap('icon.ico')
    except: pass
    app = TerrariaInstaller(root)
    root.mainloop()