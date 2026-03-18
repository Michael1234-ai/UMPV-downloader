# core/metadata.py
import yt_dlp

def get_video_info(url):
    """
    Returns basic video info: title, thumbnail, duration, uploader
    """
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "uploader": info.get("uploader")
    }

def get_formats(url):
    """
    Returns available formats for a video
    """
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    formats = []
    for f in info["formats"]:
        formats.append({
            "format_id": f["format_id"],
            "resolution": f.get("resolution"),
            "ext": f["ext"]
        })
    return formats

def get_playlist_videos(url):
    """
    Returns list of videos from a playlist
    """
    ydl_opts = {"extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(url, download=False)
    videos = []
    for entry in data["entries"]:
        videos.append({"title": entry["title"], "url": entry["url"]})
    return videos