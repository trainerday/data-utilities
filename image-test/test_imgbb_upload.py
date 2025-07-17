#!/usr/bin/env python3
"""
Test script to upload an image to imgbb.
"""

import requests
import base64
from PIL import Image
import io
import os

def create_test_image():
    """Create a simple test image."""
    # Create a simple 200x200 image with text
    img = Image.new('RGB', (200, 200), color='lightblue')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def upload_to_imgbb(api_key, image_data):
    """Upload image to imgbb."""
    
    # Convert image to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # API endpoint
    url = "https://api.imgbb.com/1/upload"
    
    # Prepare data
    data = {
        'key': api_key,
        'image': image_base64,
        'name': 'test-image'
    }
    
    try:
        # Make request
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        if result.get('success'):
            return result['data']['url']
        else:
            print(f"Upload failed: {result}")
            return None
            
    except Exception as e:
        print(f"Error uploading to imgbb: {e}")
        return None

def main():
    """Main function to test imgbb upload."""
    
    api_key = "b53de65dae499fbb17ef3cc4e274e145"
    
    print("Creating test image...")
    image_data = create_test_image()
    
    print("Uploading to imgbb...")
    url = upload_to_imgbb(api_key, image_data)
    
    if url:
        print(f"✅ Upload successful!")
        print(f"Image URL: {url}")
    else:
        print("❌ Upload failed")

if __name__ == "__main__":
    main()