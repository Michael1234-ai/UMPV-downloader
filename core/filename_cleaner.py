# core/filename_cleaner.py
import re

def clean_filename(name: str) -> str:
    """
    Removes invalid characters from filenames for Windows, macOS, Linux.
    """
    # Remove illegal characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace multiple spaces with a single space
    name = re.sub(r'\s+', ' ', name)
    return name.strip()