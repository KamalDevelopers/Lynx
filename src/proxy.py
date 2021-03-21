from urllib.parse import urlparse
from PyQt5.QtNetwork import QNetworkProxy


def setProxy(string_proxy):
    proxy = QNetworkProxy()
    urlinfo = urlparse(string_proxy)

    if urlinfo.scheme == "socks5":
        proxy.setType(QNetworkProxy.Socks5Proxy)

    elif urlinfo.scheme == "http":
        proxy.setType(QNetworkProxy.HttpProxy)

    proxy.setHostName(urlinfo.hostname)
    proxy.setPort(urlinfo.port)

    QNetworkProxy.setApplicationProxy(proxy)
