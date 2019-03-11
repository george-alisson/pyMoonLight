import socket
import time
import os
import shutil
from zeroconf import ServiceBrowser, Zeroconf

import uuid
import requests
requests.packages.urllib3.disable_warnings()
from lxml import etree
import threading

class Computer:
    
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, name + ip)

    def __repr__(self):
        return "Computer(name='{}', ip='{}')".format(self.name, self.ip)

class App:

    def __init__(self, id, title):
        self.id = id
        self.title = title

    def __repr__(self):
        return "App(id={}, title='{}')".format(self.id, self.title)

    def __gt__(self, other):
        return self.title > other.title

    def __lt__(self, other):
        return self.title < other.title

    def __le__(self, other):
        return self.title <= other.title

    def __ge__(self, other):
        return self.title >= other.title

    def __eq__(self, other):
        return self.title == other.title

    def __ne__(self, other):
        return self.title != other.title

class NvstreamListener:

    def __init__(self):
        self.pcs = []

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        pc = Computer(info.server.replace(".local.", ""), socket.inet_ntoa(info.address))
        print("Found", pc.name, pc.ip)
        self.pcs.append(pc)

class BoxArtThread(threading.Thread):

    def __init__(self, server, appid, callback, *callback_args):
        threading.Thread.__init__(self)
        self.callback = callback
        self.callback_args = callback_args
        self.server = server
        self.appid = appid

    def run(self):
        get_boxart(self.server, self.appid)
        self.callback(*self.callback_args)

def search_pcs(timeout=3, first=True):
    listener = NvstreamListener()
    print("Searching Nvstream PCs...")
    zeroconf = Zeroconf()
    try:
        browser = ServiceBrowser(zeroconf, "_nvstream._tcp.local.", listener)
        timeout *= 10 
        while timeout:
            time.sleep(0.1)
            timeout -= 1
            if first and len(listener.pcs) > 0:
                return listener.pcs[0]
    finally:
        zeroconf.close()
    return listener.pcs

KEYDIR = os.path.expanduser("~/.cache/pymoonlight")

UNIQUEID = None
def get_uniqueid():
    global UNIQUEID
    if not UNIQUEID:
        with open(os.path.join(KEYDIR, "uniqueid.dat"), "r") as f:
            UNIQUEID = f.read()
    return UNIQUEID

def get_apps(server, sort=True):
    try:
        apps = []
        url = "https://{0}:47984/applist?uniqueid={1}&uuid={2}".format(server, get_uniqueid(), uuid.uuid1().hex)
        r = requests.get(url, cert=(os.path.join(KEYDIR, "client.pem"), os.path.join(KEYDIR, "key.pem")), verify=False)
        root = etree.fromstring(r.content.decode("utf-8").encode("utf-16"))
        for eapp in root.xpath("App"):
            id = int(eapp.xpath("ID")[0].text)
            title = eapp.xpath("AppTitle")[0].text
            apps.append(App(id, title))
        if sort:
            apps.sort()
        return apps
    except:
        return list()

def get_boxart(server, appid):
    if not os.path.exists("boxart"):
        os.makedirs("boxart")
    filename = "boxart\{0}.png".format(appid)
    url = 'https://{0}:47984/appasset?appid={1}&AssetType=2&AssetIdx=0&uniqueid={2}&uuid={3}'.format(server, appid, get_uniqueid(), uuid.uuid1().hex)
    r = requests.get(url, cert=(os.path.join(KEYDIR, "client.pem"), os.path.join(KEYDIR, "key.pem")), verify=False)
    with open(filename, "wb") as img:
        img.write(r.content)
    return filename

def romeve_boxarts():
    shutil.rmtree("boxart", True)

