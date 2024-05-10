from config.ptz_controls_config import ROTATION_SPEED, LEFT, STOP, RIGHT
import time
import serial


def update_ptz_angle(angle: float, previous_angle: float):
    # Calculate how much time PTZ should rotate
    rotation_direction = LEFT
    if previous_angle < angle:
        rotation_direction = RIGHT

    new_angle = previous_angle + angle
    time_to_rotate = new_angle / ROTATION_SPEED

    time_end = time.time() + time_to_rotate
    send_pelco_command(rotation_direction)

    if time.time() == time_end:
        send_pelco_command(STOP)


# Function to calculate Pelco-D checksum
def calculate_checksum(command):
    checksum = sum(command[1:]) & 0xFF  # Calculate sum and mask to 8 bits
    return bytes([checksum])


# Function to send a Pelco-D command
def send_pelco_command(command):
    try:
        checksum = calculate_checksum(command)
        full_command = command + checksum
        # Replace with your serial port settings (consult camera manual)
        with serial.Serial("/dev/ttyUSB1", 2400, timeout=1) as ser:
            ser.write(full_command)
            print(f"Sent command: {command.hex()}")
    except serial.SerialException as e:
        print(f"Serial error: {e}")


def convert_degrees_to_pelco(degrees):
    """
    Converts degrees (0-359) to a Pelco-D pan position value (0-35999).
    """
    if not 0 <= degrees <= 359:
        raise ValueError("Degrees must be between 0 and 359.")
    return int(degrees * 100)


def set_pan_position(degrees):
    """
    Sends a Pelco-D command to set the pan position in degrees.
    """
    pelco_value = convert_degrees_to_pelco(degrees)
    # Assuming most significant byte (MSB) comes first
    msb = pelco_value // 256
    lsb = pelco_value % 256
    command = b"\xFF\x01\x00\x4B" + bytes([msb]) + bytes([lsb])  # Set Pan Position
    send_pelco_command(command)
