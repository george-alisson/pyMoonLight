import subprocess, json, os

import pexpect as pexpect


class Moonlight:
    def __init__(self, ip = None):
        # Configuration
        self.config = {}
        self.app = None
        self.ip = ip

        # Other
        self.executable = "moonlight"
        self.workingdir = "bin"
        self.configdir = "~/.config/pymoonlight"
        self.proc = None

    def loadConfig(self):
        try:
            if not os.path.exists(self.configdir):
                os.makedirs(self.configdir)
            cfg = json.loads(open(self.getConfigPath(), "r").read())
            self.config.update(cfg)
            self.ip = cfg.get("host")
        except IOError:
            print("Failed to read '{}'".format(self.getConfigPath()))

    def getConfig(self):
        return self.config

    def saveConfig(self):
        with open(self.getConfigPath(), "w") as outfile:
            json.dump(self.config, outfile)

    def execute(self, args, includeip=True):
        ar = [self.executable]
        ar += args
        if includeip and self.isIpDefined():
            ar += [self.ip]

        if not os.path.exists(self.workingdir):
            os.makedirs(self.workingdir)

        self.proc = subprocess.Popen(ar, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.workingdir)
        return self.proc

    def pair_pexpect(self):

        if not os.path.exists(self.workingdir):
            os.makedirs(self.workingdir)

        child = pexpect.spawn('{} {}'.format(self.executable, 'pair'), cwd=self.workingdir)
        child.expect('[1-9]{4}')
        return child

    def listGames(self):
        process = self.execute(["list"])
        games = []
        while True:
            line = process.stdout.readline()
            if line == '':
                break
            if "You must pair with the PC first" in line:
                return -1
            else:
                games.append(line.rstrip())
        return games

    def quit(self):
        if self.proc != None:
            self.proc.kill()
        process = self.execute(["quit"])
        process.wait()

    def unpair(self):
        if self.proc != None:
            self.proc.kill()
        process = self.execute(["unpair"])
        process.wait()

    def stream(self, app=None):
        args = ["stream"]
        if self.hasGamepadMapping():
            args.append("-mapping")
            args.append(self.getMappingPath())
        if "width" in self.config:
            args.append("-width")
            args.append(str(self.config["width"]))
        if "height" in self.config:
            args.append("-height")
            args.append(str(self.config["height"]))
        if "framerate" in self.config and self.config["framerate"]:
            args.append("-fps")
            args.append(str(self.config["framerate"]))
        if "bitrate" in self.config and self.config["bitrate"]:
            args.append("-bitrate")
            args.append(str(self.config["bitrate"]))
        if "audio" in self.config:
            args.append("-audio")
            args.append(str(self.config["audio"]))
        if "input" in self.config:
            args.append("-input")
            args.append(str(self.config["input"]))
        if "localaudio" in self.config:
            if self.config["localaudio"]:
                args.append("-localaudio")
        if "surround" in self.config:
            if self.config["surround"]:
                args.append("-surround")
        if "remote" in self.config:
            if self.config["remote"]:
                args.append("-remote")
        if "sops" in self.config:
            if not self.config["sops"]:
                args.append("-nosops")
        if "quitappafter" in self.config:
            if self.config["quitappafter"]:
                args.append("-quitappafter")
        if "codec" in self.config and self.config["codec"] != "auto":
            args.append("-codec")
            args.append(str(self.config["codec"]))
        if "unsupported" in self.config:
            if self.config["unsupported"]:
                args.append("-unsupported")
        if app:
            args.append("-app")
            args.append('"' + app + '"')

        print("Exec: " + str(args))
        return self.execute(args)

    def isIpDefined(self):
        return self.ip is not None

    def getConfigPath(self):
        return os.path.join(self.configdir, "config.txt")

    def getMappingPath(self):
        return os.path.join(self.configdir, "mapping.txt")

    def hasGamepadMapping(self):
        return os.path.isfile(self.getMappingPath())

    def clearGamepadMapping(self):
        if self.hasGamepadMapping():
            os.remove(self.getMappingPath())

    def setAction(self, action):
        self.action = action

    def setApp(self, app):
        self.app = app
