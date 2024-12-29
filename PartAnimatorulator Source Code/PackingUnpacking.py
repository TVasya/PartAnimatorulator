import os
import re
from tkinter import messagebox

def Unpack(File, UnpackPath):
    # Resolve relative path to absolute
    UnpackPath = os.path.abspath(UnpackPath)

    # Delimiters
    CarHashString = b'\x0C\x00\x00\x00....\x00\x00\x00\x00\x00\x00\x00\x00'
    AnimSlotsDelimiter = b'\x10\x40\xE3\x00'

    GeometryInvalidFileDetector = b'\x00\x40\x13\x80'
    TexturesInvalidFileDetector = b'\x00\x00\x30\xB3'


    # Ensure output directories exist
    AnimSlotsPath = os.path.join(UnpackPath, "AnimSlots")
    PivotDataPath = os.path.join(UnpackPath, "PivotData")
    os.makedirs(AnimSlotsPath, exist_ok=True)
    os.makedirs(PivotDataPath, exist_ok=True)

    # Read the binary file
    try:
        with open(File, 'rb') as f:
            # Read the first 4 bytes
            first_4_bytes = f.read(4)
            
            # Check for invalid file detectors
            if first_4_bytes == GeometryInvalidFileDetector:
                messagebox.showerror("Error", "Invalid File - Detected Geometry file.")
                return False
            if first_4_bytes == TexturesInvalidFileDetector:
                messagebox.showerror("Error", "Invalid File - Detected Texture file.")
                return False
            
            # Read the rest of the file
            f.seek(0)  # Move back to the start
            data = f.read()
    except PermissionError:
        messagebox.showerror("Error", "Permission denied while accessing the file.")
        return False

    # Locate the first delimiter (CarHashString)



    delimiter_regex = re.compile(CarHashString, re.DOTALL)
    match = delimiter_regex.search(data)
    if not match:
        messagebox.showerror("Error", "Invalid File - Required delimiters not found.")
        return False

    # Split the data into three parts
    start, end = match.span()
    before_delimiter = data[:start]
    delimiter = data[start:end]
    after_delimiter = data[end:]

    # Save AnimSlots.bin
    with open(os.path.join(UnpackPath, "AnimSlots.bin"), 'wb') as f:
        f.write(before_delimiter)

    # Save CarHashString.bin
    with open(os.path.join(UnpackPath, "CarHashString.bin"), 'wb') as f:
        f.write(delimiter)

    # Save PivotData.bin
    with open(os.path.join(UnpackPath, "PivotData.bin"), 'wb') as f:
        f.write(after_delimiter)

    # Separate AnimSlots into multiple parts using the AnimSlotsDelimiter
    animslots_parts = re.split(AnimSlotsDelimiter, before_delimiter)
    animslots_parts.pop(0)
    for i, part in enumerate(animslots_parts):
        # Prepend delimiter to each AnimSlot part
        part_filename = os.path.join(AnimSlotsPath, f"AnimSlot_{i + 1 :02d}.bin")
        with open(part_filename, 'wb') as f:
            f.write(AnimSlotsDelimiter)  # Add the delimiter at the start
            f.write(part)  # Add the actual data after the delimiter

    # Split PivotData into 21 equal parts
    part_size = len(after_delimiter) // 21
    for i in range(21):
        start_index = i * part_size
        if i == 20:  # Ensure the last part takes the remaining bytes
            end_index = len(after_delimiter)
        else:
            end_index = start_index + part_size
        part_filename = os.path.join(PivotDataPath, f"PivotPart_{i + 1:02d}.bin")
        with open(part_filename, 'wb') as f:
            f.write(after_delimiter[start_index:end_index])
    return True


def Pack(OutputFile, UnpackPath):
    # Resolve relative path to absolute
    UnpackPath = os.path.abspath(UnpackPath)

    AnimSlotsPath = os.path.join(UnpackPath, "AnimSlots")
    PivotDataPath = os.path.join(UnpackPath, "PivotData")

    try:
        # Read AnimSlots.bin
        with open(os.path.join(UnpackPath, "AnimSlots.bin"), 'rb') as f:
            animslots_bin = f.read()

        # Read CarHashString.bin
        with open(os.path.join(UnpackPath, "CarHashString.bin"), 'rb') as f:
            carhash_string = f.read()

        # Read PivotData.bin
        with open(os.path.join(UnpackPath, "PivotData.bin"), 'rb') as f:
            pivot_data_bin = f.read()

    except FileNotFoundError:
        messagebox.showerror("Error", "Missing main files in the unpacking folder.")
        return False

    # Collect all AnimSlots files
    animslots_parts = []
    animslot_files = sorted(
        [f for f in os.listdir(AnimSlotsPath) if f.startswith("AnimSlot")],
        key=lambda x: int(x.split("_")[1].split(".")[0])  # Sort by part number
    )
    for animslot_file in animslot_files:
        with open(os.path.join(AnimSlotsPath, animslot_file), 'rb') as f:
            animslots_parts.append(f.read())

    # Combine AnimSlots parts
    combined_animslots = b"".join(animslots_parts)

    # Collect all PivotData parts
    pivotdata_parts = []
    pivotdata_files = sorted(
        [f for f in os.listdir(PivotDataPath) if f.startswith("PivotPart")],
        key=lambda x: int(x.split("_")[1].split(".")[0])  # Sort by part number
    )
    for pivotdata_file in pivotdata_files:
        with open(os.path.join(PivotDataPath, pivotdata_file), 'rb') as f:
            pivotdata_parts.append(f.read())

    # Combine PivotData parts
    combined_pivotdata = b"".join(pivotdata_parts)

    # Combine all data into the final file
    final_data = combined_animslots + carhash_string + combined_pivotdata
    try:
        with open(OutputFile, 'wb') as f:
            f.write(final_data)
            return True
    except:
        return False
    

