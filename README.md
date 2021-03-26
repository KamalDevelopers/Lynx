<br />
<p align="center">
    <img src="https://i.postimg.cc/9Q4tkX70/lynx-logo.png" alt="Logo" width="80" height="80">

  <h3 align="center">Lynx Browser</h3>

  <p align="center">
    A futuristic, light and fast browser. Written using Qt and Webkit.
    <br />
    <a href="https://github.com/KamalDevelopers/Lynx/issues">Requests</a>
    ·
    <a href="https://github.com/KamalDevelopers/Phoenix-Search">Phoenix Search</a>
    ·
    <a href="https://github.com/KamalDevelopers/Lynx/issues">Report Bug</a>
  </p>
</p>

## About

Lynx is a new browser focused on simplicity, customizability, speed, and minimal resource usage. <br>
It is written in PyQt5 and uses the module PyQtWebEngine.

## Features

Currently, the Lynx browser comes with many features, such as custom extensions and themes support. <br>
There is also a Lynx Stealth mode. Which aims to bring the same functionality as incognito mode would bring on most other modern browsers. The only difference being that Lynx Stealth mode is more privacy-focused. With support for NoScript and HttpsOnly. The Lynx browser is fully open source and runs on Linux, Windows, and Mac.

## Configuration

Lynx offers customizability and configuration through the `config.ini` file inside the lynx-profile folder.
Here you may change everything from privacy preferences to themes and webkit settings.
Lynx also comes bundled with multiple extensions, to disable/enable these check out their json files.

## Installation

First install PyOpenGL manually for your platform, then you can install Lynx.
```
git clone https://github.com/KamalDevelopers/Lynx.git
cd Lynx
pip3 install -r requirements.txt
python3 run.py
```

To build Lynx into a package you can run:
`python3 build.py`

## Screenshot
***
<p align="center">
  <img src="https://i.postimg.cc/8zB88ZfG/Screenshot-2021-03-16-09-50-54.png">
</p>


## License

Distributed under the Unlicense License. See `LICENSE` for more information.

