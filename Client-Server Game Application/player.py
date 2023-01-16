#David Burnett
#251179445
#This class acts as a player, containing all player attributes 
import socket
import signal
import sys
import argparse
from urllib.parse import urlparse
import selectors

# Selector for helping us select incoming data from the server and messages typed in by the user.

sel = selectors.DefaultSelector()

# Socket for sending messages.

#Port and host data of the discovery server
DISCOVERYPORT = 7777
DISCOVERYHOST = 'localhost'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address.

server = ('', '')

# User name for tagging sent messages.

name = ''

# Inventory of items.

inventory = []

# Directions that are possible.

connections = { 
    "north" : "",
    "south" : "",
    "east" : "",
    "west" : "",
    "up" : "",
    "down" : ""
    }

#set time to wait for server response before exiting
TIMER = 5

# Signal handler for graceful exiting.  Let the server know when we're gone.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message='exit'
    client_socket.sendto(message.encode(),server)
    for item in inventory:
        message = f'drop {item}'
        client_socket.sendto(message.encode(), server)
    sys.exit(0)

# Simple function for setting up a prompt for the user.

def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)

# Function to join a room.

def join_room():
    message = f'join {name}'
 #   client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(TIMER)
    client_socket.sendto(message.encode(), server)
    try:
        response, addr = client_socket.recvfrom(1024)
    except OSError as msg:
        print('Something bad happened')
        sys.exit()
    print(response.decode())

# Function to handle commands from the user, checking them over and sending to the server as needed.

def process_command(command):

    global server

    # Parse command.

    words = command.split()

    # Check if we are dropping something.  Only let server know if it is in our inventory.

    if (words[0] == 'drop'):
        if (len(words) != 2):
            print("Invalid command")
            return
        elif (words[1] not in inventory):
            print(f'You are not holding {words[1]}')
            return

    # Send command to server, if it isn't a local only one.

    if (command != 'inventory'):
        message = f'{command}'
        client_socket.settimeout(TIMER)
        client_socket.sendto(message.encode(), server)

    # Check for particular commands of interest from the user.

    # If we exit, we have to drop everything in our inventory into the room.

    if (command == 'exit'):
        for item in inventory:
            message = f'drop {item}'
            client_socket.sendto(message.encode(), server)
        sys.exit(0)

    # If we look, we will be getting the room description to display.

    elif (command == 'look'):
        client_socket.settimeout(TIMER)
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('Something bad happened')
            sys.exit()
        print(response.decode())

    # If we inventory, we never really reached out to the room, so we just display what we have.

    elif (command == 'inventory'):
        print("You are holding:")
        if (len(inventory) == 0):
            print('  No items')
        else:
            for item in inventory:
                print(f'  {item}')

    # If we take an item, we let the server know and put it in our inventory, assuming we could take it.

    elif (words[0] == 'take'):
        client_socket.settimeout(TIMER)
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('Something bad happened')
            sys.exit()
        print(response.decode())
        words = response.decode().split()
        if ((len(words) == 2) and (words[1] == 'taken')):
            inventory.append(words[0])

    # If we drop an item, we remove it from our inventory and give it back to the room.

    elif (words[0] == 'drop'):
        client_socket.settimeout(TIMER)
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('Something bad happened')
            sys.exit()
        print(response.decode())
        inventory.remove(words[1])

    # If we're wanting to go in a direction, we check with the room and it will tell us if it's a valid
    # direction.  We can then join the new room as we know we've been dropped already from the other one.

    elif (words[0] in connections):
        client_socket.settimeout(TIMER)
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('Something bad happened')
            sys.exit()

        #Lookup the room name in discovery to see if it exists
        room = response.decode()
        lookup = 'LOOKUP ' + room
        client_socket.sendto(lookup.encode(), (DISCOVERYHOST,DISCOVERYPORT))
        client_socket.settimeout(TIMER)
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('Something bad happened')
            sys.exit()
        word = response.decode().split()
        #If the room exists, join the new room
        if word[0] == 'OK':
            server_address = urlparse(word[1])
            server = (server_address.hostname, server_address.port)
            join_room()     
        else:
            print(response.decode())

    # The player wants to say something ... print the response.

    elif (words[0] == 'say'):
        client_socket.settimeout(TIMER)
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('Something bad happened')
            sys.exit()
        print(response.decode())
        
    # Otherwise, it's an invalid command so we report it.

    else:
        client_socket.settimeout(TIMER)
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('Something bad happened')
            sys.exit()
        print(response.decode())

# Function to handle incoming messages from room.  Also look for disconnect messages to shutdown.

def handle_message_from_server(sock, mask):
    client_socket.settimeout(TIMER)
    try:
        response, addr = client_socket.recvfrom(1024)
    except OSError as msg:
        print('Something bad happened')
        sys.exit()
    words=response.decode().split(' ')
    print()
    if len(words) == 1 and words[0] == 'disconnect':
        print('Disconnected from server ... exiting!')
        sys.exit(0)
    else:
        print(response.decode())
        do_prompt()

# Function to handle incoming messages from user.

def handle_keyboard_input(file, mask):
    line=sys.stdin.readline()[:-1]
    process_command(line)
    do_prompt()

# Our main function.

def main():

    global name
    global client_socket
    global server

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a the player name and starting room

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name for the player in the game")
    parser.add_argument("room", help="name of the room")
    args = parser.parse_args()

    name = args.name
    room = args.room

    #Determine if the room exists using the lookup feature in discovery
    lookup = 'LOOKUP ' + room
    client_socket.settimeout(TIMER)
    client_socket.sendto(lookup.encode(), (DISCOVERYHOST,DISCOVERYPORT))
    try:
        response, addr = client_socket.recvfrom(1024)
    except OSError as msg:
        print('Something bad happened')
        sys.exit()
    words = response.decode().split()
    #if the room exits, retrieve the server for the room
    if words[0] == 'OK':
        server_address = urlparse(words[1])
        server = (server_address.hostname, server_address.port)

        # Send message to enter the room.

        join_room()

        # Set up our selector.

        #client_socket.setblocking(False)
        sel.register(client_socket, selectors.EVENT_READ, handle_message_from_server)
        sel.register(sys.stdin, selectors.EVENT_READ, handle_keyboard_input)
        
        # Prompt the user before beginning.

        do_prompt()

        # Now do the selection.

        while(True):
            events = sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
    else:
        print(response.decode())
        sys.exit(0)


if __name__ == '__main__':
    main()

