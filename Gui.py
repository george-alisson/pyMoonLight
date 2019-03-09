import pygame, time
from pygame.locals import *


SCREEN_RATIO = 1

def set_screen_ratio(scr):
    global SCREEN_RATIO 
    SCREEN_RATIO = (scr.get_height() / 550.0)

class Label:
    def __init__(self, text, icon="", iconType=0, userData=None, font=None, color=None, desc=""):
        self.text = text.rstrip()
        self.desc = desc.rstrip()
        self.icon = icon
        self.descFont = pygame.font.Font("res/OpenSans-Regular.ttf", int(18 * SCREEN_RATIO))
        self.iconFont = pygame.font.Font("res/Material-Design-Iconic-Font.ttf", int(30 * SCREEN_RATIO))
        self.iconType = iconType
        self.x = 0
        self.y = 0
        self.font = font
        self.userData = userData
        self.size = (0, 0)
        self.pos = (0, 0)
        self.rendered = None
        self.descRender = None
        self.iconRender = None
        if self.font == None:
            self.font = pygame.font.Font("res/OpenSans-Regular.ttf", int(30 * SCREEN_RATIO))
        self.color = color
        if self.color == None:
            self.color = [255, 255, 255]

    def get_width(self):
        return self.size[0]

    def get_height(self):
        return self.size[1]

    def getUserData(self):
        return self.userData

    def setPos(self, x, y):
        self.pos = (x, y)

    def setText(self, text):
        self.text = text.rstrip()

    def getSize(self):
        return self.size

    def getText(self):
        return self.text

    def setColor(self, color):
        self.color = color

    def setFont(self, font):
        self.font = font

    def setDesc(self, desc):
        self.desc = desc

    def setIcon(self, icon):
        self.icon = icon

    def render(self):
        if self.text != "":
            self.rendered = self.font.render(self.text, True, self.color)
            self.size = (self.rendered.get_width(), self.rendered.get_height())
        if self.desc != "":
            self.descRender = self.descFont.render(self.desc, True, [150, 150, 150])
            self.size = (self.size[0] + self.descRender.get_width(), self.size[1])
        if self.icon != "":
            if self.iconType == 0:
                self.iconRender = self.iconFont.render(self.icon, True, self.color)
            elif self.iconType == 1:
                self.iconRender = pygame.image.load(self.icon)
                x = int(self.rendered.get_height() * 0.8)
                self.iconRender = pygame.transform.smoothscale(self.iconRender, (x, x))

    def blit(self, target):
        if self.text != "" and self.rendered != None:
            target.blit(self.rendered, self.pos)
            if self.descRender != None:
                x = self.pos[0] + self.rendered.get_width() + int(10 * SCREEN_RATIO)
                y = self.pos[1] + (self.size[1] / 2) - (self.descRender.get_height() / 2) + 3
                target.blit(self.descRender, (x, y))
            if self.iconRender != None:
                x = self.pos[0] - int(10 * SCREEN_RATIO) - self.iconRender.get_width()
                y = self.pos[1] + (self.size[1] / 2) - (self.iconRender.get_height() / 2) + 2
                target.blit(self.iconRender, (x, y))
            return True
        return False

    def isHovering(self, posToCheck):
        return posToCheck[0] > self.pos[0] and posToCheck[0] < self.pos[0] + self.size[0] and posToCheck[1] > self.pos[
            1] and posToCheck[1] < self.pos[1] + self.size[1]


class Menu:
    def __init__(self, launcher, scr):
        # Initialize values
        self.bg = [51, 51, 51]
        self.fg1 = [255, 255, 255]
        self.fg2 = [154, 197, 12]
        self.screen = scr
        self.launcher = launcher
        self.items = []
        self.title = None
        self.desc = None
        self.selected = 0
        self.redraw = False
        self.scroll = 0

        # Initialize fonts
        self.font = pygame.font.Font("res/OpenSans-Regular.ttf", int(30 * SCREEN_RATIO))
        self.titleFont = pygame.font.Font("res/OpenSans-Regular.ttf", int(52 * SCREEN_RATIO))
        self.descFont = pygame.font.Font("res/OpenSans-Regular.ttf", int(16 * SCREEN_RATIO))
        self.clockFont = pygame.font.Font(None, 24)

        # Initialize joystick if needed
        self.joy = None
        if pygame.joystick.get_count() > 0:
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            self.joy = pygame.joystick.Joystick(0)
            if not self.joy.get_init():
                self.joy.init()
        else:
            print("No joysticks detected")

    def setColors(self, bg=[51, 51, 51], fg1=[255, 255, 255], fg2=[154, 197, 12]):
        self.bg = bg
        self.fg1 = fg1
        self.fg2 = fg2

    def msg(self, msg, desc=""):
        self.screen.fill(self.bg)
        renderedMsg = self.titleFont.render(msg, True, self.fg1)
        x = self.screen.get_width() / 2 - renderedMsg.get_width() / 2
        y = self.screen.get_height() / 2 - renderedMsg.get_height() / 2
        self.screen.blit(renderedMsg, (x, y))

        if desc != "":
            renderedDesc = self.descFont.render(desc, True, [150, 150, 150])
            x2 = self.screen.get_width() / 2 - renderedDesc.get_width() / 2
            y2 = self.screen.get_height() / 2 - renderedDesc.get_height() / 2 + renderedMsg.get_height()
            self.screen.blit(renderedDesc, (x2, y2))
            
        pygame.display.update()

    def menu(self, items, title=None, desc=None):
        # Initialize values
        self.items = items
        self.title = title
        self.desc = desc
        self.selected = 0
        self.scroll = 0

        if self.title != None:
            self.title.setPos(52, 52)
            self.title.setFont(self.titleFont)
        if self.desc != None:
            self.desc.setPos(52, 52)
            self.desc.setFont(self.descFont)
            self.desc.setColor([150, 150, 150])
        for item in self.items:
            item.setFont(self.font)

        # Some useful variables
        prevaxis = 0
        #updateTimer = time.time()
        parentLoaded = self.launcher.loaded
        gclock = pygame.time.Clock()

        redraw = True
        double_height = int((180 + 44 * len(self.items)) * SCREEN_RATIO)

        pygame.key.set_repeat(200, 100)

        # Main loop
        while self.launcher.loaded == parentLoaded:
            #time.sleep(0.01)
            gclock.tick(30)
            # Check for gamepad buttons
            for event in pygame.event.get(JOYBUTTONDOWN):
                # print("Btn: {0}".format(event.button))
                if event.button == 0:
                    return self.selected
                elif event.button == 14:
                    self.move_down()
                elif event.button == 13:
                    self.move_up()
                elif event.button == 1 or event.button == 6:
                    return -1

            for event in pygame.event.get(JOYHATMOTION):
                # print("Hat: {0}, value: {1}".format(event.hat, event.value))
                if event.hat == 0:
                    if event.value == (0, 1):
                        self.move_up()
                    elif event.value == (0, -1):
                        self.move_down()
                    elif event.value == (-1, 0):
                        self.move_up()
                    elif event.value == (1, 0):
                        self.move_down()

            # Check for gamepad axis
            for event in pygame.event.get(JOYAXISMOTION):
                if event.axis == 1:
                    if event.value < -0.5 and prevaxis >= -0.5:
                        self.move_up()
                    elif event.value > 0.5 and prevaxis <= 0.5:
                        self.move_down()
                    prevaxis = event.value

            # Check for mouse clicks
            for event in pygame.event.get(MOUSEBUTTONDOWN):
                if event.button == 1:
                    if self.items[self.selected].isHovering((event.pos[0], event.pos[1] - self.scroll)):
                        return self.selected
                elif event.button == 4 and self.scroll < 0:
                    #self.move_up()
                    self.scroll += int(60 * SCREEN_RATIO)
                    if self.scroll > 0:
                        self.scroll = 0
                    self.draw(False)
                elif event.button == 5 and abs(self.scroll) < double_height - self.screen.get_height():
                    #self.move_down()
                    self.scroll -= int(60 * SCREEN_RATIO)
                    if abs(self.scroll) > abs(double_height - self.screen.get_height()):
                        self.scroll = -(double_height - self.screen.get_height())
                    self.draw(False)
                elif event.button == 2:
                    return self.selected

            # Check for mouse motion
            for event in pygame.event.get(MOUSEMOTION):
                for i, button in enumerate(self.items):
                    if self.selected != i and button.isHovering((event.pos[0], event.pos[1] - self.scroll)):
                        self.selected = i
                        self.draw(False)

            for event in pygame.event.get(KEYDOWN):
                if event.key == K_RETURN:
                    return self.selected
                elif event.key == K_ESCAPE:
                    return -1
                elif event.key == K_DOWN:
                    self.move_down()
                elif event.key == K_UP:
                    self.move_up()

            pygame.event.clear()
            
            # Draw only clock if no redraw has been performed
            if redraw:
                self.draw()
                redraw = False
            else:
                self.draw_clock()

            pygame.display.update()
        return -1

    def draw_clock(self):
        clock = self.font.render(time.strftime("%H:%M:%S"), True, [100, 100, 100])
        rect = pygame.Rect(self.screen.get_width() - clock.get_width() - 20, self.screen.get_height() - clock.get_height() - 10, clock.get_width(),
                           clock.get_height())
        pygame.draw.rect(self.screen, self.bg, rect)
        self.screen.blit(clock, (rect.x, rect.y))

    def draw(self, scroll_to_pos=True):
        # Redraw entire screen if requested, can be optimized later, but for now its ok
        double = pygame.surface.Surface((self.screen.get_width(), int((180 + 45 * len(self.items)) * SCREEN_RATIO)))
        double.fill(self.bg)
        topmargin = 52
        if self.title != None:
            self.title.render()
            topmargin += self.title.getSize()[1]
            self.title.setPos(52 + (0 if self.title.iconRender is None else self.title.iconRender.get_width()), 52)
            self.title.blit(double)
        if self.desc != None:
            self.desc.setPos(52, topmargin)
            self.desc.render()
            topmargin += self.desc.getSize()[1]
            self.desc.blit(double)
        for i, item in enumerate(self.items):
            item.setColor(self.fg2 if i == self.selected else self.fg1)
            item.render()
            item.setPos(int(60 * SCREEN_RATIO) + (0 if item.iconRender is None else item.iconRender.get_width()), (item.getSize()[1] + 3) * i + topmargin + 20)
            item.blit(double)
        if scroll_to_pos:
            self.scroll = 0 if self.items[self.selected].pos[1] <= 440 * SCREEN_RATIO else int(440 * SCREEN_RATIO) - self.items[self.selected].pos[1]
        self.screen.fill(self.bg)
        self.screen.blit(double, (0, self.scroll))

    def move_up(self):
        if self.selected > 0:
            self.selected -= 1
        else:
            self.selected = len(self.items) - 1
        self.draw()

    def move_down(self):
        if self.selected < len(self.items) - 1:
            self.selected += 1
        else:
            self.selected = 0
        self.draw()
