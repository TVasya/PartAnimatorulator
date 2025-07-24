from scipy.spatial.transform import Rotation as R
import struct
import textwrap



def EulerHex(roll, pitch, yaw):
    rotation = R.from_euler('xyz', [roll, pitch, yaw], degrees=True)
    quaternion = rotation.as_quat()  # [x, y, z, w]
    hex_value = ''
    for value in quaternion:
        hex_representation = struct.pack('<f', value).hex().upper()
        hex_value += hex_representation
    return hex_value

def HexEuler(hex_values):
    quaternion = [struct.unpack('<f', bytes.fromhex(h))[0] for h in textwrap.wrap(hex_values, 8)]
    # Create the Rotation object from the quaternion [x, y, z, w]
    rotation = R.from_quat(quaternion)
    # Convert back to Euler angles (roll, pitch, yaw)
    euler_angles = rotation.as_euler('xyz', degrees=True)
    return euler_angles

def HexMatrixEuler(raw_bytes):
    """
    Converts 48 bytes (3x4 matrix) into Euler angles (degrees).
    Each row has 4 floats, but only the first 3 are used for rotation.
    Accepts raw bytes instead of hex string.
    """
    assert len(raw_bytes) == 48, "Expected 48 bytes"

    # Unpack 12 floats (little endian)
    floats = list(struct.unpack('<12f', raw_bytes))

    # Extract 3x3 rotation matrix (ignore the last column of each row)
    rotation_matrix = [
        [floats[0], floats[1], floats[2]],
        [floats[4], floats[5], floats[6]],
        [floats[8], floats[9], floats[10]]
    ]

    # Flatten and convert
    rotation = R.from_matrix(rotation_matrix)
    euler_angles = rotation.as_euler('xyz', degrees=True)
    return euler_angles

def EulerHexMatrix(x_rot, y_rot, z_rot):
    """
    Converts Euler angles (degrees) back to 48 bytes (3x4 matrix).
    
    Args:
        x_rot (float): Rotation around X-axis in degrees
        y_rot (float): Rotation around Y-axis in degrees  
        z_rot (float): Rotation around Z-axis in degrees
    
    Returns:
        bytes: 48 raw bytes in the same format as the original HexMatrixEuler input.
        
    The function creates a 3x4 matrix where:
    - First 3 columns are the rotation matrix
    - Last column is zeros (translation/padding)
    """
    # Convert Euler angles to rotation matrix
    euler_angles = [x_rot, y_rot, z_rot]
    rotation = R.from_euler('xyz', euler_angles, degrees=True)
    rotation_matrix = rotation.as_matrix()
    
    # Create the 3x4 matrix (rotation + zero column)
    matrix_3x4 = []
    for i in range(3):
        row = [
            rotation_matrix[i][0],  # R11, R21, R31
            rotation_matrix[i][1],  # R12, R22, R32
            rotation_matrix[i][2],  # R13, R23, R33
            0.0                     # Zero padding (4th column)
        ]
        matrix_3x4.extend(row)
    
    # Pack as 12 floats (little endian) into 48 bytes
    raw_bytes = struct.pack('<12f', *matrix_3x4)
    
    return raw_bytes