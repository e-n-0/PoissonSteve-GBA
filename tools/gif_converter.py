#!/usr/bin/env python3
"""
GIF to GBA Converter

This script converts a GIF animation to a format compatible with GBA development.
It outputs C arrays that can be included directly in GBA projects.
"""

import sys
import os
from PIL import Image
import argparse

def rgb_to_gba_rgb16(r, g, b):
    """Convert RGB values (0-255) to GBA RGB16 format (5-5-5)"""
    r = (r >> 3) & 0x1F
    g = (g >> 3) & 0x1F
    b = (b >> 3) & 0x1F
    return r | (g << 5) | (b << 10)

def convert_gif(gif_path, output_path, var_name, input_fps=20):
    """Convert a GIF to a C header file with frame data"""
    if not os.path.exists(gif_path):
        print(f"Error: File '{gif_path}' not found")
        return False
    
    try:
        gif = Image.open(gif_path)
    except Exception as e:
        print(f"Error opening GIF file: {e}")
        return False
    
    # Get GIF info
    is_animated = getattr(gif, "is_animated", False)
    if not is_animated:
        print("Warning: GIF is not animated, will only convert the single frame")
    
    # GBA screen dimensions
    gba_width = 240
    gba_height = 160
    
    # Original GIF dimensions
    width, height = gif.size
    
    # Calculate scaling factors to fit GBA screen
    scale_x = gba_width / width
    scale_y = gba_height / height
    scale = min(scale_x, scale_y)
    
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Calculate position to center the image
    pos_x = (gba_width - new_width) // 2
    pos_y = (gba_height - new_height) // 2
    
    frames = []
    durations = []
    
    # Process all frames
    frame_count = 0
    try:
        while True:
            # Convert and resize frame
            frame = gif.convert('RGB')
            frame = frame.resize((new_width, new_height), Image.LANCZOS)
            
            # Create a full GBA screen-sized frame
            full_frame = Image.new('RGB', (gba_width, gba_height), (0, 0, 0))
            full_frame.paste(frame, (pos_x, pos_y))
            
            # Convert to GBA format
            pixels = []
            for y in range(gba_height):
                for x in range(gba_width):
                    r, g, b = full_frame.getpixel((x, y))
                    pixels.append(rgb_to_gba_rgb16(r, g, b))
            
            frames.append(pixels)
            
            # Calculate duration based on fixed input FPS
            # Convert input FPS to frames at 60fps (GBA refresh rate)
            # For 20fps input: 60/20 = 3 GBA frames per input frame
            frames_duration = round(60 / input_fps)
            durations.append(frames_duration)
            
            frame_count += 1
            
            # Move to next frame
            gif.seek(gif.tell() + 1)
            
    except EOFError:
        # We've reached the end of the sequence
        pass
    
    # Generate C header file
    with open(output_path, 'w') as out:
        out.write("// Auto-generated GIF to GBA conversion\n")
        out.write("// Original file: " + os.path.basename(gif_path) + "\n")
        out.write(f"// Input framerate: {input_fps} fps\n\n")
        
        out.write("#ifndef " + var_name.upper() + "_H\n")
        out.write("#define " + var_name.upper() + "_H\n\n")
        
        out.write("#include <gba_types.h>\n\n")
        
        # Write each frame
        for i, frame_data in enumerate(frames):
            out.write(f"// Frame {i}\n")
            out.write(f"const u16 {var_name}_frame{i}[{gba_width * gba_height}] = {{\n    ")
            
            # Write pixel data
            for j, pixel in enumerate(frame_data):
                out.write(f"0x{pixel:04X}")
                if j < len(frame_data) - 1:
                    out.write(", ")
                if (j + 1) % 12 == 0:
                    out.write("\n    ")
            
            out.write("\n};\n\n")
        
        # Write frame array
        out.write(f"// Frame pointers\n")
        out.write(f"const u16* const {var_name}_frames[{frame_count}] = {{\n    ")
        for i in range(frame_count):
            out.write(f"{var_name}_frame{i}")
            if i < frame_count - 1:
                out.write(", ")
            if (i + 1) % 5 == 0:
                out.write("\n    ")
        out.write("\n};\n\n")
        
        # Write durations
        out.write(f"// Frame durations (in frames at 60fps)\n")
        out.write(f"// Fixed duration of {frames_duration} frames for {input_fps}fps input\n")
        out.write(f"const u16 {var_name}_durations[{frame_count}] = {{\n    ")
        for i, duration in enumerate(durations):
            out.write(f"{duration}")
            if i < len(durations) - 1:
                out.write(", ")
            if (i + 1) % 10 == 0:
                out.write("\n    ")
        out.write("\n};\n\n")
        
        # Write animation info
        out.write(f"// Animation info\n")
        out.write(f"const u16 {var_name}_frame_count = {frame_count};\n")
        
        out.write("\n#endif // " + var_name.upper() + "_H\n")
    
    print(f"Successfully converted GIF to {output_path}")
    print(f"Generated {frame_count} frames with {frames_duration} frame duration each (for {input_fps}fps source)")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Convert GIF to GBA-compatible format')
    parser.add_argument('gif_file', help='Input GIF file path')
    parser.add_argument('-o', '--output', help='Output header file path')
    parser.add_argument('-n', '--name', help='Variable name to use in output (default: animation)')
    parser.add_argument('-f', '--fps', type=int, default=20, help='Input GIF framerate (default: 20)')
    
    args = parser.parse_args()
    
    gif_path = args.gif_file
    
    # Default output path is the input filename with .h extension
    if args.output:
        output_path = args.output
    else:
        output_path = os.path.splitext(gif_path)[0] + '.h'
    
    # Default variable name
    var_name = args.name if args.name else 'animation'
    
    convert_gif(gif_path, output_path, var_name, args.fps)

if __name__ == "__main__":
    main() 