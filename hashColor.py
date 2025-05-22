import random
import hashlib

def hashColor(seed):
    # Create a hash from the seed string to ensure consistent output for the same seed
    hash_object = hashlib.md5(seed.encode())
    hash_hex = hash_object.hexdigest()
    
    # Use the first 6 characters of the hash to generate RGB values
    r = int(hash_hex[:2], 16)
    g = int(hash_hex[2:4], 16)
    b = int(hash_hex[4:6], 16)
    
    # Ensure the color is not too bright by capping the maximum value
    max_brightness = 200
    min_brightness = 80
    r = min(max(r, min_brightness), max_brightness)
    g = min(max(g, min_brightness), max_brightness)
    b = min(max(b, min_brightness), max_brightness)
    
    # Return the color as an RGB string
    return f"rgb({r},{g},{b})"