# -*- coding: utf-8 -*-
"""
Display the battery level.

Configuration parameters:
    - ac_info : path to adapter info (default: '/sys/class/power_supply/ADP0')
    - battery_info : path to battery info (default: '/sys/class/power_supply/BAT0')
    - cache_timeout : seconds between battery checks (default: 5)
    - capacity_degraded : percent below which colored as degraded (default: 50)
    - capacity_bad : percent below which colored as bad (default: 15)
    - format : display format (default: '{capacity}% {icon}')
"""

from __future__ import division  # python2 compatibility
from time import time

import codecs
import math

BLOCKS = [' ','_','▁','▂','▃','▄','▅','▆','▇','█']

class Py3status:
    # available configuration parameters

    # path to ac info
    ac_info = '/sys/class/power_supply/ADP0'
    # path to battery info
    battery_info = '/sys/class/power_supply/BAT0'
    # check for updates every 5 seconds
    cache_timeout = 5
    # display as degraded below 50% capacity
    capacity_degraded = 50
    # display as bad below 15% capacity
    capacity_bad = 15
    # format as 66% ⌁
    format = '{capacity}% {icon}'

    def _read_info(self, path, name):
        f = codecs.open(path + '/' + name, encoding='utf-8')
        value = f.readline()
        f.close()
        return value

    def j3_battery(self, i3s_output_list, i3s_config):
        capacity = int(self._read_info(self.battery_info, 'capacity'))
        ac_online = int(self._read_info(self.ac_info, 'online'))

        icon = '⌁' # ⚡
        if ac_online < 1:
            icon = BLOCKS[int(math.ceil(capacity/100*len(BLOCKS))) - 1]
        text = self.py3.safe_format(self.format, {
            'capacity': capacity,
            'icon': icon,
        })

        color = i3s_config['color_good']
        if capacity < self.capacity_degraded:
            color = i3s_config['color_degraded']
        elif capacity < self.capacity_bad:
            color = i3s_config['color_bad']

        return {
            'full_text': text,
            'color': color,
            'cached_until': time() + self.cache_timeout,
        }

if __name__ == "__main__":
    from time import sleep
    x = Py3status()
    config = {
        'color_good': '#00FF00',
        'color_degraded': '#FFFF00',
        'color_bad': '#FF0000',
    }
    while True:
        print(x.j3_battery([], config))
        sleep(1)
