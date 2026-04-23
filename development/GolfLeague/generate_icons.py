#!/usr/bin/env python3
"""
Generate iOS and PWA icon PNGs using pure PIL (no cairo dependency).
"""

import os
import sys

def generate_icons():
    """Generate icon PNGs in various sizes using PIL."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Error: PIL/Pillow not found.")
        print("Please install: pip install pillow")
        sys.exit(1)
    
    # Icon sizes needed
    sizes = {
        'apple-touch-icon.png': 180,
        'icon-192.png': 192,
        'icon-512.png': 512
    }
    
    static_dir = "static"
    os.makedirs(static_dir, exist_ok=True)
    
    print("Generating icons...")
    
    for filename, size in sizes.items():
        output_path = os.path.join(static_dir, filename)
        
        # Create image with dark background
        img = Image.new('RGBA', (size, size), (15, 23, 42, 255))  # #0f172a
        
        draw = ImageDraw.Draw(img)
        
        # Draw golf ball (white circle with dimples)
        center_x, center_y = size // 2, size // 2 - size // 12
        ball_radius = size // 4
        
        # Main ball
        draw.ellipse(
            [center_x - ball_radius, center_y - ball_radius,
             center_x + ball_radius, center_y + ball_radius],
            fill=(255, 255, 255, 255)
        )
        
        # Add dimples (small circles)
        dimple_radius = max(2, size // 64)
        dimple_positions = [
            (-0.3, -0.3), (0.0, -0.4), (0.3, -0.3),
            (-0.4, 0.0), (0.4, 0.0),
            (-0.3, 0.3), (0.0, 0.4), (0.3, 0.3),
            (-0.2, -0.1), (0.2, -0.1), (-0.2, 0.1), (0.2, 0.1)
        ]
        
        for dx, dy in dimple_positions:
            x = center_x + int(dx * ball_radius)
            y = center_y + int(dy * ball_radius)
            draw.ellipse(
                [x - dimple_radius, y - dimple_radius,
                 x + dimple_radius, y + dimple_radius],
                fill=(226, 232, 240, 200)  # Light gray for dimples
            )
        
        # Draw flag pole
        pole_width = max(3, size // 80)
        pole_x = center_x
        pole_top = center_y + ball_radius + size // 12
        pole_bottom = size - size // 6
        draw.line(
            [pole_x, pole_top, pole_x, pole_bottom],
            fill=(34, 197, 94, 255),  # Electric green
            width=pole_width
        )
        
        # Draw flag (triangle)
        flag_points = [
            (pole_x, pole_top),
            (pole_x + size // 6, pole_top + size // 12),
            (pole_x, pole_top + size // 6)
        ]
        draw.polygon(flag_points, fill=(34, 197, 94, 255))
        
        # Add glow effect around ball
        glow_radius = ball_radius + size // 32
        for i in range(3):
            alpha = 40 - i * 10
            offset = i * 2
            draw.ellipse(
                [center_x - glow_radius - offset, center_y - glow_radius - offset,
                 center_x + glow_radius + offset, center_y + glow_radius + offset],
                outline=(34, 197, 94, alpha),
                width=max(1, size // 128)
            )
        
        # Save PNG
        img.save(output_path, 'PNG')
        print(f"[OK] Created {output_path} ({size}x{size})")
    
    print("\nAll icons generated successfully!")
    print("\nIcons created:")
    for filename, size in sizes.items():
        print(f"  - {filename} ({size}x{size})")

if __name__ == "__main__":
    generate_icons()
