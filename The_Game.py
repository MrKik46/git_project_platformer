import os
import sys
import datetime
import pygame

pygame.init()

clock = pygame.time.Clock()
FPS = 60

screen_width = 1000
screen_height = 1000
tile_width = tile_height = 50
game_over = 0

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

class World():
    def __init__(self, date):
        self.tile_list = []
        dirt_image = load_image('dirt.png')
        grass_image = load_image('dirt_grass.png')
        row_count = 0
        for row in date:
            col_count = 0
            for tile in row:
                if tile != 0:
                    img = ''
                    if tile == 1:
                        img = pygame.transform.scale(grass_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif tile == 2:
                        img = pygame.transform.scale(dirt_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        tile = (img, img_rect)
                        self.tile_list.append(tile)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (155, 155, 155), tile[1], 1)


level = [
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2],
    [2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 2, 2],
    [2, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 2],
    [2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 2, 1, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2],
    [2, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 2, 2, 2, 2, 2, 2],
    [2, 0, 0, 0, 0, 1, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2],
    [2, 0, 0, 0, 1, 2, 2, 2, 4, 4, 4, 4, 4, 2, 2, 2, 2, 2, 2, 2],
    [2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]



world = World(level)

fon = pygame.transform.scale(load_image('sky.png'), (screen_width, screen_height))

running = True
while running:

    clock.tick(FPS)
    screen.blit(fon, (0, 0))

    world.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
