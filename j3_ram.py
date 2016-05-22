# -*- coding: utf-8 -*-
"""
Display the RAM (and swap) usage.

Configuration parameters:
    - cache_timeout : seconds between rate checks (default: 5)
    - colorize : true to colorize output (default: True)
        - set color thresholds via rate_good/degraded/bad
    - ram_format : display format (default: 'RAM {:.1f} GB')
    - swap_format : display format (default: 'swap {:.1f} GB')
    - rate_good : threshold above which display is colorized as good (default: 0)
    - rate_degraded : threshold above which display is colorized as degraded (default: 50)
    - rate_bad : threshold above which display is colorized as bad (default: 90)
"""

from __future__ import division  # python2 compatibility
from time import time

import math
import re
import subprocess

class Py3status:
    # available configuration parameters
    cache_timeout = 5
    colorize = True
    ram_format = 'RAM {:.1f} GB'
    swap_format = 'swap {:.1f} GB'
    rate_good = 0
    rate_degraded = 50
    rate_bad = 90

    def _get_stats(self):
        stats = {}
        result = subprocess.check_output(['free', '-m'])
        result = result.decode('utf-8').split()

        mem_index = result.index('Mem:')
        stats['ram'] = { 'total': int(result[mem_index + 1]) }

        # use new 'available' column (free 3.3.10+)
        if result.index('available') != -1:
            available = int(result[mem_index + 6])
            stats['ram']['used'] = stats['ram']['total'] - available
        # use old '-/+ buffers/cache' row
        else:
            cache_index = result.index('buffers/cache:')
            stats['ram']['used'] = int(result[cache_index + 1])

        swap_index = result.index('Swap:')
        stats['swap'] = {
            'total': int(result[swap_index + 1]),
            'used': int(result[swap_index + 2]),
        }

        return stats

    def _get_status(self, i3s_config, mode):
        stats = self._get_stats()

        used = stats[mode]['used'] / 1024
        rate = 100 * stats[mode]['used'] / (stats[mode]['total'] or 1)

        color = None
        if self.colorize:
            if rate > self.rate_bad:
                color = i3s_config['color_bad']
            elif rate > self.rate_degraded:
                color = i3s_config['color_degraded']
            elif rate > self.rate_good:
                color = i3s_config['color_good']

        text = ''
        if mode == 'ram':
            text = self.ram_format.format(used)
        elif mode == 'swap':
            text = self.swap_format.format(used)

        return {
            'cached_until': time() + self.cache_timeout,
            'color': color,
            'full_text': text,
        }

    def j3_ram(self, i3s_output_list, i3s_config):
        if not self.ram_format:
            return {}
        return self._get_status(i3s_config, 'ram')

    def j3_swap(self, i3s_output_list, i3s_config):
        if not self.swap_format:
            return {}
        return self._get_status(i3s_config, 'swap')

if __name__ == "__main__":
    from time import sleep
    x = Py3status()
    config = {
        'color_good': '#00FF00',
        'color_degraded': '#FFFF00',
        'color_bad': '#FF0000',
    }
    while True:
        print(x.j3_ram([], config))
        print(x.j3_swap([], config))
        sleep(1)
