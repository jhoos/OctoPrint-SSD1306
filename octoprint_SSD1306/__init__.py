# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import time

from octoprint.events import Events
from octoprint.printer import PrinterCallback
from datetime import timedelta
from .ssd1306 import SSD1306


class SDD1306Plugin(octoprint.plugin.StartupPlugin,
                    octoprint.plugin.ShutdownPlugin,
                    octoprint.plugin.EventHandlerPlugin,
                    PrinterCallback):

    def on_startup(self, *args, **kwargs):
        self._logger.info('Initializing SDD1306 display')
        self.display = SSD1306()
        # Write initial status, assuming printer isn't connected at startup
        self.display.write(0, 'Offline')
        self.display.commit()
        self._logger.info("SDD1306 display initialized!")

    def on_after_startup(self, *args, **kwargs):
        self._printer.register_callback(self)

    def _format_seconds(self, seconds):
        h = int(seconds / 3600)
        m = int((seconds - h * 3600) / 60)
        return '{}h {}m'.format(h, m) if h > 0 else '{}m'.format(m)

    def on_printer_send_current_data(self, data, **kwargs):
        """
        Display print progress on lines 1-3
        """
        self._logger.debug('on_printer_send_current_data: %s', data)

        completion = data['progress']['completion']

        if completion is None:
            # Job is complete or no job is started.
            self.display.clear(1, 6)
        else:
            self.display.write(1, '{}% Completed'.format(int(completion)))
            # Show elapsed time and remaining time
            elapsed = data['progress']['printTime']
            self.display.write(2, '{} Elapsed'.format(self._format_seconds(elapsed)))

            remaining = data['progress']['printTimeLeft']
            if remaining is not None:
                self.display.write(3, '{} Left'.format(self._format_seconds(remaining)))
            else:
                self.display.clear(3, 4)

        self.display.commit()

    def _format_temp(self, tool, temp):
        tool_txt = tool[0].upper()
        if tool[-1].isdigit():
            tool_txt += tool[-1]
        target_dir = '_'
        if temp['target'] > 0:
            if abs(temp['target'] - temp['actual']) < 5:
                target_dir = '-'
            else:
                target_dir = '/' if temp['target'] > temp['actual'] else '\\'
        return '{}:{}{}'.format(tool_txt, int(temp['actual']), target_dir)

    def on_printer_add_temperature(self, data):
        """
        Display printer temperatures
        """
        self._logger.debug('on_printer_add_temperature: %s', data)

        msg0 = '{} {}'.format(
            self._format_temp('bed', data['bed']),
            self._format_temp('tool0', data['tool0'])
        )

        if 'tool1' in data:
            msg1 = self._format_temp('tool1', data['tool1'])
            if 'tool2' in data:
                msg1 += ' ' + self._format_temp('tool2', data['tool2'])
            self.display.write(6, msg0)
            self.display.write(7, msg1)
        else:
            self.display.clear(6, 7)
            self.display.write(7, msg0)

        self.display.commit()

    def on_event(self, event, payload, *args, **kwargs):
        """
        Display printer status events on the first line
        """
        self._logger.debug('on_event: %s, %s', event, payload)

        if event == Events.ERROR:
            self.display.write(0, 'Error! {}'.format(payload['error']))
            self.display.commit()
        elif event == Events.PRINTER_STATE_CHANGED:
            self.display.write(0, payload['state_string'])
            if payload['state_id'] == 'OFFLINE':
                # If the printer is offline, clear printer and job messages
                self.display.clear(1, 8)
            self.display.commit()

    def on_shutdown(self, *args, **kwargs):
        self._printer.unregister_callback(self)
        self.display().stop()

    def protocol_gcode_queuing_hook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if gcode:
            if gcode == 'M117':
                self._logger.info('Intercepted M117 gcode: %s', cmd)
                words = cmd.split(' ')[1:]
                line1 = words[0]
                line2 = ''
                for i in range(1, len(words)):
                    word = words[i]
                    if len(line1) + 1 + len(word) <= 16:
                        line1 += ' ' + word
                    else:
                        line2 = ' '.join(words[i:])
                        break
                self._logger.info('Split message: "%s" "%s"', line1, line2)
                self.display.write(4, line1)
                self.display.write(5, line2)
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
                pip="https://github.com/jhoos/OctoPrint-SSD1306/archive/{target}.zip"
            )
        )

__plugin_name__ = "SSD1306 Display"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = SDD1306Plugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.protocol_gcode_queuing_hook,
    }

