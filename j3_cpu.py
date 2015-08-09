# -*- coding: utf-8 -*-
"""
Display the CPU usage.

Configuration parameters:
    - cache_timeout : seconds between rate checks (default: 1)
    - colorize : true to colorize output (default: True)
        - set color thresholds via rate_good/degraded/bad
    - format : display format (default: 'CPU {icon}')
    - mode : display mode (default: 'max')
        - 'max' to display just the CPU with max usage
        - 'avg' to display the average usage of all CPUs
        - 'all' to display each individual CPU
    - rate_good : threshold above which display is colorized as good (default: 10)
    - rate_degraded : threshold above which display is colorized as degraded (default: 40)
    - rate_bad : threshold above which display is colorized as bad (default: 90)
"""

from __future__ import division  # python2 compatibility
from time import time

import math
import re

BLOCKS = [' ','_','▁','▂','▃','▄','▅','▆','▇','█']

class Py3status:
    # available configuration parameters
    cache_timeout = 1
    colorize = True
    format = 'CPU {icon}'
    mode = 'max'
    rate_good = 10
    rate_degraded = 40
    rate_bad = 90

    # internal state
    last_time = None
    last_stats = None

    def _get_stats(self):
        stats = []
        with open('/proc/stat') as f:
            for line in f.readlines():
                if re.search(r'^cpu\d', line):
                    cols = line.split()
                    stats.append({
                        'total': sum(map(int, cols[1:])),
                        'idle': int(cols[4]),
                    })
        return stats

    def j3_cpu(self, i3s_output_list, i3s_config):
        # calculate the difference in seconds between last check and now
        now = time()
        last_time = self.last_time or now
        self.last_time = now
        diff_time = now - last_time
        if diff_time < 1: diff_time = 1

        stats = self._get_stats()
        last_stats = self.last_stats or stats
        self.last_stats = stats

        all_percent = []
        max_percent = 0
        sum_total = 0
        sum_idle = 0

        # calculate cpu used since last check
        for index, cpu in enumerate(stats):
            last_cpu = last_stats[index]
            total = cpu['total'] - last_cpu['total']
            idle = cpu['idle'] - last_cpu['idle']
            sum_total += total
            sum_idle += idle

            percent = 100 - 100 * idle / (total or 1)
            all_percent.append(percent)
            if max_percent < percent:
                max_percent = percent

        if self.mode == 'max':
            color_rate = max_percent
            icon = BLOCKS[int(math.ceil(max_percent/100*len(BLOCKS))) - 1]
        elif self.mode == 'avg':
            avg_percent = 100 - 100 * sum_idle / (sum_total or 1)
            color_rate = avg_percent
            icon = BLOCKS[int(math.ceil(avg_percent/100*len(BLOCKS))) - 1]
        else:
            avg_percent = 100 - 100 * sum_idle / (sum_total or 1)
            color_rate = avg_percent
            icon = ''
            for percent in all_percent:
                icon += BLOCKS[int(math.ceil(percent/100*len(BLOCKS))) - 1]

        color = None
        if self.colorize:
            if color_rate > self.rate_bad:
                color = i3s_config['color_bad']
            elif color_rate > self.rate_degraded:
                color = i3s_config['color_degraded']
            elif color_rate > self.rate_good:
                color = i3s_config['color_good']

        return {
            'cached_until': now + self.cache_timeout,
            'color': color,
            'full_text': self.format.format(icon=icon),
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
        #print(x.j3_cpu([], config)['full_text'])
        print(x.j3_cpu([], config))
        sleep(1)
