import requests
from colorthief import ColorThief
from io import BytesIO

def get_dominant_color_from_url(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_file = BytesIO(response.content)
        color_thief = ColorThief(image_file)
        dominant_color = color_thief.get_color(quality=1)
        return dominant_color
    else:
        raise Exception("Failed to download image")

# Example usage
url = "https://images.genius.com/2562c0f8fcb13b9f8d0f290c17971572.1000x1000x1.png"
dominant_color = get_dominant_color_from_url(url)
print("Dominant Color (RGB):", dominant_color)
