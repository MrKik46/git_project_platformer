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
menu = True
level_num = 1

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')


def load_level(filename):
    filename = "data/" + filename
    level_map = open(filename, 'r').readlines()

    rez = []
    b = level_map[0].replace("[[", "").replace("]]", "")
    for line in b.split('],['):
        row = list(map(int, line.split(',')))
        rez.append(row)
    return (rez)


def reset_level(level_num):
    player.restart(100, screen_height - 130)
    enemy_group.empty()
    spike_group.empty()
    portal_group.empty()
    level = load_level(f'level{level_num}.txt')
    return level


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


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.image = pygame.transform.scale(self.image, (200, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.click = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] and not (self.click):
            action = True
            self.click = True

        if not (pygame.mouse.get_pressed()[0]):
            self.click = False

        screen.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.restart(x, y)

    def restart(self, x, y):
        self.images_right = []
        self.images_left = []
        self.images_death = []
        self.index = 0
        self.counter = 0
        self.flag = True
        self.sp = []
        self.jumped = False
        self.second_jump = True

        for num in range(9):
            img_right = load_image(f'{num}.png')
            img_right = pygame.transform.scale(img_right, (72 * 1.15, 86 * 1.15))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_left.append(img_left)
            self.images_right.append(img_right)
        for num in range(1, 7):
            img = load_image(f'dead_{num}.png')
            img = pygame.transform.scale(img, (72 * 1.15, 86 * 1.15))
            self.images_death.append(img)

        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.player_rect = pygame.Rect(self.rect[0], self.rect[1], self.rect[2], self.rect[3])
        self.vel_y = 0

        self.direction = 0

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped and not self.second_jump:
                self.vel_y = -17
                self.jumped = True
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_a]:
                self.counter += 1
                dx -= 3
                self.direction = -1
            if key[pygame.K_d]:
                self.counter += 1
                dx += 3
                self.direction = 1
            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                elif self.direction == -1:
                    self.image = self.images_left[self.index]

            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                elif self.direction == -1:
                    self.image = self.images_left[self.index]

            # gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # check for collision
            self.player_rect = pygame.Rect(self.rect[0] + 23, self.rect[1] + 21, 30, 78)
            self.second_jump = True

            for tile in world.tile_list:
                if tile[1].colliderect(self.player_rect[0] + dx, self.player_rect[1], self.player_rect[2],
                                       self.player_rect[3]):
                    dx = 0
                if tile[1].colliderect(self.player_rect[0], self.player_rect[1] + dy, self.player_rect[2],
                                       self.player_rect[3]):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top - 21
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.top - 86 * 1.15
                        self.vel_y = 0
                        self.second_jump = False

            for enemy in enemy_group:
                enemy_rect = pygame.Rect(enemy.rect[0] + 25, enemy.rect[1], enemy.rect[2] - 35, enemy.rect[3])

                if self.player_rect.colliderect(enemy_rect):
                    game_over = -1
                    break

            for spike in spike_group:
                spike_rect = pygame.Rect(spike.rect[0], spike.rect[1] + 20, spike.rect[2], spike.rect[3] - 20)

                if self.player_rect.colliderect(spike_rect):
                    game_over = -1
                    break

            for portal in portal_group:
                portal_rect = (portal.rect[0] + 10, portal.rect[1] + 20, portal.rect[2] - 20, portal.rect[3] - 20)

                if self.player_rect.colliderect(portal_rect):
                    game_over = 1

            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            if self.flag:
                dt = datetime.datetime.now().second
                if dt not in self.sp:
                    self.sp.append(dt)
                    if len(self.sp) > 5:
                        self.flag = False
                        self.image = self.images_death[5]
                    else:
                        self.image = self.images_death[len(self.sp)]
            else:
                if self.rect.y < 2000:
                    self.rect.y += 5

        screen.blit(self.image, self.rect)
        return game_over


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(load_image('skeleton.png'), (60 * 1.3, 58 * 1.3))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.move_counter += 1
        self.rect.x += self.move_direction
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
            self.image = pygame.transform.flip(self.image, True, False)


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(load_image('spike.png'), (tile_width, tile_height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(load_image('portal.png'), (tile_width, tile_height * 1.5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 25


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
                    elif tile == 3:
                        skeleton = Enemy(col_count * tile_height, row_count * tile_width - 25)
                        enemy_group.add(skeleton)

                    elif tile == 4:
                        spike = Spike(col_count * tile_height, row_count * tile_width)
                        spike_group.add(spike)

                    elif tile == 10:
                        portal = Portal(col_count * tile_height, row_count * tile_width)
                        portal_group.add(portal)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


level = load_level(f'level{level_num}.txt')

enemy_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
player = Player(100, screen_height - 130)

world = World(level)

fon = pygame.transform.scale(load_image('fon.png'), (screen_width, screen_height))
restart_img = load_image('restart.png')
start_img = load_image('start.png')
exit_img = load_image('exit.png')

restart_button = Button(screen_width // 2 - 100, screen_height // 2, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

running = True
while running:

    clock.tick(FPS)

    screen.blit(fon, (0, 0))
    if menu:
        if exit_button.draw():
            running = False
        if start_button.draw():
            menu = False
    else:
        world.draw()

        portal_group.draw(screen)

        game_over = player.update(game_over)
        if game_over == 0:
            enemy_group.update()

        enemy_group.draw(screen)
        spike_group.draw(screen)

        if game_over == -1:
            if restart_button.draw():
                game_over = 0
                player = Player(100, screen_height - 130)

        if game_over == 1:
            if level_num < 12:
                level_num += 1
                print(level)
                level = reset_level(level_num)
                world = World(level)
                game_over = 0
            else:
                level_num = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
