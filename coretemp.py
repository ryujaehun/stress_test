#!/usr/bin/python2
import socket
import subprocess
import collections
import datetime
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import gc
from math import ceil
import numpy as np

NB_PROBES = 3600
color={0:'c',1:'m',2:'k',3:'y'}
gpu_cmd=" lspci | grep ' VGA ' | cut -d' ' -f 1"
pro = subprocess.Popen(gpu_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
t, e = pro.communicate()
num_of_gpu=len(t.decode('UTF-8').split('\n')[:-1])
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
    gpu_temp=temp2.decode('UTF-8').split('\n')[:-1]
    gpu_temp=list(map(int,gpu_temp))





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
    gpu_temps=np.array([collections.OrderedDict() for i in range(num_of_gpu)])

    # Measurements
    while nb_probes < NB_PROBES:
        current_time = time.asctime().split(' ')[3] # Get measurement time. We split because we're only interested in the HH:MM:SS signal
        #print(current_time)
        cpu_temp, gpu_temp =  probe_temperature()
        cpu_temps[current_time] = cpu_temp
        for i in range(num_of_gpu):
            gpu_temps[i][current_time] = gpu_temp[i]
        nb_probes += 1
        time.sleep(sleep_time_in_seconds) # wait until next measurement
        plot_temperatures(cpu_temps,gpu_temps)


    #return cpu_temps, gpu_temps

def plot_temperatures(cpu_temps, gpu_temps):
    """ Plot CPU/GPU temperature evolution over time """
    fig = plt.figure(figsize=(40,20))
    plt.grid()
    x = range(len(cpu_temps))
    cpu_avg = sum([t for t in cpu_temps.values()])/float(len([t for t in cpu_temps.values()]))
    gpu_avg=np.zeros(num_of_gpu,dtype=float)
    for i in range(num_of_gpu):
        gpu_avg[i] = sum([t for t in gpu_temps[i].values()])/float(len([t for t in gpu_temps[i].values()]))
    cpu_avg_plot = plt.axhline(y=cpu_avg, xmin=0, xmax=len(cpu_temps), color='r', linestyle='--')
    gpu_avg_plot=np.zeros(num_of_gpu,dtype=object)
    for i in range(num_of_gpu):
        gpu_avg_plot[i] = plt.axhline(y=gpu_avg[i], xmin=0, xmax=len(gpu_temps[i]), color=color[i], linestyle='--')
    cpu_plot = plt.plot(x, cpu_temps.values(), 'ro-')
    gpu_plot=np.zeros(num_of_gpu,dtype=object)
    for i in range(num_of_gpu):
        gpu_plot[i] = plt.plot(x, gpu_temps[i].values(), color[i]+'o-')
    locs, labels = plt.xticks(x, cpu_temps.keys())
    plt.ylim(ymin = min([temp for temp in cpu_temps.values() + gpu_temps[0].values()]) - 10,
             ymax = max([temp for temp in cpu_temps.values() + gpu_temps[0].values()]) + 10)
    plt.xlim(xmin=-1, xmax=len(x))
    fig.autofmt_xdate()
    plt.ylabel("Temperature (in Celcius)")
    _list=np.stack((gpu_plot,gpu_avg_plot),axis=1).reshape(-1,2*num_of_gpu)[0]
    _list=np.append(_list,cpu_plot)
    _list=np.append(_list,cpu_avg_plot)
    _list2=np.zeros(num_of_gpu*2+2,dtype=object)
    for i in range(0,num_of_gpu*2,2):
        _list2[i]='GPU '+ str(i//2)+'temperature'
        _list2[i+1]="Average GPU "+ str(i//2)+" temperature : %.1fC" %(gpu_avg[i//2])
    _list2[-2]='CPU'
    _list2[-1]="Average CPU temperature : %.1fC" %(cpu_avg)
    plt.legend(_list,
               _list2,
               loc = "best")
    plt.suptitle("Evolution of the CPU/GPU temperature\nbetween %s and %s" %(cpu_temps.keys()[0], cpu_temps.keys()[-1]), fontsize=20)
    plt.savefig(socket.gethostname()+"_CPU_GPU_temperature.png",quality=100)
    plt.close(fig)
    del fig
    gc.collect()
if __name__ == '__main__':
    probe_for_duration(hour=23, minute=50, second=30)
    probe_for_duration(hour=23, minute=50, second=30)
    probe_for_duration(hour=23, minute=50, second=30)
    probe_for_duration(hour=23, minute=50, second=30)
    probe_for_duration(hour=23, minute=50, second=30)
