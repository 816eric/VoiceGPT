import os
import subprocess
import platform
import yt_dlp
import shutil
import time

class YouTube:
    def __init__(self):
        self.browser_process = None
        self.system = platform.system()
        self.youtube_url = None  # Store the URL for matching
        if self.system == "Windows":
            # On Windows, use Microsoft Edge.
            self.browser_cmd = self._find_edge_windows()
            if not self.browser_cmd:
                raise Exception("Microsoft Edge not found on Windows. Please install Edge or provide its full path.")
        elif self.system == "Linux":
            # On Linux, use Google Chrome.
            self.browser_cmd = self._find_chrome_linux()
            if not self.browser_cmd:
                raise Exception("Google Chrome not found on Linux. Please install Chrome or provide its full path.")
        elif self.system == "Darwin":
            # On macOS, use Google Chrome.
            self.browser_cmd = self._find_chrome_mac()
            if not self.browser_cmd:
                raise Exception("Google Chrome not found on macOS. Please install Chrome or provide its full path.")
        else:
            raise Exception("Unsupported OS")
    
    def _find_edge_windows(self):
        edge_path = shutil.which("msedge")
        if edge_path:
            return edge_path
        potential_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for path in potential_paths:
            if os.path.exists(path):
                return path
        return None

    def _find_chrome_linux(self):
        try:
            # Check if chromium-browser is installed
            result = subprocess.run(['which', 'chromium-browser'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # If the result is empty, chromium-browser is not installed
            if not result.stdout:
                raise EnvironmentError("chromium-browser is not installed on this system.")
                return None
            else:
                path = result.stdout.decode().strip()
                print(f"chromium-browser is installed at: {path}")
                return path
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    def _find_chrome_mac(self):
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        return path if os.path.exists(path) else None

    def play_video(self, query):
        """
        Searches YouTube for a video matching the query and opens the YouTube URL directly
        in the browser. On Windows, Microsoft Edge is used.
        """
        search_query = f"ytsearch1:{query}"
        ydl_opts = {'quiet': True, 'noplaylist': True, 'cachedir': False}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            video_info = info['entries'][0] if 'entries' in info else info

        video_id = video_info.get("id")
        self.youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        video_title = video_info.get("title", "Unknown Title")
        print(f"✅ Found video: {video_title}")
        print(f"Opening URL: {self.youtube_url}")

        if self.system == "Windows":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            self.browser_process = subprocess.Popen(
                [self.browser_cmd, "--new-window", self.youtube_url],
                creationflags=creationflags
            )
        else:
            self.browser_process = subprocess.Popen(
                [self.browser_cmd, "--new-window", self.youtube_url]
            )

    def close_video(self):
        """
        Attempts to close the browser window that is displaying YouTube.
        On Windows, enumerates all top-level windows and sends WM_CLOSE to any whose title
        contains "YouTube".
        On Linux/macOS, calls terminate() on the stored process.
        """
        if self.browser_process:
            print("Attempting to close the video...")
            if self.system == "Windows":
                try:
                    import win32gui
                    import win32con

                    def enum_callback(hwnd, results):
                        title = win32gui.GetWindowText(hwnd)
                        if "YouTube" in title:
                            results.append(hwnd)

                    windows = []
                    win32gui.EnumWindows(enum_callback, windows)
                    if windows:
                        for hwnd in windows:
                            print(f"Closing window: {win32gui.GetWindowText(hwnd)}")
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                        # Wait a bit for windows to close
                        time.sleep(2)
                    else:
                        print("Warning: No window with 'YouTube' found to close.")
                except Exception as e:
                    print("Error using win32gui to close window:", e)
            else:
                self.browser_process.terminate()
            self.browser_process = None
        else:
            print("No video process is currently open.")

# Example usage:
if __name__ == "__main__":
    yt = YouTube()
    query = input("Enter search query for YouTube video: ")
    yt.play_video(query)
    input("Press Enter to close the video...")
    yt.close_video()
