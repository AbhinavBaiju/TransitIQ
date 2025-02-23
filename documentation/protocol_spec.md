# Serial Communication Protocol

<<<<<<< HEAD
## Overview
The traffic analysis system uses the SerialTransfer library to communicate between the Python application and Arduino controller. This protocol handles the transmission of vehicle counts for each lane direction.

## Data Structure

The protocol uses a structured data format with four unsigned 16-bit integers (uint16_t):

| Field | Type     | Description         | Value Range |
|-------|----------|-------------------|-------------|
| north | uint16_t | North Lane Count   | 0-65535     |
| south | uint16_t | South Lane Count   | 0-65535     |
| east  | uint16_t | East Lane Count    | 0-65535     |
| west  | uint16_t | West Lane Count    | 0-65535     |

## Communication Parameters

- Protocol: SerialTransfer
- Baud Rate: 115200
- Data Format: Binary (struct)
- Connection: USB Serial

## Implementation Notes

- The SerialTransfer library handles packet framing, error checking, and data integrity
- Data is automatically serialized/deserialized between Python and Arduino
- No manual checksum or start byte handling is required
=======
## Packet Structure

| Byte | Description       | Value Range |
|------|-------------------|-------------|
| 0    | Start Byte        | 0xAA        |
| 1-2  | North Vehicle Count | 0-65535     |
| 3-4  | South Vehicle Count | 0-65535     |
| 5-6  | East Vehicle Count  | 0-65535     |
| 7    | Checksum (XOR)    | 0-255       |

## Timing Parameters

- Baud Rate: 115200
- Update Frequency: 2Hz
- Packet Timeout: 500ms
>>>>>>> dfb34fe6b9906401cf53677317d7e17972301446
