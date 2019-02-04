# OctoPrint-SSD1306

This plugin utilizes a 128x64 SSD1306-based display to display printer and job status for OctoPrint.  It provides a convenient way to view job status directly on the Raspberry Pi without needing to open a web page, for printers that either don't have a display or won't respond to commands to update their display.

It is loosely based on the OctoPrint-Lcd1602 plugin at /home/pi/oprint/lib/python2.7/site-packages/SSD1306_Display-0.1.0-py2.7.egg/octoprint_SSD1306/font, but probably doesn't bear much resemblance to it anymore.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/jhoos/OctoPrint-SDD1306/archive/master.zip

## Manual Installation 

Clone the repo from GitHub onto your OctoPrint device, then do:

    cd OctoPrint-SDD1306
    . ~/oprint/bin/activate
    python setup.py install


