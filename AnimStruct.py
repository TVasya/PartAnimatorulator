import binascii
import re
import HashTools
import struct
from tkinter import messagebox
import shutil
import os
import EulerHexTools
class AnimSlot:
    
    def __init__(self, path, name):
        self.name = name
        self.path = path
        self.NameLength = 0

    def GetName(self):
        start_hex = "06 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
        end_hex = "74 00"

        start_bytes = bytes.fromhex(start_hex)
        end_bytes = bytes.fromhex(end_hex)
        with open(self.path, 'rb') as file:
            data = file.read()
        start_index = data.find(start_bytes) + len(start_bytes)
        end_index = data.find(end_bytes)
        if start_index != -1 and end_index != -1 and start_index < end_index:
            extracted_data = data[start_index:end_index + 1]
            self.name = extracted_data
            match = re.search(r'^(.*?)(?:_q\x00|_t)', extracted_data.decode())
            if match:
                Name = match.group(1)
            self.NameLength = len(Name)
            return Name
    
    def Rename(self, new_name):
        if self.NameLength < len(new_name):
            # Calculate how many extra bytes we need
            extra_bytes_needed = (len(new_name) - self.NameLength) * 2
            formatted_string = f"{new_name}_q\x00{new_name}_t\x00"
            
            start_hex = "06 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
            end_hex = "74 00"

            start_bytes = bytes.fromhex(start_hex)
            end_bytes = bytes.fromhex(end_hex)
            
            new_name_bytes = formatted_string if isinstance(formatted_string, bytes) else formatted_string.encode('utf-8')
            
            with open(self.path, 'rb') as file:
                data = file.read()
            
            start_index = data.find(start_bytes) + len(start_bytes)
            end_index = data.find(end_bytes)
            
            if start_index != -1 and end_index != -1 and start_index < end_index:
                # Remove extra_bytes_needed number of bytes after the end_index
                new_content = (
                    data[:start_index] +
                    new_name_bytes +
                    data[end_index + len(end_bytes) + extra_bytes_needed:]
                )
                
                with open(self.path, 'wb') as file:
                    file.write(new_content)
                
                self.name = new_name_bytes
                return True
            return False
            
        elif self.NameLength > len(new_name):
            formatted_string = f"{new_name}_q\x00{new_name}_t" + (((self.NameLength - len(new_name))*2)*'\x00') +'\x00'
            
            start_hex = "06 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
            end_hex = "74 00"

            start_bytes = bytes.fromhex(start_hex)
            end_bytes = bytes.fromhex(end_hex)
            
            new_name_bytes = formatted_string if isinstance(formatted_string, bytes) else formatted_string.encode('utf-8')
            
            with open(self.path, 'rb') as file:
                data = file.read()
            
            start_index = data.find(start_bytes) + len(start_bytes)
            end_index = data.find(end_bytes)
            
            if start_index != -1 and end_index != -1 and start_index < end_index:
                new_content = (
                    data[:start_index] +
                    new_name_bytes +
                    data[end_index + len(end_bytes):]
                )
                
                with open(self.path, 'wb') as file:
                    file.write(new_content)
                
                self.name = new_name_bytes
                return True
            return False
        else:
            formatted_string = f"{new_name}_q\x00{new_name}_t\x00"

            start_hex = "06 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
            end_hex = "74 00"

            start_bytes = bytes.fromhex(start_hex)
            end_bytes = bytes.fromhex(end_hex)
            
            new_name_bytes = formatted_string if isinstance(formatted_string, bytes) else formatted_string.encode('utf-8')
            
            with open(self.path, 'rb') as file:
                data = file.read()
            
            start_index = data.find(start_bytes) + len(start_bytes)
            end_index = data.find(end_bytes)
            
            if start_index != -1 and end_index != -1 and start_index < end_index:
                new_content = (
                    data[:start_index] +
                    new_name_bytes +
                    data[end_index + len(end_bytes):]
                )
                
                with open(self.path, 'wb') as file:
                    file.write(new_content)
                
                self.name = new_name_bytes
                return True
            return False
    
    '''        
    def Copy(self, folder_path):
        # Convert the folder path to an absolute path
        folder_path = os.path.abspath(folder_path)

        # Ensure the folder exists
        if not os.path.isdir(folder_path):
            raise ValueError(f"The provided folder path '{folder_path}' does not exist.")

        # List all files in the folder
        anim_slot_files = [f for f in os.listdir(folder_path) if f.startswith("AnimSlot_") and f.endswith(".bin")]

        # Find the highest file number
        max_number = 0
        for file_name in anim_slot_files:
            try:
                # Extract the number from the file name
                number = int(file_name.replace("AnimSlot_", "").replace(".bin", ""))
                max_number = max(max_number, number)
            except ValueError:
                # Skip files that do not match the naming convention
                continue

        # Determine the new file name
        new_number = max_number + 1
        new_file_name = f"AnimSlot_{new_number:02}.bin"
        new_file_path = os.path.join(folder_path, new_file_name)

        # Copy the current file to the new file
        shutil.copy(self.path, new_file_path)

        return new_file_path
    '''


class Pivot:
    def __init__(self, path):
        self.path = path
        self.x = None
        self.y = None
        self.z = None
        self.w = None
        self.Rx = None # rx is real!!1!1!
        self.Ry = None
        self.Rz = None

    def GetValues(self):
        with open(self.path, 'rb') as file:
            # Read the first 16 bytes (4 floats, 4 bytes each, big-endian)
            raw_data = file.read(64)
            
            if len(raw_data) < 64:
                raise ValueError("File does not contain enough data for a Pivot.")
            
            self.Rx, self.Ry, self.Rz = EulerHexTools.HexMatrixEuler(raw_data[:48])

            # Unpack the 4 floats from the last 16 bytes (big-endian)
            self.x, self.y, self.z, self.w = struct.unpack('<4f', raw_data[-16:])
            
        return self.x, self.y, self.z, self.w, self.Rx, self.Ry, self.Rz
    
    def UpdateValues(self, x=None, y=None, z=None, w=None, Rx=None, Ry=None, Rz=None):
        # Set new values if provided
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if z is not None:
            self.z = z
        if w is not None:
            self.w = w
        if Rx is not None:
            self.Rx = Rx
        if Ry is not None:
            self.Ry = Ry
        if Rz is not None:
            self.Rz = Rz

        # Pack the updated values as big-endian floats
        updated_position = struct.pack('<4f', self.x, self.y, self.z, self.w)
        updated_rotation = EulerHexTools.EulerHexMatrix(self.Rx, self.Ry, self.Rz)
        
        with open(self.path, 'r+b') as file:
            
            file.write(updated_rotation)
            file.write(updated_position)
            return True
        return False

    def __str__(self):
        return f"Pivot(X: {self.x}, Y: {self.y}, Z: {self.z}, W: {self.w})"
    
class CarName:
    def __init__(self, path):
        self.path = path
    def GetName(self):
        with open(self.path, 'rb') as file:
            bytes_data = file.read(8)

            # Extract bytes from the 5th to 8th position (index 4 to 7)
            Hash = bytes_data[4:8]
            return HashTools.FindHash(Hash.hex().upper())
    def Rename(self, NewName):
        # Convert the hex string to bytes
        if NewName.startswith('0x') or NewName.startswith('0X'):
            NewName = NewName[2:]
            if len(NewName) != 8:
                messagebox.showerror("Error", "Invalid Hash - Hash is too short or too long. Hash must be 8 characters (with 0x 10 characters)")
                return False
            else:
                with open(self.path, 'rb+') as file:
                # Read the first 8 bytes
                    bytes_data = file.read(8)
                    bytes_data = bytes_data[:4] + bytes.fromhex(NewName)
                    file.seek(0)
                    file.write(bytes_data)
                    return True
        else:    
            HashedName = HashTools.b_string_hash(NewName, 1)
            new_bytes = bytes.fromhex(HashedName)

            # Open the file in binary read/write mode
            with open(self.path, 'rb+') as file:
                # Read the first 8 bytes
                bytes_data = file.read(8)
                bytes_data = bytes_data[:4] + new_bytes
                file.seek(0)
                file.write(bytes_data)
                return True

