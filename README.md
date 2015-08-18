j3status
========

Miscellaneous modules for [py3status](https://github.com/ultrabug/py3status), an extensible [i3status](http://i3wm.org/i3status/) wrapper written in python.

Modules
-------

### `j3_battery`

Display the battery level.

Configuration parameters:
- `ac_info` : path to adapter info (default: '/sys/class/power_supply/ADP0')
- `battery_info` : path to battery info (default: '/sys/class/power_supply/BAT0')
- `cache_timeout` : seconds between battery checks (default: 5)
- `capacity_degraded` : percent below which colored as degraded (default: 50)
- `capacity_bad` : percent below which colored as bad (default: 15)
- `format` : display format (default: '{capacity}% {icon}')

### `j3_cpu`

Display the CPU usage.

Configuration parameters:
- `cache_timeout` : seconds between rate checks (default: 1)
- `colorize` : true to colorize output (default: True)
    - set color thresholds via rate_good/degraded/bad
- `format` : display format (default: 'CPU {icon}')
- `mode` : display mode (default: 'max')
    - 'max' to display just the CPU with max usage
    - 'avg' to display the average usage of all CPUs
    - 'all' to display each individual CPU
- `rate_good` : threshold above which display is colorized as good (default: 10)
- `rate_degraded` : threshold above which display is colorized as degraded (default: 40)
- `rate_bad` : threshold above which display is colorized as bad (default: 90)

### `j3_diskio`

Display the current disk transfer rate.

Configuration parameters:
- `cache_timeout` : seconds between rate checks (default: 1)
- `colorize` : true to colorize output (default: True)
    - set color thresholds via rate_good/degraded/bad
- `indicator_read` : indicator for read rate (default: ⇑)
- `indicator_write` : indicator for write rate (default: ⇓)
- `indicator_combined` : indicator for combined rate (default: ⇕)
- `format` : display format (default: '{max} {device}{direction}')
    - try '{total} {device}' to show combined read and write totals
    - try '{read}⇑ {write}⇓ {device}' to show separate read and write totals
    - format tokens :
        - '{direction}' : icon indicating most-active direction (read or write)
        - '{device}' : device label (ie 'sda')
        - '{max}' : rate of most-active direction
        - '{total}' : combined rate of both read and write totals
        - '{read}' : read (trasmitted) rate
        - '{write}' : write (received) rate
- `format_all_idle` : display format when all devices are idle (default: 'idle net')
- `format_idle` : display format for an individual idle device (default: '')
    - try 'idle {device}' to display for each device something when idle
- `devices`: list of devices to check (default: 'eth0 wlan0')
- `device_labels`: list of labels to use to display device names (default: '')
    - try 'a b' to display 'a' instead of 'sda' and 'b' instead of 'sdb'
- `mode` : display mode (default: 'max')
    - 'max' to display just the most-active device
    - 'all' to display all devices
- `separator` : separator to use when displaying multiple devices (default: '|')
- `rate_format` : formatting of rate number (default: '{value:4.0f}{units}'
    - used by '{max}', '{total}', '{read}', and {'write'} totals in format parameter
    - uses units defined by rate_b/kb/mb/gb/tb parameters
- `rate_b` : indicator for B/s units (default: ' B/s')
- `rate_kb` : indicator for KB/s units (default: 'KB/s')
- `rate_mb` : indicator for MB/s units (default: 'MB/s')
- `rate_gb` : indicator for GB/s units (default: 'GB/s')
- `rate_tb` : indicator for TB/s units (default: 'TB/s')
- `rate_good` : threshold above which display is colorized as good (default: 1048576)
- `rate_degraded` : threshold above which display is colorized as degraded (default: 10485760)
- `rate_bad` : threshold above which display is colorized as bad (default: 104857600)

### `j3_netio`

Display the current network transfer rate.

Configuration parameters:
- `cache_timeout` : seconds between rate checks (default: 1)
- `colorize` : true to colorize output (default: True)
    - set color thresholds via rate_good/degraded/bad
- `direction_up` : indicator for upload rate (default: ⇑)
- `direction_down` : indicator for download rate (default: ⇓)
- `direction_both` : indicator for combined rate (default: ⇕)
- `format` : display format (default: '{max} {interface}{direction}')
    - try '{total} {interface}' to show combined up and down totals
    - try '{up}⇑ {down}⇓ {interface}' to show separate up and down totals
    - format tokens :
        - '{direction}' : icon indicating most-active direction (up or down)
        - '{interface}' : interface label (ie 'eth0')
        - '{max}' : rate of most-active direction
        - '{total}' : combined rate of both up and down totals
        - '{up}' : up (trasmitted) rate
        - '{down}' : down (received) rate
- `format_all_idle` : display format when all interfaces are idle (default: 'idle net')
- `format_idle` : display format for an individual idle interface (default: '')
    - try 'idle {interface}' to display for each interface something when idle
- `interfaces`: list of interfaces to check (default: 'eth0 wlan0')
- `interface_labels`: list of labels to use to display interface names (default: '')
    - try 'E W' to display 'E' instead of 'eth0' and 'W' instead of 'wlan0'
- `mode` : display mode (default: 'max')
    - 'max' to display just the most-active interface
    - 'all' to display all interfaces
- `separator` : separator to use when displaying multiple interfaces (default: '|')
- `rate_format` : formatting of rate number (default: '{value:4.0f}{units}'
    - used by '{max}', '{total}', '{up}', and {'down'} totals in format parameter
    - uses units defined by rate_b/kb/mb/gb/tb parameters
- `rate_b` : indicator for B/s units (default: ' B/s')
- `rate_kb` : indicator for KB/s units (default: 'KB/s')
- `rate_mb` : indicator for MB/s units (default: 'MB/s')
- `rate_gb` : indicator for GB/s units (default: 'GB/s')
- `rate_tb` : indicator for TB/s units (default: 'TB/s')
- `rate_good` : threshold above which display is colorized as good (default: 1048576)
- `rate_degraded` : threshold above which display is colorized as degraded (default: 10485760)
- `rate_bad` : threshold above which display is colorized as bad (default: 104857600)

### `j3_ram`

Display the RAM (and swap) usage.

Configuration parameters:
- `cache_timeout` : seconds between rate checks (default: 5)
- `colorize` : true to colorize output (default: True)
    - set color thresholds via rate_good/degraded/bad
- `ram_format` : display format (default: 'RAM {:.1f} GB')
- `swap_format` : display format (default: 'swap {:.1f} GB')
- `rate_good` : threshold above which display is colorized as good (default: 0)
- `rate_degraded` : threshold above which display is colorized as degraded (default: 50)
- `rate_bad` : threshold above which display is colorized as bad (default: 90)

### `j3_weather`

Display current conditions from [openweathermap.org](http://openweathermap.org).

Configuration parameters:
- `cache_timeout` : seconds between requests for weather updates (default: 1800)
- `direction_precision` : wind direction precision (default: 2)
    - 1 : N E S W
    - 2 : N NE E SE S etc
    - 3 : N NNE NE ENE E etc
- `format` : display format (default: '{city} {temp}°F {icon} {sky} {humidity}%rh {pressure}inHg {direction} {wind}mph')
    - corresponding metric format would be '{city} {temp}°C {icon} {sky} {humidity}%rh {pressure}hPa {direction} {wind}m/s'
    - city : city name (eg 'Seattle')
    - temp : temperature (eg '35')
    - icon : weather icon (eg '☀')
    - sky : weather conditions (eg 'Clear' or 'Rain' or 'Haze' etc)
    - humidity : relative humidity (eg '50')
    - pressure : barometric pressure (eg '29.58')
    - direction : wind direction (eg 'NW')
    - wind : wind speed (eg '11')
- `location` : city,country of location for which to show weather (default: 'Seattle,US')
    - see http://openweathermap.org/city
    - for US, a location like 'Springfield IL' will also work
- `request_timeout` : seconds after which to abort request (default: 10)
- `timezone` : timezone of location (default: 'America/Los_Angeles')
    - used to determine if it's currently day or night at the location
- `units` : imperial or metric units (default: 'imperial')
    - imperial :
        - temperature : fahrenheit
        - pressure : inches of mercury
        - wind : miles per hour
    - metric :
        - temperature : celsius
        - pressure : hectopascal
        - wind : meters per second

Usage
-----

To [use py3status](https://github.com/ultrabug/py3status#usage), you specify `py3status` as the `status_command` in the `bar` block of your [i3 config file](http://i3wm.org/docs/userguide.html#configuring). By default, py3status will load any modules you place in your `~/.i3/py3status` directory. You can also use the `-i` or `--include` flag with py3status to specify other directories from which to load modules.

So copy the modules you want to use into `~/.i3/py3status` (or another configured directory), and specify each module name with an "order" directive in your [i3status config file](http://i3wm.org/i3status/manpage.html#_configuration).  For example, to use the `j3_ram` module, add an order directive like this:
```
order += "j3_ram"
```

Then add a block for the module to configure whatever options from the module you want to override, like this:
```
j3_ram {
    ram_format = 'RAM {:.1f}G'
    swap_format = 'swap {:.1f}G'
}
```

Restart i3 to see your changes (`i3-msg restart`).

