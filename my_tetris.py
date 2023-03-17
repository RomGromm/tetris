import pygame as pg
import sys
from copy import deepcopy
from random import randrange, choice

W, H = 10, 20
TILE = 35
GAME_RESOLUTION = W * TILE, H * TILE
RESOLUTION = 650, 740
FPS = 60

pg.init()
window = pg.display.set_mode(RESOLUTION)
game_window = pg.Surface(GAME_RESOLUTION)
clock = pg.time.Clock()

pg.mixer.music.load('main_music.mp3')
pg.mixer.music.play(-1)
pg.mixer.music.set_volume(1)

grid = [pg.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figures_coordinates = [
    [(-1, 0), (-2, 0), (0, 0), (1, 0)],
    [(-1, 0), (-1, 1), (0, 0), (0, -1)],
    [(0, -1), (-1, -1), (-1, 0), (0, 0)],
    [(0, 0), (-1, 0), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, 0)],
    [(-1, 0), (-1, -1), (-1, 1), (0, -1)],
]

figures = [[pg.Rect(x + W // 2, y + 1, 1, 1) for x, y in pos] for pos in figures_coordinates]
figure_rect = pg.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)]

current_figure = deepcopy(choice(figures))
next_figure = deepcopy(choice(figures))

animation_speed, animation_count, animation_limit = 50, 0, 1500

get_random_color = lambda: (randrange(40, 256), randrange(40, 256), randrange(40, 256))

figure_color = get_random_color()
next_figure_color = get_random_color()

main_font = pg.font.SysFont("cambria", 65)
second_font = pg.font.SysFont("cambria", 35)

title = main_font.render("ТЕТРИС", True, (255, 255, 255))
first_word = second_font.render("СЛЕДУЮЩАЯ", True, (255, 255, 255))
second_word = second_font.render("ФИГУРА:", True, (255, 255, 255))
score_word = second_font.render("СЧЕТ:", True, (255, 255, 255))
third_word = second_font.render("СОБРАНО", True, (255, 255, 255))
fourth_word = second_font.render("ЛИНИЙ:", True, (255, 255, 255))

background = pg.image.load('bg.jpg').convert()

score = 0
deleted_lines, count_of_lines = 0, 0
scores = {
    0: 0,
    1: 100,
    2: 300,
    3: 700,
    4: 1500
}

title_record = second_font.render("РЕКОРД:", True, (255, 255, 255))


def get_record():
    try:
        with open("tetris_record.txt") as file:
            return file.readline()
    except FileNotFoundError:
        with open("tetris_record.txt", "w") as file:
            file.write('0')


def set_record(score, record):
    new_record = max(int(score), int(record))
    with open("tetris_record.txt", "w") as output_file:
        output_file.write(str(new_record))


def check_borders():
    if current_figure[i].x < 0 or current_figure[i].x > W - 1:
        return False
    elif current_figure[i].y > H - 1 or field[current_figure[i].y][current_figure[i].x]:
        return False
    return True


while True:

    pg.mixer.music.set_volume(1)

    pg.mixer.music.unpause()

    record = get_record()

    window.blit(background, (0, 0))
    window.blit(game_window, (20, 20))

    game_window.fill(pg.Color('black'))

    dx = 0
    turn = False
    pause = False

    for i in range(count_of_lines):
        pg.time.wait(200)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT or event.key == pg.K_d:
                dx += 1
            elif event.key == pg.K_LEFT or event.key == pg.K_a:
                dx -= 1
            elif event.key == pg.K_SPACE or event.key == pg.K_RETURN:
                animation_limit = 100
            elif (event.key == pg.K_UP or event.key == pg.K_DOWN or
                    event.key == pg.K_w or event.key == pg.K_s):
                turn = True

    old_figure = deepcopy(current_figure)

    for i in range(4):
        current_figure[i].x += dx
        if not check_borders():
            current_figure = deepcopy(old_figure)
            break

    animation_count += animation_speed

    if animation_count > animation_limit:
        animation_count = 0
        old_figure = deepcopy(current_figure)
        for i in range(4):
            current_figure[i].y += 1
            if not check_borders():
                for j in range(4):
                    field[old_figure[j].y][old_figure[j].x] = figure_color
                current_figure, figure_color = next_figure, next_figure_color
                next_figure, next_figure_color = deepcopy(choice(figures)), get_random_color()
                animation_limit = 1500
                animation_speed += 2
                break

    center_of_rotation = current_figure[0]
    old_figure = deepcopy(current_figure)
    if turn:
        for i in range(4):
            x = current_figure[i].y - center_of_rotation.y
            y = current_figure[i].x - center_of_rotation.x
            current_figure[i].x = center_of_rotation.x - x
            current_figure[i].y = center_of_rotation.y + y
            if not check_borders():
                current_figure = deepcopy(old_figure)
                break

    last_line = H - 1
    # deleted_lines = 0
    count_of_lines = 0

    for row in range(H - 1, -1, -1):
        tiles_in_row = 0
        for i in range(W):
            if field[row][i]:
                tiles_in_row += 1
            field[last_line][i] = field[row][i]
        if tiles_in_row < W:
            last_line -= 1
        else:
            count_of_lines += 1

    score += scores[count_of_lines]

    deleted_lines += count_of_lines

    [pg.draw.rect(game_window, (120, 120, 120), rect, 1) for rect in grid]

    for i in range(4):
        figure_rect.x = current_figure[i].x * TILE
        figure_rect.y = current_figure[i].y * TILE
        pg.draw.rect(game_window, figure_color, figure_rect)

    for y, row in enumerate(field):
        for x, column in enumerate(row):
            if column:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pg.draw.rect(game_window, column, figure_rect)

    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 338
        figure_rect.y = next_figure[i].y * TILE + 235
        pg.draw.rect(window, next_figure_color, figure_rect)

    window.blit(title, (395, 10))

    window.blit(first_word, (400, 130))
    window.blit(second_word, (440, 170))

    window.blit(third_word, (438, 360))
    window.blit(fourth_word, (448, 400))
    window.blit(second_font.render(str(deleted_lines), True, pg.Color('white')), (465, 440))

    window.blit(score_word, (465, 600))
    window.blit(second_font.render(str(score), True, pg.Color('white')), (465, 640))

    for i in range(W):
        if field[0][i]:
            set_record(score, record)
            field = [[0 for x in range(W)] for y in range(H)]
            animation_speed, animation_count, animation_limit = 50, 0, 1500
            score = 0
            deleted_lines, count_of_lines = 0, 0
            pg.time.wait(500)

    pg.display.flip()
    clock.tick(FPS)
