#!/usr/bin/env python
import os
import sys
import time
import pygame
import threading
import signal
from Gui import Menu, Label, set_screen_ratio
from Moonlight import Moonlight
from pygame.locals import *
from IPKeyboard import IPVKeyboard
import Nvstream
import GameMenu


def signalHandler(signal, frame):
    Startup.thread.stop()
    sys.exit(0)


class QuitThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.active = True
        self.joy = None
        self.running = True

    def setActive(self, active):
        self.active = active

    def stop(self):
        self.running = False

    def run(self):
        print("Quit thread starting")
        if not pygame.joystick.get_init():
            pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            if not self.joy.get_init():
                self.joy.init()
        else:
            return 0

        print("Quit thread running")
        while self.running:
            if self.active:
                if self.joy.get_button(4) and self.joy.get_button(5) and self.joy.get_button(6):
                    print("Force stream quit!")
                    Startup.menu.msg("Stopping stream")
                    Startup.moonlight.quit()
                time.sleep(0.25)


class Startup:
    def __init__(self):
        self.screen = None
        self.menu = None
        self.moonlight = None
        self.loaded = 0
        self.thread = None

    def main(self):
        # Initialize Startup

        # Set working directory
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        # Set driver, fix problems on certain devices
        #drivers = ['fbcon', 'directfb', 'svgalib']
        #found = False
        #for driver in drivers:
        #    if not os.getenv('SDL_VIDEODRIVER'):
        #        os.putenv('SDL_VIDEODRIVER', driver)
        #    try:
        #        pygame.display.init()
        #        print("Using {0} as video driver".format(driver))
        #    except pygame.error:
        #        continue
        #    found = True
        #    break

        #if not found:
        #    print("Suitable video driver not found!")
        #    sys.exit(2)

        try:
            pygame.display.init()
            driver = pygame.display.get_driver()
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            print("Using {0} as video driver".format(driver))
        except pygame.error:
            print("Suitable video driver not found!")
            sys.exit(2)

        # Initialize PyGame
        print("Initializing PyGame")
        pygame.init()
        pygame.font.init()
        pygame.display.init()
        #self.screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h),
        #                                       pygame.FULLSCREEN)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        self.screen = pygame.display.set_mode((1280,720), pygame.NOFRAME)
        self.screen.fill((0, 0, 0))
        pygame.display.update()

        set_screen_ratio(self.screen)

        # Initialize other stuff
        print("Initializing menu")
        self.menu = Menu(self, self.screen)

        print("Initializing moonlight")
        self.moonlight = Moonlight()
        self.moonlight.loadConfig()

        if len(sys.argv) > 1:
            if sys.argv[1] == "map":
                self.loadMapping()
                return
            else:
                self.moonlight.ip = sys.argv[1]
        
        self.thread = QuitThread()
        self.thread.start()
        return self.loadMainMenu()

    def loadMainMenu(self):
        self.loaded = 1
        if not self.moonlight.isIpDefined():
            return self.loadSetPC()
        items = [Label(i, j) for i, j in [("Stream", u"\uF12F"), ("Steam Big Picture", u"\uF35D"), ("Settings", u"\uF1C6"), ("Computer", u"\uF2DC"), 
                                          ("Quit Stream", u"\uF2DE"), ("Map Gamepad", u"\uF298"), ("Exit", u"\uF134")]]
        items[0].setDesc("Current PC: {0}".format(self.moonlight.ip))
        out = self.menu.menu(items, title=Label("Moonlight", "res/moonlight.png", 1), desc=Label("Stream games from your computer with NVIDIA's GameStream"))
        if out == 0:
            return self.loadStream()
        if out == 1:
            return self.loadStartSteam()
        elif out == 2:
            return self.loadSettings()
        elif out == 3:
            return self.loadHostSettings()
        elif out == 4:
            return self.loadForceQuit()
        elif out == 5:
            return self.loadMapping(True)
        else:
            self.thread.stop()
            sys.exit(0)

    def loadSetPC(self):
        items = [Label(i, j) for i, j in [("Search Local Network", u"\uF1C1"), ("Set Host IP", u"\uF2DA"), ("Exit", u"\uF134")]]
        out = self.menu.menu(items, title=Label("Moonlight", "res/moonlight.png", 1), desc=Label("Stream games from your computer with NVIDIA's GameStream"))
        if out == 0:
            return self.loadFindHost()
        if out == 1:
            return self.loadKeyBoard()
        else:
            self.thread.stop()
            sys.exit(0)

    def loadHostSettings(self):
        self.loaded = 6
        items = [Label(i, j) for i, j in [("Set Host IP", u"\uF2DA"), ("Search Local Network", u"\uF1C1"), ("Pair", u"\uF295"), ("Unpair", u"\uF294"), ("Back", u"\uF2EA")]]
        items[0].setDesc("Current PC: {0}".format(self.moonlight.ip))
        out = self.menu.menu(items, title=Label("Computer"))
        if out == 0:
            return self.loadKeyBoard()
        if out == 1:
            return self.loadFindHost()
        elif out == 2:
            return self.loadPair()
        elif out == 3:
            return self.loadUnpair()
        else:
            return self.loadMainMenu()

    def loadFindHost(self):
        self.menu.msg("Searching local network...", desc="Please wait")
        found = Nvstream.search_pcs(first=False)
        items = []
        for pc in found:
            items.append(Label(pc.name.upper(), desc=pc.ip))
        items.append(Label("Back", u"\uF2EA", userData=0))
        out = self.menu.menu(items, title=Label("Computers"), desc=Label("NVIDIA's GameStream host computers found in local network"))
        if out != -1:
            selected = items[out]
            if selected.getUserData() != 0:
                self.moonlight.ip = selected.desc
                self.moonlight.config["host"] = selected.desc
                self.moonlight.saveConfig()
                return self.loadMainMenu()

        if not self.moonlight.isIpDefined():
            return self.loadSetPC()
        return self.loadHostSettings()

    def loadKeyBoard(self):
        self.loaded = 5
        kbd = IPVKeyboard(self.screen)
        if not self.moonlight.isIpDefined():
            found = Nvstream.search_pcs()
            if found:
                kbd.value = found.ip
            else:
                kbd.value = "192.168.0.100"
        else:
            kbd.value = self.moonlight.ip
        kbd.start()
        if kbd.result == 1:
            self.moonlight.ip = kbd.value
            self.moonlight.config["host"] = kbd.value
            self.moonlight.saveConfig()
            return self.loadMainMenu()
        else:
            if not self.moonlight.isIpDefined():
                return self.loadSetPC()
            return self.loadHostSettings()


    def loadMapping(self, loadMenu=False):
        proc = self.moonlight.execute(["map", "-input /dev/input/event0"], False)
        while True:
            line = proc.stdout.readline()
            if line == '':
                break
            self.menu.msg(line.rstrip())
        if loadMenu:
            return self.loadMainMenu()

    def loadPair(self):
        self.loaded = 2
        self.menu.msg("Pairing with PC", desc="Please wait")
        proc = self.moonlight.pair_pexpect()

        time_remaining = 1200
        while True:
            if not proc.isalive():
                break

            if time_remaining <= 0:
                break

            if proc.after:
                self.menu.msg(proc.after, desc="Enter above PIN on PC in the next {} seconds".format(time_remaining // 4))

            if self.get_cancel_event():
                return self.loadHostSettings()

            time.sleep(0.25)

            time_remaining -= 1

        return self.loadMainMenu()

    def loadUnpair(self):
        self.menu.msg("Unpairing with PC", desc="Please wait")
        self.moonlight.unpair()
        return self.loadMainMenu()

    def get_cancel_event(self):
        for event in pygame.event.get(KEYDOWN):
            if event.key == K_ESCAPE:
                return True
        
        for event in pygame.event.get(JOYBUTTONDOWN):
            if event.button == 1 or event.button == 6:
                return True

        return False

    def _loadStream(self):
        self.loaded = 3
        self.menu.msg("Getting game list")
        gList = self.moonlight.listGames()
        if gList == -1:
            return self.loadPair()

        games = [Label("Back", u"\uF2EA", userData=0)] + [Label(i) for i in gList]

        out = self.menu.menu(games, title=Label("Games"),
                             desc=Label("You can force quit stream at any time by holding LB+RB+Back"))
        if out != -1:
            game = games[out]
            if game.getUserData() == 0:
                return self.loadMainMenu()
            else:
                self.menu.setColors(bg=[0, 0, 0])
                self.menu.msg("Stream starting")
                proc = self.moonlight.stream(game.getText().split(". ")[1].rstrip())
                while True:
                    line = proc.stdout.readline()
                    if line == '':
                        break
                    self.menu.msg("Stream starting", desc=line.rstrip())
                self.menu.msg("Please wait", desc="Waiting for process to end")
                proc.wait()
                self.menu.setColors()
                return self.loadMainMenu()
        else:
            return self.loadMainMenu()

    def loadStream(self):
        self.loaded = 3
        gm = GameMenu.GameMenu(self.screen)
        apps = Nvstream.get_apps(self.moonlight.ip)
        if not apps:
            return self.loadPair()

        def get_tiles_by_apps(apps):
            tiles = []
            for app in apps:
                filename = os.path.join(Nvstream.BOXARTDIR, "{0}.png".format(app.id))
                tile = GameMenu.Tile(app.title, filename)
                if not os.path.isfile(filename):
                    t = Nvstream.BoxArtThread(self.moonlight.ip, app.id, gm.draw_tile, tile)
                    t.start()
                tiles.append(tile)
            return tiles

        gm.set_itens(get_tiles_by_apps(apps))
        out = gm.start()

        if out:
            self.menu.setColors(bg=(0, 0, 0))
            self.menu.msg("Stream starting")
            proc = self.moonlight.stream(out)
            while True:
                line = proc.stdout.readline()
                if line == '':
                    break
                self.menu.msg("Stream starting", desc=line.rstrip())
            self.menu.msg("Please wait", desc="Waiting for process to end")
            proc.wait()
            self.menu.setColors()
            return self.loadMainMenu()
        else:
            return self.loadMainMenu()

    def loadStartSteam(self):
        self.menu.setColors(bg=[0, 0, 0])
        self.menu.msg("Stream starting")
        proc = self.moonlight.stream("steam")
        while True:
            line = proc.stdout.readline()
            if line == '':
                break
            self.menu.msg("Stream starting", desc=line.rstrip())
        self.menu.msg("Please wait", desc="Waiting for process to end")
        proc.wait()
        self.menu.setColors()
        return self.loadMainMenu()

    def loadSettings(self):
        self.loaded = 4
        # Create Settings menu items
        items = [Label(i, j) for i, j in
                 [("Resolution", u"\uF364"), ("Framerate", u"\uF31D"), ("Bitrate", u"\uF19E"), ("Surround Sound", u"\uF3B7"), 
                  ("Local Audio", u"\uF3BB"), ("Clear Mapping", u"\uF154"), ("Advanced Settings", u"\uF3B8"), ("Back", u"\uF2EA")]]
        cfg = self.moonlight.getConfig()
        if "width" in cfg:
            if "height" in cfg:
                items[0].setDesc("{0}x{1}".format(cfg["width"], cfg["height"]))
        else:
            items[0].setDesc("Default (1280x720)")
        if "framerate" in cfg:
            if cfg["framerate"]:
                items[1].setDesc("{0}FPS".format(cfg["framerate"]))
            else:
                items[1].setDesc("Auto")
        else:
            items[1].setDesc("Default (auto)")
        if "bitrate" in cfg:
            if cfg["bitrate"]:
                items[2].setDesc("{0}Kbps".format(cfg["bitrate"]))
            else:
                items[2].setDesc("Auto")
        else:
            items[2].setDesc("Default (auto)")
        if "surround" in cfg:
            if cfg["surround"]:
                items[3].setDesc("Enabled")
            else:
                items[3].setDesc("Disabled")
        else:
            items[3].setDesc("Default (disabled)")
        if "localaudio" in cfg:
            if cfg["localaudio"]:
                items[4].setDesc("Enabled")
            else:
                items[4].setDesc("Disabled")
        else:
            items[4].setDesc("Default (disabled)")
        if self.moonlight.hasGamepadMapping():
            items[5].setDesc("Status: defined")
        else:
            items[5].setDesc("Status: already unset")

        # Display settings menu and wait for response
        out = self.menu.menu(items, title=Label("Settings"))
        if out == 0:
            return self.loadSetResolution()
        elif out == 1:
            return self.loadSetFramerate()
        elif out == 2:
            return self.loadSetBitrate()
        elif out == 3:
            return self.loadSetSurround()
        elif out == 4:
            return self.loadSetLocalAudio()
        elif out == 5:
            return self.loadClearMapping()
        elif out == 6:
            return self.loadAdvSettings()
        else:
            return self.loadMainMenu()

    def loadAdvSettings(self):
        self.loaded = 7
        # Create Settings menu items
        items = [Label(i, j) for i, j in
                 [("Packet Size", u"\uF30C"), ("Remote Optimizations", u"\uF310"), ("GFE Graphics Optimization", u"\uF17E"),
                 ("Video Codec", u"\uF19D"), ("Quit App After Session", u"\uF1AE"), ("Unsupported GFE", u"\uF1F0"),
                 ("Clear Settings", u"\uF154"), ("Back", u"\uF2EA")]]
        cfg = self.moonlight.getConfig()
        if "packetsize" in cfg:
            items[0].setDesc("{0}B".format(cfg["packetsize"]))
        else:
            items[0].setDesc("Default (1024B)")
        if "remote" in cfg:
            if cfg["remote"]:
                items[1].setDesc("Enabled")
            else:
                items[1].setDesc("Disabled")
        else:
            items[1].setDesc("Default (disabled)")
        if "sops" in cfg:
            if cfg["sops"]:
                items[2].setDesc("Enabled")
            else:
                items[2].setDesc("Disabled")
        else:
            items[2].setDesc("Default (enabled)")
        if "codec" in cfg:
            items[3].setDesc("{0}".format({"auto": "Auto", "h264": "AVC (H.264)", "h265": "HEVC (H.265)"}.get(cfg["codec"])))
        else:
            items[3].setDesc("Default (auto)")
        if "quitappafter" in cfg:
            if cfg["quitappafter"]:
                items[4].setDesc("Enabled")
            else:
                items[4].setDesc("Disabled")
        else:
            items[4].setDesc("Default (disabled)")
        if "unsupported" in cfg:
            if cfg["unsupported"]:
                items[5].setDesc("Enabled")
            else:
                items[5].setDesc("Disabled")
        else:
            items[5].setDesc("Default (disabled)")

        # Display settings menu and wait for response
        out = self.menu.menu(items, title=Label("Advanced Settings"))
        if out == 0:
            return self.loadSetPacketSize()
        elif out == 1:
            return self.loadSetRemote()
        elif out == 2:
            return self.loadSetGameSettings()
        elif out == 3:
            return self.loadSetCodec()
        elif out == 4:
            return self.loadSetQuitAppAfter()
        elif out == 5:
            return self.loadSetUnsupported()
        elif out == 6:
            return self.loadClearSettings()
        else:
            return self.loadSettings()

    def loadSetResolution(self):
        # First, select aspect ratio
        items = [Label(i) for i in ["16:9", "16:10", "4:3", "Cancel"]]
        out = self.menu.menu(items, title=Label("Aspect Ratio"),
                                desc=Label("Select aspect ratio, most common is 16:9"))
        if out == 0:
            aspect = 1.77777777778
        elif out == 1:
            aspect = 1.6
        elif out == 2:
            aspect = 1.33333333333
        else:
            return self.loadSettings()

        # Select resolution
        items = [Label(i) for i in ["360p", "540p", "720p", "1080p", "1440p", "2160p", "Cancel"]]
        out = self.menu.menu(items, title=Label("Resolution"),
                                desc=Label("Select stream resolution. 720p is recommended for WiFi and 1080p for LAN"))
        if out == 0:
            self.moonlight.config["width"] = int(aspect * 360)
            self.moonlight.config["height"] = 360
        elif out == 1:
            self.moonlight.config["width"] = int(aspect * 540)
            self.moonlight.config["height"] = 540
        elif out == 2:
            self.moonlight.config["width"] = int(aspect * 720)
            self.moonlight.config["height"] = 720
        elif out == 3:
            self.moonlight.config["width"] = int(aspect * 1080)
            self.moonlight.config["height"] = 1080
        elif out == 4:
            self.moonlight.config["width"] = int(aspect * 1440)
            self.moonlight.config["height"] = 1440
        elif out == 5:
            self.moonlight.config["width"] = int(aspect * 2160)
            self.moonlight.config["height"] = 2160
        else:
            return self.loadSettings()

        self.moonlight.saveConfig()
        return self.loadSettings()

    def loadSetFramerate(self):
        items = [Label(i) for i in ["Auto", "30FPS", "60FPS", "Cancel"]]
        out = self.menu.menu(items, title=Label("Framerate"),
                                desc=Label("60FPS is recommended only for high speed LAN"))
        if out == 0:
            self.moonlight.config["framerate"] = 0
        if out == 1:
            self.moonlight.config["framerate"] = 30
        elif out == 2:
            self.moonlight.config["framerate"] = 60
        else:
            return self.loadSettings()

        self.moonlight.saveConfig()
        return self.loadSettings()

    def loadSetCodec(self):
        items = [Label(i) for i in ["Auto", "AVC (H.264)", "HEVC (H.265)", "Cancel"]]
        out = self.menu.menu(items, title=Label("Video Codec"), 
                             desc=Label("Select codec to use. Will still use H.264 if server doesn't support HEVC"))
        if out == 0:
            self.moonlight.config["codec"] = "auto"
        if out == 1:
            self.moonlight.config["codec"] = "h264"
        elif out == 2:
            self.moonlight.config["codec"] = "h265"
        else:
            return self.loadAdvSettings()

        self.moonlight.saveConfig()
        return self.loadAdvSettings()

    def loadSetBitrate(self):
        items = [Label(i) for i in ["Auto", "2Mbps", "5Mbps", "8Mbps", "10Mbps", "15Mbps", "20Mbps", "25Mbps", "Cancel"]]
        out = self.menu.menu(items, title=Label("Bitrate"), 
                             desc=Label("Higer the bitrate, better the quality. Default is based on resolution and fps, lower it if you experiencing FPS drops"))
        if out == 0:
            self.moonlight.config["bitrate"] = 0
        if out == 1:
            self.moonlight.config["bitrate"] = 2000
        elif out == 2:
            self.moonlight.config["bitrate"] = 5000
        elif out == 3:
            self.moonlight.config["bitrate"] = 8000
        elif out == 4:
            self.moonlight.config["bitrate"] = 10000
        elif out == 5:
            self.moonlight.config["bitrate"] = 15000
        elif out == 6:
            self.moonlight.config["bitrate"] = 20000
        elif out == 7:
            self.moonlight.config["bitrate"] = 25000
        else: 
            return self.loadSettings()

        self.moonlight.saveConfig()
        return self.loadSettings()

    def loadSetPacketSize(self):
        items = [Label(i) for i in ["512B", "1024B", "2048B", "4096B", "Cancel"]]
        out = self.menu.menu(items, title=Label("Packet Size"), desc=Label("Specify the maximum Packet Size. Default is 1024B"))
        if out == 0:
            self.moonlight.config["packetsize"] = 512
        elif out == 1:
            self.moonlight.config["packetsize"] = 1024
        elif out == 2:
            self.moonlight.config["packetsize"] = 2048
        elif out == 3:
            self.moonlight.config["packetsize"] = 4096
        else:
            return self.loadAdvSettings()
            
        self.moonlight.saveConfig()
        return self.loadAdvSettings()

    def loadSetLocalAudio(self):
        items = [Label(i) for i in ["Enabled", "Disabled", "Cancel"]]
        out = self.menu.menu(items, title=Label("Local Audio"),
                                desc=Label("If enabled, audio will play on host PC, not here"))
        if out == 0:
            self.moonlight.config["localaudio"] = True
        elif out == 1:
            self.moonlight.config["localaudio"] = False
        else:
            return self.loadSettings()

        self.moonlight.saveConfig()
        return self.loadSettings()

    def loadClearMapping(self):
        items = [Label(i, j) for i, j in [("Cancel", u"\uF136"), ("Clear", u"\uF154")]]
        out = self.menu.menu(items, title=Label("Clear Mapping"),
            desc=Label("This option will clear the current Gamepad Mapping. Are you sure?"))
        if out == 1:
            self.moonlight.clearGamepadMapping()

        return self.loadSettings()

    def loadSetSurround(self):
        items = [Label(i) for i in ["Enabled", "Disabled", "Cancel"]]
        out = self.menu.menu(items, title=Label("Surround Sound"),
                                desc=Label("If enabled, will stream 5.1 surround sound"))
        if out == 0:
            self.moonlight.config["surround"] = True
        elif out == 1:
            self.moonlight.config["surround"] = False
        else:
            return self.loadSettings()

        self.moonlight.saveConfig()
        return self.loadSettings()

    def loadSetRemote(self):
        items = [Label(i) for i in ["Enabled", "Disabled", "Cancel"]]
        out = self.menu.menu(items, title=Label("Remote Optimizations"),
                                desc=Label("If enabled, will use QOS settings to optimize for internet instead of local network"))
        if out == 0:
            self.moonlight.config["remote"] = True
        elif out == 1:
            self.moonlight.config["remote"] = False
        else:
            return self.loadAdvSettings()

        self.moonlight.saveConfig()
        return self.loadAdvSettings()

    def loadClearSettings(self):
        items = [Label(i, j) for i, j in [("Cancel", u"\uF136"), ("Clear", u"\uF154")]]
        out = self.menu.menu(items, title=Label("Clear Settings"), 
                             desc=Label("This option will clear all the current settings. Are you sure?"))
        if out == 1:
            self.moonlight.config = {}
            self.moonlight.saveConfig()
            self.moonlight.loadConfig()
            Nvstream.romeve_boxarts()
            return self.loadMainMenu()

        return self.loadAdvSettings()

    def loadSetGameSettings(self):
        items = [Label(i) for i in ["Enabled", "Disabled", "Cancel"]]
        out = self.menu.menu(items, title=Label("GFE Graphics Optimization"),
                                desc=Label("If enabled, GeForce Experience (GFE) will change graphical game settings for optimal performance and quality"))
        if out == 0:
            self.moonlight.config["sops"] = True
        elif out == 1:
            self.moonlight.config["sops"] = False
        else:
            return self.loadAdvSettings()

        self.moonlight.saveConfig()
        return self.loadAdvSettings()

    def loadSetQuitAppAfter(self):
        items = [Label(i) for i in ["Enabled", "Disabled", "Cancel"]]
        out = self.menu.menu(items, title=Label("Quit App After Session"),
                                desc=Label("If enabled, will send quit app request to remote after quitting session"))
        if out == 0:
            self.moonlight.config["quitappafter"] = True
        elif out == 1:
            self.moonlight.config["quitappafter"] = False
        else:
            return self.loadAdvSettings()

        self.moonlight.saveConfig()
        return self.loadAdvSettings()

    def loadSetUnsupported(self):
        items = [Label(i) for i in ["Enabled", "Disabled", "Cancel"]]
        out = self.menu.menu(items, title=Label("Unsupported GFE"),
                                desc=Label("If enabled, will try streaming if GeForce Experience (GFE) version or options are unsupported"))
        if out == 0:
            self.moonlight.config["unsupported"] = True
        elif out == 1:
            self.moonlight.config["unsupported"] = False
        else:
            return self.loadAdvSettings()

        self.moonlight.saveConfig()
        return self.loadAdvSettings()

    def loadForceQuit(self):
        self.menu.msg("Quittting all streams", desc="Please wait")
        self.moonlight.quit()
        return self.loadMainMenu()

if __name__ == "__main__":
    Startup = Startup()
    signal.signal(signal.SIGINT, signalHandler)
    Startup.main()
