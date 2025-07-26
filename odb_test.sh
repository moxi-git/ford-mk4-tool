#!/usr/bin/env bash

port="/dev/ttyUSB0" # your OBD serial port
baudrate=115200

if [[ ! -e "$port" ]]; then
  echo "Port $port not found!"
  exit 1
fi

# Configure the serial port baud rate and settings
stty -F "$port" "$baudrate" cs8 -cstopb -parenb -icanon -echo raw

# Send an OBD command (e.g. "0100" to query supported PIDs)
echo -ne "0100\r" >"$port"

# Read response for 2 seconds (adjust timeout as needed)
timeout 2 cat "$port" >response.txt

echo "Response from OBD:"
cat response.txt
