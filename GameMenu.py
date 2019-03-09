import os
import pygame
from pygame.locals import *
import Moonlight

SCREEN_RATIO = 1

def set_screen_ratio(scr):
    global SCREEN_RATIO
    SCREEN_RATIO = (scr.get_height() / 1080.0)

class Tile:

    def __init__(self, text, image="res/nobox.png", fontsize=30, bgcolor=(60, 60, 60), fgcolor=(255, 255, 255), is_back=False):
        self.text = text
        self.bgcolor = bgcolor
        self.fgcolor = fgcolor
        self.font = pygame.font.Font("res/OpenSans-Regular.ttf", int(fontsize * SCREEN_RATIO))
        self.image = image
        
        self.image_render = None
        self.text_render = None
        self.tile_render = None
        self.size = (int(300 * SCREEN_RATIO), int(400 * SCREEN_RATIO))
        self.pos = (0, 0)
        self.grid = (0, 0)
        self.is_back = is_back
        self.set_text_layer_height()

    #adapeted from https://www.pygame.org/wiki/TextWrap
    def draw_text(self, surface, text, rect):
        rect = Rect(rect)
        rect.left = (surface.get_width() - rect.right) / 2
        y = rect.top
        line_spacing = -2

        font_height = self.font.size("Tg")[1]

        while text:
            i = 1
            if y + font_height > rect.bottom:
                break

            while self.font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1

            if i < len(text): 
                i = text.rfind(" ", 0, i) + 1

            image = self.font.render(text[:i], True, self.fgcolor)

            surface.blit(image, (rect.centerx - image.get_width() / 2, y))
            y += font_height + line_spacing

            text = text[i:]

        return y

    def set_text_layer_height(self, value=90):
        self.text_layer_height = int(value * SCREEN_RATIO)

    def render(self):
        if self.text:
            text_layer = pygame.surface.Surface((int(270 * SCREEN_RATIO), self.text_layer_height), pygame.SRCALPHA, 32)
            #text_layer = text_layer.convert_alpha()
            text_layer.fill((30, 30, 30, 180))
            height = 8 + self.draw_text(text_layer, self.text, (0, 0, int(240 * SCREEN_RATIO), self.text_layer_height + 2))
            self.text_render = pygame.surface.Surface((int(270 * SCREEN_RATIO), height), pygame.SRCALPHA, 32)
            self.text_render.blit(text_layer, (0, 0))
        if self.image:
            if not os.path.isfile(self.image):
                self.image_render = pygame.image.load("res/nobox.png")
            else:
                self.image_render = pygame.image.load(self.image)
            w, h = int(self.size[0] * 0.9), int(self.size[1] * 0.9)
            self.image_render = pygame.transform.smoothscale(self.image_render, (w, h))
        self.tile_render = pygame.surface.Surface(self.size)
        

    def blit(self, target):
        if self.tile_render != None:
            self.tile_render.fill(self.bgcolor)
            if self.image_render != None:
                x = (self.size[0] - self.image_render.get_width()) / 2
                y = (self.size[1] - self.image_render.get_height()) / 2
                self.tile_render.blit(self.image_render, (x, y))
            if self.text_render != None:
                x = (self.size[0] - self.text_render.get_width()) / 2
                y = self.size[1] - (self.text_render.get_height() + int(20 * SCREEN_RATIO))
                self.tile_render.blit(self.text_render, (x, y))
            target.blit(self.tile_render, self.pos)
            return True
        return False

    def get_width(self):
        return self.size[0]

    def get_height(self):
        return self.size[1]

    def is_hovering(self, posToCheck):
        return posToCheck[0] > self.pos[0] and posToCheck[0] < self.pos[0] + self.size[0] and posToCheck[1] > self.pos[
            1] and posToCheck[1] < self.pos[1] + self.size[1]

class GameMenu:

    def __init__(self, screen, items=[], bgcolor=(30, 30, 30), tilecolor=(60, 63, 65),  selcolor=(60, 100, 0)):
        set_screen_ratio(screen)
        self.bgcolor = bgcolor
        self.screen = screen
        self.double = None
        self.__running = False
        self.scroll = 0
        self.selected = (0, 0)
        self.selcolor = selcolor
        self.tilecolor = tilecolor
        self.wmargin = 30
        self.hmargin = 52
        self.padding = 10
        self.msg("Loading game list", "Please wait")
        self.set_itens(items)

    def center_rows(self):
        if self.rows:
            self.wmargin = (self.screen.get_width() - (self.wmargin * 2) - (len(self.rows[0]) * (self.items[0].get_width()))) / 2            

    def set_itens(self, items):
        items = [Tile("Back", "res/back.png", 50, is_back=True)] + items
        self.rows = []
        col = []
        width = 0
        i = 0
        j = 0
        for item in items:
            col.append(item)
            item.grid = (i, j)
            if item.get_width() + width < self.screen.get_width() - (self.wmargin * 2) - (self.padding * j) - item.get_width():
                width += item.get_width()
                j += 1
            else:
                self.rows.append(col)
                col = []
                width = 0
                i += 1
                j = 0
        if col:
            self.rows.append(col)
        self.items = items

    def stop(self):
        self.__running = False

    def get_selected_app(self):
        selected = self.get_tile_at(self.selected)
        if not selected.is_back:
            return selected.text

    def start(self):
        self.__running = True
        gclock = pygame.time.Clock()

        redraw = True
        double_height = self.hmargin * 2 + int(len(self.rows) * 410 * SCREEN_RATIO)
        self.double = pygame.surface.Surface((self.screen.get_width(), double_height))

        self.center_rows()
        prevaxis = 0
        pygame.key.set_repeat(300, 300)

        while self.__running:
            gclock.tick(30)

            for event in pygame.event.get(MOUSEMOTION):
                for tile in self.items:
                    if tile.grid != self.selected and tile.is_hovering((event.pos[0], event.pos[1] - self.scroll)):
                        self.change_selection(tile, False)
                        
            for event in pygame.event.get(MOUSEBUTTONDOWN):
                if event.button == 1:
                    selected = self.get_tile_at(self.selected)
                    if selected.is_hovering((event.pos[0], event.pos[1] - self.scroll)):
                        return self.get_selected_app()
                elif event.button == 4 and self.scroll < 0:
                    #self.move_up()
                    self.scroll += int(200 * SCREEN_RATIO)
                    if self.scroll > 0:
                        self.scroll = 0
                    self.draw_double()
                elif event.button == 5 and abs(self.scroll) < double_height - self.screen.get_height():
                    #self.move_down()
                    self.scroll -= int(200 * SCREEN_RATIO)
                    if abs(self.scroll) > double_height - self.screen.get_height():
                        self.scroll = -(double_height - self.screen.get_height())
                    self.draw_double()
                elif event.button == 2:
                    return self.get_selected_app()

            for event in pygame.event.get(KEYDOWN):
                if event.key == K_ESCAPE:
                    self.stop()
                elif event.key == K_UP:
                    self.move_up()
                elif event.key == K_DOWN:
                    self.move_down()
                elif event.key == K_LEFT:
                    self.move_left()
                elif event.key == K_RIGHT:
                    self.move_right()
                elif event.key == K_RETURN:
                    return self.get_selected_app()

            for event in pygame.event.get(JOYHATMOTION):
                # print("Hat: {0}, value: {1}".format(event.hat, event.value))
                if event.hat == 0:
                    if event.value == (0, 1):
                        self.move_up()
                    elif event.value == (0, -1):
                        self.move_down()
                    elif event.value == (-1, 0):
                        self.move_left()
                    elif event.value == (1, 0):
                        self.move_right()

            for event in pygame.event.get(JOYAXISMOTION):
                # print("Axis: {0}".format(event.axis))
                if event.axis == 1:
                    if event.value < -0.5 and prevaxis >= -0.5:
                        self.move_up()
                    elif event.value > 0.5 and prevaxis <= 0.5:
                        self.move_down()
                    prevaxis = event.value
                elif event.axis == 0:
                    if event.value < -0.5 and prevaxis >= -0.5:
                        self.move_left()
                    elif event.value > 0.5 and prevaxis <= 0.5:
                        self.move_right()
                    prevaxis = event.value

            for event in pygame.event.get(JOYBUTTONDOWN):
                #print("Btn: {0}".format(event.button))
                if event.button == 0:
                    return self.get_selected_app()
                elif event.button == 1 or event.button == 6:
                    self.stop()

            pygame.event.clear()

            if redraw:
                self.double.fill(self.bgcolor)
                for tile in self.items:
                    self.draw_tile(tile)
                self.screen.fill(self.bgcolor)
                self.screen.blit(self.double, (0, 0))
                redraw = False
            
            pygame.display.update()

    def move_up(self):
        i, j = self.selected
        if i - 1 >= 0:
            row = self.rows[i - 1]
        else:
            row = self.rows[-1]
        while j >= len(row):
            j -= 1
        self.change_selection(row[j])

    def move_down(self):
        i, j = self.selected
        if i + 1 <= len(self.rows) - 1:
            row = self.rows[i + 1]
        else:
            row = self.rows[0]
        while j >= len(row):
            j -= 1
        self.change_selection(row[j])

    def move_right(self):
        i, j = self.selected
        if j + 1 < len(self.rows[i]):
            tile = self.rows[i][j + 1]
        else:
            tile = self.rows[i][0]
        self.change_selection(tile)

    def move_left(self):
        i, j = self.selected
        if j - 1 >= 0:
            tile = self.rows[i][j - 1]
        else:
            tile = self.rows[i][-1]
        self.change_selection(tile)

    def msg(self, msg, desc=""):
        self.screen.fill(self.bgcolor)
        font = pygame.font.Font("res/OpenSans-Regular.ttf", int(100 * SCREEN_RATIO))
        rendered_msg = font.render(msg, True, (255, 255, 255))
        x = self.screen.get_width() / 2 - rendered_msg.get_width() / 2
        y = self.screen.get_height() / 2 - rendered_msg.get_height() / 2
        self.screen.blit(rendered_msg, (x, y))

        if desc != "":
            descfont = pygame.font.Font("res/OpenSans-Regular.ttf", int(30 * SCREEN_RATIO))
            rendered_desc = descfont.render(desc, True, (150, 150, 150))
            x2 = self.screen.get_width() / 2 - rendered_desc.get_width() / 2
            y2 = self.screen.get_height() / 2 - rendered_desc.get_height() / 2 + rendered_msg.get_height()
            self.screen.blit(rendered_desc, (x2, y2))
        pygame.display.update()

    def change_selection(self, tile, scroll_to_pos = True):
        selected = self.get_tile_at(self.selected)
        selected.set_text_layer_height()
        self.selected = tile.grid
        if not tile.is_back:
            tile.set_text_layer_height(360)
        self.draw_tile(selected)
        self.draw_tile(tile)
        if scroll_to_pos: 
            self.scroll = 0 if tile.pos[1] <= (520 * SCREEN_RATIO) else int(550 * SCREEN_RATIO) - tile.pos[1]
        self.draw_double()

    def draw_double(self):
        self.screen.fill(self.bgcolor)
        self.screen.blit(self.double, (0, self.scroll))

    def draw_tile(self, tile):
        if self.double:
            tile.bgcolor = self.selcolor if tile.grid == self.selected else self.tilecolor
            tile.render()
            x = (tile.size[0] + self.padding) * tile.grid[1] + self.wmargin
            y = (tile.size[1] + self.padding) * tile.grid[0] + self.hmargin
            tile.pos = (x, y)
            tile.blit(self.double)

    def get_tile_at(self, pos):
        return self.rows[pos[0]][pos[1]]


        
        
