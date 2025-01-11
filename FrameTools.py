import json
import EulerHexTools
import re
import os
import numpy as np
from scipy.interpolate import interp1d
from tkinter import messagebox

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

#chatgpt intensives 
def ExportFrames(json_file, object_key, output_txt_file):
      
    try:
        # Load the JSON data
        with open(json_file, 'r') as file:
            data = json.load(file)
        
        # Check if the specified object exists in the JSON
        if object_key not in data:
            print(f"Error: The key '{object_key}' was not found in the JSON file.")
            return False
        
        # Get the frame data for the specified object
        frames = data[object_key]
        
        if not isinstance(frames, list) or not frames:
            print(f"Error: The object '{object_key}' does not contain valid frame data.")
            return False
        
        # Extract and write frame data to the output text file
        with open(output_txt_file, 'w') as output_file:
            for frame_set in frames:
                for frame, coords in frame_set.items():
                    x, y, z = coords["x"], coords["y"], coords["z"]
                    output_file.write(f"{x} {y} {z}\n")
        
        print(f"Frame data successfully written to '{output_txt_file}'.")
        return True
    
    except FileNotFoundError:
        print(f"Error: The file '{json_file}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def ImportFrames(json_file_path, animslot_key, txt_file_path):
    try:
        # Load the JSON file
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)

        # Ensure the animslot exists
        if animslot_key not in data:
            print(f"Error: Animslot '{animslot_key}' not found in JSON.")
            return False

        animslot_frames = data[animslot_key][0]  # Assuming frames are in the first list element
        frame_keys = list(animslot_frames.keys())  # Get the frame keys in the JSON
        num_json_frames = len(frame_keys)

        # Read the .txt file
        with open(txt_file_path, 'r') as txt_file:
            txt_lines = txt_file.readlines()

        if not txt_lines:
            print("Error: The TXT file is empty.")
            return False

        num_txt_frames = len(txt_lines)

        # Check if the TXT file has more frames than the JSON animslot
        if num_txt_frames != num_json_frames:
            messagebox.showerror("Error", f"Error: Couldn't import frames. Expected {num_json_frames} frames, recieved {num_txt_frames} frames.")
            return False

        # Import the data
        for i, line in enumerate(txt_lines):
            values = line.strip().split()
            if len(values) != 3:
                print(f"Warning: Skipping invalid line {i + 1}: {line}")
                continue

            try:
                x_deg, y_deg, z_deg = map(float, values)

                # Update the JSON data (convert degrees back to float)
                frame_key = frame_keys[i]  # Get the corresponding frame key in JSON
                animslot_frames[frame_key] = {
                    "x": x_deg,
                    "y": y_deg,
                    "z": z_deg
                }

            except ValueError:
                print(f"Warning: Skipping invalid line {i + 1}: {line}")
                continue

        # Save the updated JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Animation successfully imported into animslot '{animslot_key}' in JSON.")
        return True

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return False

    except json.JSONDecodeError:
        print("Error: Failed to decode JSON file. Please ensure it is properly formatted.")
        return False

    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        return False