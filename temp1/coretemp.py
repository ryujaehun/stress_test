#!/usr/bin/python2

import subprocess
import collections
import datetime
import time
import matplotlib.pyplot as plt

from math import ceil

NB_PROBES = 3600


def probe_temperature():
    """ Return the CPU and GPU temperature, in degrees centigrade (Celcius) """
    cmd = "inxi -s | grep Sensors | awk '{print $6,$10}'"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    cmd2="nvidia-smi -q -d temperature | grep 'GPU Current'| awk '{print $5}'"
    p1 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    temp, error = p.communicate()
    temp2, error2 = p1.communicate()
    t=temp.decode('utf8').replace('\n','').split(' ')
    cpu_temp=int(float(t[0][:-1]))
    gpu_temp=temp2.split('\n')[:-1]

    gpu_temp=list(map(int,gpu_temp))
    #print(gpu_temp)


    return cpu_temp,gpu_temp

def probe_for_duration(hour=0, minute=0, second=0):
    """ Probe the CPU/GPU temperature for the input duration
    Returns 2 OrderedDict with keys: time of the measurement and
    values: temperature
    """
    duration = datetime.time(hour=hour, minute=minute, second=second)
    duration_in_seconds = (3600*hour) + (60 * minute) + second
    sleep_time_in_seconds = ceil(float(duration_in_seconds) / NB_PROBES) # sleep time between 2 measurments

    # Init
    nb_probes = 0
    cpu_temps = collections.OrderedDict()
    gpu_temps0 = collections.OrderedDict()
    gpu_temps1 = collections.OrderedDict()
    gpu_temps2 = collections.OrderedDict()
    gpu_temps3 = collections.OrderedDict()

    # Measurements
    while nb_probes < NB_PROBES:
        current_time = time.asctime().split(' ')[3] # Get measurement time. We split because we're only interested in the HH:MM:SS signal
        #print(current_time)
        cpu_temp, gpu_temp =  probe_temperature()
        cpu_temps[current_time] = cpu_temp
        gpu_temps0[current_time] = gpu_temp[0]
        gpu_temps1[current_time] = gpu_temp[1]
        gpu_temps2[current_time] = gpu_temp[2]
        gpu_temps3[current_time] = gpu_temp[3]

        nb_probes += 1
        time.sleep(sleep_time_in_seconds) # wait until next measurement
        plot_temperatures(cpu_temps,gpu_temps0,gpu_temps1,gpu_temps2,gpu_temps3)


    #return cpu_temps, gpu_temps

def plot_temperatures(cpu_temps, gpu_temps0,gpu_temps1,gpu_temps2,gpu_temps3):
    """ Plot CPU/GPU temperature evolution over time """
    # Plot structure

    fig = plt.figure(figsize=(200,20))
    plt.grid()
    x = range(len(cpu_temps))
    cpu_avg = sum([t for t in cpu_temps.values()])/float(len([t for t in cpu_temps.values()]))
    gpu_avg0 = sum([t for t in gpu_temps0.values()])/float(len([t for t in gpu_temps0.values()]))
    gpu_avg1 = sum([t for t in gpu_temps1.values()])/float(len([t for t in gpu_temps1.values()]))
    gpu_avg2 = sum([t for t in gpu_temps2.values()])/float(len([t for t in gpu_temps2.values()]))
    gpu_avg3 = sum([t for t in gpu_temps3.values()])/float(len([t for t in gpu_temps3.values()]))
    #cpu_avg_plot = plt.axhline(y=cpu_avg, xmin=0, xmax=len(cpu_temps), color='r', linestyle='--')
    #gpu_avg_plot = plt.axhline(y=gpu_avg, xmin=0, xmax=len(gpu_temps), color='b', linestyle='--')
    cpu_plot = plt.plot(x, cpu_temps.values(), 'ro-')
    gpu_plot0 = plt.plot(x, gpu_temps0.values(), 'co-')
    gpu_plot1 = plt.plot(x, gpu_temps1.values(), 'mo-')
    gpu_plot2 = plt.plot(x, gpu_temps2.values(), 'yo-')
    gpu_plot3 = plt.plot(x, gpu_temps3.values(), 'ko-')
    locs, labels = plt.xticks(x, cpu_temps.keys())
    plt.ylim(ymin = min([temp for temp in cpu_temps.values() + gpu_temps0.values()]) - 10,
             ymax = max([temp for temp in cpu_temps.values() + gpu_temps1.values()]) + 10)
    plt.xlim(xmin=-1, xmax=len(x))
    fig.autofmt_xdate()
    plt.ylabel("Temperature (in Celcius)")
    plt.legend([gpu_plot0,gpu_plot1,gpu_plot2,gpu_plot3, cpu_plot],
               ["GPU temperature", "Average GPU temperature : %.1fC" %(gpu_avg0),"GPU temperature", "Average GPU temperature : %.1fC" %(gpu_avg1),
                "GPU temperature", "Average GPU temperature : %.1fC" %(gpu_avg2),"GPU temperature", "Average GPU temperature : %.1fC" %(gpu_avg3),
                "CPU", "Average CPU temperature : %.1fC" %(cpu_avg)],
               loc = "best")
    plt.suptitle("Evolution of the CPU/GPU temperature\nbetween %s and %s" %(cpu_temps.keys()[0], cpu_temps.keys()[-1]), fontsize=20)
    plt.savefig("CPU_GPU_temperature.pdf")

if __name__ == '__main__':
    #probe_temperature()
    probe_for_duration(hour=23, minute=50, second=30)
#    probe_temperature()

