import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ExcelHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = 0
        self.file_to_watch = 'การประเมิน HS4.xlsx'
        self.script_to_run = 'update_dashboard.py'

    def on_modified(self, event):
        # ตรวจสอบว่าเป็นไฟล์ Excel ที่เราสนใจหรือไม่
        if event.src_path.endswith(self.file_to_watch):
            # ป้องกันการรันซ้ำซ้อนในเสี้ยววินาที (Debounce)
            current_time = time.time()
            if current_time - self.last_modified > 2:
                print(f"Detected changes in {self.file_to_watch}. Updating dashboard...")
                try:
                    # รันสคริปต์อัปเดตที่เราทำไว้ก่อนหน้า
                    subprocess.run(['python', self.script_to_run], check=True)
                    self.last_modified = current_time
                except Exception as e:
                    print(f"Error updating dashboard: {e}")

if __name__ == "__main__":
    print("Auto-Update System Started...")
    print("Monitoring 'การประเมิน HS4.xlsx'. Press Ctrl+C to stop.")
    
    event_handler = ExcelHandler()
    observer = Observer()
    # เฝ้าดูในโฟลเดอร์ปัจจุบัน (.)
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
