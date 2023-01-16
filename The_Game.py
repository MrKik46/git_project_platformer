import os
import sys
import datetime
import pygame

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()

clock = pygame.time.Clock()
FPS = 60

screen_size_cef = 1
screen_width = 1800 * screen_size_cef
screen_height = 1000 * screen_size_cef
tile_width = tile_height = 50 * screen_size_cef
game_over = 0
level_num = 4
level_col = 5
score = 0
menu = True
show_res = False
flag = True

font = pygame.font.SysFont('IMPACT', int(30 * screen_size_cef))
font_2 = pygame.font.SysFont('IMPACT', int(50 * screen_size_cef))

golden = (255, 223, 0)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Omniknight Adventure')


def show_text(message, font_, text_col, x, y):
    img = font_.render(message, True, text_col)
    screen.blit(img, (x, y))


def load_level(filename):
    filename = "data/" + filename
    level_map = open(filename, 'r').readlines()

    rez = []
    b = level_map[0].replace("[[", "").replace("]]", "")
    for line in b.split('],['):
        row = list(map(int, line.split(',')))
        rez.append(row)
    return rez


def reset_level(level_number):
    player.restart(100 * screen_size_cef, screen_height - (130 * screen_size_cef))
    enemy_group.empty()
    spike_group.empty()
    portal_group.empty()
    level = load_level(f'level{level_number}.txt')
    return level


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def start_cords(date, tile_w):
    for row in date:
        for tile in row:
            if tile == -1:
                return row.index(-1) * tile_w, date.index(row) * tile_w


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.image = pygame.transform.scale(self.image, (200 * screen_size_cef, 100 * screen_size_cef))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.click = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] and not self.click:
            action = True
            self.click = True

        if not (pygame.mouse.get_pressed()[0]):
            self.click = False

        screen.blit(self.image, self.rect)

        return action


class Player:
    def __init__(self, x, y):
        self.restart(x, y)

    def restart(self, x, y):
        self.images_right = []
        self.images_left = []
        self.images_death = []
        self.attack_right = []
        self.attack_left = []
        self.sp = []
        self.attack_index = 0
        self.attack_cooldown = 0
        self.pressed_mouse = []
        self.index = 0
        self.counter = 0
        self.healf = 3
        self.flag = True
        self.jumped = False
        self.second_jump = True
        self.attack_flag = False

        for num in range(9):
            img_right = load_image(f'{num}.png')
            img_right = pygame.transform.scale(img_right, (72 * 1.15 * screen_size_cef, 86 * 1.15 * screen_size_cef))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_left.append(img_left)
            self.images_right.append(img_right)

        for num in range(1, 7):
            img = load_image(f'dead_{num}.png')
            img = pygame.transform.scale(img, (72 * 1.15 * screen_size_cef, 86 * 1.15 * screen_size_cef))
            self.images_death.append(img)

        for num in range(1, 5):
            img = load_image(f'at_{num}.png')
            img_right = pygame.transform.scale(img, (72 * 1.15 * screen_size_cef, 86 * 1.15 * screen_size_cef))
            img_left = pygame.transform.flip(img_right, True, False)
            self.attack_left.append(img_left)
            self.attack_right.append(img_right)

        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.vel_x = 0

        self.direction = 0

        self.hit_cooldown = 0

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        attack_rect = 0

        self.player_rect = pygame.Rect(self.rect[0] + (23 * screen_size_cef), self.rect[1] + (21 * screen_size_cef),
                                       30 * screen_size_cef, 78 * screen_size_cef)

        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped and not self.second_jump:
                jump_sound.play()
                self.vel_y = (-17 * screen_size_cef)
                self.jumped = True
            if not key[pygame.K_SPACE]:
                self.jumped = False
            if key[pygame.K_a]:
                self.counter += 1
                dx -= (3 * screen_size_cef)
                self.direction = -1
            if key[pygame.K_d]:
                self.counter += 1
                dx += (3 * screen_size_cef)
                self.direction = 1
            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                elif self.direction == -1:
                    self.image = self.images_left[self.index]

            if pygame.mouse.get_pressed()[0] and self.attack_flag == False:
                self.attack_flag = True

            if self.attack_flag and (not (pygame.mouse.get_pressed()[0])):

                self.attack_cooldown += 1
                if self.attack_cooldown == 5:
                    self.attack_index += 1
                elif self.attack_cooldown > 5:
                    self.attack_cooldown = 0
                if self.attack_index < 4:
                    if pygame.mouse.get_pos()[0] >= self.player_rect[0]:
                        self.image = self.attack_right[self.attack_index]
                        if self.attack_index >= 2:
                            attack_rect = pygame.Rect(self.player_rect[0], self.player_rect[1],
                                                      self.player_rect[2] + (65 * screen_size_cef),
                                                      self.player_rect[3])
                        self.direction = 1
                    else:
                        self.image = self.attack_left[self.attack_index]
                        if self.attack_index >= 2:
                            attack_rect = pygame.Rect(self.player_rect[0] - (65 * screen_size_cef), self.player_rect[1],
                                                      self.player_rect[2] + (65 * screen_size_cef),
                                                      self.player_rect[3])
                        self.direction = -1
                    if self.attack_index >= 2:
                        for enemy in enemy_group:
                            enemy_rect = pygame.Rect(enemy.rect[0] + (25 * screen_size_cef), enemy.rect[1],
                                                     enemy.rect[2] - (35 * screen_size_cef),
                                                     enemy.rect[3])
                            if attack_rect.colliderect(enemy_rect):
                                death_sound.play()
                                enemy.kill()

                else:
                    self.attack_index = 0
                    self.attack_flag = False
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

            if self.vel_x < 0:
                self.vel_x += 1 * screen_size_cef
            elif self.vel_x > 0:
                self.vel_x -= 1 * screen_size_cef

            self.vel_y += 1 * screen_size_cef
            if self.vel_y > 10 * screen_size_cef:
                self.vel_y = 10 * screen_size_cef

            dy += self.vel_y
            dx += self.vel_x

            self.second_jump = True

            for tile in world.tile_list:
                if tile[1].colliderect(self.player_rect[0] + dx, self.player_rect[1], self.player_rect[2],
                                       self.player_rect[3]):
                    dx = 0
                if tile[1].colliderect(self.player_rect[0], self.player_rect[1] + dy, self.player_rect[2],
                                       self.player_rect[3]):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top - (21 * screen_size_cef)
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.top - (86 * 1.15 * screen_size_cef)
                        self.vel_y = 0
                        self.second_jump = False

            if self.hit_cooldown > 0:
                self.hit_cooldown -= 1

            for enemy in enemy_group:
                enemy_rect = pygame.Rect(enemy.rect[0] + 50 * screen_size_cef, enemy.rect[1] + 70 * screen_size_cef,
                                         enemy.rect[2] - 35 * screen_size_cef,
                                         enemy.rect[3])
                view = pygame.Rect(enemy_rect[0] - 300 * screen_size_cef, enemy_rect[1] - 130 * screen_size_cef,
                                   enemy_rect[2] + 550 * screen_size_cef,
                                   enemy_rect[3] + 200 * screen_size_cef)
                if self.player_rect.colliderect(enemy_rect):
                    if self.hit_cooldown == 0:
                        if enemy_rect[0] >= self.player_rect[0]:
                            self.vel_x -= 12 * screen_size_cef
                        else:
                            self.vel_x += 12 * screen_size_cef
                        self.vel_y -= 10 * screen_size_cef
                        self.healf -= 1
                        self.hit_cooldown = 50
                        death_sound.play()
                    break
                if self.player_rect.colliderect(view):
                    if self.player_rect[0] > enemy_rect[0]:
                        enemy.walk_right()
                    else:
                        enemy.walk_left()
                else:
                    enemy.roam()
            for spike in spike_group:
                spike_rect = pygame.Rect(spike.rect[0], spike.rect[1] + 20 * screen_size_cef, spike.rect[2],
                                         spike.rect[3] - 20 * screen_size_cef)

                if self.player_rect.colliderect(spike_rect):
                    death_sound.play()
                    self.healf -= 3
                    break

            if self.healf == 0:
                game_over = -1

            for portal in portal_group:
                portal_rect = (
                    portal.rect[0] + 10 * screen_size_cef, portal.rect[1] + 20 * screen_size_cef,
                    portal.rect[2] - 20 * screen_size_cef, portal.rect[3] - 20 * screen_size_cef)

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
                if self.rect.y < 2000 * screen_size_cef:
                    self.rect.y += 5

        screen.blit(self.image, self.rect)
        return game_over, self.healf


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(load_image('skeleton.png'),
                                            (60 * 1.3 * screen_size_cef, 58 * 1.3 * screen_size_cef))
        self.rect = self.image.get_rect()

        self.vel_y = 0
        self.vel_x = 0
        self.rect.x = x
        self.rect.y = y - 70 * screen_size_cef
        self.move_direction = 1
        self.move_counter = 0
        self.move_counter_2 = 0
        self.move_index = 0
        self.move = []
        self.flag = False

        for num in range(1, 8):
            img = load_image(f'w{num}.png')
            img_right = pygame.transform.scale(img, (128 * 1.15 * screen_size_cef, 128 * 1.15 * screen_size_cef))
            img_left = pygame.transform.flip(img_right, True, False)
            self.move.append(img_left)

    def walk_left(self):
        if level[self.rect[1] // int(50 * screen_size_cef) + 2][(self.rect[0] // int(50 * screen_size_cef)) + 1] \
                not in [19, 18, 17, 2, 1] \
                and level[self.rect[1] // int(50 * screen_size_cef) + 1][
            (self.rect[0] // int(50 * screen_size_cef)) + 1] \
                not in [19, 18, 17, 2, 1]:
            self.move_counter_2 += 1
            self.rect.x -= int(2 * screen_size_cef)
            if self.move_counter_2 > 5:
                self.move_index += 1
                self.move_counter_2 = 0
                if self.move_index > 6:
                    self.move_index = 0
                self.image = self.move[self.move_index]
            self.fall('left')
            self.jump('left')
        else:
            self.roam()

    def walk_right(self):
        if level[self.rect[1] // int(50 * screen_size_cef) + 2][(self.rect[0] // int(50 * screen_size_cef)) + 2] \
                not in [19, 18, 17, 2, 1] \
                and level[self.rect[1] // int(50 * screen_size_cef) + 1][
            (self.rect[0] // int(50 * screen_size_cef)) + 2] \
                not in [19, 18, 17, 2, 1]:
            self.move_counter_2 += 1
            self.rect.x += int(2 * screen_size_cef)
            if self.move_counter_2 > 5:
                self.move_index += 1
                self.move_counter_2 = 0
                if self.move_index > 6:
                    self.move_index = 0
                self.image = self.move[self.move_index]
                self.image = pygame.transform.flip(self.image, True, False)
            self.fall('right')
            self.jump('right')
        else:
            self.roam()

    def fall(self, direction):
        if direction == 'left':
            if level[self.rect[1] // int(50 * screen_size_cef) + 3][((self.rect[0]) // int(50 * screen_size_cef)) + 2] \
                    == 0:
                self.rect.y += tile_width
        if direction == 'right':
            if level[self.rect[1] // int(50 * screen_size_cef) + 3][((self.rect[0]) // int(50 * screen_size_cef)) + 1] \
                    == 0:
                self.rect.y += tile_width

    def jump(self, direction):
        if direction == 'left':
            if level[self.rect[1] // int(50 * screen_size_cef) + 2][
                (self.rect[0] // int(50 * screen_size_cef)) + 1] in [19, 18, 17, 2, 1] \
                    and level[self.rect[1] // int(50 * screen_size_cef) + 1][(self.rect[0] // int(50 * screen_size_cef))
                                                                             + 1] not in [19, 18, 17, 2, 1]:
                self.rect.y -= tile_width

        if direction == 'right':
            if level[self.rect[1] // int(50 * screen_size_cef) + 2][
                (self.rect[0] // int(50 * screen_size_cef)) + 2] in [19, 18, 17, 2, 1] \
                    and level[self.rect[1] // int(50 * screen_size_cef) + 1][(self.rect[0] // int(50 * screen_size_cef))
                                                                             + 2] not in [19, 18, 17, 2, 1]:
                self.rect.y -= tile_width

    def roam(self):
        self.move_counter_2 += 1
        self.move_counter += 1
        if level[self.rect[1] // int(50 * screen_size_cef) + 2][(self.rect[0] // int(50 * screen_size_cef)) + 1] \
                not in [19, 18, 17, 2, 1] and \
                level[self.rect[1] // int(50 * screen_size_cef) + 2][(self.rect[0] // int(50 * screen_size_cef)) + 3] \
                not in [19, 18, 17, 2, 1]:
            self.rect.x += (self.move_direction * screen_size_cef)
        else:
            if level[self.rect[1] // int(50 * screen_size_cef) + 2][(self.rect[0] // int(50 * screen_size_cef)) + 3] \
                    in [19, 18, 17, 2, 1]:
                self.rect.x -= 1
            else:
                self.rect.x += 1
            self.move_direction *= -1
            if self.flag:
                self.flag = False
            else:
                self.flag = True

        if self.move_counter_2 > 5:
            self.move_index += 1
            self.move_counter_2 = 0
            if self.move_index > 6:
                self.move_index = 0
            self.image = self.move[self.move_index]
            if not self.flag:
                self.image = pygame.transform.flip(self.image, True, False)

        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
            if self.flag:
                self.flag = False
            else:
                self.flag = True
        if self.move_direction == 1:
            self.fall('right')
        else:
            self.fall('left')


class Money(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(load_image('coin.png'),
                                            (tile_width // 1.5 * screen_size_cef, tile_height // 1.5))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


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
        self.rect.y = y - 25 * screen_size_cef


class World:
    def __init__(self, date):
        self.tile_list = []
        dirt_image = load_image('dirt.png')
        grass_image = load_image('dirt_grass.png')
        grass_top_right_image = load_image('dirt_grass_right_top.png')
        grass_atr_image = load_image('grass_atr.png')
        grass_tl_image = load_image('grass_tl.png')
        grass_atl_image = load_image('grass_atl.png')
        tile3_image = load_image('tile3.png')
        tile2_image = load_image('tile2.png')
        bookshelf_image = load_image('bookshelf.png')
        candle_image = load_image('candle.png')
        lamp_image = load_image('lamp.png')
        tree1 = load_image('tree1.png')
        tree2 = load_image('tree2.png')
        tree3 = load_image('tree3.png')
        bush_image = load_image('bush.png')
        mushroom_image = load_image('mushroom.png')
        row_count = 0
        for row in range(len(date)):
            col_count = 0
            for tile in date[row]:
                if tile != 0:
                    if int(tile) == 1:
                        img = pygame.transform.scale(grass_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 2:
                        img = pygame.transform.scale(dirt_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 3:
                        skeleton = Enemy(col_count * tile_height, row_count * tile_width - 25 * screen_size_cef)
                        enemy_group.add(skeleton)
                    elif int(tile) == 4:
                        spike = Spike(col_count * tile_height, row_count * tile_width)
                        spike_group.add(spike)
                    elif int(tile) == 5:
                        img = pygame.transform.scale(bookshelf_image, (tile_width * 1, tile_height * 1.5))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height - 25 * screen_size_cef
                        img_rect.width = 0
                        img_rect.height = 0
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 6:
                        img = pygame.transform.scale(candle_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        img_rect.width = 0
                        img_rect.height = 0
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 7:
                        img = pygame.transform.scale(lamp_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        img_rect.width = 0
                        img_rect.height = 0
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 8:
                        img = pygame.transform.scale(tile2_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 9:
                        img = pygame.transform.scale(tile3_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        img_rect.width = 0
                        img_rect.height = 0
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 10:
                        portal = Portal(col_count * tile_height, row_count * tile_width)
                        portal_group.add(portal)
                    elif int(tile) == 11:
                        coin = Money(col_count * tile_height + (tile_height // 2),
                                     row_count * tile_width + (tile_width // 2))
                        Money_group.add(coin)
                    elif int(tile) == 12:
                        img = pygame.transform.scale(mushroom_image, (tile_width * 3, tile_height * 3))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width - 40 * screen_size_cef
                        img_rect.y = row_count * tile_height - 100 * screen_size_cef
                        img_rect.width = 0
                        img_rect.height = 0
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 13:
                        img = pygame.transform.scale(bush_image, (tile_width * 2, tile_height * 2))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width - 50 * screen_size_cef
                        img_rect.y = row_count * tile_height - 50 * screen_size_cef
                        img_rect.width = 0
                        img_rect.height = 0
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 14:
                        img = pygame.transform.scale(tree1, (tile_width * 2, tile_height * 4))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width - 25 * screen_size_cef
                        img_rect.y = row_count * tile_height - 150 * screen_size_cef
                        img_rect.width = 0
                        img_rect.height = 0
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 15:
                        img = pygame.transform.scale(tree2, (tile_width * 2, tile_height * 2.5))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width - 25 * screen_size_cef
                        img_rect.y = row_count * tile_height - 75 * screen_size_cef
                        img_rect.width = 0
                        img_rect.height = 0
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 16:
                        img = pygame.transform.scale(tree3, (tile_width * 3, tile_height * 4.5))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width - 40 * screen_size_cef
                        img_rect.y = row_count * tile_height - 175 * screen_size_cef
                        img_rect.width = 0
                        img_rect.height = 0
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 17:
                        img = pygame.transform.scale(grass_top_right_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 18:
                        img = pygame.transform.scale(grass_atr_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 19:
                        img = pygame.transform.scale(grass_tl_image, (tile_width, tile_height))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_width
                        img_rect.y = row_count * tile_height
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    elif int(tile) == 20:
                        img = pygame.transform.scale(grass_atl_image, (tile_width, tile_height))
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


level = load_level(f'level{level_num}.txt')

enemy_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
Money_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()

start_x, start_y = start_cords(level, tile_width)
player = Player(start_x, start_y)

world = World(level)

fon = pygame.transform.scale(load_image('forest.png'), (screen_width, screen_height))
restart_img = load_image('restart.png')
start_img = load_image('start.png')
exit_img = load_image('exit.png')
results_img = load_image('results.png')
back_img = load_image('back.png')

HP_3 = pygame.transform.scale(load_image('Hp3.png'), (100 * screen_size_cef, 30 * screen_size_cef))
HP_2 = pygame.transform.scale(load_image('Hp2.png'), (100 * screen_size_cef, 30 * screen_size_cef))
HP_1 = pygame.transform.scale(load_image('Hp1.png'), (100 * screen_size_cef, 30 * screen_size_cef))
HP_0 = pygame.transform.scale(load_image('Hp0.png'), (100 * screen_size_cef, 30 * screen_size_cef))

pickup_coin_sound = pygame.mixer.Sound('data/pickupCoin.wav')
pickup_coin_sound.set_volume(0.5)
jump_sound = pygame.mixer.Sound('data/jump.wav')
jump_sound.set_volume(0.2)
teleport = pygame.mixer.Sound('data/teleport.wav')
teleport.set_volume(0.5)
death_sound = pygame.mixer.Sound('data/hit.wav')
death_sound.set_volume(0.5)
# pygame.mixer.music.load('data/bg_music.mp3')
# pygame.mixer.music.play(-1, 0.0, 5000)
# pygame.mixer.music.set_volume(0.5)

coin_pic = Money(tile_height // 2, tile_width // 2)
Money_group.add(coin_pic)

restart_button = Button(screen_width // 2 - 100 * screen_size_cef, screen_height // 2, restart_img)
start_button = Button(screen_width // 2 - 350 * screen_size_cef, screen_height // 2, start_img)
results_button = Button(screen_width // 2 - 100 * screen_size_cef, screen_height // 2, results_img)
back_button = Button(screen_width // 2 - 100 * screen_size_cef, screen_height // 2 + 300 * screen_size_cef, back_img)
exit_button = Button(screen_width // 2 + 150 * screen_size_cef, screen_height // 2, exit_img)
exit_button_2 = Button(screen_width // 2 - 100 * screen_size_cef, screen_height // 2 + 90 * screen_size_cef, exit_img)

running = True
while running:
    sp = []
    clock.tick(FPS)
    screen.blit(fon, (0, 0))
    if menu:
        show_text('Вы - герой игры Dota 2,  рыцарь Omniknight.', font_2, (50, 200, 80),
                  screen_width // 2 - 400 * screen_size_cef,
                  screen_height // 2 - 350 * screen_size_cef)
        show_text('Вы пробираетесь через лес,  пытаясь добраться', font_2, (50, 200, 80),
                  screen_width // 2 - 400 * screen_size_cef,
                  screen_height // 2 - 300 * screen_size_cef)
        show_text('до своей башни,  попутно избегая все ловушки, ', font_2, (50, 200, 80),
                  screen_width // 2 - 400 * screen_size_cef,
                  screen_height // 2 - 250 * screen_size_cef)
        show_text('препятствия и собирая золотые монеты', font_2, (50, 200, 80),
                  screen_width // 2 - 400 * screen_size_cef,
                  screen_height // 2 - 200 * screen_size_cef)
        show_text('Чем больше вы соберёте,  тем лучше.', font_2, (50, 200, 80),
                  screen_width // 2 - 400 * screen_size_cef,
                  screen_height // 2 - 150 * screen_size_cef)
        show_text('Удачи!', font_2, (50, 200, 80),
                  screen_width // 2 - 50 * screen_size_cef,
                  screen_height // 2 + 200 * screen_size_cef)
        show_text('P.S Остерегайтесь  лесьников', font_2, (50, 200, 80),
                  screen_width // 2 - 250 * screen_size_cef,
                  screen_height // 2 + 350 * screen_size_cef)
        if results_button.draw():
            show_res = True
            menu = False
        if exit_button.draw():
            running = False
        if start_button.draw():
            menu = False
            flag = True
    elif show_res:
        if os.path.exists('data\coins.txt'):
            file = open('data\coins.txt', 'r')
            for i in file.readlines():
                sp.append(i)
            if len(sp) < 10:
                kol = len(sp)
            else:
                kol = 10
            sp = sp[::-1]
            for i in range(kol):
                text = sp[i].replace("\n", "")
                show_text(f'{i + 1})  {text}', font_2, (50, 200, 80),
                          screen_width // 2 - 200 * screen_size_cef,
                          100 * screen_size_cef + (60 * screen_size_cef * i))
        else:
            show_text('Результатов ещё нет', font_2, (50, 200, 80),
                      screen_width // 2 - 250 * screen_size_cef,
                      screen_height // 2)

        if back_button.draw():
            menu = True
            show_res = False

    else:
        game_over, healf = player.update(game_over)
        world.draw()
        portal_group.draw(screen)
        Money_group.draw(screen)
        if game_over == 0:
            for coin in Money_group:
                if coin.rect.colliderect(
                        pygame.Rect(player.rect[0] + 23 * screen_size_cef, player.rect[1] + 21 * screen_size_cef,
                                    30 * screen_size_cef, 78 * screen_size_cef)):
                    score += 1
                    pickup_coin_sound.play()
                    Money_group.remove(coin)
            show_text('X    ' + str(score), font, golden, tile_width - 10 * screen_size_cef,
                      tile_height - 43 * screen_size_cef)

        enemy_group.draw(screen)
        spike_group.draw(screen)

        if healf >= 3:
            NHP = HP_3
        elif healf == 2:
            NHP = HP_2
        elif healf == 1:
            NHP = HP_1
        else:
            NHP = HP_0

        screen.blit(NHP, (tile_width + 50 * screen_size_cef, tile_height - 40 * screen_size_cef))

        if game_over == -1:
            show_text('YOU DIED!', font_2, (200, 200, 200), screen_width // 2 - 95 * screen_size_cef,
                      screen_height // 2 - 50 * screen_size_cef)
            if flag:
                if os.path.exists('data\coins.txt'):
                    file = open('data\coins.txt', 'r')
                    for i in file.readlines():
                        sp.append(i)
                    file = open('data\coins.txt', 'w')
                    sp.append(f'Collected coins: {score}\n')
                    file.writelines(sp)
                    file.close()
                else:
                    file = open('data\coins.txt', 'w')
                    file.write(f'Collected coins: {score}\n')
                    file.close()
                flag = False
            if restart_button.draw():
                level = reset_level(level_num)
                world = World(level)
                game_over = 0
                score = 0
                flag = True

        if game_over == 1:
            if level_num < level_col:
                level_num += 1
                enemy_group.empty()
                Money_group.empty()
                Money_group.add(coin_pic)
                teleport.play()
                level = reset_level(level_num)
                world = World(level)
                start_x, start_y = start_cords(level, tile_width)
                player.restart(start_x, start_y)
                game_over = 0
            else:
                if flag:
                    if os.path.exists('data\coins.txt'):
                        file = open('data\coins.txt', 'r')
                        for i in file.readlines():
                            sp.append(i)
                        file = open('data\coins.txt', 'w')
                        sp.append(f'Collected coins: {score}\n')
                        file.writelines(sp)
                        file.close()
                    else:
                        file = open('data\coins.txt', 'w')
                        file.write(f'{score}\n')
                        file.close()
                    flag = False
                show_text('Поздравляем! Вы нашили свою башню!', font_2, (50, 200, 80),
                          screen_width // 2 - 400 * screen_size_cef,
                          screen_height // 2 - 50 * screen_size_cef)
                if exit_button_2.draw():
                    running = False
                    flag = True
                if restart_button.draw():
                    flag = True
                    level_num = 0
                    level = reset_level(level_num)
                    world = World(level)
                    score = 0
                    game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
