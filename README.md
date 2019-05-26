# Reverstrix

Decentralized Reversi running on Matrix

# Setup

Requires: pygame, pygame_menu, matrix_client, Python 3.6+

Install them with

    sudo pip3 install pygame pygame-menu matrix_client

And run with

    python3 reversi.py

# Playing

1. Enter matrix username (Including "@") sign and password. Logging in could take a few seconds.
2. Select a room to play in using the arrow keys and enter. Rooms are labelled with the room name and the first 5 characters of the ID.
3. If no game is active, one will be started with you and the last member in the room that is not you.
4. Both you and your opponent must have the "Change Settings" permission. (By default 50+)
5. The currently active player will be shown in the top left. When it is your turn, use the arrow keys to move your selection, and spacebar or enter to place a tile.
6. The game will automatically end when no more moves can be made. 