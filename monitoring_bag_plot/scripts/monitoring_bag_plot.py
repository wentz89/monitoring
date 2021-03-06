#!/usr/bin/env python
'''
   Copyright (c) 2018, University of Hannover
                       Institute for Systems Engineering - RTS
                       Professor Bernardo Wagner
 
   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions
   are met:
 
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.
    * Neither the name of Willow Garage, Inc. nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.
 
   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
   FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
   COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
   INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
   BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
   LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
   ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
   POSSIBILITY OF SUCH DAMAGE.
''' 

import rospy
import rosnode
import csv
import datetime
import rosbag
import sys
import matplotlib.pyplot as plt
import argparse

from math import hypot
from monitoring_msgs.msg import *
from std_msgs.msg import Float64

start_time = None
value_dict = {}
combine = False
search_for_key = False
legends = []
lines = []
legend = None
fig = None
ax = None
key_list = None
lined = {}
#bag_dir = '/home/michael/youbot_local_dev/youbot_rosbag_20180828_szenario1/fahrt3.bag'
#bag_dir = '/home/michael/youbot_local_dev/youbot_rosbag_20180828_szenario2/fahrt1.bag'
bag_dir = '/home/michael/youbot_local_dev/youbot_rosbag_20180830_szenario3/fahrt1.bag'

def init():
    rospy.init_node("monitoring_bag_plot")
    if key_list:
        for argument in key_list:
            value_dict[argument] = {'timestamp':[], 'value':[], 'unit':[]}
    get_bag_data()
    plot()

def get_bag_data():
    global start_time
    global value_dict
    bag = rosbag.Bag(bag_dir)
    init = True
    for topic, msg, t in bag.read_messages():
        if init:
            start_time = t
            init = False
        if search_for_key:
            if topic == "/monitoring":
                for element in msg.info[0].values:
                    for argument in search_term:
                        if argument in element.key and element.key not in value_dict.keys():
                            value_dict[element.key] = {'timestamp':[], 'value':[], 'unit':[]}
        for key in value_dict.keys():
            if topic == "/monitoring":
                for element in msg.info[0].values:
                    if element.key == key:
                        temp_time = t - start_time
                        temp_time = temp_time.to_sec()
                        value_dict[key]['timestamp'].append(str(temp_time))
                        value_dict[key]['value'].append(str(element.value))
                        value_dict[key]['unit'].append(str(element.unit))
def plot():
    i = 1
    global legend
    global fig, ax
    global lined

    #plt.style.use('ggplot')

    fig, ax = plt.subplots()
    plt.tick_params(colors = 'black')
    for key in value_dict.keys():
        if not value_dict[key]['value'][0].replace('.','',1).isdigit():
            continue
        if not combine:
            plt.figure(i)
            plt.plot(value_dict[key]['timestamp'],value_dict[key]['value'])
            plt.title(key)
            plt.xlabel("time in sec")
            plt.grid(True)
            if not value_dict[key]['unit']:
                plt.ylabel("")
            else:
                plt.ylabel(value_dict[key]['unit'][0])
        else:
            temp, = ax.plot(value_dict[key]['timestamp'],value_dict[key]['value'],label = key)
            lines.append(temp)
            plt.xlabel("time in sec")
            legend = ax.legend()
            ax.grid(True)
        i = i + 1
    if combine:
        for legline, origline in zip(legend.get_lines(), lines):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline
        fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()

def onpick(event):
    global lined
    # on the pick event, find the orig line corresponding to the
    # legend proxy line, and toggle the visibility
    legline = event.artist
    origline = lined[legline]
    vis = not origline.get_visible()
    origline.set_visible(vis)
    # Change the alpha on the line in the legend so we can see what lines
    # have been toggled
    if vis:
        legline.set_alpha(1.0)
    else:
        legline.set_alpha(0.2)
    fig.canvas.draw()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot values from ROS Bag')
    parser.add_argument('-c', help='combine all values into one plot', action = 'store_true')
    parser.add_argument('-s', help='search for all keys containing this string', nargs=1)
    parser.add_argument('-keys', help='plot all keys equal to this string', nargs='+')
    args = parser.parse_args()
    search_term = None
    if not args.s == None:
        search_for_key = True
        search_term = args.s
    combine = args.c
    key_list = args.keys
    init()
    """
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        try:
            rate.sleep()
        except rospy.ROSInterruptException:
            rospy.loginfo("ERROR")
            pass
    rospy.logout("node - shutdown, writing to file")
    #plt.plot(value_dict["overall cpu load"]['timestamp'],value_dict["overall cpu load"]['value'])
    #plt.show()
    """
"""
with open("ping_data"+ str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S"))+".csv", "w") as file:
        i = 0
        file.write("timestamp,ping ms \n")
        for data in node_dict['Ping']:
            file.write(str(node_dict['timestamp'][i]))
            file.write(",")
            file.write(str(data))
            file.write("\n")
            i = i + 1

"""
