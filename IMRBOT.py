#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Infinite Magicraid Bot + Macro Editor
Version: 0.03
"""

# ============================================
# 📁 ОПРЕДЕЛЕНИЕ ПУТИ К ПРОГРАММЕ (ДОБАВИТЬ ПЕРВЫМ!)
# ============================================
import sys
from pathlib import Path

# ✅ Получаем абсолютный путь к папке, где лежит IMRBOT.py
SCRIPT_DIR = Path(__file__).parent.resolve()

def program_path(*parts):
    """Создаёт абсолютный путь относительно папки программы"""
    return SCRIPT_DIR / Path(*parts)

# ============================================
# 📦 ИМПОРТЫ
# ============================================
import os
import time
import ctypes
import keyboard
import pyautogui
import win32gui
import win32process
import psutil
import threading
import json
import traceback
import urllib.request
import urllib.error
import hashlib
import shutil
import re
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

# ============================================
# 📁 ОПРЕДЕЛЕНИЕ ПУТИ К ПРОГРАММЕ
# ============================================
# ✅ Получаем абсолютный путь к папке, где лежит IMRBOT.py
SCRIPT_DIR = Path(__file__).parent.resolve()

# ✅ Функция для создания путей относительно папки программы
def program_path(*parts):
    """Создаёт путь относительно папки программы"""
    return SCRIPT_DIR / Path(*parts)

# ============================================
# 🔢 ВЕРСИЯ ПРОГРАММЫ
# ============================================
VERSION = "0.03"

# ============================================
# 🌐 ПРОВЕРКА ОБНОВЛЕНИЙ (GitHub Raw + ИСПРАВЛЕНИЯ)
# ============================================
class UpdateChecker:
    # ✅ GitHub Raw URLs
    UPDATE_URL = "https://raw.githubusercontent.com/diablogolod1/IMRBOTPUBLICK/main/IMRBOT.py"
    VERSION_URL = "https://raw.githubusercontent.com/diablogolod1/IMRBOTPUBLICK/main/macros/version_info.json"
    
    # ✅ Пути через program_path()
    VERSION_FILE = program_path("macros", "version_info.json")
    BACKUP_FOLDER = program_path("backups")
    MAIN_FILE = program_path("IMRBOT.py")
    CACHE_FILE = program_path("macros", "update_cache.json")
    CACHE_DURATION = 3600  # Кэш на 1 час
    
    @staticmethod
    def get_local_version():
        return VERSION
    
    @staticmethod
    def _load_cache():
        """✅ Загрузка кэша версий"""
        try:
            if UpdateChecker.CACHE_FILE.exists():
                with open(UpdateChecker.CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return None
    
    @staticmethod
    def _save_cache(version):
        """✅ Сохранение версии в кэш"""
        try:
            UpdateChecker.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(UpdateChecker.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump({'version': version, 'timestamp': time.time()}, f)
        except:
            pass
    
    @staticmethod
    def get_remote_version():
        """✅ Получение версии с GitHub (с кэшированием)"""
        # ✅ Сначала проверяем кэш
        cache_data = UpdateChecker._load_cache()
        
        # ✅ ИСПРАВЛЕНО: было "if cache_" → стало "if cache_data:"
        if cache_data:
            cache_time = cache_data.get('timestamp', 0)
            cache_version = cache_data.get('version')
            if time.time() - cache_time < UpdateChecker.CACHE_DURATION:
                print(f"✅ Версия из кэша: {cache_version}")
                return cache_version
        
        # ✅ Запрашиваем с GitHub
        try:
            req = urllib.request.Request(
                UpdateChecker.VERSION_URL,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                version = data.get('version', None)
                if version:
                    UpdateChecker._save_cache(version)
                    print(f"✅ Версия с GitHub: {version}")
                return version
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("⚠️ GitHub вернул 429")
                return cache_data.get('version') if cache_data else None
            else:
                print(f"❌ Ошибка HTTP {e.code}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return cache_data.get('version') if cache_data else None
        return None
    
    @staticmethod
    def get_remote_changelog():
        try:
            req = urllib.request.Request(UpdateChecker.VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('changelog', [])
        except:
            return []
    
    @staticmethod
    def compare_versions(local, remote):
        if not local or not remote:
            return False
        try:
            local_parts = [int(x) for x in str(local).strip().split('.')]
            remote_parts = [int(x) for x in str(remote).strip().split('.')]
            max_len = max(len(local_parts), len(remote_parts))
            local_parts += [0] * (max_len - len(local_parts))
            remote_parts += [0] * (max_len - len(remote_parts))
            for l, r in zip(local_parts, remote_parts):
                if r > l:
                    return True
                elif r < l:
                    return False
            return False
        except:
            return False
    
    @staticmethod
    def download_update(callback=None):
        try:
            UpdateChecker.BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)
            temp_file = UpdateChecker.BACKUP_FOLDER / "IMRBOT_update.tmp"
            
            print(f"🔄 Загрузка: {UpdateChecker.UPDATE_URL}")
            print(f"📁 В папку: {UpdateChecker.BACKUP_FOLDER}")
            
            def report_hook(block_num, block_size, total_size):
                if callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, downloaded * 100 / total_size)
                    callback(int(percent), downloaded, total_size)
            
            req = urllib.request.Request(UpdateChecker.UPDATE_URL, headers={'User-Agent': 'Mozilla/5.0'})
            urllib.request.urlretrieve(UpdateChecker.UPDATE_URL, str(temp_file), reporthook=report_hook)
            
            if temp_file.exists() and temp_file.stat().st_size > 50000:
                try:
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        compile(f.read(), str(temp_file), 'exec')
                    print(f"✅ Файл загружен: {temp_file} ({temp_file.stat().st_size} байт)")
                    return str(temp_file)
                except SyntaxError as e:
                    print(f"❌ Ошибка синтаксиса: {e}")
                    temp_file.unlink(missing_ok=True)
                    return None
            temp_file.unlink(missing_ok=True)
            return None
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return None
    
    @staticmethod
    def apply_update(new_file, main_file=None):
        if main_file is None:
            main_file = str(UpdateChecker.MAIN_FILE)
        
        try:
            UpdateChecker.BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup = UpdateChecker.BACKUP_FOLDER / f"IMRBOT.py.backup.{timestamp}"
            
            print(f"📁 Основной файл: {main_file}")
            print(f"📁 Бэкап: {backup}")
            print(f"📁 Новый файл: {new_file}")
            
            if Path(main_file).exists():
                shutil.copy2(main_file, backup)
                print(f"✅ Бэкап создан в: {backup}")
            else:
                print(f"⚠️ Исходный файл не найден: {main_file}")
                return False
            
            shutil.copy2(new_file, main_file)
            print(f"✅ Файл обновлён: {main_file}")
            
            if Path(main_file).exists() and Path(main_file).stat().st_size > 50000:
                try:
                    with open(main_file, 'r', encoding='utf-8') as f:
                        compile(f.read(), main_file, 'exec')
                    print("✅ Синтаксис корректен, обновление успешно!")
                    if Path(new_file).exists():
                        Path(new_file).unlink()
                    UpdateChecker._cleanup_old_backups()
                    return True
                except SyntaxError as e:
                    print(f"❌ Ошибка синтаксиса: {e}")
                    if backup.exists():
                        shutil.copy2(backup, main_file)
                        print("✅ Выполнен откат")
                    return False
            
            print("❌ Файл не прошёл проверку")
            if backup.exists():
                shutil.copy2(backup, main_file)
            return False
        except Exception as e:
            print(f"❌ Ошибка применения: {e}")
            return False
    
    @staticmethod
    def _cleanup_old_backups(keep_count=5):
        try:
            backups = sorted(
                UpdateChecker.BACKUP_FOLDER.glob("IMRBOT.py.backup.*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            for old_backup in backups[keep_count:]:
                old_backup.unlink()
        except:
            pass
    
    @staticmethod
    def download_update(callback=None):
        """✅ Скачивание обновления с прогрессом и ОТЛАДКОЙ"""
        try:
            # ✅ Создаём папку для бэкапов
            UpdateChecker.BACKUP_FOLDER.mkdir(exist_ok=True)
            temp_file = UpdateChecker.BACKUP_FOLDER / "IMRBOT_update.tmp"
            
            print(f"🔄 Начинаем загрузку с: {UpdateChecker.UPDATE_URL}")
            
            def report_hook(block_num, block_size, total_size):
                if callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, downloaded * 100 / total_size)
                    callback(int(percent), downloaded, total_size)
                if block_num % 10 == 0:
                    print(f"📥 Загрузка: {block_num * block_size} байт")
            
            req = urllib.request.Request(
                UpdateChecker.UPDATE_URL,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            urllib.request.urlretrieve(
                UpdateChecker.UPDATE_URL,
                str(temp_file),
                reporthook=report_hook
            )
            
            # ✅ Проверка размера файла
            if temp_file.exists():
                file_size = temp_file.stat().st_size
                print(f"✅ Файл загружен: {file_size} байт")
                
                if file_size > 50000:  # Минимум 50KB для Python файла
                    # ✅ Проверка синтаксиса
                    try:
                        with open(temp_file, 'r', encoding='utf-8') as f:
                            compile(f.read(), str(temp_file), 'exec')
                        print("✅ Синтаксис файла корректен")
                        return str(temp_file)
                    except SyntaxError as e:
                        print(f"❌ Ошибка синтаксиса: {e}")
                        temp_file.unlink(missing_ok=True)
                        return None
                else:
                    print(f"❌ Файл слишком маленький: {file_size} байт")
                    temp_file.unlink(missing_ok=True)
                    return None
            else:
                print("❌ Файл не был создан")
                return None
                
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP ошибка {e.code}: {e}")
            if e.code == 429:
                print("⚠️ GitHub блокирует запросы (429). Повторите через 5 минут.")
            return None
        except urllib.error.URLError as e:
            print(f"❌ Ошибка подключения: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка загрузки обновления: {e}")
            print(traceback.format_exc())
            return None
    
    @staticmethod
    def apply_update(new_file, main_file=None):
        """✅ Применение обновления с бэкапом и откатом"""
        if main_file is None:
            main_file = UpdateChecker.MAIN_FILE
        
        try:
            UpdateChecker.BACKUP_FOLDER.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup = UpdateChecker.BACKUP_FOLDER / f"{main_file}.backup.{timestamp}"
            
            print(f"📁 Создаём бэкап: {backup}")
            
            if Path(main_file).exists():
                shutil.copy2(main_file, backup)
                print(f"✅ Бэкап создан: {backup}")
            else:
                print(f"⚠️ Исходный файл не найден: {main_file}")
            
            print(f"📁 Копируем новый файл: {new_file} → {main_file}")
            shutil.copy2(new_file, main_file)  # ✅ copy2 вместо move
            
            if Path(main_file).exists() and Path(main_file).stat().st_size > 50000:
                try:
                    with open(main_file, 'r', encoding='utf-8') as f:
                        compile(f.read(), main_file, 'exec')
                    print("✅ Обновление применено успешно")
                    UpdateChecker._cleanup_old_backups()
                    
                    # ✅ Удаляем временный файл
                    if Path(new_file).exists():
                        Path(new_file).unlink()
                    
                    return True
                except SyntaxError as e:
                    print(f"❌ Ошибка синтаксиса: {e}")
                    if backup.exists():
                        shutil.copy2(backup, main_file)
                        print("✅ Выполнен откат")
                    return False
            
            print("❌ Файл не прошёл проверку размера")
            if backup.exists():
                shutil.copy2(backup, main_file)
            return False
            
        except Exception as e:
            print(f"❌ Ошибка применения обновления: {e}")
            print(traceback.format_exc())
            try:
                backups = list(UpdateChecker.BACKUP_FOLDER.glob(f"{main_file}.backup.*"))
                if backups:
                    latest = max(backups, key=lambda p: p.stat().st_mtime)
                    shutil.copy2(latest, main_file)
                    print(f"✅ Выполнен аварийный откат: {latest}")
            except:
                pass
            return False
    
    @staticmethod
    def _cleanup_old_backups(keep_count=5):
        """✅ Удаление старых бэкапов"""
        try:
            backups = sorted(
                UpdateChecker.BACKUP_FOLDER.glob(f"{UpdateChecker.MAIN_FILE}.backup.*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            for old_backup in backups[keep_count:]:
                old_backup.unlink()
                print(f"🗑️ Удалён старый бэкап: {old_backup.name}")
        except:
            pass


# ============================================
# 🖥️ ОТКЛЮЧЕНИЕ МАСШТАБИРОВАНИЯ WINDOWS
# ============================================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

# ============================================
# 📦 OCR ПРОВЕРКА
# ============================================
OCR_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    print("⚠️ pytesseract не установлен. Поиск текста будет недоступен.")
    print("   Установите: pip install pytesseract pillow")


# ============================================
# 📦 МЕНЕДЖЕР МАКРОСОВ
# ============================================
class MacroRecorder:
    def __init__(self):
        self.recording = False
        self.events = []
        self.start_time = None
        self.last_click_time = None
        self.hwnd = None
        self.mouse_thread = None
        self.stop_thread = False
    
    def start_recording(self, hwnd):
        try:
            self.recording = True
            self.events = []
            self.start_time = time.time()
            self.last_click_time = time.time()
            self.hwnd = hwnd
            self.stop_thread = False
            print(f"🔴 ЗАПИСЬ МАКРОСА НАЧАТА (окно: {hwnd})")
            self.mouse_thread = threading.Thread(target=self._mouse_listener_loop, daemon=True)
            self.mouse_thread.start()
        except Exception as e:
            print(f"❌ Ошибка запуска записи макроса: {e}")
            self.recording = False
    
    def _mouse_listener_loop(self):
        try:
            import mouse
            last_state = False
            while not self.stop_thread:
                try:
                    current_state = mouse.is_pressed('left')
                    if current_state and not last_state and self.recording and self.hwnd:
                        x, y = pyautogui.position()
                        self.record_click(x, y)
                    last_state = current_state
                    time.sleep(0.05)
                except Exception as e:
                    time.sleep(0.1)
        except ImportError:
            print("❌ Библиотека mouse не установлена! pip install mouse")
        except Exception as e:
            print(f"Критическая ошибка в записи макроса: {e}")
    
    def stop_recording(self):
        try:
            self.recording = False
            self.stop_thread = True
            if self.mouse_thread and self.mouse_thread.is_alive():
                self.mouse_thread.join(timeout=2.0)
            print(f"⏹️ ЗАПИСЬ МАКРОСА ОСТАНОВЛЕНА (записано кликов: {len(self.events)})")
        except Exception as e:
            print(f"❌ Ошибка остановки записи: {e}")
    
    def record_click(self, x, y):
        try:
            if not self.recording or not self.hwnd:
                return
            current_time = time.time()
            time_diff = current_time - self.last_click_time
            self.last_click_time = current_time
            rect = win32gui.GetClientRect(self.hwnd)
            w, h = rect[2], rect[3]
            left, top = win32gui.ClientToScreen(self.hwnd, (0, 0))
            rx = round((x - left) / w, 2) if w > 0 else 0.5
            ry = round((y - top) / h, 2) if h > 0 else 0.5
            self.events.append({'time': time_diff, 'x': rx, 'y': ry})
        except Exception as e:
            print(f"❌ Ошибка записи клика: {e}")
    
    def save_macro(self, filename=None, custom_path=None):
        try:
            if not self.events:
                return None
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"macro_{timestamp}.txt"
            filepath = Path(custom_path) / filename if custom_path else Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# Макрос записан автоматически\n")
                for i, event in enumerate(self.events):
                    f.write(f"CLICK:{event['x']},{event['y']}\n")
                    if i < len(self.events) - 1 and event['time'] > 0.1:
                        f.write(f"WAIT:{event['time']:.2f}\n")
            return str(filepath.absolute())
        except Exception as e:
            print(f"❌ Ошибка сохранения макроса: {e}")
            return None


# ============================================
# 🖱️ ЗАПИСЬ ВЫБОРА СЕРВЕРА
# ============================================
class ServerSelectorRecorder:
    def __init__(self):
        self.recording = False
        self.events = []
        self.hwnd = None
        self.mouse_thread = None
        self.stop_thread = False
        self.start_time = None
        self.last_event_time = None
        self.event_lock = threading.Lock()
        self.is_button_pressed = False
        self.drag_threshold = 0.01
        self.sample_rate = 0.015
    
    def start_recording(self, hwnd):
        try:
            self.recording = True
            self.events = []
            self.hwnd = hwnd
            self.stop_thread = False
            self.start_time = time.time()
            self.last_event_time = self.start_time
            self.is_button_pressed = False
            self.mouse_thread = threading.Thread(target=self._mouse_listener_loop, daemon=True)
            self.mouse_thread.start()
        except Exception as e:
            print(f"❌ Ошибка запуска записи: {e}")
            self.recording = False
    
    def _mouse_listener_loop(self):
        try:
            import mouse
            last_button_state = False
            last_x, last_y = pyautogui.position()
            while not self.stop_thread:
                try:
                    current_time = time.time()
                    current_x, current_y = pyautogui.position()
                    current_button_state = mouse.is_pressed('left')
                    if not self.recording:
                        time.sleep(self.sample_rate)
                        continue
                    try:
                        rect = win32gui.GetClientRect(self.hwnd)
                        w, h = rect[2], rect[3]
                        left, top = win32gui.ClientToScreen(self.hwnd, (0, 0))
                        rx = (current_x - left) / w if w > 0 else 0.5
                        ry = (current_y - top) / h if h > 0 else 0.5
                    except:
                        rx, ry = 0.5, 0.5
                    time_diff = current_time - self.last_event_time
                    if current_button_state and not last_button_state:
                        self.is_button_pressed = True
                        self._add_event('MOUSE_DOWN', rx, ry, time_diff)
                    elif self.is_button_pressed and current_button_state:
                        dx = abs(rx - last_x) if isinstance(last_x, float) else 1.0
                        dy = abs(ry - last_y) if isinstance(last_y, float) else 1.0
                        if dx > self.drag_threshold or dy > self.drag_threshold:
                            self._add_event('MOUSE_DRAG', rx, ry, time_diff)
                            last_x, last_y = rx, ry
                    elif not current_button_state and last_button_state:
                        self._add_event('MOUSE_UP', rx, ry, time_diff)
                        self.is_button_pressed = False
                    last_button_state = current_button_state
                    time.sleep(self.sample_rate)
                except:
                    time.sleep(self.sample_rate)
        except ImportError:
            print("❌ Библиотека mouse не установлена! pip install mouse")
    
    def _add_event(self, event_type, x, y, time_diff):
        try:
            with self.event_lock:
                self.events.append({'type': event_type, 'x': round(x, 4), 'y': round(y, 4), 'time': time_diff})
                self.last_event_time = time.time()
        except:
            pass
    
    def stop_recording(self):
        try:
            self.recording = False
            self.stop_thread = True
            if self.mouse_thread and self.mouse_thread.is_alive():
                self.mouse_thread.join(timeout=2.0)
        except:
            pass
    
    def save_server_macro(self, filepath):
        try:
            if not self.events:
                return None
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# Макрос выбора сервера (ЗАЖАТИЕ + ПЕРЕТАСКИВАНИЕ)\n")
                for event in self.events:
                    f.write(f"{event['type']}:{event['x']},{event['y']},{event['time']:.3f}\n")
            return filepath
        except:
            return None
    
    def load_server_macro(self, filepath):
        try:
            if not os.path.exists(filepath):
                return []
            events = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if line.startswith('MOUSE_DOWN:'):
                        parts = line[11:].split(',')
                        if len(parts) >= 3:
                            events.append({'type': 'MOUSE_DOWN', 'x': float(parts[0]), 'y': float(parts[1]), 'time': float(parts[2])})
                    elif line.startswith('MOUSE_DRAG:'):
                        parts = line[11:].split(',')
                        if len(parts) >= 3:
                            events.append({'type': 'MOUSE_DRAG', 'x': float(parts[0]), 'y': float(parts[1]), 'time': float(parts[2])})
                    elif line.startswith('MOUSE_UP:'):
                        parts = line[9:].split(',')
                        if len(parts) >= 3:
                            events.append({'type': 'MOUSE_UP', 'x': float(parts[0]), 'y': float(parts[1]), 'time': float(parts[2])})
            return events
        except:
            return []
    
    def is_recorded(self):
        return len(self.events) > 0


# ============================================
# 🔍 ПОИСК ТЕКСТА ЧЕРЕЗ TESSERACT OCR
# ============================================
class TextFinder:
    def __init__(self):
        self.ocr_available = OCR_AVAILABLE
        self._init_tesseract()
    
    def _init_tesseract(self):
        try:
            import pytesseract
            from PIL import Image
            possible_paths = [r'C:\Program Files\Tesseract-OCR\tesseract.exe', r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe']
            try:
                pytesseract.get_tesseract_version()
                self.ocr_available = True
            except:
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        try:
                            pytesseract.get_tesseract_version()
                            self.ocr_available = True
                            break
                        except:
                            continue
            self.pytesseract = pytesseract
            self.Image = Image
        except ImportError:
            self.ocr_available = False
    
    def find_text_on_screen(self, search_text, region=None, timeout=5, confidence=0.5, running_flag=None, single_attempt=False):
        if not self.ocr_available:
            return None
        start_time = time.time()
        while time.time() - start_time < timeout:
            if running_flag is not None and not running_flag:
                return None
            try:
                if region:
                    screenshot = pyautogui.screenshot(region=region)
                    offset_x, offset_y = region[0], region[1]
                else:
                    screenshot = pyautogui.screenshot()
                    offset_x, offset_y = 0, 0
                custom_config = r'--oem 3 --psm 11 -l rus+eng'
                data = self.pytesseract.image_to_data(screenshot, config=custom_config, output_type=self.pytesseract.Output.DICT)
                for i, text in enumerate(data['text']):
                    if text.strip().upper() == search_text.upper():
                        conf = int(data['conf'][i])
                        if conf > confidence * 100:
                            x = offset_x + data['left'][i] + data['width'][i] // 2
                            y = offset_y + data['top'][i] + data['height'][i] // 2
                            return (x, y, text, conf)
            except:
                pass
            if single_attempt:
                break
            time.sleep(0.3)
        return None


# ============================================
# 🖼️ ПОИСК ИЗОБРАЖЕНИЙ
# ============================================
class ImageFinder:
    def __init__(self):
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        self.custom_image_folder = None
    
    def set_custom_folder(self, folder_path):
        if folder_path and os.path.exists(folder_path):
            self.custom_image_folder = Path(folder_path)
            return True
        return False
    
    def get_image_folder(self):
        if self.custom_image_folder and self.custom_image_folder.exists():
            return self.custom_image_folder
        return self.templates_dir
    
    def find_image_on_screen(self, image_name, region=None, timeout=5, confidence=0.8, running_flag=None, single_attempt=False):
        folder = self.get_image_folder()
        template_path = folder / f"{image_name}.png"
        if not template_path.exists():
            template_path = folder / image_name
            if not template_path.exists():
                return None
        start_time = time.time()
        while time.time() - start_time < timeout:
            if running_flag is not None and not running_flag:
                return None
            try:
                import cv2
                import numpy as np
                template = cv2.imread(str(template_path))
                if template is None:
                    return None
                screenshot = pyautogui.screenshot()
                screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                if region:
                    screenshot_cv = screenshot_cv[region[1]:region[1]+region[3], region[0]:region[0]+region[2]]
                result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val >= confidence:
                    h, w = template.shape[:2]
                    x = region[0] + max_loc[0] + w // 2 if region else max_loc[0] + w // 2
                    y = region[1] + max_loc[1] + h // 2 if region else max_loc[1] + h // 2
                    return (x, y, image_name, max_val)
            except:
                pass
            if single_attempt:
                break
            time.sleep(0.3)
        return None
    
    def get_available_templates(self):
        templates = []
        folder = self.get_image_folder()
        if folder.exists():
            for f in folder.glob('*.png'):
                templates.append(f.stem)
            for f in folder.glob('*.jpg'):
                templates.append(f.stem)
        return sorted(templates)
    
    def get_folder_path(self):
        return str(self.get_image_folder().absolute())


# ============================================
# 🤖 РАБОЧИЙ КЛАСС БОТА
# ============================================
class BotWorker(QObject):
    finished = pyqtSignal(str)
    log_msg = pyqtSignal(str)
    update_acc_label = pyqtSignal(str)
    update_current_line = pyqtSignal(int)
    
    def __init__(self, accounts, active_macro=None, run_macro_only=False,
                 use_server_selection=False, server_macro_path=None, 
                 current_email="", current_password="", image_folder_path=None):
        super().__init__()
        self.accounts = accounts
        self.running = True
        self.paused = False
        self.text_finder = TextFinder()
        self.image_finder = ImageFinder()
        if image_folder_path:
            self.image_finder.set_custom_folder(image_folder_path)
        self.active_macro = active_macro
        self.is_macro_only_mode = run_macro_only
        self.use_server_selection = use_server_selection
        self.server_macro_path = server_macro_path
        self.current_email = current_email
        self.current_password = current_password
        self.hwnd = None
        self.is_running = False
        self.current_line = 0
        self.pause_event = threading.Event()
        self.pause_event.set()
    
    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_event.clear()
            self.log_msg.emit("⏸️ ПАУЗА")
        else:
            self.pause_event.set()
            self.log_msg.emit("▶️ ПРОДОЛЖЕНИЕ")
    
    def find_game_hwnd(self):
        hwnds = []
        def callback(hwnd, lparam):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = psutil.Process(pid)
                    if proc.name().lower() == "infinitemagicraid.exe":
                        hwnds.append(hwnd)
            except:
                pass
            return True
        win32gui.EnumWindows(callback, 0)
        if hwnds:
            return hwnds[0]
        return None
    
    def get_window_region(self, hwnd):
        try:
            rect = win32gui.GetClientRect(hwnd)
            w, h = rect[2], rect[3]
            left, top = win32gui.ClientToScreen(hwnd, (0, 0))
            return (left, top, w, h), w, h
        except:
            return ((0, 0, 800, 600), 800, 600)
    
    def absolute_click(self, hwnd, rx, ry, delay=0.5):
        try:
            if not self.running:
                return False
            region, w, h = self.get_window_region(hwnd)
            left, top = region[0], region[1]
            tx = left + int(rx * w)
            ty = top + int(ry * h)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.3)
            pyautogui.moveTo(tx, ty, duration=0.2)
            time.sleep(0.1)
            pyautogui.mouseDown(tx, ty, button='left')
            time.sleep(0.1)
            pyautogui.mouseUp(tx, ty, button='left')
            time.sleep(delay)
            return True
        except:
            return False
    
    def move_cursor_to(self, hwnd, rx, ry, delay=0.3):
        try:
            if not self.running:
                return False
            region, w, h = self.get_window_region(hwnd)
            left, top = region[0], region[1]
            tx = left + int(rx * w)
            ty = top + int(ry * h)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
            pyautogui.moveTo(tx, ty, duration=0.3)
            time.sleep(delay)
            return True
        except:
            return False
    
    def execute_server_macro(self, hwnd):
        try:
            if not self.use_server_selection or not self.server_macro_path:
                return
            if not os.path.exists(self.server_macro_path):
                self.log_msg.emit("Макрос выбора сервера не найден")
                return
            events = self._load_server_macro(self.server_macro_path)
            if not events:
                return
            for event in events:
                if not self.running:
                    return
                self.pause_event.wait(timeout=0.1)
                if event['time'] > 0.005:
                    time.sleep(min(event['time'], 0.5))
                if event['type'] == 'MOUSE_DOWN':
                    self._mouse_down(hwnd, event['x'], event['y'])
                elif event['type'] == 'MOUSE_DRAG':
                    self._move_mouse(hwnd, event['x'], event['y'], duration=0)
                elif event['type'] == 'MOUSE_UP':
                    self._mouse_up(hwnd, event['x'], event['y'])
        except Exception as e:
            self.log_msg.emit(f"❌ Ошибка макроса сервера: {e}")
    
    def _load_server_macro(self, filepath):
        try:
            events = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if line.startswith('MOUSE_DOWN:'):
                        parts = line[11:].split(',')
                        if len(parts) >= 3:
                            events.append({'type': 'MOUSE_DOWN', 'x': float(parts[0]), 'y': float(parts[1]), 'time': float(parts[2])})
                    elif line.startswith('MOUSE_DRAG:'):
                        parts = line[11:].split(',')
                        if len(parts) >= 3:
                            events.append({'type': 'MOUSE_DRAG', 'x': float(parts[0]), 'y': float(parts[1]), 'time': float(parts[2])})
                    elif line.startswith('MOUSE_UP:'):
                        parts = line[9:].split(',')
                        if len(parts) >= 3:
                            events.append({'type': 'MOUSE_UP', 'x': float(parts[0]), 'y': float(parts[1]), 'time': float(parts[2])})
            return events
        except:
            return []
    
    def _move_mouse(self, hwnd, rx, ry, duration=0):
        try:
            region, w, h = self.get_window_region(hwnd)
            left, top = region[0], region[1]
            tx = left + int(rx * w)
            ty = top + int(ry * h)
            pyautogui.moveTo(tx, ty, duration=duration)
        except:
            pass
    
    def _mouse_down(self, hwnd, rx, ry):
        try:
            region, w, h = self.get_window_region(hwnd)
            left, top = region[0], region[1]
            tx = left + int(rx * w)
            ty = top + int(ry * h)
            win32gui.SetForegroundWindow(hwnd)
            pyautogui.mouseDown(tx, ty, button='left')
        except:
            pass
    
    def _mouse_up(self, hwnd, rx, ry):
        try:
            region, w, h = self.get_window_region(hwnd)
            left, top = region[0], region[1]
            tx = left + int(rx * w)
            ty = top + int(ry * h)
            pyautogui.mouseUp(tx, ty, button='left')
        except:
            pass
    
    def run_authorization(self, hwnd, email, password):
        try:
            self.log_msg.emit("\n=== АВТОРИЗАЦИЯ ===")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)
            if not self.running:
                return False
            self.log_msg.emit("Выход из текущего аккаунта...")
            self.absolute_click(hwnd, 0.50, 0.50, delay=1.0)
            if not self.running:
                return False
            self.absolute_click(hwnd, 0.97, 0.14, delay=1.0)
            if not self.running:
                return False
            self.absolute_click(hwnd, 0.50, 0.50, delay=1.0)
            elapsed = 0
            while elapsed < 3 and self.running:
                time.sleep(0.5)
                elapsed += 0.5
            if not self.running:
                return False
            self.log_msg.emit("Авторизация...")
            win32gui.SetForegroundWindow(hwnd)
            self.absolute_click(hwnd, 0.71, 0.88, delay=1.0)
            if not self.running:
                return False
            elapsed = 0
            while elapsed < 2 and self.running:
                time.sleep(0.5)
                elapsed += 0.5
            if not self.running:
                return False
            self.absolute_click(hwnd, 0.49, 0.36, delay=0.5)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.3)
            if not self.running:
                return False
            self.log_msg.emit(f"   Ввод email: {email[:5]}***")
            pyautogui.write(email, interval=0.02)
            if not self.running:
                return False
            self.absolute_click(hwnd, 0.49, 0.44, delay=0.5)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.3)
            if not self.running:
                return False
            self.log_msg.emit(f"   Ввод пароля: {password[:3]}***")
            pyautogui.write(password, interval=0.02)
            if not self.running:
                return False
            self.absolute_click(hwnd, 0.49, 0.72, delay=0.5)
            if self.use_server_selection:
                elapsed = 0
                while elapsed < 2 and self.running:
                    time.sleep(0.5)
                    elapsed += 0.5
                if self.running:
                    self.execute_server_macro(hwnd)
            if not self.running:
                return False
            self.absolute_click(hwnd, 0.49, 0.79, delay=0.5)
            time.sleep(2)
            self.log_msg.emit("Загрузка (15 сек)...")
            elapsed = 0
            while elapsed < 15 and self.running:
                time.sleep(0.5)
                elapsed += 0.5
            return True
        except Exception as e:
            self.log_msg.emit(f"❌ Ошибка авторизации: {e}")
            return False
    
    def run_macro_only(self, hwnd):
        try:
            self.log_msg.emit("\n=== ЗАПУСК ТОЛЬКО МАКРОСА ===")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)
            if not self.running:
                return
            if self.active_macro:
                self.log_msg.emit("📜 Запуск макроса...")
                self.run_macro(hwnd, self.active_macro)
            else:
                self.log_msg.emit("⚠️ Макрос не выбран!")
        except Exception as e:
            self.log_msg.emit(f"❌ Ошибка запуска макроса: {e}")
    
    def run_macro(self, hwnd, macro_content):
        try:
            self.log_msg.emit("\n=== ВЫПОЛНЕНИЕ МАКРОСА ===")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)
            if not self.running:
                return False
            lines = macro_content.split('\n')
            is_infinite_loop = False
            if lines:
                first_line = lines[0].strip()
                last_line = lines[-1].strip()
                if first_line.startswith('НАЧАЛО_ЦИКЛА') and last_line == 'КОНЕЦ_ЦИКЛА':
                    try:
                        loop_count = int(first_line.split('(')[1].split(')')[0])
                        if loop_count == 0:
                            is_infinite_loop = True
                            self.log_msg.emit("🔄 Обнаружен БЕСКОНЕЧНЫЙ цикл (0)")
                    except:
                        pass
            if is_infinite_loop:
                while self.running:
                    self.pause_event.wait(timeout=0.1)
                    if not self._execute_macro_lines(hwnd, lines):
                        break
                    if not self.running:
                        break
                    self.log_msg.emit("🔄 Цикл завершён, начинаем заново...")
                    time.sleep(1)
            else:
                self._execute_macro_lines(hwnd, lines)
            return True
        except Exception as e:
            self.log_msg.emit(f"❌ Ошибка выполнения макроса: {e}")
            return False
    
    def _execute_macro_lines(self, hwnd, lines):
        try:
            i = 0
            loop_stack = []
            while i < len(lines):
                if not self.running:
                    self.log_msg.emit("⛔ Выполнение прервано пользователем")
                    return False
                self.pause_event.wait(timeout=0.1)
                if not self.running:
                    return False
                line = lines[i].strip()
                self.current_line = i + 1
                self.update_current_line.emit(self.current_line)
                if line:
                    self.log_msg.emit(f"[{i+1}] {line[:50]}")
                    if line.startswith('НАЧАЛО_ЦИКЛА'):
                        try:
                            loop_count = int(line.split('(')[1].split(')')[0])
                            loop_stack.append({'start_index': i, 'count': loop_count, 'current': 0})
                            self.log_msg.emit(f"🔄 Начало цикла: {loop_count} повторений")
                        except:
                            self.log_msg.emit("⚠️ Ошибка parsing цикла")
                    elif line == 'КОНЕЦ_ЦИКЛА':
                        if loop_stack:
                            current_loop = loop_stack[-1]
                            current_loop['current'] += 1
                            if current_loop['count'] == 0 or current_loop['current'] < current_loop['count']:
                                i = current_loop['start_index']
                                self.log_msg.emit(f"🔄 Повтор цикла ({current_loop['current']}/{current_loop['count'] if current_loop['count'] > 0 else '∞'})")
                                continue
                            else:
                                loop_stack.pop()
                                self.log_msg.emit("✅ Цикл завершён")
                    else:
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.1)
                        if not self.running:
                            return False
                        self.pause_event.set()
                        self.execute_macro_command(hwnd, line, i + 1)
                        if not self.running:
                            return False
                        time.sleep(0.2)
                i += 1
            return True
        except Exception as e:
            self.log_msg.emit(f"❌ Ошибка выполнения строк макроса: {e}")
            return False
    
    def execute_macro_command(self, hwnd, command, line_num):
        try:
            command = command.strip()
            if not command or command.startswith('#'):
                return True
            
            if not self.running:
                return False
            
            # ============================================
            # 🔍 ETextWait - Ждать текст (НОВАЯ ЛОГИКА)
            # ============================================
            elif command.startswith('ETextWait('):
                try:
                    params = command[10:-1].split(',')
                    if len(params) >= 3:
                        interval = float(params[0].strip())
                        timeout = float(params[1].strip())
                        search_text = params[2].strip().strip('"').strip("'")
                    else:
                        self.log_msg.emit("✗ ETextWait: неверный формат")
                        return False
                    
                    self.log_msg.emit(f'⏳ ETextWait: интервал={interval}с, таймаут={timeout}с, текст="{search_text}"')
                    region, w, h = self.get_window_region(hwnd)
                    search_region = (region[0], region[1], region[2], region[3])
                    
                    start_time = time.time()
                    found = False
                    attempt_count = 0
                    result_coords = None
                    
                    # 🔄 ЭТАП 1: Цикл поиска
                    while time.time() - start_time < timeout and self.running:
                        if not self.running:
                            break
                        
                        attempt_count += 1
                        self.pause_event.wait(timeout=min(0.1, interval))
                        
                        if not self.running:
                            break
                        
                        result = self.text_finder.find_text_on_screen(
                            search_text, 
                            region=search_region, 
                            timeout=1.0, 
                            running_flag=self.running, 
                            single_attempt=True
                        )
                        
                        if result:
                            x, y, text, conf = result
                            rx = (x - region[0]) / w
                            ry = (y - region[1]) / h
                            result_coords = (rx, ry, text)
                            self.log_msg.emit(f"✓ Текст '{text}' найден! (попытка #{attempt_count})")
                            self.log_msg.emit(f"📍 Координаты: ({rx:.4f}, {ry:.4f})")
                            found = True
                            break  # ⚠️ СРАЗУ ВЫХОДИМ ИЗ ЦИКЛА
                        
                        if attempt_count % 10 == 0:
                            elapsed = time.time() - start_time
                            self.log_msg.emit(f"⏳ Поиск: попытка #{attempt_count} ({elapsed:.1f}с из {timeout}с)...")
                        
                        time.sleep(interval)  # ✅ Ждём перед следующей попыткой
                    
                    # ✅ ЭТАП 2: Клик по сохранённым координатам (ПОСЛЕ цикла!)
                    if found and result_coords:
                        rx, ry, text = result_coords
                        self.log_msg.emit("🔄 Выполняю клик...")
                        time.sleep(0.3)  # Небольшая пауза перед кликом
                        self.absolute_click(hwnd, rx, ry, delay=0.5)
                        self.log_msg.emit(f"✅ Клик выполнен по ({rx:.4f}, {ry:.4f})")
                    elif not found and self.running:
                        self.log_msg.emit(f"⏰ Таймаут ETextWait ({timeout}с, попыток: {attempt_count})")
                    
                    self.pause_event.set()
                    return True
                    
                except Exception as e:
                    self.log_msg.emit(f"✗ Ошибка ETextWait: {e}")
                    return False
            
            # ============================================
            # 🖼️ EIMGWait - Ждать изображение (НОВАЯ ЛОГИКА)
            # ============================================
            elif command.startswith('EIMGWait('):
                try:
                    params = command[9:-1].split(',')
                    if len(params) >= 3:
                        interval = float(params[0].strip())
                        timeout = float(params[1].strip())
                        image_name = params[2].strip().strip('"').strip("'")
                    else:
                        self.log_msg.emit("✗ EIMGWait: неверный формат")
                        return False
                    
                    if not image_name:
                        self.log_msg.emit("✗ EIMGWait: не указано имя изображения")
                        return False
                    
                    self.log_msg.emit(f'⏳ EIMGWait: интервал={interval}с, таймаут={timeout}с, изображение="{image_name}"')
                    region, w, h = self.get_window_region(hwnd)
                    search_region = (region[0], region[1], region[2], region[3])
                    
                    start_time = time.time()
                    found = False
                    attempt_count = 0
                    result_coords = None
                    
                    # 🔄 ЭТАП 1: Цикл поиска
                    while time.time() - start_time < timeout and self.running:
                        if not self.running:
                            break
                        
                        attempt_count += 1
                        self.pause_event.wait(timeout=min(0.1, interval))
                        
                        if not self.running:
                            break
                        
                        result = self.image_finder.find_image_on_screen(
                            image_name, 
                            region=search_region, 
                            timeout=1.0, 
                            running_flag=self.running, 
                            single_attempt=True
                        )
                        
                        if result:
                            x, y, name, conf = result
                            rx = (x - region[0]) / w
                            ry = (y - region[1]) / h
                            result_coords = (rx, ry, name)
                            self.log_msg.emit(f"✓ Изображение '{name}' найдено! (попытка #{attempt_count})")
                            self.log_msg.emit(f"📍 Координаты: ({rx:.4f}, {ry:.4f})")
                            found = True
                            break  # ⚠️ СРАЗУ ВЫХОДИМ ИЗ ЦИКЛА
                        
                        if attempt_count % 10 == 0:
                            elapsed = time.time() - start_time
                            self.log_msg.emit(f"⏳ Поиск: попытка #{attempt_count} ({elapsed:.1f}с из {timeout}с)...")
                        
                        time.sleep(interval)  # ✅ Ждём перед следующей попыткой
                    
                    # ✅ ЭТАП 2: Клик по сохранённым координатам (ПОСЛЕ цикла!)
                    if found and result_coords:
                        rx, ry, name = result_coords
                        self.log_msg.emit("🔄 Выполняю клик...")
                        time.sleep(0.3)  # Небольшая пауза перед кликом
                        self.absolute_click(hwnd, rx, ry, delay=0.5)
                        self.log_msg.emit(f"✅ Клик выполнен по ({rx:.4f}, {ry:.4f})")
                    elif not found and self.running:
                        self.log_msg.emit(f"⏰ Таймаут EIMGWait ({timeout}с, попыток: {attempt_count})")
                    
                    self.pause_event.set()
                    return True
                    
                except Exception as e:
                    self.log_msg.emit(f"✗ Ошибка EIMGWait: {e}")
                    return False
            
            # ============================================
            # ОСТАЛЬНЫЕ КОМАНДЫ (без изменений)
            # ============================================
            elif command.startswith('CLICK:'):
                coords = command[6:].strip()
                try:
                    rx, ry = map(float, coords.split(','))
                    if not self.running:
                        return False
                    result = self.absolute_click(hwnd, rx, ry, delay=0.5)
                    return result
                except Exception as e:
                    self.log_msg.emit(f"✗ Ошибка координат: {coords} - {e}")
                    return False
            
            elif command.startswith('WAIT:'):
                try:
                    seconds = float(command[5:].strip())
                    self.log_msg.emit(f"⏳ Ожидание: {seconds} сек...")
                    elapsed = 0
                    interval = 0.5
                    while elapsed < seconds and self.running:
                        self.pause_event.wait(timeout=min(interval, seconds - elapsed))
                        elapsed += interval
                        if not self.running:
                            break
                    return True
                except Exception as e:
                    self.log_msg.emit(f"✗ Ошибка времени: {command} - {e}")
                    return False
            
            elif command.startswith('EText:'):
                text_to_type = command[6:].strip()
                if text_to_type == '{EMAIL}':
                    text_to_type = self.current_email
                    self.log_msg.emit("⌨️ Ввод EMAIL аккаунта")
                elif text_to_type == '{PASSWORD}':
                    text_to_type = self.current_password
                    self.log_msg.emit("⌨️ Ввод PASSWORD аккаунта")
                else:
                    self.log_msg.emit(f"⌨️ Ввод текста: {text_to_type[:20]}...")
                pyautogui.write(text_to_type, interval=0.05)
                return True
            
            elif command.startswith('IMG:'):
                image_name = command[4:].strip()
                self.log_msg.emit(f"🖼️ Поиск изображения: {image_name}...")
                region, w, h = self.get_window_region(hwnd)
                search_region = (region[0], region[1], region[2], region[3])
                result = None
                start_time = time.time()
                while time.time() - start_time < 5 and self.running:
                    self.pause_event.wait(timeout=0.1)
                    if not self.running:
                        return False
                    result = self.image_finder.find_image_on_screen(
                        image_name, 
                        region=search_region, 
                        timeout=0.5, 
                        running_flag=self.running, 
                        single_attempt=True
                    )
                    if result:
                        break
                    time.sleep(0.3)
                
                if result:
                    x, y, name, conf = result
                    rx = (x - region[0]) / w
                    ry = (y - region[1]) / h
                    self.log_msg.emit(f"✓ Изображение '{name}' найдено!")
                    self.absolute_click(hwnd, rx, ry, delay=0.5)
                    return True
                else:
                    self.log_msg.emit(f"✗ Изображение '{image_name}' не найдено")
                    return False
            
            elif command.startswith('TEXT:'):
                search_text = command[5:].strip()
                self.log_msg.emit(f"🔍 Поиск текста: '{search_text}' (курсор без клика)...")
                region, w, h = self.get_window_region(hwnd)
                search_region = (region[0], region[1], region[2], region[3])
                result = None
                start_time = time.time()
                while time.time() - start_time < 5 and self.running:
                    self.pause_event.wait(timeout=0.1)
                    if not self.running:
                        return False
                    result = self.text_finder.find_text_on_screen(
                        search_text, 
                        region=search_region, 
                        timeout=0.5, 
                        running_flag=self.running, 
                        single_attempt=True
                    )
                    if result:
                        break
                    time.sleep(0.3)
                
                if result:
                    x, y, text, conf = result
                    rx = (x - region[0]) / w
                    ry = (y - region[1]) / h
                    self.log_msg.emit(f"✓ Текст '{text}' найден! Навожу курсор на ({rx:.2f}, {ry:.2f})")
                    self.move_cursor_to(hwnd, rx, ry, delay=0.3)
                    return True
                else:
                    self.log_msg.emit(f"✗ Текст '{search_text}' не найден")
                    return False
            
            return True
            
        except Exception as e:
            self.log_msg.emit(f"❌ Ошибка выполнения команды: {e}")
            return False
    
    def run(self):
        try:
            if self.is_running:
                self.finished.emit("Предупреждение: уже выполняется!")
                return
            self.is_running = True
            self.paused = False
            self.pause_event.set()
            hwnd = self.find_game_hwnd()
            if not hwnd:
                self.finished.emit("Ошибка: окно не найдено!")
                self.is_running = False
                return
            self.hwnd = hwnd
            win32gui.ShowWindow(hwnd, 9)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(2)
            if not self.running:
                self.finished.emit("Выполнение отменено")
                self.is_running = False
                return
            self.log_msg.emit("=== НАЧАЛО РАБОТЫ ===")
            region, w, h = self.get_window_region(hwnd)
            self.log_msg.emit(f"Размер окна: {w}x{h}")
            if self.text_finder.ocr_available:
                self.log_msg.emit("✅ OCR доступен (поиск текста включён)")
            else:
                self.log_msg.emit("⚠️ OCR недоступен (поиск текста отключён)")
            image_folder = self.image_finder.get_folder_path()
            self.log_msg.emit(f"📁 Папка изображений: {image_folder}")
            self.log_msg.emit("⚠️ НЕ СВОРАЧИВАЙТЕ ИГРУ ВО ВРЕМЯ РАБОТЫ!")
            self.log_msg.emit("⌨️ F1 - ЭКСТРЕННАЯ ОСТАНОВКА")
            self.log_msg.emit("⌨️ F5 - ПАУЗА/ПРОДОЛЖЕНИЕ выполнения")
            if self.is_macro_only_mode:
                self.run_macro_only(hwnd)
                self.finished.emit("Завершено.")
                self.is_running = False
                return
            for acc in self.accounts:
                if not self.running:
                    self.log_msg.emit("⛔ Выполнение прервано пользователем")
                    break
                try:
                    if '+' in acc:
                        email, password = acc.split('+', 1)
                    else:
                        continue
                except Exception as e:
                    self.log_msg.emit(f"Ошибка: {e}")
                    continue
                self.current_email = email
                self.current_password = password
                self.update_acc_label.emit(f"Аккаунт: {email}")
                self.log_msg.emit(f"\n{'='*50}")
                self.log_msg.emit(f"--- Вход: {email} ---")
                self.log_msg.emit(f"{'='*50}")
                if not self.run_authorization(hwnd, email, password):
                    if not self.running:
                        break
                    self.log_msg.emit(f"⚠️ Пропуск аккаунта {email} из-за ошибки авторизации")
                    continue
                if self.active_macro and self.running:
                    self.log_msg.emit(f"📜 Запуск макроса для {email}...")
                    self.run_macro(hwnd, self.active_macro)
                if not self.running:
                    break
                self.log_msg.emit(f"✅ Аккаунт {email} завершён")
                time.sleep(2)
            if self.running:
                self.finished.emit("Завершено. Все аккаунты обработаны.")
            else:
                self.finished.emit("Выполнение прервано пользователем")
        except Exception as e:
            self.log_msg.emit(f"❌ ОШИБКА: {e}")
            self.log_msg.emit(traceback.format_exc())
            self.finished.emit(f"Ошибка: {e}")
        finally:
            self.is_running = False


# ============================================
# 📋 ВИДЖЕТ РЕДАКТОРА С НОМЕРАМИ СТРОК
# ============================================
class LineNumberEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
    
    def line_number_area_width(self):
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val /= 10
            digits += 1
        return 20 + self.fontMetrics().horizontalAdvance('9') * digits
    
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
    
    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(50, 50, 50))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(150, 150, 150))
                painter.drawText(0, top, self.line_number_area.width() - 5, 
                               self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
        painter.end()
    
    def highlight_current_line(self, line_num):
        self.extra_selections = []
        if 1 <= line_num <= self.blockCount():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(255, 255, 0, 100)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.setPosition(0)
            selection.cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor, line_num - 1)
            self.extra_selections.append(selection)
        self.setExtraSelections(self.extra_selections)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


# ============================================
# 📋 ВИДЖЕТ СПИСКА МАКРОСОВ
# ============================================
class MacroListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.current_item = None
    
    def startDrag(self, supportedActions):
        drag = QDrag(self)
        mime = QMimeData()
        drag.setMimeData(mime)
        selected_items = self.selectedItems()
        if selected_items:
            self.current_item = selected_items[0]
        drag.exec(supportedActions)


# ============================================
# ⚙️ ДИАЛОГ НАСТРОЕК
# ============================================
class VisibilitySettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Настройки Окна")
        self.setFixedSize(450, 400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.window_settings = {
            'window_width': 1400,
            'window_height': 900
        }
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel("📐 Настройки Размера Окна")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e94560;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Информация
        info = QLabel(
            "💡 Окно автоматически сохранит последний размер\n"
            "💡 Вы также можете изменить размер перетаскиванием краёв"
        )
        info.setStyleSheet("color: #95a5a6; font-size: 12px; line-height: 1.6;")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        layout.addSpacing(20)
        
        # Размер окна
        size_group = QGroupBox("📏 Размер Окна (пиксели)")
        size_layout = QVBoxLayout(size_group)
        
        size_input_layout = QHBoxLayout()
        
        self.spin_width = QSpinBox()
        self.spin_width.setRange(800, 3840)
        self.spin_width.setValue(1400)
        self.spin_width.setPrefix("Ширина:  ")
        self.spin_width.setSuffix(" px")
        self.spin_width.setStyleSheet("font-size: 13px; padding: 5px;")
        
        self.spin_height = QSpinBox()
        self.spin_height.setRange(600, 2160)
        self.spin_height.setValue(900)
        self.spin_height.setPrefix("Высота:  ")
        self.spin_height.setSuffix(" px")
        self.spin_height.setStyleSheet("font-size: 13px; padding: 5px;")
        
        size_input_layout.addWidget(self.spin_width)
        size_input_layout.addWidget(self.spin_height)
        size_layout.addLayout(size_input_layout)
        
        # Пресеты
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Быстрый выбор:"))
        
        btn_small = QPushButton("800x600")
        btn_small.setFixedHeight(30)
        btn_small.clicked.connect(lambda: self._set_size(800, 600))
        
        btn_medium = QPushButton("1200x800")
        btn_medium.setFixedHeight(30)
        btn_medium.clicked.connect(lambda: self._set_size(1200, 800))
        
        btn_large = QPushButton("1400x900")
        btn_large.setFixedHeight(30)
        btn_large.clicked.connect(lambda: self._set_size(1400, 900))
        
        btn_full = QPushButton("1920x1080")
        btn_full.setFixedHeight(30)
        btn_full.clicked.connect(lambda: self._set_size(1920, 1080))
        
        presets_layout.addWidget(btn_small)
        presets_layout.addWidget(btn_medium)
        presets_layout.addWidget(btn_large)
        presets_layout.addWidget(btn_full)
        size_layout.addLayout(presets_layout)
        
        layout.addWidget(size_group)
        
        layout.addStretch()
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        btn_save = QPushButton("💾 Сохранить")
        btn_save.setFixedHeight(45)
        btn_save.setStyleSheet("background-color: #27ae60; font-size: 14px; font-weight: bold;")
        btn_save.clicked.connect(self.save_settings)
        
        btn_cancel = QPushButton("❌ Отмена")
        btn_cancel.setFixedHeight(45)
        btn_cancel.setStyleSheet("background-color: #e74c3c; font-size: 14px; font-weight: bold;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
    
    def _set_size(self, width, height):
        self.spin_width.setValue(width)
        self.spin_height.setValue(height)
    
    def save_settings(self):
        self.window_settings = {
            'window_width': self.spin_width.value(),
            'window_height': self.spin_height.value()
        }
        self.accept()
    
    def get_settings(self):
        return self.window_settings
    
    def load_settings(self, settings):
        self.window_settings = settings
        self.spin_width.setValue(settings.get('window_width', 1400))
        self.spin_height.setValue(settings.get('window_height', 900))

# ============================================
# 🔄 ДИАЛОГ ОБНОВЛЕНИЯ (С ОТЛАДКОЙ)
# ============================================
class UpdateDialog(QDialog):
    def __init__(self, local_version, remote_version, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔄 Доступно обновление")
        self.setFixedSize(400, 200)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        layout = QVBoxLayout(self)
        
        title = QLabel(f"✨ Новая версия {remote_version} доступна!")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #27ae60;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        info = QLabel(f"Ваша версия: {local_version}\n\nХотите обновить?")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        btn_layout = QHBoxLayout()
        
        self.btn_update = QPushButton("✅ Обновить")
        self.btn_update.setStyleSheet("background: #27ae60; color: white; height: 35px; font-weight: bold;")
        self.btn_update.clicked.connect(self.accept)
        
        self.btn_skip = QPushButton("❌ Позже")
        self.btn_skip.setStyleSheet("background: #e74c3c; color: white; height: 35px;")
        self.btn_skip.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_skip)
        layout.addLayout(btn_layout)
    
    def show_progress(self, percent, downloaded, total):
        self.progress.setVisible(True)
        self.progress.setValue(int(percent))
        self.progress.setFormat(f"{int(percent)}% ({downloaded}/{total} байт)")
        QApplication.processEvents()
    
    def set_updating(self, updating):
        self.btn_update.setEnabled(not updating)
        self.btn_skip.setEnabled(not updating)
        if updating:
            self.btn_update.setText("⏳ Загрузка...")
    
    def add_debug_message(self, message):
        """✅ Добавление сообщения в лог отладки"""
        self.debug_log.setVisible(True)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.debug_log.append(f"[{timestamp}] {message}")
        self.debug_log.verticalScrollBar().setValue(self.debug_log.verticalScrollBar().maximum())

# ============================================
# 🎨 СОВРЕМЕННЫЕ СТИЛИ ИНТЕРФЕЙСА
# ============================================
MODERN_STYLESHEET = """
QMainWindow {
    background-color: #1a1a2e;
}
QWidget {
    background-color: #1a1a2e;
    color: #ecf0f1;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QGroupBox {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 10px;
    margin-top: 15px;
    padding-top: 15px;
    font-weight: bold;
    color: #e94560;
    font-size: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    color: #e94560;
}
QPushButton {
    background-color: #0f3460;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 15px;
    font-weight: bold;
    font-size: 11px;
    min-width: 50px;
}
QPushButton:hover {
    background-color: #e94560;
}
QPushButton:pressed {
    background-color: #c0392b;
}
QPushButton:disabled {
    background-color: #34495e;
    color: #7f8c8d;
}
QLineEdit {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
    padding: 8px 12px;
    color: #ecf0f1;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #e94560;
}
QTextEdit, QPlainTextEdit {
    background-color: #0f0f1a;
    border: 2px solid #0f3460;
    border-radius: 6px;
    padding: 10px;
    color: #ecf0f1;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}
QListWidget {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
    color: #ecf0f1;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #e94560;
}
QListWidget::item:hover {
    background-color: #0f3460;
}
QProgressBar {
    background-color: #16213e;
    border: none;
    border-radius: 6px;
    height: 20px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #e94560;
    border-radius: 6px;
}
QCheckBox {
    color: #ecf0f1;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #0f3460;
    background-color: #16213e;
}
QCheckBox::indicator:checked {
    background-color: #e94560;
    border-color: #e94560;
}
QLabel {
    color: #ecf0f1;
    font-size: 13px;
}
QComboBox {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
    padding: 8px 12px;
    color: #ecf0f1;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #ecf0f1;
    border: 2px solid #0f3460;
    selection-background-color: #e94560;
}
QScrollBar:vertical {
    background-color: #16213e;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background-color: #0f3460;
    border-radius: 6px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #e94560;
}
QTabWidget::pane {
    border: 2px solid #0f3460;
    border-radius: 10px;
    background-color: #16213e;
}
QTabBar::tab {
    background-color: #0f3460;
    color: #ecf0f1;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 3px;
}
QTabBar::tab:selected {
    background-color: #e94560;
}
QTabBar::tab:hover:!selected {
    background-color: #1a1a2e;
}
QSpinBox, QDoubleSpinBox {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
    padding: 8px;
    color: #ecf0f1;
}
"""

# Цвета для логов
LOG_COLORS = {
    'info': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'error': '#e74c3c',
    'process': '#9b59b6',
    'highlight': '#e94560'
}

# ============================================
# 🖥️ ИНТЕРФЕЙС ПРИЛОЖЕНИЯ
# ============================================
class InfiniteBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Infinite Magicraid Bot v{VERSION}")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setStyleSheet(MODERN_STYLESHEET)
    
        # Состояние
        self.is_bot_running = False
        self.is_loading_file = False
        self.is_capturing = False
        self.is_recording_server = False
        self.is_macro_operation = False
        self.accounts = []
        self.accounts_file_path = None
    
        # Компоненты
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.macro_recorder = MacroRecorder()
        self.server_recorder = ServerSelectorRecorder()
        self.text_finder = TextFinder()
        self.image_finder = ImageFinder()
        self.game_hwnd = None
        self.worker = None
        self.thread = None
        self.last_cursor_position = 0
    
        # Пути
        self.macro_folder_path = program_path("macros")
        self.macro_folder_path.mkdir(parents=True, exist_ok=True)
        self.server_macro_path = self.macro_folder_path / "server_selection.txt"
        self.config_path = program_path("macros", "config.json")
    
        # Настройки окна (только размер)
        self.visibility_settings = {
            'window_width': 1400,
            'window_height': 900
        }
    
        # ✅ ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ (важно!)
        self.log_widget = None
        self.server_widget = None
        self.macro_list_widget = None
        self.help_widget = None
    
        # ✅ ПРОВЕРКА ОБНОВЛЕНИЙ ПРИ ЗАПУСКЕ
        self.check_for_updates()
    
        # Инициализация UI
        self.init_main_interface()
        self.load_config()
        self.load_last_macro()
    
        # Горячие клавиши
        QTimer.singleShot(1000, self.register_hotkeys)
    
    def check_for_updates(self):
        """Проверка обновлений при запуске"""
        try:
            local_version = UpdateChecker.get_local_version()
            remote_version = UpdateChecker.get_remote_version()
            
            print(f"🔍 Версии: локальная={local_version}, удалённая={remote_version}")
            
            if remote_version and UpdateChecker.compare_versions(local_version, remote_version):
                dialog = UpdateDialog(local_version, remote_version, self)
                
                def on_download_progress(percent, downloaded, total):
                    dialog.show_progress(percent, downloaded, total)
                
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    dialog.set_updating(True)
                    new_file = UpdateChecker.download_update(on_download_progress)
                    
                    if new_file:
                        if UpdateChecker.apply_update(new_file):
                            QMessageBox.information(self, "✅ Обновление успешно", 
                                "Программа обновлена!\nПерезапустите приложение.")
                            sys.exit(0)
                        else:
                            QMessageBox.warning(self, "❌ Ошибка", "Не удалось применить обновление.")
                    else:
                        QMessageBox.warning(self, "❌ Ошибка", "Не удалось загрузить обновление.")
        except Exception as e:
            print(f"⚠️ Ошибка проверки обновлений: {e}")
    
    def register_hotkeys(self):
        try:
            def listener():
                keyboard.add_hotkey('f1', self.emergency_stop)
                keyboard.add_hotkey('f2', self.toggle_server_recording)
                keyboard.add_hotkey('f3', self.start_bot)
                keyboard.add_hotkey('f4', self.start_macro_only)
                keyboard.add_hotkey('f5', self.toggle_pause)
                keyboard.wait()
            threading.Thread(target=listener, daemon=True).start()
        except:
            pass
    
    def log_msg(self, message):
        if self.log:
            QMetaObject.invokeMethod(self.log, "append", Qt.ConnectionType.QueuedConnection, Q_ARG(str, message))
    
    def init_main_interface(self):
        """Создание современного главного интерфейса"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        top_panel = self.create_top_panel()
        main_layout.addWidget(top_panel)
        
        # === ЦЕНТРАЛЬНАЯ ОБЛАСТЬ С ВКЛАДКАМИ ===
        center_widget = self.create_center_tabs()
        main_layout.addWidget(center_widget, stretch=1)
        
        # === НИЖНЯЯ ПАНЕЛЬ УПРАВЛЕНИЯ ===
        bottom_panel = self.create_bottom_control_panel()
        main_layout.addWidget(bottom_panel)
        
        self.stack.addWidget(main_widget)
    
    def create_top_panel(self):
        """Верхняя панель с информацией и настройками"""
        panel = QGroupBox("📊 ИНФОРМАЦИЯ")
        layout = QHBoxLayout(panel)
        layout.setSpacing(20)
    
        # Аккаунты
        acc_group = QVBoxLayout()
        self.acc_label = QLabel("Аккаунтов: 0")  # ✅ ДОБАВЛЕНО
        self.acc_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        self.acc_display = QLabel("Текущий: ---")
        self.acc_display.setStyleSheet("font-size: 14px; color: #ecf0f1;")
        acc_group.addWidget(self.acc_label)
        acc_group.addWidget(self.acc_display)
    
        # Статус бота
        status_group = QVBoxLayout()
        self.status_label = QLabel("Статус: ⏹️ Остановлен")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(25)
        status_group.addWidget(self.status_label)
        status_group.addWidget(self.progress_bar)
    
        # OCR и версии
        info_group = QVBoxLayout()
        ocr_status = "✅ OCR" if self.text_finder.ocr_available else "⚠️ OCR"
        ocr_color = "#27ae60" if self.text_finder.ocr_available else "#e74c3c"
        self.ocr_label = QLabel(ocr_status)
        self.ocr_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {ocr_color};")
        self.version_label = QLabel(f"v{VERSION}")
        self.version_label.setStyleSheet("font-size: 14px; color: #9b59b6;")
        info_group.addWidget(self.ocr_label)
        info_group.addWidget(self.version_label)
    
        # Кнопки
        btn_group = QHBoxLayout()
        self.btn_load_accounts = QPushButton("📂 Загрузить аккаунты")
        self.btn_load_accounts.setFixedSize(180, 45)
        self.btn_load_accounts.clicked.connect(self.load_file)
    
        self.btn_settings = QPushButton("⚙️ Настройки")
        self.btn_settings.setFixedSize(120, 45)
        self.btn_settings.clicked.connect(self.open_settings_dialog)
    
        btn_group.addWidget(self.btn_load_accounts)
        btn_group.addWidget(self.btn_settings)
    
        # Добавление в layout
        layout.addLayout(acc_group)
        layout.addStretch()
        layout.addLayout(status_group)
        layout.addStretch()
        layout.addLayout(info_group)
        layout.addStretch()
        layout.addLayout(btn_group)
    
        return panel
    
    def create_center_tabs(self):
        """Центральная область с вкладками"""
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Вкладка 1: Редактор макросов
        editor_tab = self.create_macro_editor_tab()
        tabs.addTab(editor_tab, "📜 Редактор Макросов")
        
        # Вкладка 2: Выбор сервера
        server_tab = self.create_server_tab()
        tabs.addTab(server_tab, "🖱️ Выбор Сервера")
        
        # Вкладка 3: Список макросов
        list_tab = self.create_macro_list_tab()
        tabs.addTab(list_tab, "📂 Список Макросов")
        
        # Вкладка 4: Помощь
        help_tab = self.create_help_tab()
        tabs.addTab(help_tab, "💡 Помощь")
        
        return tabs
    
    def create_macro_editor_tab(self):
        """Вкладка редактора макросов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Панель имени макроса
        name_panel = QHBoxLayout()
        name_panel.addWidget(QLabel("Имя макроса:"))
        self.macro_name_input = QLineEdit()
        self.macro_name_input.setPlaceholderText("Введите имя макроса (без .txt)")
        self.macro_name_input.setFixedHeight(40)
        name_panel.addWidget(self.macro_name_input, stretch=1)
        
        # Кнопки управления макросом
        self.btn_new_macro = QPushButton("➕ Новый")
        self.btn_new_macro.setFixedSize(100, 40)
        self.btn_new_macro.clicked.connect(self.add_new_macro)
        
        self.btn_load_macro = QPushButton("📂 Загрузить")
        self.btn_load_macro.setFixedSize(100, 40)
        self.btn_load_macro.clicked.connect(self.load_macro_from_list)
        
        self.btn_save_macro = QPushButton("💾 Сохранить")
        self.btn_save_macro.setFixedSize(100, 40)
        self.btn_save_macro.clicked.connect(self.save_current_macro)
        
        self.btn_delete_macro = QPushButton("🗑️ Удалить")
        self.btn_delete_macro.setFixedSize(100, 40)
        self.btn_delete_macro.clicked.connect(self.delete_current_macro)
        
        name_panel.addWidget(self.btn_new_macro)
        name_panel.addWidget(self.btn_load_macro)
        name_panel.addWidget(self.btn_save_macro)
        name_panel.addWidget(self.btn_delete_macro)
        
        layout.addLayout(name_panel)
        
        # Панель инструментов макроса
        toolbar = self.create_macro_toolbar()
        layout.addWidget(toolbar)
        
        # Редактор с номерами строк
        self.macro_editor = LineNumberEdit()
        self.macro_editor.setPlaceholderText(
            "# Формат команд:\n"
            "# CLICK:x,y - клик по координатам\n"
            "# WAIT:секунды - ожидание\n"
            "# TEXT:слово - найти текст через OCR\n"
            "# EText:текст - ввести текст\n"
            "# EText:{EMAIL} или {PASSWORD} - данные аккаунта\n"
            "# ETextWait(интервал, таймаут, \"текст\")\n"
            "# EIMGWait(интервал, таймаут, \"имя\")\n"
            "# IMG:название - найти изображение и кликнуть\n"
            "# НАЧАЛО_ЦИКЛА(N) / КОНЕЦ_ЦИКЛА\n"
        )
        self.macro_editor.cursorPositionChanged.connect(self.save_cursor_position)
        layout.addWidget(self.macro_editor, stretch=1)
        
        # Индикатор текущей строки
        self.line_indicator = QLabel("Текущая строка: -")
        self.line_indicator.setStyleSheet("color: #e94560; font-weight: bold;")
        layout.addWidget(self.line_indicator)
        
        return widget
    
    def create_macro_toolbar(self):
        """Панель инструментов для добавления команд"""
        toolbar = QGroupBox("🛠️ Инструменты")
        layout = QHBoxLayout(toolbar)
        layout.setSpacing(8)
        
        buttons = [
            ("⏱️ WAIT", self.add_wait_command, "Добавить ожидание"),
            ("🎯 CLICK", self.capture_coordinate, "Захват координаты"),
            ("🔍 TEXT", self.add_text_search_command, "Поиск текста"),
            ("⏳ ETextWait", self.add_etext_wait_command, "Ждать текст"),
            ("⏳ EIMGWait", self.add_eimg_wait_command, "Ждать изображение"),
            ("🔄 ЦИКЛ", self.add_loop_command, "Добавить цикл"),
            ("⌨️ EText", self.add_etext_command, "Ввод текста"),
            ("🖼️ IMG", self.add_img_command, "Поиск изображения"),
        ]
        
        for text, handler, tooltip in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(35)
            btn.setToolTip(tooltip)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
        
        layout.addStretch()
        return toolbar
    
    def create_server_tab(self):
        """Вкладка выбора сервера"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
    
        # Статус записи
        status_box = QGroupBox("📹 Статус Записи")
        status_layout = QVBoxLayout(status_box)
    
        self.lbl_server_status = QLabel("Статус: не записано")
        self.lbl_server_status.setStyleSheet("font-size: 14px; color: #e74c3c; font-weight: bold;")
        status_layout.addWidget(self.lbl_server_status)
    
        self.server_details = QLabel("")
        self.server_details.setStyleSheet("color: #95a5a6;")
        status_layout.addWidget(self.server_details)
    
        layout.addWidget(status_box)
    
        # Управление записью
        control_box = QGroupBox("🎮 Управление")
        control_layout = QHBoxLayout(control_box)
    
        self.btn_server_record = QPushButton("🔴 Начать запись (F2)")
        self.btn_server_record.setFixedHeight(45)
        self.btn_server_record.setStyleSheet("font-size: 12px; padding: 5px 10px;")
        self.btn_server_record.clicked.connect(self.start_server_recording)
    
        self.btn_server_stop = QPushButton("⏹️ Остановить запись")
        self.btn_server_stop.setFixedHeight(45)
        self.btn_server_stop.setStyleSheet("font-size: 12px; padding: 5px 10px;")
        self.btn_server_stop.clicked.connect(self.stop_server_recording)
        self.btn_server_stop.setEnabled(False)
    
        self.chk_use_server = QCheckBox("Использовать при запуске")
        self.chk_use_server.setStyleSheet("font-size: 12px; spacing: 5px;")
        self.chk_use_server.stateChanged.connect(self.on_server_checkbox_changed)
    
        control_layout.addWidget(self.btn_server_record)
        control_layout.addWidget(self.btn_server_stop)
        control_layout.addStretch()
        control_layout.addWidget(self.chk_use_server)
    
        layout.addWidget(control_box)
    
        # Инструкция
        info_box = QGroupBox("📖 Инструкция")
        info_layout = QVBoxLayout(info_box)
        instructions = QLabel(
            "1. Нажмите 'Начать запись'\n"
            "2. Зажмите ЛКМ в начальной точке списка серверов\n"
            "3. Перетащите курсор до нужного сервера\n"
            "4. Отпустите ЛКМ\n"
            "5. Нажмите 'Остановить запись' или F2\n"
            "6. Включите 'Использовать при запуске бота'"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #ecf0f1; line-height: 1.6; font-size: 11px;")
        info_layout.addWidget(instructions)
    
        layout.addWidget(info_box)
        layout.addStretch()
    
        # СОХРАНЯЕМ КАК АТРИБУТ
        self.server_widget = widget
        return widget
    
    def create_macro_list_tab(self):
        """Вкладка списка макросов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
    
        # Панель папок
        folder_panel = QHBoxLayout()
        self.lbl_macro_folder = QLabel(f"📁 Папка макросов:")
        self.lbl_macro_folder.setStyleSheet("font-weight: bold; font-size: 11px;")
    
        self.btn_select_macro_folder = QPushButton("📂 Выбрать")
        self.btn_select_macro_folder.setFixedHeight(30)
        self.btn_select_macro_folder.setMaximumWidth(100)
        self.btn_select_macro_folder.setStyleSheet("font-size: 11px; padding: 3px 8px;")
        self.btn_select_macro_folder.clicked.connect(self.select_macro_folder)
    
        self.lbl_image_folder = QLabel(f"🖼️ Папка изображений:")
        self.lbl_image_folder.setStyleSheet("font-weight: bold; font-size: 11px;")
    
        self.btn_select_image_folder = QPushButton("📂 Выбрать")
        self.btn_select_image_folder.setFixedHeight(30)
        self.btn_select_image_folder.setMaximumWidth(100)
        self.btn_select_image_folder.setStyleSheet("font-size: 11px; padding: 3px 8px;")
        self.btn_select_image_folder.clicked.connect(self.select_image_folder)
    
        folder_panel.addWidget(self.lbl_macro_folder)
        folder_panel.addWidget(self.btn_select_macro_folder)
        folder_panel.addStretch()
        folder_panel.addWidget(self.lbl_image_folder)
        folder_panel.addWidget(self.btn_select_image_folder)
    
        layout.addLayout(folder_panel)
    
        # Список макросов
        list_box = QGroupBox("📋 Доступные макросы")
        list_layout = QVBoxLayout(list_box)
    
        self.macro_list = MacroListWidget()
        self.macro_list.setMinimumHeight(300)
        self.macro_list.itemDoubleClicked.connect(self.on_macro_double_click)
        self.refresh_macro_list()
    
        list_layout.addWidget(self.macro_list)
    
        layout.addWidget(list_box)
    
        # СОХРАНЯЕМ КАК АТРИБУТ
        self.macro_list_widget = widget
        return widget
    
    def create_help_tab(self):
        """Вкладка помощи"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
    
        help_box = QGroupBox("📖 Справка по командам")
        help_layout = QVBoxLayout(help_box)
    
        help_text = QLabel(
            "<h3 style='color: #e94560; font-size: 14px;'>Команды макросов:</h3>"
            "<table style='color: #ecf0f1; line-height: 1.8; font-size: 11px;'>"
            "<tr><td><b>CLICK:x,y</b></td><td>Клик по относительным координатам (0-1)</td></tr>"
            "<tr><td><b>WAIT:сек</b></td><td>Ожидание указанное время</td></tr>"
            "<tr><td><b>TEXT:слово</b></td><td>Найти текст и навести курсор</td></tr>"
            "<tr><td><b>EText:текст</b></td><td>Ввести текст с клавиатуры</td></tr>"
            "<tr><td><b>EText:{EMAIL}</b></td><td>Вставить email текущего аккаунта</td></tr>"
            "<tr><td><b>EText:{PASSWORD}</b></td><td>Вставить пароль текущего аккаунта</td></tr>"
            "<tr><td><b>ETextWait(инт, тайм, \"текст\")</b></td><td>Ждать появления текста</td></tr>"
            "<tr><td><b>EIMGWait(инт, тайм, \"имя\")</b></td><td>Ждать появления изображения</td></tr>"
            "<tr><td><b>IMG:название</b></td><td>Найти изображение и кликнуть</td></tr>"
            "<tr><td><b>НАЧАЛО_ЦИКЛА(N)</b></td><td>Начало цикла (0=бесконечный)</td></tr>"
            "<tr><td><b>КОНЕЦ_ЦИКЛА</b></td><td>Конец цикла</td></tr>"
            "</table>"
            "<h3 style='color: #3498db; margin-top: 15px; font-size: 14px;'>Горячие клавиши:</h3>"
            "<ul style='color: #ecf0f1; line-height: 1.8; font-size: 11px;'>"
            "<li><b>F1</b> - Экстренная остановка</li>"
            "<li><b>F2</b> - Запись выбора сервера (вкл/выкл)</li>"
            "<li><b>F3</b> - Запуск бота</li>"
            "<li><b>F4</b> - Запуск только макроса</li>"
            "<li><b>F5</b> - Пауза/Продолжение</li>"
            "</ul>"
        )
        help_text.setWordWrap(True)
        help_text.setTextFormat(Qt.TextFormat.RichText)
        help_layout.addWidget(help_text)
    
        layout.addWidget(help_box)
    
        # СОХРАНЯЕМ КАК АТРИБУТ
        self.help_widget = widget
        return widget
    
    def create_bottom_control_panel(self):
        """Нижняя панель с кнопками управления и логом"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
    
        # Кнопки управления
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
    
        self.btn_run = QPushButton("🚀 ЗАПУСТИТЬ БОТА (F3)")
        self.btn_run.setFixedHeight(60)
        self.btn_run.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #34495e;
            }
        """)
        self.btn_run.clicked.connect(self.start_bot)
    
        self.btn_macro_only = QPushButton("📜 ТОЛЬКО МАКРОС (F4)")
        self.btn_macro_only.setFixedHeight(60)
        self.btn_macro_only.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #9b59b6;
            }
            QPushButton:disabled {
                background-color: #34495e;
            }
        """)
        self.btn_macro_only.clicked.connect(self.start_macro_only)
    
        self.btn_pause = QPushButton("⏸️ ПАУЗА (F5)")
        self.btn_pause.setFixedHeight(60)
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
            QPushButton:disabled {
                background-color: #34495e;
            }
        """)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setEnabled(False)
    
        self.btn_stop = QPushButton("⛔ СТОП (F1)")
        self.btn_stop.setFixedHeight(60)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_stop.clicked.connect(self.emergency_stop)
    
        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_macro_only)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_stop)
    
        layout.addLayout(btn_layout)
    
        # Лог событий - СОХРАНЯЕМ КАК АТРИБУТ
        self.log_widget = QGroupBox("📋 Лог Событий")
        log_layout = QVBoxLayout(self.log_widget)
    
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(200)
        self.log.verticalScrollBar().valueChanged.connect(
            lambda: self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())
        )
    
        log_layout.addWidget(self.log)
    
        # Кнопки лога
        log_btn_layout = QHBoxLayout()
        self.btn_clear_log = QPushButton("🗑️ Очистить")
        self.btn_clear_log.setFixedHeight(30)
        self.btn_clear_log.setMaximumWidth(120)
        self.btn_clear_log.clicked.connect(lambda: self.log.clear())
    
        self.btn_save_log = QPushButton("💾 Сохранить")
        self.btn_save_log.setFixedHeight(30)
        self.btn_save_log.setMaximumWidth(120)
        self.btn_save_log.clicked.connect(self.save_log)
    
        log_btn_layout.addWidget(self.btn_clear_log)
        log_btn_layout.addWidget(self.btn_save_log)
        log_btn_layout.addStretch()
    
        log_layout.addLayout(log_btn_layout)
        layout.addWidget(self.log_widget)
    
        return panel
    def append_to_log(self, message, log_type='info'):
        """Добавление сообщения в лог с цветом"""
        try:
            if self.log:
                color = LOG_COLORS.get(log_type, LOG_COLORS['info'])
                
                # Форматирование сообщения
                timestamp = datetime.now().strftime("%H:%M:%S")
                formatted_msg = f"<span style='color: #7f8c8d;'>[{timestamp}]</span> <span style='color: {color};'>{message}</span>"
                
                self.log.append(formatted_msg)
                
                # Автопрокрутка
                scrollbar = self.log.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                
                # Подсветка текущей строки в редакторе
                if self.worker and hasattr(self.worker, 'current_line'):
                    if self.macro_editor:
                        self.macro_editor.highlight_current_line(self.worker.current_line)
                        self.line_indicator.setText(f"Текущая строка: {self.worker.current_line}")
                        
        except Exception as e:
            print(f"Ошибка добавления в лог: {e}")
    
    def save_log(self):
        """Сохранение лога в файл"""
        try:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Сохранить лог", 
                f"bot_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Текстовые файлы (*.txt)"
            )
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.log.toPlainText())
                self.append_to_log(f"✅ Лог сохранён: {filepath}", 'success')
        except Exception as e:
            self.append_to_log(f"❌ Ошибка сохранения лога: {e}", 'error')
            
    def update_bot_status(self, running=False, paused=False):
        """Обновление статуса бота"""
        if running:
            if paused:
                self.status_label.setText("Статус: ⏸️ На паузе")
                self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f39c12;")
                self.btn_pause.setText("▶️ ПРОДОЛЖИТЬ (F5)")
            else:
                self.status_label.setText("Статус: ▶️ Выполняется")
                self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
                self.btn_pause.setText("⏸️ ПАУЗА (F5)")
            self.progress_bar.setVisible(True)
            self.progress_bar.setFormat("Выполнение...")
        else:
            self.status_label.setText("Статус: ⏹️ Остановлен")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
            self.btn_pause.setText("⏸️ ПАУЗА (F5)")
            self.progress_bar.setVisible(False)
        
        self.btn_run.setEnabled(not running)
        self.btn_macro_only.setEnabled(not running)
        self.btn_pause.setEnabled(running)
    
    def update_account_display(self, email):
        """Обновление отображения текущего аккаунта"""
        self.acc_display.setText(f"Текущий: {email}")
        self.append_to_log(f"👤 Аккаунт: {email}", 'process')        
    
    def select_macro_folder(self):
        try:
            folder = QFileDialog.getExistingDirectory(self, "Выберите папку для макросов", str(self.macro_folder_path))
            if folder:
                self.macro_folder_path = Path(folder)
                self.macro_folder_path.mkdir(exist_ok=True)
                self.server_macro_path = self.macro_folder_path / "server_selection.txt"
                self.config_path = self.macro_folder_path / "config.json"
                self.lbl_macro_folder.setText(f"📁 Папка макросов: {self.macro_folder_path}")
                self.append_to_log(f"✅ Папка макросов изменена: {self.macro_folder_path}")
                self.refresh_macro_list()
                self.save_config()
        except Exception as e:
            self.append_to_log(f"❌ Ошибка выбора папки макросов: {e}")
    
    def select_image_folder(self):
        try:
            folder = QFileDialog.getExistingDirectory(self, "Выберите папку с изображениями", str(self.image_finder.get_image_folder()))
            if folder:
                if self.image_finder.set_custom_folder(folder):
                    self.lbl_image_folder.setText(f"📁 Папка: {folder}")
                    self.append_to_log(f"✅ Папка изображений изменена: {folder}")
                    self.save_config()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось установить папку!")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка выбора папки: {e}")
    
    def append_to_log(self, message):
        try:
            if self.log:
                if not self.is_bot_running and "✅ Аккаунт" in message:
                    return
                self.log.append(message)
                scrollbar = self.log.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                if self.worker and hasattr(self.worker, 'current_line'):
                    if self.macro_editor:
                        self.macro_editor.highlight_current_line(self.worker.current_line)
                        cursor = self.macro_editor.textCursor()
                        cursor.movePosition(QTextCursor.MoveOperation.Start)
                        for _ in range(self.worker.current_line - 1):
                            cursor.movePosition(QTextCursor.MoveOperation.Down)
                        self.macro_editor.setTextCursor(cursor)
        except Exception as e:
            print(f"Ошибка добавления в лог: {e}")
    
    def toggle_pause(self):
        try:
            if self.worker and self.worker.is_running:
                self.worker.toggle_pause()
                if self.worker.paused:
                    self.btn_pause.setText("▶️ ПРОДОЛЖИТЬ (F5)")
                    self.btn_pause.setStyleSheet("background: #27ae60; color: white; height: 60px; font-weight: bold; font-size: 14px;")
                else:
                    self.btn_pause.setText("⏸️ ПАУЗА (F5)")
                    self.btn_pause.setStyleSheet("background: #f39c12; color: white; height: 60px; font-weight: bold; font-size: 14px;")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка паузы: {e}")
    
    def toggle_server_recording(self):
        try:
            if self.is_recording_server:
                self.stop_server_recording()
            else:
                self.start_server_recording()
        except Exception as e:
            self.append_to_log(f"❌ Ошибка переключения записи: {e}")
    
    def open_settings_dialog(self):
        """✅ Открытие диалога настроек"""
        try:
            dialog = VisibilitySettingsDialog(self)
            dialog.load_settings(self.visibility_settings)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                settings = dialog.get_settings()
                self.visibility_settings['window_width'] = settings['window_width']
                self.visibility_settings['window_height'] = settings['window_height']
                self.resize(settings['window_width'], settings['window_height'])
                self.save_config()
                self.append_to_log("⚙️ Настройки сохранены")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка открытия настроек: {e}")
    
    def go_back_to_page1(self):
        try:
            if self.worker:
                self.worker.running = False
            if self.thread and self.thread.isRunning():
                self.thread.quit()
                self.thread.wait(2000)
            self.stack.setCurrentIndex(0)
            self.append_to_log("⬅️ Возврат к выбору файла аккаунтов")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка возврата: {e}")
    
    def on_server_checkbox_changed(self, state):
        try:
            if state == Qt.CheckState.Checked:
                if not self.server_recorder.is_recorded() and not self.server_macro_path.exists():
                    QMessageBox.warning(self, "Ошибка", "Сначала выполните запись выбора сервера!")
                    self.chk_use_server.setChecked(False)
                    return
                self.append_to_log("✅ Выбор сервера будет выполнен при запуске")
            else:
                self.append_to_log("⚠️ Выбор сервера отключён")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка изменения чекбокса сервера: {e}")
    
    def save_cursor_position(self):
        try:
            self.last_cursor_position = self.macro_editor.textCursor().position()
        except:
            pass
    
    def insert_at_cursor(self, text):
        try:
            cursor = self.macro_editor.textCursor()
            cursor.setPosition(self.last_cursor_position)
            cursor.insertText(text)
            self.macro_editor.setTextCursor(cursor)
            self.save_cursor_position()
        except Exception as e:
            self.append_to_log(f"❌ Ошибка вставки текста: {e}")
    
    def refresh_macro_list(self):
        try:
            self.macro_list.clear()
            self.macro_folder_path.mkdir(exist_ok=True)
            for f in self.macro_folder_path.glob('*.txt'):
                if f.name != 'config.json' and f.name != 'server_selection.txt':
                    self.macro_list.addItem(f.name)
            if self.macro_list.count() == 1:
                self.macro_list.item(0).setSelected(True)
        except Exception as e:
            self.append_to_log(f"❌ Ошибка обновления списка макросов: {e}")
    
    def add_new_macro(self):
        if self.is_macro_operation:
            return
        try:
            self.is_macro_operation = True
            name = self.macro_name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Ошибка", "Введите имя макроса!")
                return
            self.macro_folder_path.mkdir(exist_ok=True)
            path = self.macro_folder_path / f"{name}.txt"
            if not path.exists():
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("# Новый макрос\n")
                self.append_to_log(f"✅ Макрос создан: {path}")
                self.macro_name_input.setText(name)
                self.refresh_macro_list()
            else:
                QMessageBox.warning(self, "Ошибка", "Макрос с таким именем уже существует!")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка создания макроса: {e}")
        finally:
            self.is_macro_operation = False
    
    def load_macro_from_list(self):
        if self.is_macro_operation:
            return
        try:
            self.is_macro_operation = True
            current_item = self.macro_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Ошибка", "Выберите макрос из списка!")
                return
            name = current_item.text()
            path = self.macro_folder_path / name
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.macro_name_input.setText(name.replace('.txt', ''))
                self.macro_editor.setPlainText(content)
                self.append_to_log(f"✅ Макрос загружен: {name}")
                self.last_cursor_position = len(content)
        except Exception as e:
            self.append_to_log(f"❌ Ошибка загрузки макроса: {e}")
        finally:
            self.is_macro_operation = False
    
    def on_macro_double_click(self, item):
        if self.is_macro_operation:
            return
        try:
            self.is_macro_operation = True
            name = item.text()
            path = self.macro_folder_path / name
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.macro_name_input.setText(name.replace('.txt', ''))
                self.macro_editor.setPlainText(content)
                self.append_to_log(f"✅ Макрос загружен: {name}")
                self.last_cursor_position = len(content)
        except Exception as e:
            self.append_to_log(f"❌ Ошибка загрузки макроса: {e}")
        finally:
            self.is_macro_operation = False
    
    def save_current_macro(self):
        if self.is_macro_operation:
            return
        try:
            self.is_macro_operation = True
            name = self.macro_name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Ошибка", "Введите имя макроса!")
                return
            if not name.endswith('.txt'):
                name += '.txt'
            self.macro_folder_path.mkdir(exist_ok=True)
            path = self.macro_folder_path / name
            content = self.macro_editor.toPlainText()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.append_to_log(f"✅ Макрос сохранён: {path}")
            self.refresh_macro_list()
        except Exception as e:
            self.append_to_log(f"❌ Ошибка сохранения макроса: {e}")
        finally:
            self.is_macro_operation = False
    
    def delete_current_macro(self):
        if self.is_macro_operation:
            return
        try:
            self.is_macro_operation = True
            name = self.macro_name_input.text().strip()
            if not name:
                current_item = self.macro_list.currentItem()
                if current_item:
                    name = current_item.text()
                else:
                    QMessageBox.warning(self, "Ошибка", "Введите имя макроса или выберите его из списка!")
                    return
            if not name.endswith('.txt'):
                name += '.txt'
            path = self.macro_folder_path / name
            if not path.exists():
                QMessageBox.warning(self, "Ошибка", f"Макрос {name} не найден!")
                return
            reply = QMessageBox.question(self, "Подтверждение удаления", f"Вы действительно хотите удалить макрос '{name}'?\n\nЭто действие нельзя отменить!", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    path.unlink()
                    self.macro_name_input.clear()
                    self.macro_editor.setPlainText("")
                    self.refresh_macro_list()
                    self.append_to_log(f"🗑️ Макрос удалён: {name}")
                    if self.config_path.exists():
                        self.save_config()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось удалить макрос:\n{e}")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка удаления макроса: {e}")
        finally:
            self.is_macro_operation = False
    
    def load_last_macro(self):
        try:
            config_file = self.macro_folder_path / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    last_macro = config.get('last_macro', None)
                    if last_macro:
                        path = self.macro_folder_path / last_macro
                        if path.exists():
                            with open(path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            self.macro_name_input.setText(last_macro.replace('.txt', ''))
                            self.macro_editor.setPlainText(content)
                            self.append_to_log(f"📜 Последний макрос загружен: {last_macro}")
                            self.refresh_macro_list()
        except:
            pass
    
    def load_config(self):
        try:
            config_file = program_path("macros", "config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
                # ✅ Исправляем ключи (убираем пробелы)
                config = {k.strip(): v for k, v in config.items()}
            
                # ✅ Загрузка аккаунтов
                accounts_path = config.get('accounts_file', '').strip()
                if accounts_path and os.path.exists(accounts_path):
                    self.accounts_file_path = accounts_path
                    with open(accounts_path, 'r', encoding='utf-8') as f:
                        self.accounts = [l.strip() for l in f if l.strip()]
                    # ✅ Используем acc_label вместо count_label
                    if hasattr(self, 'acc_label'):
                        self.acc_label.setText(f"Аккаунтов: {len(self.accounts)}")
                    self.append_to_log(f"✅ Загружено аккаунтов: {len(self.accounts)}")
            
                # ✅ Загрузка папки макросов
                macro_folder = config.get('macro_folder', '').strip()
                if macro_folder and os.path.exists(macro_folder):
                    self.macro_folder_path = Path(macro_folder)
                    self.server_macro_path = self.macro_folder_path / "server_selection.txt"
                    self.config_path = program_path("macros", "config.json")
                    if hasattr(self, 'lbl_macro_folder'):
                        self.lbl_macro_folder.setText(f"📁 Папка макросов: {self.macro_folder_path}")
            
                # ✅ Загрузка настройки сервера
                if config.get('use_server_selection', False):
                    if self.server_macro_path.exists():
                        if hasattr(self, 'chk_use_server'):
                            self.chk_use_server.setChecked(True)
                        events = self.server_recorder.load_server_macro(self.server_macro_path)
                        if events:
                            self.server_recorder.events = events
                            down_count = sum(1 for e in events if e['type'] == 'MOUSE_DOWN')
                            drag_count = sum(1 for e in events if e['type'] == 'MOUSE_DRAG')
                            up_count = sum(1 for e in events if e['type'] == 'MOUSE_UP')
                            if hasattr(self, 'lbl_server_status'):
                                self.lbl_server_status.setText(f"Статус: записано ({down_count} нажатий, {drag_count} перетаскиваний, {up_count} отпусканий)")
                                self.lbl_server_status.setStyleSheet("color: #27ae60;")
            
                # ✅ Загрузка папки изображений
                image_folder = config.get('image_folder', '').strip()
                if image_folder and os.path.exists(image_folder):
                    self.image_finder.set_custom_folder(image_folder)
                    if hasattr(self, 'lbl_image_folder'):
                        self.lbl_image_folder.setText(f"📁 Папка изображений: {image_folder}")
            
                # ✅ Загрузка размера окна
                if 'visibility_settings' in config:
                    saved_settings = config.get('visibility_settings', {})
                    self.visibility_settings['window_width'] = saved_settings.get('window_width', 1400)
                    self.visibility_settings['window_height'] = saved_settings.get('window_height', 900)
                    self.resize(self.visibility_settings['window_width'], self.visibility_settings['window_height'])
            
                self.append_to_log("✅ Конфигурация загружена")
            
        except Exception as e:
            self.append_to_log(f"❌ Ошибка загрузки конфигурации: {e}")
            print(f"Debug: {e}")
    
    def save_config(self):
        """✅ Сохранение конфигурации"""
        try:
            config_file = program_path("macros", "config.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)
        
            # Обновляем размеры из текущего окна
            self.visibility_settings['window_width'] = self.width()
            self.visibility_settings['window_height'] = self.height()
        
            config = {
                'accounts_file': self.accounts_file_path,
                'macro_folder': str(self.macro_folder_path.absolute()),
                'use_server_selection': self.chk_use_server.isChecked() if hasattr(self, 'chk_use_server') else False,
                'last_macro': self.macro_name_input.text().strip() + '.txt' if hasattr(self, 'macro_name_input') and self.macro_name_input.text().strip() else None,
                'visibility_settings': {
                    'window_width': self.visibility_settings['window_width'],
                    'window_height': self.visibility_settings['window_height']
                },
                'image_folder': self.image_finder.get_folder_path()
            }
        
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        
            print(f"✅ Конфиг сохранён: {config_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения конфигурации: {e}")
    
    def add_wait_command(self):
        try:
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Время ожидания")
            dialog.setLabelText("Введите время ожидания в секундах:")
            dialog.setInputMode(QInputDialog.InputMode.DoubleInput)
            dialog.setDoubleValue(1.0)
            dialog.setDoubleMinimum(0.1)
            dialog.setDoubleMaximum(300.0)
            dialog.setDoubleDecimals(1)
            if dialog.exec() == QInputDialog.DialogCode.Accepted:
                wait_time = dialog.doubleValue()
                command = f"WAIT:{wait_time}\n"
                self.insert_at_cursor(command)
                self.append_to_log(f"⏱️ Добавлено ожидание: {wait_time} сек")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка добавления ожидания: {e}")
    
    def add_etext_wait_command(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("ETextWait - Ждать текст")
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Интервал опроса (сек):"))
            interval_spin = QDoubleSpinBox()
            interval_spin.setRange(0.1, 10.0)
            interval_spin.setValue(1.0)
            interval_spin.setDecimals(1)
            layout.addWidget(interval_spin)
            layout.addWidget(QLabel("Таймаут ожидания (сек):"))
            timeout_spin = QDoubleSpinBox()
            timeout_spin.setRange(1.0, 300.0)
            timeout_spin.setValue(30.0)
            timeout_spin.setDecimals(1)
            layout.addWidget(timeout_spin)
            layout.addWidget(QLabel("Текст для поиска:"))
            text_input = QLineEdit()
            text_input.setPlaceholderText("Например: Пропустить")
            layout.addWidget(text_input)
            btn_ok = QPushButton("OK")
            btn_ok.clicked.connect(dialog.accept)
            layout.addWidget(btn_ok)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                interval = interval_spin.value()
                timeout = timeout_spin.value()
                search_text = text_input.text().strip()
                if search_text:
                    command = f'ETextWait({interval},{timeout},"{search_text}")\n'
                    self.insert_at_cursor(command)
                    self.append_to_log(f'⏳ Добавлен ETextWait: интервал={interval}с, таймаут={timeout}с, текст="{search_text}"')
                else:
                    QMessageBox.warning(self, "Ошибка", "Введите текст для поиска!")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка добавления ETextWait: {e}")
    
    def add_eimg_wait_command(self):
        try:
            templates = self.image_finder.get_available_templates()
            if not templates:
                folder = self.image_finder.get_image_folder()
                folder.mkdir(exist_ok=True)
                QMessageBox.information(self, "Нет шаблонов", f"Папка {folder} пуста!\nПоложите картинки (.png/.jpg) в папку изображений.")
                return
            dialog = QDialog(self)
            dialog.setWindowTitle("EIMGWait - Ждать изображение")
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Интервал опроса (сек):"))
            interval_spin = QDoubleSpinBox()
            interval_spin.setRange(0.1, 10.0)
            interval_spin.setValue(1.0)
            interval_spin.setDecimals(1)
            layout.addWidget(interval_spin)
            layout.addWidget(QLabel("Таймаут ожидания (сек):"))
            timeout_spin = QDoubleSpinBox()
            timeout_spin.setRange(1.0, 300.0)
            timeout_spin.setValue(30.0)
            timeout_spin.setDecimals(1)
            layout.addWidget(timeout_spin)
            layout.addWidget(QLabel("Выберите изображение:"))
            combo = QComboBox()
            combo.addItems(sorted(templates))
            combo.setEditable(True)
            layout.addWidget(combo)
            btn_ok = QPushButton("OK")
            btn_ok.clicked.connect(dialog.accept)
            layout.addWidget(btn_ok)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                interval = interval_spin.value()
                timeout = timeout_spin.value()
                image_name = combo.currentText().strip()
                if image_name.lower().endswith('.png') or image_name.lower().endswith('.jpg') or image_name.lower().endswith('.jpeg'):
                    image_name = os.path.splitext(image_name)[0]
                command = f'EIMGWait({interval},{timeout},"{image_name}")\n'
                self.insert_at_cursor(command)
                self.append_to_log(f'⏳ Добавлен EIMGWait: интервал={interval}с, таймаут={timeout}с, изображение="{image_name}"')
        except Exception as e:
            self.append_to_log(f"❌ Ошибка добавления EIMGWait: {e}")
    
    def add_text_search_command(self):
        try:
            if not self.text_finder.ocr_available:
                QMessageBox.warning(self, "OCR недоступен", "Библиотека pytesseract не установлена!\nУстановите: pip install pytesseract pillow")
                return
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Поиск текста")
            dialog.setLabelText("Введите текст для поиска (например: Пропустить):")
            dialog.setTextValue("")
            if dialog.exec() == QInputDialog.DialogCode.Accepted:
                search_text = dialog.textValue().strip()
                if search_text:
                    command = f"TEXT:{search_text}\n"
                    self.insert_at_cursor(command)
                    self.append_to_log(f"🔍 Добавлен поиск текста: TEXT:{search_text} [курсор без клика]")
                else:
                    QMessageBox.warning(self, "Ошибка", "Введите текст для поиска!")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка добавления поиска текста: {e}")
    
    def add_loop_command(self):
        try:
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Цикл")
            dialog.setLabelText("Введите количество повторений (0 = бесконечный цикл):")
            dialog.setInputMode(QInputDialog.InputMode.IntInput)
            dialog.setIntValue(10)
            dialog.setIntMinimum(0)
            dialog.setIntMaximum(1000)
            if dialog.exec() == QInputDialog.DialogCode.Accepted:
                loop_count = dialog.intValue()
                if loop_count == 0:
                    self.append_to_log("🔄 Добавлен БЕСКОНЕЧНЫЙ цикл (до F1 или конца аккаунтов)")
                else:
                    self.append_to_log(f"🔄 Добавлен цикл: {loop_count} повторений")
                command = f"НАЧАЛО_ЦИКЛА({loop_count})\n# Ваши команды здесь\nКОНЕЦ_ЦИКЛА\n"
                self.insert_at_cursor(command)
        except Exception as e:
            self.append_to_log(f"❌ Ошибка добавления цикла: {e}")
    
    def add_etext_command(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Ввод текста (EText)")
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Введите текст или используйте константы:"))
            text_input = QLineEdit()
            text_input.setPlaceholderText("Текст или {EMAIL} или {PASSWORD}")
            layout.addWidget(text_input)
            info = QLabel("💡 {EMAIL} - вставит email текущего аккаунта\n💡 {PASSWORD} - вставит пароль текущего аккаунта")
            info.setStyleSheet("color: #f39c12; font-size: 11px;")
            layout.addWidget(info)
            btn_layout = QHBoxLayout()
            btn_ok = QPushButton("OK")
            btn_ok.clicked.connect(dialog.accept)
            btn_cancel = QPushButton("Отмена")
            btn_cancel.clicked.connect(dialog.reject)
            btn_layout.addWidget(btn_ok)
            btn_layout.addWidget(btn_cancel)
            layout.addLayout(btn_layout)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                text = text_input.text().strip()
                if text:
                    command = f"EText:{text}\n"
                    self.insert_at_cursor(command)
                    if text == '{EMAIL}':
                        self.append_to_log("⌨️ Добавлен ввод EMAIL аккаунта: EText:{EMAIL}")
                    elif text == '{PASSWORD}':
                        self.append_to_log("⌨️ Добавлен ввод PASSWORD аккаунта: EText:{PASSWORD}")
                    else:
                        self.append_to_log(f"⌨️ Добавлен ввод текста: EText:{text[:30]}...")
                else:
                    QMessageBox.warning(self, "Ошибка", "Введите текст!")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка добавления EText: {e}")
    
    def add_img_command(self):
        try:
            templates = self.image_finder.get_available_templates()
            if not templates:
                folder = self.image_finder.get_image_folder()
                folder.mkdir(exist_ok=True)
                QMessageBox.information(self, "Нет шаблонов", f"Папка {folder} пуста!\nПоложите картинки (.png/.jpg) в папку изображений.")
                return
            dialog = QInputDialog(self)
            dialog.setWindowTitle("🖼️ Выбор изображения")
            dialog.setLabelText(f"Выберите изображение (папка: {self.image_finder.get_folder_path()}) (найдено: {len(templates)})")
            dialog.setComboBoxItems(sorted(templates))
            dialog.setComboBoxEditable(True)
            if dialog.exec() == QInputDialog.DialogCode.Accepted:
                image_name = dialog.textValue().strip()
                if image_name:
                    if image_name.lower().endswith('.png') or image_name.lower().endswith('.jpg') or image_name.lower().endswith('.jpeg'):
                        image_name = os.path.splitext(image_name)[0]
                    command = f"IMG:{image_name}\n"
                    self.insert_at_cursor(command)
                    self.append_to_log(f"🖼️ Добавлен поиск изображения: IMG:{image_name}")
                else:
                    QMessageBox.warning(self, "Ошибка", "Введите название изображения!")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка добавления IMG: {e}")
    
    def capture_coordinate(self):
        if self.is_capturing:
            self.append_to_log("⚠️ Уже идёт захват координаты!")
            return
        self.is_capturing = True
        try:
            self.save_cursor_position()
            hwnds = []
            def callback(hwnd, lparam):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        proc = psutil.Process(pid)
                        if proc.name().lower() == "infinitemagicraid.exe":
                            hwnds.append(hwnd)
                except:
                    pass
                return True
            win32gui.EnumWindows(callback, 0)
            if not hwnds:
                self.append_to_log("❌ Окно игры не найдено! Запустите игру.")
                self.is_capturing = False
                QMessageBox.warning(self, "Ошибка", "Окно игры не найдено!\nЗапустите Infinitemagicraid.exe")
                return
            game_hwnd = hwnds[0]
            self.append_to_log("🎯 Окно игры найдено, готовимся к захвату...")
            win32gui.ShowWindow(game_hwnd, 9)
            win32gui.SetForegroundWindow(game_hwnd)
            time.sleep(0.5)
            self.append_to_log("🎯 Сворачиваю бот... Кликните ОДИН раз в окне игры!")
            self.showMinimized()
            time.sleep(0.3)
            win32gui.SetForegroundWindow(game_hwnd)
            time.sleep(0.2)
            clicked = False
            click_coords = None
            click_event = threading.Event()
            def on_click_listener():
                nonlocal clicked, click_coords
                try:
                    import mouse
                    start_time = time.time()
                    last_state = False
                    while time.time() - start_time < 15 and not clicked:
                        if keyboard.is_pressed('esc'):
                            self.append_to_log("❌ Захват отменён (Esc)")
                            click_event.set()
                            return
                        current_state = mouse.is_pressed('left')
                        if current_state and not last_state:
                            time.sleep(0.05)
                            x, y = pyautogui.position()
                            click_coords = (x, y)
                            clicked = True
                            self.append_to_log(f"✓ Клик зафиксирован: ({x}, {y})")
                            click_event.set()
                            return
                        last_state = current_state
                        time.sleep(0.02)
                    if not clicked:
                        self.append_to_log("❌ Таймаут ожидания клика (15 сек)")
                        click_event.set()
                except ImportError:
                    self.append_to_log("❌ Библиотека mouse не установлена!")
                    click_event.set()
                except Exception as e:
                    self.append_to_log(f"❌ Ошибка захвата: {e}")
                    click_event.set()
            listener_thread = threading.Thread(target=on_click_listener, daemon=True)
            listener_thread.start()
            click_event.wait(timeout=16)
            self.showNormal()
            self.activateWindow()
            time.sleep(0.2)
            if clicked and click_coords:
                try:
                    x, y = click_coords
                    rect = win32gui.GetClientRect(game_hwnd)
                    w, h = rect[2], rect[3]
                    left, top = win32gui.ClientToScreen(game_hwnd, (0, 0))
                    if left <= x <= left + w and top <= y <= top + h:
                        rx = round((x - left) / w, 2) if w > 0 else 0.5
                        ry = round((y - top) / h, 2) if h > 0 else 0.5
                        rx = max(0, min(1, rx))
                        ry = max(0, min(1, ry))
                        command = f"CLICK:{rx:.2f},{ry:.2f}\n"
                        self.insert_at_cursor(command)
                        self.append_to_log(f"✅ Координата захвачена: CLICK:{rx:.2f},{ry:.2f}")
                    else:
                        self.append_to_log("⚠️ Клик был вне окна игры! Попробуйте ещё раз.")
                except Exception as e:
                    self.append_to_log(f"❌ Ошибка обработки координат: {e}")
            else:
                self.append_to_log("❌ Клик не зафиксирован")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка захвата координаты: {e}")
        finally:
            self.is_capturing = False
    
    def start_server_recording(self):
        if self.is_recording_server:
            self.append_to_log("⚠️ Уже идёт запись выбора сервера!")
            return
        try:
            self.is_recording_server = True
            hwnds = []
            def callback(hwnd, lparam):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        proc = psutil.Process(pid)
                        if proc.name().lower() == "infinitemagicraid.exe":
                            hwnds.append(hwnd)
                except:
                    pass
                return True
            win32gui.EnumWindows(callback, 0)
            if not hwnds:
                QMessageBox.warning(self, "Ошибка", "Окно игры не найдено!\nЗапустите игру перед записью.")
                self.append_to_log("❌ Окно игры не найдено!")
                self.is_recording_server = False
                return
            self.game_hwnd = hwnds[0]
            win32gui.ShowWindow(self.game_hwnd, 9)
            win32gui.SetForegroundWindow(self.game_hwnd)
            self.btn_server_record.setEnabled(False)
            self.btn_server_record.setText("Идёт запись... (F2 для остановки)")
            self.btn_server_record.setStyleSheet("background: #e74c3c; color: white; height: 40px; font-weight: bold;")
            self.append_to_log("🔴 ЗАПИСЬ ВЫБОРА СЕРВЕРА НАЧАТА")
            self.append_to_log("ИНСТРУКЦИЯ:")
            self.append_to_log("1. Зажмите ЛКМ в начальной точке")
            self.append_to_log("2. Перетащите курсор в нужное место")
            self.append_to_log("3. Отпустите ЛКМ")
            self.append_to_log("4. Нажмите F2 для остановки записи")
            self.server_recorder.start_recording(self.game_hwnd)
        except Exception as e:
            self.append_to_log(f"❌ Ошибка запуска записи: {e}")
            self.is_recording_server = False
            self.btn_server_record.setEnabled(True)
            self.btn_server_record.setText("Запись выбора сервера")
            self.btn_server_record.setStyleSheet("background: #e67e22; color: white; height: 40px; font-weight: bold;")
            QMessageBox.critical(self, "Ошибка", f"Не удалось начать запись:\n{e}")
    
    def stop_server_recording(self):
        if not self.is_recording_server:
            return
        try:
            self.is_recording_server = False
            self.server_recorder.stop_recording()
            self.macro_folder_path.mkdir(exist_ok=True)
            saved_path = self.server_recorder.save_server_macro(self.server_macro_path)
            self.btn_server_record.setEnabled(True)
            self.btn_server_record.setText("Запись выбора сервера")
            self.btn_server_record.setStyleSheet("background: #e67e22; color: white; height: 40px; font-weight: bold;")
            events_count = len(self.server_recorder.events)
            down_count = sum(1 for e in self.server_recorder.events if e['type'] == 'MOUSE_DOWN')
            drag_count = sum(1 for e in self.server_recorder.events if e['type'] == 'MOUSE_DRAG')
            up_count = sum(1 for e in self.server_recorder.events if e['type'] == 'MOUSE_UP')
            self.lbl_server_status.setText(f"Статус: записано ({down_count} нажатий, {drag_count} перетаскиваний, {up_count} отпусканий)")
            self.lbl_server_status.setStyleSheet("color: #27ae60;")
            self.append_to_log("⏹️ ЗАПИСЬ ВЫБОРА СЕРВЕРА ОСТАНОВЛЕНА")
            self.append_to_log(f"Сохранено {events_count} событий в {self.server_macro_path}")
            self.append_to_log(f"   Нажатий: {down_count}, Перетаскиваний: {drag_count}, Отпусканий: {up_count}")
            self.showNormal()
            self.activateWindow()
            self.save_config()
        except Exception as e:
            self.append_to_log(f"❌ Ошибка остановки записи: {e}")
            self.is_recording_server = False
            self.btn_server_record.setEnabled(True)
            self.btn_server_record.setText("Запись выбора сервера")
            self.btn_server_record.setStyleSheet("background: #e67e22; color: white; height: 40px; font-weight: bold;")
    
    def load_file(self):
        if self.is_loading_file:
            return
        try:
            self.is_loading_file = True
            self.append_to_log("\n🔄 Выбор файла аккаунтов...")
            p, _ = QFileDialog.getOpenFileName(self, "Выберите файл аккаунтов", "", "Текстовые файлы (*.txt)")
            if p:
                self.accounts_file_path = p
                self.path_label.setText(p)
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        self.accounts = [line.strip() for line in f if line.strip()]
                    self.count_label.setText(f"Аккаунтов: {len(self.accounts)}")
                    self.append_to_log(f"✅ Загружено: {len(self.accounts)} аккаунтов")
                    self.save_config()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")
        except Exception as e:
            self.append_to_log(f"❌ Ошибка загрузки файла: {e}")
        finally:
            self.is_loading_file = False
    
    def cleanup_worker(self):
        try:
            if self.worker:
                self.worker.running = False
                self.worker = None
            if self.thread and self.thread.isRunning():
                self.thread.quit()
                self.thread.wait(2000)
            self.thread = None
        except Exception as e:
            self.append_to_log(f"❌ Ошибка очистки воркера: {e}")
    
    def start_bot(self):
        if self.is_bot_running:
            QMessageBox.warning(self, "Внимание", "Бот уже запущен!")
            return
    
        if self.chk_use_server.isChecked():
            if not self.server_recorder.is_recorded() and not self.server_macro_path.exists():
                QMessageBox.warning(self, "Ошибка", "Сначала выполните запись выбора сервера!")
                return
    
        if not self.accounts:
            QMessageBox.warning(self, "Внимание", "Загрузите файл с аккаунтами!")
            return
    
        self.cleanup_worker()
    
        active_macro = self.macro_editor.toPlainText() if self.macro_editor else ""
        if not active_macro.strip():
            reply = QMessageBox.question(self, "Макрос пуст", 
                "Редактор макросов пуст! Запустить только авторизацию?", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
    
        self.is_bot_running = True
    
        # ✅ ДОБАВЛЕНО: Обновление статуса
        self.update_bot_status(running=True)
    
        self.btn_run.setEnabled(False)
        self.btn_macro_only.setEnabled(False)
        self.btn_pause.setEnabled(True)
    
        self.thread = QThread()
        use_server_selection = self.chk_use_server.isChecked() if hasattr(self, 'chk_use_server') else False
    
        if use_server_selection:
            self.append_to_log("🔹 Выбор сервера будет выполнен (по записанному макросу)")
    
        self.worker = BotWorker(
            self.accounts, 
            active_macro=active_macro, 
            run_macro_only=False, 
            use_server_selection=use_server_selection, 
            server_macro_path=str(self.server_macro_path) if use_server_selection else None, 
            image_folder_path=self.image_finder.get_folder_path()
        )
    
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.log_msg.connect(self.append_to_log)
        self.worker.update_acc_label.connect(self.acc_display.setText if hasattr(self, 'acc_display') else lambda x: None)
        self.worker.update_current_line.connect(self.macro_editor.highlight_current_line if self.macro_editor else lambda x: None)
        self.worker.finished.connect(self.bot_finished)
        self.thread.start()
    
    def start_macro_only(self):
        if self.is_bot_running:
            QMessageBox.warning(self, "Внимание", "Бот уже запущен!")
            return
    
        self.cleanup_worker()
    
        active_macro = self.macro_editor.toPlainText() if self.macro_editor else ""
        if not active_macro.strip():
            QMessageBox.warning(self, "Внимание", 
                "Редактор макросов пуст!\nЗагрузите или создайте макрос.")
            return
    
        self.is_bot_running = True
    
        # ✅ ДОБАВЛЕНО: Обновление статуса
        self.update_bot_status(running=True)
    
        self.btn_run.setEnabled(False)
        self.btn_macro_only.setEnabled(False)
        self.btn_pause.setEnabled(True)
    
        self.thread = QThread()
        self.worker = BotWorker(
            self.accounts, 
            active_macro=active_macro, 
            run_macro_only=True, 
            use_server_selection=False, 
            server_macro_path=None, 
            image_folder_path=self.image_finder.get_folder_path()
        )
    
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.log_msg.connect(self.append_to_log)
        self.worker.update_acc_label.connect(self.acc_display.setText if hasattr(self, 'acc_display') else lambda x: None)
        self.worker.update_current_line.connect(self.macro_editor.highlight_current_line if self.macro_editor else lambda x: None)
        self.worker.finished.connect(self.bot_finished)
        self.thread.start()
    
    def bot_finished(self, msg):
        if not self.is_bot_running:
            return
    
        self.append_to_log(f"\n{msg}")
    
        # ✅ ДОБАВЛЕНО: Обновление статуса
        self.update_bot_status(running=False)
    
        self.btn_run.setEnabled(True)
        self.btn_macro_only.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("⏸️ ПАУЗА (F5)")
        self.btn_pause.setStyleSheet("background: #f39c12; color: white; height: 60px; font-weight: bold; font-size: 14px;")
        self.is_bot_running = False
        self.save_config()
    
    def emergency_stop(self):
        try:
            self.append_to_log("\n<b style='color:red;'>⛔ СТОП (F1) - Экстренная остановка</b>")
        
            if self.worker:
                try:
                    self.worker.running = False
                    self.worker.paused = False
                    self.worker.pause_event.set()
                except Exception as e:
                    self.append_to_log(f"⚠️ Ошибка остановки воркера: {e}")
        
            self.is_bot_running = False
            self.is_capturing = False
            self.is_recording_server = False
            self.is_macro_operation = False
            self.is_loading_file = False
        
            # ✅ ДОБАВЛЕНО: Обновление статуса
            self.update_bot_status(running=False)
        
            try:
                self.btn_run.setEnabled(True)
                self.btn_macro_only.setEnabled(True)
                self.btn_pause.setEnabled(False)
                self.btn_pause.setText("⏸️ ПАУЗА (F5)")
                self.btn_pause.setStyleSheet("background: #f39c12; color: white; height: 60px; font-weight: bold; font-size: 14px;")
            except Exception as e:
                self.append_to_log(f"⚠️ Ошибка восстановления кнопок: {e}")
        
            try:
                if self.macro_editor:
                    self.macro_editor.setExtraSelections([])
            except Exception as e:
                self.append_to_log(f"⚠️ Ошибка очистки подсветки: {e}")
        
            try:
                if self.thread and self.thread.isRunning():
                    self.thread.quit()
                    self.thread.wait(2000)
            except Exception as e:
                self.append_to_log(f"⚠️ Ошибка остановки потока: {e}")
        
            self.append_to_log("<b style='color:red;'>✅ Выполнение остановлено</b>")
        
        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в emergency_stop: {e}")
            print(traceback.format_exc())
            try:
                self.is_bot_running = False
                self.update_bot_status(running=False)
                self.btn_run.setEnabled(True)
                self.btn_macro_only.setEnabled(True)
                self.btn_pause.setEnabled(False)
            except:
                pass
    
    def closeEvent(self, event):
        try:
            if self.worker:
                self.worker.running = False
            if self.thread and self.thread.isRunning():
                self.thread.quit()
                self.thread.wait(2000)
            name = self.macro_name_input.text().strip()
            if name:
                content = self.macro_editor.toPlainText()
                self.macro_folder_path.mkdir(exist_ok=True)
                if not name.endswith('.txt'):
                    name += '.txt'
                path = self.macro_folder_path / name
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.save_config()
                self.append_to_log(f"💾 Макрос автосохранён: {name}")
            event.accept()
        except Exception as e:
            print(f"❌ Ошибка при закрытии: {e}")
            event.accept()


# ============================================
# 🔹 ГЛАВНАЯ ТОЧКА ВХОДА
# ============================================
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = InfiniteBotApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Критическая ошибка запуска: {e}")
        print(traceback.format_exc())
        sys.exit(1)




