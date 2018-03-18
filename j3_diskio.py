# -*- coding: utf-8 -*-
"""
Display the current disk transfer rate.

Configuration parameters:
    - cache_timeout : seconds between rate checks (default: 1)
    - colorize : true to colorize output (default: True)
        - set color thresholds via rate_good/degraded/bad
    - indicator_read : indicator for read rate (default: ⇑)
    - indicator_write : indicator for write rate (default: ⇓)
    - indicator_combined : indicator for combined rate (default: ⇕)
    - format : display format (default: '{max} {device}{direction}')
        - try '{total} {device}' to show combined read and write totals
        - try '{read}⇑ {write}⇓ {device}' to show separate read and write totals
        - format tokens :
            - '{direction}' : icon indicating most-active direction (read or write)
            - '{device}' : device label (ie 'sda')
            - '{max}' : rate of most-active direction
            - '{total}' : combined rate of both read and write totals
            - '{read}' : read (trasmitted) rate
            - '{write}' : write (received) rate
    - format_all_idle : display format when all devices are idle (default: 'idle net')
    - format_idle : display format for an individual idle device (default: '')
        - try 'idle {device}' to display for each device something when idle
    - devices: list of devices to check (default: 'eth0 wlan0')
    - device_labels: list of labels to use to display device names (default: '')
        - try 'a b' to display 'a' instead of 'sda' and 'b' instead of 'sdb'
    - mode : display mode (default: 'max')
        - 'max' to display just the most-active device
        - 'all' to display all devices
    - separation : separator to use when displaying multiple devices (default: '|')
    - rate_format : formatting of rate number (default: '{value:4.0f}{units}'
        - used by '{max}', '{total}', '{read}', and {'write'} totals in format parameter
        - uses units defined by rate_b/kb/mb/gb/tb parameters
    - rate_b : indicator for B/s units (default: ' B/s')
    - rate_kb : indicator for KB/s units (default: 'KB/s')
    - rate_mb : indicator for MB/s units (default: 'MB/s')
    - rate_gb : indicator for GB/s units (default: 'GB/s')
    - rate_tb : indicator for TB/s units (default: 'TB/s')
    - rate_good : threshold above which display is colorized as good (default: 1048576)
    - rate_degraded : threshold above which display is colorized as degraded (default: 10485760)
    - rate_bad : threshold above which display is colorized as bad (default: 104857600)
"""

from __future__ import division  # python2 compatibility
from time import time

class Py3status:
    # available configuration parameters

    cache_timeout = 1
    colorize = True
    indicator_read = '⇑'   # ⬆ ⇑ ⇧ ▲ △
    indicator_write = '⇓' # ⬇ ⇓ ⇩ ▼ ▽
    indicator_combined = '⇕' # ⬍ ⇕ ↕
    format = '{max} {device}{direction}'
    #format = '{total} {device}'
    #format = '{read}⇑ {write}⇓ {device}'
    format_all_idle = 'idle disk'
    format_idle = ''
    #format_idle = 'idle {device}'
    devices = 'sda'
    device_labels = ''
    #device_labels = 'a b'
    mode = 'max'
    separation = '|'
    rate_format = '{value:4.0f}{units}'
    #rate_format = '{value:.0f}{units}'
    rate_b  = ' B/s'
    rate_kb = 'KB/s'
    rate_mb = 'MB/s'
    rate_gb = 'GB/s'
    rate_tb = 'TB/s'
    rate_good = 2 << 19 # 1 MB/s
    rate_degraded = (2 << 19) * 10 # 10 MB/s
    rate_bad = (2 << 19) * 100 # 100 MB/s

    # internal state
    last_time = None
    last_stats = None

    def _get_stats(self, devices):
        stats = {}
        for device in devices:
            sd = stats[device] = { 'read': 0, 'write': 0 }
            try:
                fname = '/sys/block/{}/stat'.format(device)
                with open(fname) as f:
                    line = f.readline()
                    cols = line.split()
                    sd['read'] = int(cols[2]) * 512
                    sd['write'] = int(cols[6]) * 512
            except IOError:
                pass # ignore unavailable device
            sd['total'] = sd['read'] + sd['write']
        return stats

    def _format_bytes(self, b):
        fmt = self.rate_format

        x = b >> 10
        if not x: return fmt.format(value=b, units=self.rate_b)
        x = x >> 10
        if not x: return fmt.format(value=b/(2<<10-1), units=self.rate_kb)
        x = x >> 10
        if not x: return fmt.format(value=b/(2<<20-1), units=self.rate_mb)
        x = x >> 10
        if not x: return fmt.format(value=b/(2<<30-1), units=self.rate_gb)

        return fmt.format(value=b/(2<<40-1), units=self.rate_tb)

    def j3_diskio(self, i3s_output_list, i3s_config):
        devices = self.devices.split()
        device_labels = dict(zip(devices, self.device_labels.split()))

        # calculate the difference in seconds between last check and now
        now = time()
        last_time = self.last_time or now
        self.last_time = now
        diff_time = now - last_time
        if diff_time < 1: diff_time = 1

        stats = self._get_stats(devices)
        last_stats = self.last_stats or stats
        self.last_stats = stats
        overall_max_total = 0

        # calculate bytes read/write/total since last check
        diffs = {}
        for device in devices:
            di = diffs[device] = {}
            si = stats[device]
            li = last_stats[device]
            for way in ['read', 'write', 'total']:
                di[way] = int((si[way] - li[way]) / diff_time)

        # show only most-active device in 'max' mode
        if self.mode == 'max':
            device = max(diffs, key=lambda i: diffs[i]['total'])
            diffs = { device: diffs[device] }

        # build list of text for each device
        text = []
        for device in diffs:
            di = diffs[device]
            # format stats for active device
            if di['total']:
                # determine most-active overall total number of bytes
                if overall_max_total < di['total']:
                    overall_max_total = di['total']

                # determine most-active direction for 'max' formatting
                max_direction = 'write' if di['write'] > di['read'] else 'read'
                max_value = di[max_direction]
                max_icon = self.indicator_combined
                if max_direction == 'read': max_icon = self.indicator_read
                if max_direction == 'write': max_icon = self.indicator_write

                text.append(self.py3.safe_format(self.format, {
                    'device': device_labels.get(device) or device,
                    'max': self._format_bytes(max_value),
                    'direction': max_icon,
                    'read': self._format_bytes(di['read']),
                    'write': self._format_bytes(di['write']),
                    'total': self._format_bytes(di['total']),
                )))
            # show idle text for inactive device
            elif self.format_idle:
                text.append(self.py3.safe_format(self.format_idle, {
                    'device': device_labels.get(device) or device,
                )))

        # colorize output based on rate of most-active device
        color = None
        if self.colorize:
            if overall_max_total > self.rate_bad:
                color = i3s_config['color_bad']
            elif overall_max_total > self.rate_degraded:
                color = i3s_config['color_degraded']
            elif overall_max_total > self.rate_good:
                color = i3s_config['color_good']

        return {
            'cached_until': now + self.cache_timeout,
            'color': color,
            # show idle text if no active devices
            'full_text': self.py3.composite_join(self.separation, text) or self.format_all_idle,
        }

if __name__ == "__main__":
    """
    Test this module by calling it directly.
    """
    from time import sleep
    x = Py3status()
    config = {
        'color_good': '#00FF00',
        'color_degraded': '#FFFF00',
        'color_bad': '#FF0000',
    }
    while True:
        print(x.j3_diskio([], config)['full_text'])
        #print(x.j3_diskio([], config))
        sleep(1)
