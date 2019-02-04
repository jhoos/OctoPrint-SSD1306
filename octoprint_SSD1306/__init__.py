# coding=utf-8
from __future__ import absolute_import
from octoprint.printer.estimation import PrintTimeEstimator
import octoprint.plugin
import octoprint.events
import time
from datetime import timedelta
from .ssd1306 import SSD1306


class SDD1306Plugin(octoprint.plugin.StartupPlugin,
                    octoprint.plugin.ShutdownPlugin,
                    octoprint.plugin.EventHandlerPlugin,
                    octoprint.plugin.ProgressPlugin):

    def __init__(self):
        self.display = SSD1306()
        self.start = time.time()

    def on_startup(self, *args, **kwargs):
        self._logger.info('Initializing SDD1306 display')
        self.display.clear()
        self.display.write(3, 'Offline')
        self.display.commit()
        self._logger.info("SDD1306 display initialized!")

    def on_print_progress(self, storage, path, progress, *args, **kwargs):
        self._logger.info('on_print_progress: %s, %s, %s', storage, path, progress)
        self.display.clear(0, 3)
        self.display.write(0, 'Completed: {}%'.format(progress))

        if progress == 0:
            self.start = time.time()
        elif progress == 100:
            self.display.clear(0, 3)
        else:
            now = time.time()
            elapsed = now - self.start
            self.display.write(1, 'Elapsed:   {}'.format(timedelta(seconds=int(elapsed))))
            if progress > 9 or elapsed > 600:
                remaining = elapsed * (100.0 / progress - 1)
                remaining_str = str(timedelta(seconds=int(remaining)))
            else:
	        remaining_str = '-:--:--'
            self.display.write(2, 'Remaining: {}'.format(remaining_str))

        self.display.commit()

    def on_event(self, event, payload, *args, **kwargs):
        self._logger.info('on_event: %s, %s', event, payload)
        if event == 'Error':
            self.display.clear(3, 4)
            self.display.write(3, 'Error! {}'.format(payload['error']))
        elif event == 'PrinterStateChanged':
            self.display.clear(3, 4)
            self.display.write(3, payload['state_string'].replace('Operational', 'Ready'))
        self.display.commit()

    def on_shutdown(self, *args, **kwargs):
        self.display.clear()
        self.display.write(3, 'Bye')
        self.display.commit()

    def get_update_information(self):
        return dict(
            SSD1306Plugin=dict(
                displayName="SSD1306 Display",
                displayVersion=self._plugin_version,
                type="github_release",
                current=self._plugin_version,
                user="jhoos",
                repo="OctoPrint-SDD1306",
                pip="https://github.com/jhoos/octoprint-SSD1306/archive/{target}.zip"
            )
        )

__plugin_name__ = "SSD1306 Display"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = SDD1306Plugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

