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
    # Convert back to Euler angles (roll, pitch, yaw) in radians
    euler_angles = rotation.as_euler('xyz', degrees=True)
    return euler_angles