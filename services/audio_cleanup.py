import os
import time
import logging
from config import settings

def purge_stale_audio(audio_dir: str = settings.AUDIO_DIR, max_age_seconds: int = settings.AUDIO_RETENTION_SECONDS):
    """
    Scans the audio directory and removes files older than max_age_seconds.
    Reads defaults dynamically from config settings.
    """
    if not os.path.exists(audio_dir):
        return

    now = time.time()
    deleted_count = 0

    for filename in os.listdir(audio_dir):
        file_path = os.path.join(audio_dir, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    logging.error(f"[Cleanup Error] Could not delete {filename}: {e}")

    if deleted_count > 0:
        logging.info(f"[Audio Retention Engine] Automatically purged {deleted_count} expired audio file(s).")