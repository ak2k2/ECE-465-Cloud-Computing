from PIL import Image
import random


def generate_large_image(width, height, filename):
    # Create a new image with white background
    img = Image.new("RGB", (width, height), "white")
    pixels = img.load()  # Create a pixel map

    # Traverse through the pixels and assign random colors
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i, j] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )

    # Save the image
    img.save(filename)


# Call the function with the dimensions you want
# This is an example and may not be exactly 500 MB. You may need to adjust the dimensions.
generate_large_image(8000, 8000, "large_image.png")
