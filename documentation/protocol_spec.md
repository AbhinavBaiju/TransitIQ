# Serial Communication Protocol

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
