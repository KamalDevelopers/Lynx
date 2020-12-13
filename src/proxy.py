from urllib.parse import urlparse
from PyQt5.QtNetwork import *

def setProxy(string_proxy):
    proxy = QNetworkProxy()
    urlinfo = urlparse(string_proxy)
    proxy.setType(QNetworkProxy.HttpProxy)
    proxy.setHostName(urlinfo.hostname)
    proxy.setPort(urlinfo.port)
    QNetworkProxy.setApplicationProxy(proxy)
