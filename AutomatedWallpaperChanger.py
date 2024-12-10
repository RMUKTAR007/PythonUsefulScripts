import requests
import ctypes
import os
import time
import schedule
from datetime import datetime

class WallpaperChanger:
    def __init__(self):
        # Your Unsplash API key (sign up at https://unsplash.com/developers)
        self.api_key = "TUM500767sObegcCxfRSincBESXGNlSaBQcIfqEYHGE"
        
        # Create a folder for wallpapers if it doesn't exist
        self.wallpaper_dir = os.path.join(os.path.expanduser("~"), "Wallpapers")
        if not os.path.exists(self.wallpaper_dir):
            os.makedirs(self.wallpaper_dir)
            
    def get_random_image(self, query="nature"):
        """Fetch a random image from Unsplash"""
        url = "https://api.unsplash.com/photos/random"



        headers = {"Authorization": f"Client-ID {self.api_key}"}
        params = {
            "query": query,
            "orientation": "landscape",
            "content_filter": "high"
        }
        
        for attempt in range(3):  # Retry up to 3 times
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                return data["urls"]["full"], data["user"]["name"]
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: Error fetching image: {str(e)}")
                time.sleep(5)  # Wait before retrying
        return None, None

    def download_image(self, image_url, photographer):
        """Download the image and save it"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Create filename with timestamp and photographer name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wallpaper_{timestamp}_{photographer.replace(' ', '_')}.jpg"
            filepath = os.path.join(self.wallpaper_dir, filename)
            
            # Save the image
            with open(filepath, "wb") as f:
                f.write(response.content)
                
            return filepath
            
        except Exception as e:
            
            print(f"Error downloading image: {str(e)}")
            return None

    def set_wallpaper(self, image_path):
        """Set the wallpaper on Windows"""
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            print(f"Wallpaper changed successfully at {datetime.now().strftime('%H:%M:%S')}")
            return True
        except Exception as e:
            print(f"Error setting wallpaper: {str(e)}")
            return False

    def cleanup_old_wallpapers(self, keep_last=10):
        """Delete old wallpapers to save space"""
        try:
            wallpapers = [f for f in os.listdir(self.wallpaper_dir) if f.endswith('.jpg')]
            wallpapers.sort(reverse=True)
            
            for wallpaper in wallpapers[keep_last:]:
                os.remove(os.path.join(self.wallpaper_dir, wallpaper))
                
        except Exception as e:
            print(f"Error cleaning up wallpapers: {str(e)}")

    def change_wallpaper(self, query="nature"):
        """Main function to change wallpaper"""
        print("\nFetching new wallpaper...")
        
        # Get random image URL and photographer name
        image_url, photographer = self.get_random_image(query)
        if not image_url:
            return
            
        # Download the image
        image_path = self.download_image(image_url, photographer)
        if not image_path:
            return
            
        # Set as wallpaper
        if self.set_wallpaper(image_path):
            print(f"Photo by: {photographer}")
            
        # Cleanup old wallpapers
        self.cleanup_old_wallpapers()

def main():
    changer = WallpaperChanger()
    
    # Get user preferences
    print("Wallpaper Changer Settings")
    print("-------------------------")
    query = input("Enter image category (e.g., nature, city, abstract) [default: nature]: ").strip() or "nature"
    interval = int(input("Enter change interval in minutes [default: 1]: ").strip() or "1")
    
    # Schedule the wallpaper change
    schedule.every(interval).minutes.do(changer.change_wallpaper, query=query)
    
    # Initial change
    changer.change_wallpaper(query)
    
    print(f"\nWallpaper will change every {interval} minute(s)")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nWallpaper changer stopped")

if __name__ == "__main__":
    main()