# -*- coding: utf-8 -*-

import re
import time
import pygame
from pygame_vkeyboard.vkeyboard import VKey
from pygame.locals import *
from pygame_vkeyboard import VKeyboard, VKeyboardRenderer, VKeyboardLayout

DEFAULT_MSG = [u'Enter the IP address of your', 'GameStream PC']
ERROR_MSG = u'Invalid IP address'
SUCCESS_MSG = u'IP address saved!'
MSG_BKG_COLOR = (5, 10, 15)
MSG_SCS_BKG_COLOR = (60, 90, 60)
MSG_ERR_BKG_COLOR = (90, 60, 60)
MSG_TXT_COLOR = (240, 240, 240)
MSG_BKG_HEIGHT = 80

IP_BKG_COLOR = (40, 45, 50)
IP_TXT_COLOR = (240, 240, 240)
IP_LAYOUT = ['123', '456', '789', '', '']
IP_INPUT_REGEX = r"[0-9.]"
IP_REGEX = r"(^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$)"

SCREEN_RATIO = 1

def set_screen_ratio(scr):
    global SCREEN_RATIO
    SCREEN_RATIO = (scr.get_height() / 300.0)


class VSystemKey(VKey):
    def __init__(self, value, parent):
        VKey.__init__(self, value)
        self.font = pygame.font.Font('res/Material-Design-Iconic-Font.ttf', int(18 * SCREEN_RATIO))
        self.parent = parent
        self.text_color = ((250, 250, 250), (255, 255, 255), (30, 30, 30))


class VEnterKey(VSystemKey):
    def __init__(self, parent):
        #VSystemKey.__init__(self, u'\uf48a', parent)
        VSystemKey.__init__(self, u'\uf269', parent)
        self.background_color = ((50, 80, 50), (25, 50, 25), (240, 255, 240))
        self.text_color = ((250, 250, 250), (255, 255, 255), (50, 80, 50))

    def update_buffer(self, buffer):
        self.parent.key_enter_click()
        return buffer


class VNewBackKey(VSystemKey):
    def __init__(self, parent):
        VSystemKey.__init__(self, u'\uf1d9', parent)
        self.background_color = ((200, 150, 60), (70, 55, 0), (255, 245, 204))
        self.text_color = ((250, 250, 250), (255, 255, 255), (200, 150, 60))

    def update_buffer(self, buffer):
        return buffer[:-1]


class VCancelKey(VSystemKey):
    def __init__(self, parent):
        VSystemKey.__init__(self, u'\uf135', parent)
        self.background_color = ((135, 50, 50), (70, 0, 26), (255, 204, 204))
        self.text_color = ((250, 250, 250), (255, 255, 255), (135, 50, 50))

    def update_buffer(self, buffer):
        self.parent.key_cancel_click()
        return u''

class VDotKey(VKey):
    def __init__(self):
        VKey.__init__(self, '.')
        self.background_color = ((60, 80, 205), (0, 26, 70), (204, 245, 255))
        self.text_color = ((250, 250, 250), (255, 255, 255), (60, 80, 205))

class VZeroKey(VKey):
    def __init__(self):
        VKey.__init__(self, '0')
        self.length = 3

    def set_size(self, size):
        self.size = (size * self.length + ((self.length - 1) * 5), size)


class BackColorVKbdRenderer(VKeyboardRenderer):
    def __init__(self):
        font = pygame.font.Font('res/Roboto-Regular.ttf', int(22 * SCREEN_RATIO))
        VKeyboardRenderer.__init__(self, font, (30, 30, 30),
        ((250, 252, 251), (148, 158, 164), (230, 232, 231)),
        ((255, 255, 255), (255, 255, 255), (0, 0, 0)))
        self.number_key_background_color = (
            (60, 62, 61), (44, 53, 57), (125, 130, 135))

    def draw_key(self, surface, key):
        if hasattr(key, 'background_color'):
            background_color = key.background_color
        elif re.match(r'[0-9]', key.value):
            background_color = self.number_key_background_color
        else:
            background_color = self.key_background_color
        if hasattr(key, 'font'):
            font = key.font
        else:
            font = self.font
        if hasattr(key, 'text_color'):
            text_color = key.text_color
        else:
            text_color = self.text_color
        if hasattr(key, 'text_color'):
            text_color = key.text_color
        else:
            text_color = self.text_color
        pygame.draw.rect(
            surface, background_color[key.state], key.position + (key.size[0] + 4, key.size[1] + 4))
        size = font.size(key.value)
        x = key.position[0] + ((key.size[0] - size[0]) / 2) + 2
        y = key.position[1] + ((key.size[1] - size[1]) / 2) + 2
        surface.blit(font.render(
            key.value, 1, text_color[key.state], None), (x, y))


class MyVKeyboard(VKeyboard):

    def __init__(self, surface, text_consumer, layout, renderer):
        self.last_hovered = None
        VKeyboard.__init__(self, surface, text_consumer, layout, renderer=renderer)
    
    def on_key_up(self):
        if self.last_pressed is not None:
            self.set_key_state(self.last_pressed, 0)
            if self.last_hovered is not None:
                self.set_key_state(self.last_hovered, 2)
            self.buffer = self.last_pressed.update_buffer(self.buffer)
            self.text_consumer(self.buffer)
            self.last_pressed = None

    def on_event(self, event):
        if self.state > 0:
            if event.type == MOUSEBUTTONDOWN:
                key = self.layout.get_key_at(pygame.mouse.get_pos())
                if key is not None:
                    self.on_key_down(key)
            elif event.type == MOUSEBUTTONUP:
                self.on_key_up()
    
    def append_text(self, text):
        self.buffer += text
        self.text_consumer(self.buffer)

    def set_text(self, text):
        self.buffer = text
        self.text_consumer(self.buffer)


def layout_set_size(self, size, surface_size):
    self.size = size
    self.position = (0, surface_size[1] - self.size[1])
    y = self.position[1] + self.padding
    for row in self.rows:
        r = len(row)
        width = (r * self.key_size) + ((r + 1) * self.padding)
        x = (surface_size[0] - width) / 2
        if row.space is not None:
            x -= ((row.space.length - 1) * self.key_size +
                  ((row.space.length - 1) * self.padding)) / 2
        row.set_size((x, y), self.key_size, self.padding)
        y += self.padding + self.key_size


class IPVKeyboard(object):

    def __init__(self, window=None):
        set_screen_ratio(window)
        self.__running = False
        self.window = window
        self.result = None
        self.value = None
        self.keyboard = None
        self.layout = None
        self.msg_background = None
        self.ip_background = None

    def key_enter_click(self):
        if re.match(IP_REGEX, self.keyboard.buffer):
            self.message(SUCCESS_MSG, 0)
            time.sleep(0.8)
            self.result = 1
            self.value = self.keyboard.buffer
            self.stop()
        else:
            self.message(ERROR_MSG, 1)

    def key_cancel_click(self):
        self.result = 2
        self.stop()

    def message(self, msg=DEFAULT_MSG, state=-1):
        if state == -1:
            bgcolor = MSG_BKG_COLOR
        elif state == 1:
            bgcolor = MSG_ERR_BKG_COLOR
        else:
            bgcolor = MSG_SCS_BKG_COLOR

        self.msg_background.fill(bgcolor)
        font = pygame.font.Font('res/Roboto-Regular.ttf', int(24 * SCREEN_RATIO))
        if isinstance(msg,  list):
            for i, line in enumerate(msg):
                text = font.render(line, 1, MSG_TXT_COLOR)
                x = (self.msg_background.get_rect().width // 2) - \
                    (text.get_rect().width // 2)
                y = (self.msg_background.get_rect().height // 2) - \
                    (text.get_rect().height // 2) - \
                    int(15 * SCREEN_RATIO) + (int(30 * SCREEN_RATIO) * i)
                self.msg_background.blit(text, (x, y))
        else:
            text = font.render(msg, 1, MSG_TXT_COLOR)
            x = (self.msg_background.get_rect().width // 2) - \
                (text.get_rect().width // 2)
            y = (self.msg_background.get_rect().height // 2) - \
                (text.get_rect().height // 2)
            self.msg_background.blit(text, (x, y))
        self.window.blit(self.msg_background, (0, 0))
        pygame.display.flip()

    def consumer(self, text=""):
        self.ip_background.fill(IP_BKG_COLOR)
        font = pygame.font.Font('res/Roboto-Regular.ttf', int(30 * SCREEN_RATIO))
        txt = font.render(text, 1, IP_TXT_COLOR)
        x = (self.ip_background.get_rect().width // 2) - \
            (txt.get_rect().width // 2)
        y = (self.ip_background.get_rect().height // 2) - \
            (txt.get_rect().height // 2)
        self.ip_background.blit(txt, (x, y))
        self.window.blit(self.ip_background,
                         (0, int(MSG_BKG_HEIGHT * SCREEN_RATIO)))
        pygame.display.flip()

    def start(self):
        self.configure_background()
        self.configure_layout()
        self.keyboard = MyVKeyboard(self.window, self.consumer, self.layout, BackColorVKbdRenderer())
        self.configure_key_back()
        self.keyboard.enable()
        prevaxis = 0
        self.select_key(self.layout.rows[0].keys[0])
        if self.value is not None:
            self.keyboard.set_text(self.value)

        gclock = pygame.time.Clock()

        self.__running = True
        while self.__running:
            pygame.display.flip()
            #time.sleep(0.01)
            gclock.tick(30)

            for event in pygame.event.get(MOUSEBUTTONDOWN):
                self.mousebutton_events(event)

            for event in pygame.event.get(MOUSEBUTTONUP):
                self.mousebutton_events(event)

            for event in pygame.event.get(KEYDOWN):
                self.keydown_events(event)

            for event in pygame.event.get(MOUSEMOTION):
                key = self.layout.get_key_at(pygame.mouse.get_pos())
                if key is not None:
                    if key != self.keyboard.last_hovered:
                        self.unselect_last_key()
                        self.select_key(key)

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
                    if not isinstance(self.keyboard.last_hovered, VEnterKey):
                        self.message()
                    self.hit_key(self.keyboard.last_hovered)
                elif event.button == 3:
                    self.message()
                    self.hit_key(self.backkey)
                elif event.button == 1 or event.button == 6:
                    self.hit_key(self.cancelkey)
                elif event.button == 7:
                    self.hit_key(self.enterkey)
                elif event.button == 2:
                    self.message()
                    self.hit_key(self.dotkey)

            pygame.event.clear()

    def hit_key(self, key):
        self.keyboard.on_key_down(key)
        pygame.display.flip()
        time.sleep(0.1)
        self.keyboard.on_key_up()

    def move_right(self):
        self.unselect_last_key()

        i, j = self.find_last_hovered_key()
        if j + 1 < len(self.layout.rows[i].keys):
            key = self.layout.rows[i].keys[j + 1]
        else:
            key = self.layout.rows[i].keys[0]

        self.select_key(key)

    def move_left(self):
        self.unselect_last_key()

        i, j = self.find_last_hovered_key()
        if j - 1 >= 0:
            key = self.layout.rows[i].keys[j - 1]
        else:
            key = self.layout.rows[i].keys[-1]

        self.select_key(key)

    def move_down(self):
        self.unselect_last_key()

        i, j = self.find_last_hovered_key()
        if i + 1 < len(self.layout.rows) - 1:
            row = self.layout.rows[i + 1]
        else:
            row = self.layout.rows[0]
            j = 3 if j > 0 else 1
        if i == 2:
            j = 1 if j > 2 else 0
        key = row.keys[j]

        self.select_key(key)

    def move_up(self):
        self.unselect_last_key()

        i, j = self.find_last_hovered_key()
        if i - 1 >= 0:
            row = self.layout.rows[i - 1]
        else:
            row = self.layout.rows[-2]
            j = 1 if j > 2 else 0
        if i == 3:
            j = 3 if j > 0 else 1
        key = row.keys[j]

        self.select_key(key)

    def select_key(self, key):
        self.keyboard.set_key_state(key, 2)
        self.keyboard.last_hovered = key

    def unselect_last_key(self):
        self.keyboard.set_key_state(self.keyboard.last_hovered, 0)

    def find_last_hovered_key(self):
        for i, row in enumerate(self.layout.rows):
            for j, key in enumerate(row.keys):
                if key == self.keyboard.last_hovered:
                    return (i, j)
        return (0,0)

    def stop(self):
        self.__running = False

    def configure_key_back(self):
        del self.layout.rows[-1].keys[-1]

    def configure_layout(self):
        VKeyboardLayout.set_size = layout_set_size
        self.layout = VKeyboardLayout(IP_LAYOUT, allow_space=False,
                                 allow_special_chars=False, allow_uppercase=False)
        self.backkey = VNewBackKey(self)
        self.dotkey = VDotKey()
        self.cancelkey = VCancelKey(self)
        self.enterkey = VEnterKey(self)
        self.zerokey = VZeroKey()
        self.layout.rows[0].add_key(self.backkey, False)
        self.layout.rows[1].add_key(self.dotkey, False)
        self.layout.rows[2].add_key(self.cancelkey, False)
        self.layout.rows[3].add_key(self.enterkey, False)
        self.layout.rows[3].add_key(self.zerokey, True)
        self.layout.rows[3].space = self.zerokey

    def mousebutton_events(self, event):
        self.keyboard.on_event(event)
        key = self.layout.get_key_at(pygame.mouse.get_pos())
        if not isinstance(key, VEnterKey):
            self.message()

    def keydown_events(self, event):
        if event.key == K_BACKSPACE:
            self.message()
            self.hit_key(self.backkey)
        elif event.key == K_RETURN:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.hit_key(self.enterkey)
            else:
                if not isinstance(self.keyboard.last_hovered, VEnterKey):
                    self.message()
                self.hit_key(self.keyboard.last_hovered)
        elif event.key == K_DELETE:
            self.message()
            self.keyboard.set_text(u'')
        elif event.key == K_ESCAPE:
            self.hit_key(self.cancelkey)
        elif event.key == K_UP:
            self.move_up()
        elif event.key == K_DOWN:
            self.move_down()
        elif event.key == K_LEFT:
            self.move_left()
        elif event.key == K_RIGHT:
            self.move_right()
        elif re.match(IP_INPUT_REGEX, event.unicode):
            self.message()
            self.keyboard.append_text(event.unicode)

    def configure_background(self):
        self.msg_background = pygame.Surface(
            (self.window.get_rect().width, int(MSG_BKG_HEIGHT * SCREEN_RATIO)))
        self.msg_background = self.msg_background.convert()
        self.ip_background = pygame.Surface(
            (self.window.get_rect().width, self.window.get_rect().height // 2 - int(MSG_BKG_HEIGHT * SCREEN_RATIO)))
        self.ip_background = self.ip_background.convert()
        self.consumer()
        self.message()


