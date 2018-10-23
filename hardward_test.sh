#! /bin/bash
stress -c 12 --io 4  --hdd 1 --hdd-bytes 1024m -t 36000m --vm-bytes $(awk '/MemFree/{printf "%d\n", $2 * 0.097;}' < /proc/meminfo)k --vm-keep -m 10
