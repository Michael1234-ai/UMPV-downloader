# core/formats.py
from .metadata import get_formats

def list_video_formats(url: str) -> list:
    """
    Returns only video formats (with resolution)
    """
    all_formats = get_formats(url)
    video_formats = [f for f in all_formats if f["resolution"] not in (None, "audio")]
    return video_formats

def list_audio_formats(url: str) -> list:
    """
    Returns only audio formats
    """
    all_formats = get_formats(url)
    audio_formats = [f for f in all_formats if f["resolution"] in (None, "audio")]
    return audio_formats

def get_highest_quality(url: str, kind="video") -> dict:
    """
    Returns the highest quality format for video or audio
    """
    if kind == "video":
        formats = list_video_formats(url)
        # Sort by resolution descending
        formats.sort(key=lambda x: int(x["resolution"].replace("p", "") if x["resolution"] else 0), reverse=True)
    elif kind == "audio":
        formats = list_audio_formats(url)
        # Prefer larger file sizes? yt-dlp doesn't expose in get_formats by default, so just pick first
    else:
        return None

    return formats[0] if formats else None

def get_lowest_quality(url: str, kind="video") -> dict:
    """
    Returns the lowest quality format
    """
    if kind == "video":
        formats = list_video_formats(url)
        formats.sort(key=lambda x: int(x["resolution"].replace("p", "") if x["resolution"] else 0))
    elif kind == "audio":
        formats = list_audio_formats(url)
    else:
        return None

    return formats[0] if formats else None