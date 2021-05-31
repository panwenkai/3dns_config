# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 16:11:11 2015

@author: WenkaiPan
"""
import numpy as np
import gc
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D

temp_filename = 'C://Users//WenkaiPan//Desktop//3dns//Release//ELA_3D_generated.temp'   # Windows
hist_filename = 'C://Users//WenkaiPan//Desktop//3dns//Release//ELA_3D_generated.hist'  # Windows
temporal_profile_filename = 'C://Users//WenkaiPan//Desktop//3dns//Debug//Library//LP_30ns_triple.dat'
path = "D://ELA_3D_int//"

def get_frame(file_object):
    last_time = 0
    _3d = []
    _2d = []
    _1d = []
    begin = False
    for line in file_object:
        if 'PAGE FLOAT' in line:
            time = line.replace('PAGE FLOAT' , ' ')
            time_stripped = time.strip()
            time_value = float(time_stripped)
            if begin:
                _3d.append(_2d)
                _2d = []
                yield _3d, last_time
                last_time = 1e9 * time_value
                _3d = []
            else:
                begin = True
            continue
        elif (begin):
            if 'end sheet' in line:
                #print line
                sheet_number = int(line.replace('//end sheet', ' ').strip())
                _3d.append(_2d)
                _2d = []
            elif (len(line)>1):
                _1d = line.split()
                _1d = map(float, _1d)
                _2d.append(_1d)

#########################################################################
# Get the laser profile
temporal_profile_file = open(temporal_profile_filename)   # Windows
profile_timestamp_list = []
profile_intensity_list = []
for line in temporal_profile_file:
    time, intensity = line.split(',')
    time = float(time) * 1e9
    intensity = float(intensity)
    profile_timestamp_list.append(time)
    profile_intensity_list.append(intensity)
    
temporal_profile_file.close()        

############################################################################
# Scan the temp and hist file to get melt portion
myfile_temp = open(temp_filename)   # temperature file
myfile_hist = open(hist_filename)  # history file
                
hist_generator = get_frame(myfile_hist)
temp_generator = get_frame(myfile_temp)


report_timestamp_list = []
top_melt_percentage_list = []
bottom_melt_percentage_list = []
overall_melt_percentage_list = []

print 'Scanning the process!'
while True:
    try:
        hist_frame, hist_time = hist_generator.next()
        temp_frame, temp_time = temp_generator.next()
    except StopIteration as e:
        break
    # print hist_time
    overall_total_nodes = 0
    overall_melt_nodes = 0
    for i in range(len(hist_frame)):
        for j in range(len(hist_frame[i])):
            for k in range(len(hist_frame[i][j])):
                overall_total_nodes += 1.0
                if hist_frame[i][j][k]%4 == 3:  # slush
                    overall_melt_nodes += 0.5
                elif hist_frame[i][j][k]%4 == 0: # liquid
                    overall_melt_nodes += 1.0

    
    layer_total_nodes = 0
    top_melt_nodes = 0
    bottom_melt_nodes = 0
    for i in range(len(hist_frame)):
        for j in range(len(hist_frame[i][0])):
            layer_total_nodes += 1.0
            if hist_frame[i][0][j]%4 == 3:
                top_melt_nodes += 0.5
            elif hist_frame[i][0][j]%4 == 0:
                top_melt_nodes += 1.0

            if hist_frame[i][-1][j]%4 == 3:
                bottom_melt_nodes += 0.5
            elif hist_frame[i][-1][j]%4 == 0:
                bottom_melt_nodes += 1.0
               
    top_melt_percentage = top_melt_nodes/layer_total_nodes*100.0
    bottom_melt_percentage = bottom_melt_nodes/layer_total_nodes*100.0
    overall_melt_percentage = overall_melt_nodes/overall_total_nodes*100.0

    report_timestamp_list.append(hist_time)
    top_melt_percentage_list.append(top_melt_percentage)
    bottom_melt_percentage_list.append(bottom_melt_percentage)
    overall_melt_percentage_list.append(overall_melt_percentage)

myfile_temp.close()
myfile_hist.close()


#########################################################
#analysis temp and hist file
myfile_temp = open(temp_filename)   # temperature file
myfile_hist = open(hist_filename)  # history file
                
hist_generator = get_frame(myfile_hist)
temp_generator = get_frame(myfile_temp)

index = 0 
while True:
    try:
        hist_frame, hist_time = hist_generator.next()
        #temp_frame, temp_time = temp_generator.next()
    except StopIteration as e:
        break
        
    number_of_i = len(hist_frame)/2
    number_of_j = len(hist_frame[0])
    number_of_k = len(hist_frame[0][0])/2
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_xlim(0,60)
    ax.set_ylim(60,0)
    ax.set_zlim(20,0)
    for i in range(number_of_i):
        for j in range(number_of_j):
            for k in range(number_of_k):
                if hist_frame[i][j][k]%4 == 3:
                    I = [i-0.5, i+0.5]
                    J = [j-0.5, j+0.5]
                    K = [k-0.5, k+0.5]
                    
                    X, Y = np.meshgrid(I, K)
                    Z = J
                    ax.plot_surface(X,Y,Z[0], alpha=0.5)
                    ax.plot_surface(X,Y,Z[1], alpha=0.5)
                    
                    Y, Z = np.meshgrid(K, J)
                    X = I
                    ax.plot_surface(X[0],Y,Z, alpha=0.5)
                    ax.plot_surface(X[1],Y,Z, alpha=0.5)
                    
                    X, Z = np.meshgrid(I, J)
                    Y = K
                    ax.plot_surface(X,Y[0],Z, alpha=0.5)
                    ax.plot_surface(X,Y[1],Z, alpha=0.5)

    ax.set_title(str(hist_time))
    filename = path + str(index) + '.jpg'
    index += 1
        
    fig.savefig(filename, dpi=500)
    fig.clf()
    plt.close()
    del hist_frame
    gc.collect()