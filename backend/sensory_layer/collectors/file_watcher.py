import asyncio
import time
import os
import csv
from typing import Callable, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileDropHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[dict], None]):
        self.callback = callback

    def on_created(self, event):
        if event.is_directory:
            return
            
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        if filename.endswith('.csv'):
            print(f"👀 [SENSORY] File Detected: {filepath}")
            self.process_csv(filepath)
        elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"👁️ [SENSORY] Image Detected: {filepath}")
            self.process_image(filepath)

    def process_csv(self, filepath: str):
        """Reads the CSV and converts rows into BIZIT events."""
        try:
            filename = os.path.basename(filepath)
            time.sleep(0.5)
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    biz_event = {
                        "source": "FILE_SENSOR",
                        "event_type": row.get("event_type", "UNKNOWN_FILE_EVENT").upper(),
                        "timestamp": time.time(),
                        "payload": row,
                        "metadata": {"origin_file": filename}
                    }
                    self.callback(biz_event)
            print(f"✅ [SENSORY] Ingested {filename}")
        except Exception as e:
            print(f"❌ [SENSORY] Error processing CSV: {e}")

    def process_image(self, filepath: str):
        """Visual Cortex Analysis."""
        from PIL import Image
        try:
            time.sleep(0.5)
            with Image.open(filepath) as img:
                width, height = img.size
                
                # Mock Vision Agent Logic
                event = {
                    "source": "VISUAL_CORTEX",
                    "event_type": "VISUAL_ANALYSIS",
                    "timestamp": time.time(),
                    "payload": {
                        "filename": os.path.basename(filepath),
                        "resolution": f"{width}x{height}",
                        "insight": "MARKET_TREND_DETECTED",
                        # Mock: Wide images are bullish, tall are bearish
                        "sentiment": "BULLISH" if width >= height else "BEARISH"
                    }
                }
                self.callback(event)
                print(f"✅ [SENSORY] Vision Agent analyzed {os.path.basename(filepath)}")
        except Exception as e:
            print(f"❌ [SENSORY] Vision Error: {e}")

class FileWatcherCollector:
    def __init__(self, dropzone_path: str, event_callback: Callable[[dict], None]):
        self.path = dropzone_path
        self.callback = event_callback
        self.observer = Observer()

    def start(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path, exist_ok=True)
            
        event_handler = FileDropHandler(self.callback)
        self.observer.schedule(event_handler, self.path, recursive=False)
        self.observer.start()
        print(f"[SENSORY] File Watcher Active at: {self.path}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
