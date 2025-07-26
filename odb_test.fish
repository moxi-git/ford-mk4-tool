#!/usr/bin/env fish

set port /dev/ttyUSB0 # your OBD serial port
set baudrate 115200

if not test -e $port
    echo "Port $port not found!"
    exit 1
end

# Configure the serial port baud rate and settings
stty -F $port $baudrate cs8 -cstopb -parenb -icanon -echo raw

# Send an OBD command (e.g. "0100" to query supported PIDs)
echo -n "0100\r" >$port

# Read response for 2 seconds (adjust timeout as needed)
timeout 2 cat $port >response.txt

echo "Response from OBD:"
cat response.txt
