# import the pygame module, so you can use it
import os

import pygame
import pygame.locals as pl
import pygameMenu

import pygame_textinput
from pygameMenu.locals import *
from matrix_client.client import MatrixClient, Room, User


def change_room(room):
    pass


def set_room(room):
    global room_id
    global room_menu
    global start_game
    room_menu.disable()
    print(str(room))
    start_game = True
    room_id = room


def event_handler(event):
    if event["type"] == "reverstrix":
        global state
        state = event["content"]


def validate_move(board, x, y, col):
    dirs = [
        (-1, 1),
        (0, 1),
        (1, 1),
        (-1, 0),
        (1, 0),
        (-1, -1),
        (0, -1),
        (1, -1)
    ]
    if board[y][x] != -1 or not 7 >= x >= 0 or not 7 >= y >= 0:
        return False
    flipped = []
    for dir in dirs:
        go = True
        temp_flip = []
        pos = [x, y]
        while go:
            pos = list(pos)
            pos[0] += dir[0]
            pos[1] += dir[1]
            if not 7 >= pos[0] >= 0 or not 7 >= pos[1] >= 0 or board[pos[1]][pos[0]] == -1:
                go = False
            elif board[pos[1]][pos[0]] != col:
                temp_flip.append(pos)
            else:
                for flip in temp_flip:
                    flipped.append(flip)
                go = False
    if len(flipped) == 0:
        return False
    else:
        return flipped


def update_state(state):
    global room
    room.send_state_event("reverstrix", state)


def draw_board(surface, size, cell_size, xi, xf, yi, yf, board):
    for x in range(0, size, int(cell_size)):
        x = x + xi
        pygame.draw.line(surface, (0, 0, 0), (x, yi), (x, yf))
    for y in range(0, size, int(cell_size)):
        y = y + yi
        pygame.draw.line(surface, (0, 0, 0), (xi, y), (xf, y))
    for piece in state["pieces"]:
        if piece["player"] == 0:
            piece_color = (255, 0, 0)
        else:
            piece_color = (0, 0, 255)
        pos = (
            int(xi + piece["x"] * cell_size + (cell_size / 2)),
            int(yi + piece["y"] * cell_size + (cell_size / 2))
        )
        board[piece["y"]][piece["x"]] = piece["player"]
        pygame.draw.circle(surface, piece_color, pos, int(cell_size / 2))

# define a main function
def main():
    global client
    global room_menu
    global start_game
    global room_id
    global state
    global game_running
    global game_ended
    global last_state_id
    global room
    global cursor_x
    global cursor_y
    start_game = False
    game_running = False
    game_ended = False
    last_state_id = "0"
    # initialize the pygame module
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # load and set the logo
    # logo = pygame.image.load("logo32x32.png")
    # pygame.display.set_icon(logo)
    pygame.display.set_caption("Reverstrix")

    cursor_x = 0
    cursor_y = 0

    # create a surface on screen that has the size of 240 x 180
    swidth = 960
    sheight = 540
    surface: pygame.Surface = pygame.display.set_mode((swidth, sheight))

    logging_in = True
    passwording = False

    textinput = pygame_textinput.TextInput(
        antialias=True,
        text_color=(255, 255, 255),
        cursor_color=(255, 255, 255),
        font_family="Arial",
    )

    passwordinput = pygame_textinput.TextInput(
        antialias=True,
        text_color=(255, 255, 255),
        cursor_color=(255, 255, 255),
        font_family="Arial",
        replace_with="*"
    )

    room_menu = pygameMenu.TextMenu(surface,
                                    dopause=False,
                                    font=pygameMenu.fonts.FONT_BEBAS,
                                    menu_color=(30, 50, 107),
                                    menu_color_title=(120, 45, 30),
                                    title="Reverstrix",
                                    window_width=swidth,
                                    window_height=sheight,
                                    menu_width=swidth,
                                    menu_height=sheight,
                                    enabled=False
                                    )
    rooms = [
    ]
    # define a variable to control the main loop
    running = True

    font_family = "Arial"

    if not os.path.isfile(font_family):
        font_family = pygame.font.match_font(font_family)

    title_font = pygame.font.Font(font_family, 50)

    header_font = pygame.font.Font(font_family, 35)
    username = ""
    password = ""

    client = None

    # main loop
    while running:
        # event handling, gets all event from the event queue
        events = pygame.event.get()
        if room_menu.is_enabled() and not room_menu.is_disabled():
            room_menu.mainloop(events)
        elif logging_in:
            surface.fill((0, 0, 0))
            if not textinput.update(events):
                title_render = title_font.render("MATRIX LOGIN", True, (32, 32, 255))
                login_prompt_render = header_font.render("Login:", True, (255, 255, 255))
                surface.blit(title_render, (0,  0))
                surface.blit(login_prompt_render, (0, 50))
                surface.blit(textinput.get_surface(), (35, 100))
            else:
                username = textinput.get_text()
                logging_in = False
                passwording = True
        elif passwording:
            surface.fill((0, 0, 0))
            if not passwordinput.update(events):
                title_render = title_font.render("MATRIX LOGIN", True, (32, 32, 255))
                login_prompt_render = header_font.render("Login:", True, (255, 255, 255))
                login_username_render = header_font.render(username, True, (255, 255, 255))
                password_prompt_render = header_font.render("Password", True, (255, 255, 255))
                surface.blit(title_render, (0, 0))
                surface.blit(login_prompt_render, (0, 50))
                surface.blit(login_username_render, (35, 100))
                surface.blit(password_prompt_render, (0, 150))
                surface.blit(passwordinput.get_surface(), (35, 200))
            else:
                password = passwordinput.get_text()
                passwording = False
                user_details = username.split(":")
                user = user_details[0].replace("@","")
                domain = user_details[1]
                client = MatrixClient("https://" + domain)
                token = client.login(username, password, sync=True)
                rooms = []
                for room_id in client.rooms:
                    room = client.rooms[room_id]
                    rooms.append(
                        (room.display_name + "  " + room_id[0:5], room_id)
                    )
                    room_menu.enable()
                room_menu.add_selector("Room",
                                       rooms,
                                       onchange=change_room,
                                       onreturn=set_room
                                       )
        elif start_game:
            surface.fill((48, 149, 48))
            room = client.rooms[room_id]
            room.add_state_listener(event_handler, "reverstrix")
            client.start_listener_thread()
            # room_events = room.get_events()
            members = room.get_joined_members()
            opponent = "0"
            for member in members:
                member: User
                if member.user_id != client.user_id:
                    opponent = member.user_id
            states = client.api.get_room_state(room.room_id)
            found = False
            for room_state in states:
                if room_state["type"] == "reverstrix" and room_state["content"]["status"] == "running":
                    found = True
                    last_state_id = room_state["event_id"]
                    state = room_state["content"]
            if not found:
                # Create reversetrix
                state = {
                    "pieces": [
                        {
                            "x": 3,
                            "y": 3,
                            "player": 0
                        },
                        {
                            "x": 4,
                            "y": 3,
                            "player": 1
                        },
                        {
                            "x": 3,
                            "y": 4,
                            "player": 1
                        },
                        {
                            "x": 4,
                            "y": 4,
                            "player": 0
                        }
                    ],
                    "turn": 0,
                    "players": [
                        client.user_id,
                        opponent
                    ],
                    "status": "running"
                }
                room.send_state_event("reverstrix", state)
                print("Started")
            if state:
                start_game = False
                game_running = True
        attempt_place = False
        for event in events:
            # only do something if the event is of type QUIT
            if event.type == pygame.KEYDOWN:
                if event.key == pl.K_UP:
                    cursor_y = max(cursor_y - 1, 0)
                elif event.key == pl.K_DOWN:
                    cursor_y = min(cursor_y + 1, 7)
                elif event.key == pl.K_LEFT:
                    cursor_x = max(cursor_x - 1, 0)
                elif event.key == pl.K_RIGHT:
                    cursor_x = min(cursor_x + 1, 7)
                elif event.key == pl.K_SPACE or event.key == pl.K_KP_ENTER:
                    attempt_place = True
            elif event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
                game_running = False
        if game_running:
            turn_mod = state["turn"] % 2
            surface.fill((48, 149, 48))
            board = []
            for y in range(8):
                board.append([-1, -1, -1, -1, -1, -1, -1, -1])
            size = 500
            cell_size = 500/8
            xi = ((swidth - size) / 2)
            xf = swidth - ((swidth - size) / 2)
            yi = ((sheight - size) / 2)
            yf = sheight - ((sheight - size) / 2)
            draw_board(surface, size, cell_size, xi, xf, yi, yf, board)
            player_turn = state["players"][turn_mod]
            if turn_mod == 0:
                turn_color = (255, 0, 0)
            else:
                turn_color = (0, 0, 255)
            if player_turn == client.user_id:
                turn_render = header_font.render("Your Turn", True, turn_color)
            else:
                turn_render = header_font.render(player_turn + "'s Turn", True, turn_color)
            surface.blit(turn_render, (0, 0))
            if player_turn == client.user_id:
                available = []
                for y in range(8):
                    for x in range(8):
                        result = (x, y, validate_move(board, x, y, turn_mod))
                        if result[2]:
                            available.append(result)
                for available_move in available:
                    if turn_mod == 0:
                        indicator_color = (255, 0, 0)
                    else:
                        indicator_color = (0, 0, 255)
                    pos = (
                        int(xi + available_move[0] * cell_size)+5,
                        int(yi + available_move[1] * cell_size)+10
                    )
                    turn_render = header_font.render(str(len(available_move[2])), True, indicator_color)
                    surface.blit(turn_render, pos)
                if len(available) == 0:
                    state["turn"] += 1
                    turn_mod = state["turn"] % 2
                    for y in range(8):
                        for x in range(8):
                            result = (x, y, validate_move(board, x, y, turn_mod))
                            if result[2]:
                                available.append(result)
                    if len(available) == 0:
                        state["status"] = "ended"
                        game_running = False
                        game_ended = True
                    update_state(state)
                if attempt_place:
                    result = validate_move(board, cursor_x, cursor_y, turn_mod)
                    if result:
                        print("Result of move: " + str(result))
                        state["pieces"].append({
                            "x": cursor_x,
                            "y": cursor_y,
                            "player": turn_mod
                        })
                        for piece in state["pieces"]:
                            for taken in result:
                                if piece["x"] == taken[0] and piece["y"] == taken[1]:
                                    piece["player"] = turn_mod
                        state["turn"] += 1
                        update_state(state)
            indicator_xi = int(cursor_x * cell_size) + xi
            indicator_yi = int(cursor_y * cell_size) + yi
            indicator_xf = indicator_xi + int(cell_size)
            indicator_yf = indicator_yi + int(cell_size)
            highlight_col = (128, 128, 128)
            if player_turn == client.user_id:
                highlight_col = (255, 255, 255)
            pygame.draw.line(surface, highlight_col, (indicator_xi, indicator_yi), (indicator_xf, indicator_yi))
            pygame.draw.line(surface, highlight_col, (indicator_xf, indicator_yi), (indicator_xf, indicator_yf))
            pygame.draw.line(surface, highlight_col, (indicator_xf, indicator_yf), (indicator_xi, indicator_yf))
            pygame.draw.line(surface, highlight_col, (indicator_xi, indicator_yi), (indicator_xi, indicator_yf))
            # room_events = room.get_events()
            # print(str(room_events) + " //// " + str(state))
        elif game_ended:
            surface.fill((48, 149, 48))
            board = []
            for y in range(8):
                board.append([-1, -1, -1, -1, -1, -1, -1, -1])
            size = 500
            cell_size = 500 / 8
            xi = ((swidth - size) / 2)
            xf = swidth - ((swidth - size) / 2)
            yi = ((sheight - size) / 2)
            yf = sheight - ((sheight - size) / 2)
            draw_board(surface, size, cell_size, xi, xf, yi, yf, board)
        pygame.display.update()


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    # call the main function
    main()
