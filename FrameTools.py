import json
import EulerHexTools
import re
import os
import numpy as np
from scipy.interpolate import interp1d

#this part was fully written by ai because im lazy and i want to finish it before 2025

def InjectFramesIntoAnimSlot(frame_data, animslot_data):
    """
    Injects frame data into an AnimSlot binary data (first occurrence only).
    """
    # Define the delimiters
    frame_start_delimiter_regex = re.compile(b'\x00\x00\x00[\x00\x01]\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00')
    frame_end_delimiter_regex = re.compile(b'\x0F\x00.\x14..\x00\x00\x01', re.DOTALL)
    
    # Find the first occurrence of the start delimiter
    match_start = frame_start_delimiter_regex.search(animslot_data)
    if not match_start:
        return animslot_data  # No start delimiter found, return original data
    
    start_pos = match_start.start()
    
    # Find the corresponding end delimiter
    match_end = frame_end_delimiter_regex.search(animslot_data, pos=start_pos + len(match_start.group(0)))
    if not match_end:
        return animslot_data  # No end delimiter found, return original data
    
    end_pos = match_end.start()
    
    # Get the frame values
    frame_values = []
    for frame_name, angles in sorted(frame_data.items()):  # Sort to maintain order
        if frame_name.startswith("FRAME"):
            # Convert Euler angles back to hex
            hex_data = EulerHexTools.EulerHex(angles['x'], angles['y'], angles['z'])
            # Convert hex string to bytes
            frame_bytes = bytes.fromhex(hex_data)
            frame_values.append(frame_bytes)
    
    # Combine all frame data
    new_frame_data = b''.join(frame_values)
    
    # Replace the old frame data with the new data
    new_data = bytearray(animslot_data)
    new_data[start_pos + len(match_start.group(0)):end_pos] = new_frame_data
    
    return bytes(new_data)


def ExtractFrames(animslot_path, output_json_path):
    """
    Extracts frame data from the first occurrence in AnimSlot files.
    """
    # Define the delimiters
    frame_start_delimiter_regex = re.compile(b'\x00\x00\x00[\x00\x01]\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00')
    frame_end_delimiter_regex = re.compile(b'\x0F\x00.\x14..\x00\x00\x01', re.DOTALL)

    # Initialize dictionary to store frames from all AnimSlot files
    frames_data = {}

    # Iterate over all AnimSlot files in the directory
    for file_name in sorted(os.listdir(animslot_path)):
        if file_name.startswith("AnimSlot") and file_name.endswith(".bin"):
            file_path = os.path.join(animslot_path, file_name)
            
            with open(file_path, 'rb') as f:
                data = f.read()

            # Find the first occurrence of the start delimiter
            match_start = frame_start_delimiter_regex.search(data)
            if not match_start:
                continue  # Skip if no start delimiter found
            
            start_pos = match_start.start()
            
            # Find the corresponding end delimiter
            match_end = frame_end_delimiter_regex.search(data, pos=start_pos + len(match_start.group(0)))
            if not match_end:
                continue  # Skip if no end delimiter found

            end_pos = match_end.start()
            frame_data = data[start_pos + len(match_start.group(0)):end_pos]

            # Process each 16-byte chunk
            file_frames = {}
            frame_counter = 1
            for i in range(0, len(frame_data), 16):
                frame_chunk = frame_data[i:i+16]
                hex_data = frame_chunk.hex().upper()
                
                # Parse through EulerHexTools.HexEuler()
                roll, pitch, yaw = EulerHexTools.HexEuler(hex_data)
                
                # Create frame entry with the specified format
                frame_name = f"FRAME{frame_counter:02d}"
                frame_counter += 1
                
                file_frames[frame_name] = {
                    "x": roll,
                    "y": pitch,
                    "z": yaw
                }

            # Add processed frames to the main dictionary
            file_name = "TEMP/AnimSlots/" + file_name
            frames_data[file_name] = [file_frames]  # Wrap in list to match desired format

    # Write frames to a JSON file
    try:
        with open(output_json_path, 'w') as json_file:
            json.dump(frames_data, json_file, indent=4)
        print(f"Frames written successfully to {output_json_path}")
    except IOError as e:
        print(f"Error writing to JSON file: {e}")

def Interpolate(data, animslot_key):
    if animslot_key not in data:
        print(f"Animation slot {animslot_key} not found.")
        return data

    for animation in data[animslot_key]:
        frames = list(animation.keys())
        n_frames = len(frames)
        t = np.linspace(0, 1, n_frames)
        
        if n_frames < 2:
            print("Not enough frames for interpolation.")
            continue

        # Get first and last frame values
        first_frame = animation[frames[0]]
        last_frame = animation[frames[-1]]

        # Interpolate for x, y, and z
        for axis in ['x', 'y', 'z']:
            start_value = first_frame[axis]
            end_value = last_frame[axis]
            ease = t**2 * (3 - 2 * t)  # Smoothstep formula
            interpolated_values = start_value + ease * (end_value - start_value)

            # Update the values in each frame
            for i, frame in enumerate(frames):
                animation[frame][axis] = interpolated_values[i]

    return data