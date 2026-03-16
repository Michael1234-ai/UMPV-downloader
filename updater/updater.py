# updater/updater.py
import requests
import webbrowser

CURRENT_VERSION = "1.0.0"  # Update this with your current app version
REPO_API = "https://api.github.com/repos/yourusername/UltimateDownloader/releases/latest"

class Updater:
    def __init__(self, current_version=CURRENT_VERSION, repo_api=REPO_API):
        self.current_version = current_version
        self.repo_api = repo_api
        self.latest_version = None
        self.latest_url = None

    def check_update(self):
        """
        Check the latest GitHub release and compare with current version
        """
        try:
            response = requests.get(self.repo_api, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.latest_version = data.get("tag_name")
                self.latest_url = data.get("html_url")

                if self.latest_version != self.current_version:
                    return True
                else:
                    return False
            else:
                print(f"Error fetching updates: {response.status_code}")
                return False
        except Exception as e:
            print(f"Update check failed: {e}")
            return False

    def notify_update(self):
        """
        Open the latest release page in browser
        """
        if self.latest_url:
            webbrowser.open(self.latest_url)
        else:
            print("No update URL available.")