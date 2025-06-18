from PIL import Image
import os

# Open the PNG image
img = Image.open('logo_transparent.png')

# Convert to RGBA if not already
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Create ICO file
img.save('app_icon.ico', format='ICO')
