#David Burnett
#251179445
#This class maps room names into server addresses
import signal
import socket
import sys
from urllib.parse import urlparse

#The room's socket

discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#The room's port
DISCOVERYPORT = 7777

#List of room names and a list of their server details
#Each index in servers corresponds to the repective index in names
names = []
servers = []

# Signal handler for graceful exiting.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)

#Processes the message recieved
def process_message(message, addr, room_socket):
    words = message.split()

    length = len(names)
    valid = True
    #Attempts to register the room
    if words[0] == 'REGISTER':
        for x in range(length):
            if words[1] == servers[x] or words[2] == names[x]:
                valid = False
        if valid:
            servers.append(words[1])
            names.append(words[2])
            print('Registerd ' + words[2] + ' at server address: ' + words[1])
            return 'OK'
        return 'NOTOK, Could Not Register'
    #Attempts to deregister the room
    elif words[0] == 'DEREGISTER':
        for x in range(length):
            if words[1] == names[x]:
                print('Deregisterd ' + names[x] + ' at server address: ' + servers[x])
                servers.pop(x)
                names.pop(x)
                return 'OK'
        return 'NOTOK, Could Not Deregister'
    #Attempts to find the server details of the specified room
    elif words[0] == 'LOOKUP':
        for x in range(length):
            if words[1] == names[x]:
                print(words[1] + ' Lookup Successful')
                return 'OK ' + servers[x]
        return 'NOTOK, Room Not Found'

    return 'NOTOK, An Error Occurred'


def main():

    # Register our signal handler for shutting down.
    signal.signal(signal.SIGINT, signal_handler)

    #Create the socket.
    discovery_socket.bind(('', DISCOVERYPORT))

    print('\nRoom will wait for players at port: ' + str(discovery_socket.getsockname()[1]))

    #Loop forever waiting for messages

    while True:

        # Receive a packet process it.

        message, addr = discovery_socket.recvfrom(1024)

        # Process the message and retrieve a response.

        response = process_message(message.decode(), addr, discovery_socket)

        # Send the response message back.

        discovery_socket.sendto(response.encode(),addr)

if __name__ == '__main__':
    main()