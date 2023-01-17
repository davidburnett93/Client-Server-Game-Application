# Client-Server-Game-Application
This is a simple client server application that supports multiple clients (players) and servers (rooms).
Players can intereact with other players as well as the room they are in.

Player commands:
  Look: Displays the name, description, and contents of the room.
  Take (item): Takes the item from the room and add it to the player's inventory.
  Drop (item): Takes the item from the player's inventory and adds it to the room.
  Inventory: List the player's inventory.
  Say: Sends a message to everyone in the room. Once prompted with 'What did you want to say?' you must begin your message with say, however it will not be included in the sent message.
  Exit: Leave the game, dropping all items from inventory.
  
  Up: Go to the room located up.
  Down: Go to the room located down.
  North: Go to the room located north.
  South: Go to the room located south.
  East: Go to the room located east.
  West: Go to the room located west.
  
Discovery.py:
  Must be run first.
  No command line parameters.
Room.py:
  The command line must include any rooms connected to it in the form '-direction (name of room)' as well as the the name of the room, its description in " " and items in the room.
  Example: python3 room.py -n Kitchen Foyer "The entryway to an old house. A doorway leads away from the room to the north" vase rug boots.
Player.Py:
  The command line includes the name of the player and the desired starting location.
  Example: python3 player.py Alice Foyer.
