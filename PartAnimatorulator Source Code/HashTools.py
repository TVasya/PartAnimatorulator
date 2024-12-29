import os, sys

def b_string_hash(string, saving):
    default_file_path = 'DefaultHashes.txt'
    user_file_path = 'UserHashes.txt'

    with open(default_file_path, 'r') as default_file:
        default_names = default_file.readlines()

    with open(user_file_path, 'r') as user_file:
        user_names = user_file.readlines()

    default_names = [name.strip() for name in default_names]
    user_names = [name.strip() for name in user_names]

    if string is None:
        return 0

    result = -1

    for char in string:
        result = result * 0x21 + ord(char)

    # Mask the result to keep only the last 4 bytes
    result &= 0xFFFFFFFF

    # Convert to bytes in little-endian order (reverse byte order)
    reversed_bytes = result.to_bytes(4, byteorder='big')[::-1]

    # Convert back to hexadecimal string
    if saving:
        for name in default_names + user_names:
            if string == name:
                return ''.join(f"{byte:02X}" for byte in reversed_bytes)
        with open(user_file_path, "a") as f:
            f.write("\n"+string)
    return ''.join(f"{byte:02X}" for byte in reversed_bytes)
    

def FindHash(Hash):
    result_name = None
    default_file_path = 'DefaultHashes.txt'
    user_file_path = 'UserHashes.txt'
    # Open DefaultHashes.txt and UserHashes.txt to read the content
    try:
        with open(default_file_path, 'r') as default_file:
            default_names = default_file.readlines()

        with open(user_file_path, 'r') as user_file:
            user_names = user_file.readlines()

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None

    # Strip newline characters and process each name
    default_names = [name.strip() for name in default_names]
    user_names = [name.strip() for name in user_names]

    # Iterate through both lists and compare hashes
    for name in default_names + user_names:
        hashed_name = b_string_hash(name, 0)

        if hashed_name == Hash:
            result_name = name
            break

    # If no match found, return the hash input
    if result_name:
        return result_name
    else:
        return '0x' + Hash
