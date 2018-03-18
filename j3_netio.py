# -*- coding: utf-8 -*-
"""
Display the current network transfer rate.

Configuration parameters:
    - cache_timeout : seconds between rate checks (default: 1)
    - colorize : true to colorize output (default: True)
        - set color thresholds via rate_good/degraded/bad
    - direction_up : indicator for upload rate (default: ⇑)
    - direction_down : indicator for download rate (default: ⇓)
    - direction_both : indicator for combined rate (default: ⇕)
    - format : display format (default: '{max} {interface}{direction}')
        - try '{total} {interface}' to show combined up and down totals
        - try '{up}⇑ {down}⇓ {interface}' to show separate up and down totals
        - format tokens :
            - '{direction}' : icon indicating most-active direction (up or down)
            - '{interface}' : interface label (ie 'eth0')
            - '{max}' : rate of most-active direction
            - '{total}' : combined rate of both up and down totals
            - '{up}' : up (trasmitted) rate
            - '{down}' : down (received) rate
    - format_all_idle : display format when all interfaces are idle (default: 'idle net')
    - format_idle : display format for an individual idle interface (default: '')
        - try 'idle {interface}' to display for each interface something when idle
    - interfaces: list of interfaces to check (default: 'eth0 wlan0')
    - interface_labels: list of labels to use to display interface names (default: '')
        - try 'E W' to display 'E' instead of 'eth0' and 'W' instead of 'wlan0'
    - mode : display mode (default: 'max')
        - 'max' to display just the most-active interface
        - 'all' to display all interfaces
    - separation : separator to use when displaying multiple interfaces (default: '|')
    - rate_format : formatting of rate number (default: '{value:4.0f}{units}'
        - used by '{max}', '{total}', '{up}', and {'down'} totals in format parameter
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
    direction_up = '⇑'   # ⬆ ⇑ ⇧ ▲ △
    direction_down = '⇓' # ⬇ ⇓ ⇩ ▼ ▽
    direction_both = '⇕' # ⬍ ⇕ ↕
    format = '{max} {interface}{direction}'
    #format = '{total} {interface}'
    #format = '{up}⇑ {down}⇓ {interface}'
    format_all_idle = 'idle net'
    format_idle = ''
    #format_idle = 'idle {interface}'
    interfaces = 'eth0 wlan0'
    interface_labels = ''
    #interface_labels = 'E W'
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

    def _get_stats(self, interfaces):
        stats = {}
        for interface in interfaces:
            si = stats[interface] = { 'tx': 0, 'rx': 0 }
            try:
                for way in ['tx', 'rx']:
                    fname = '/sys/class/net/{}/statistics/{}_bytes'.format(interface, way)
                    with open(fname) as f:
                        si[way] = int(f.readline())
            except IOError:
                pass # ignore unavailable interface
            si['total'] = si['tx'] + si['rx']
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

    def j3_netio(self, i3s_output_list, i3s_config):
        interfaces = self.interfaces.split()
        interface_labels = dict(zip(interfaces, self.interface_labels.split()))

        # calculate the difference in seconds between last check and now
        now = time()
        last_time = self.last_time or now
        self.last_time = now
        diff_time = now - last_time
        if diff_time < 1: diff_time = 1

        stats = self._get_stats(interfaces)
        last_stats = self.last_stats or stats
        self.last_stats = stats
        overall_max_total = 0

        # calculate bytes up/down/total since last check
        diffs = {}
        for interface in interfaces:
            di = diffs[interface] = {}
            si = stats[interface]
            li = last_stats[interface]
            for way in ['tx', 'rx', 'total']:
                di[way] = int((si[way] - li[way]) / diff_time)

        # show only most-active interface in 'max' mode
        if self.mode == 'max':
            interface = max(diffs, key=lambda i: diffs[i]['total'])
            diffs = { interface: diffs[interface] }

        # build list of text for each interface
        text = []
        for interface in diffs:
            di = diffs[interface]
            # format stats for active interface
            if di['total']:
                # determine most-active overall total number of bytes
                if overall_max_total < di['total']:
                    overall_max_total = di['total']

                # determine most-active direction for 'max' formatting
                max_direction = 'tx' if di['tx'] > di['rx'] else 'rx'
                max_value = di[max_direction]
                max_icon = self.direction_both
                if max_direction == 'tx': max_icon = self.direction_up
                if max_direction == 'rx': max_icon = self.direction_down

                text.append(self.py3.safe_format(self.format, {
                    'interface': interface_labels.get(interface) or interface,
                    'max': self._format_bytes(max_value),
                    'direction': max_icon,
                    'up': self._format_bytes(di['tx']),
                    'down': self._format_bytes(di['rx']),
                    'total': self._format_bytes(di['total']),
                }))
            # show idle text for inactive interface
            elif self.format_idle:
                text.append(self.py3.safe_format(self.format_idle, {
                    'interface': interface_labels.get(interface) or interface,
                }))

        # colorize output based on rate of most-active interface
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
            # show idle text if no active interfaces
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
        #print(x.j3_netio([], config)['full_text'])
        print(x.j3_netio([], config))
        sleep(1)
