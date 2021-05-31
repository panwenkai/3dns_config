# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 16:11:11 2015

@author: WenkaiPan
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec

temp_filename = 'C://Users//WenkaiPan//Desktop//3dns//Release//ELA_3D_generated.temp'   # Windows
hist_filename = 'C://Users//WenkaiPan//Desktop//3dns//Release//ELA_3D_generated.hist'  # Windows
temporal_profile_filename = 'C://Users//WenkaiPan//Desktop//3dns//Debug//Library//LP_30ns_triple.dat'
path = "D://ELA_3D_high//"

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
        temp_frame, temp_time = temp_generator.next()
    except StopIteration as e:
        break
    

    for i in range(len(hist_frame)):
        for j in range(len(hist_frame[i][0])):
            if hist_frame[i][0][j]%4 == 3:  # slush
                hist_frame[i][0][j] = 0
            elif hist_frame[i][0][j]%4 == 0: # liquid
                hist_frame[i][0][j] = 1
            else:  # solid
                hist_frame[i][0][j] = 1
                
            if hist_frame[i][-1][j]%4 == 3:  # slush
                hist_frame[i][-1][j] = 0
            elif hist_frame[i][-1][j]%4 == 0: # liquid
                hist_frame[i][-1][j] = 1
            else:  # solid
                hist_frame[i][-1][j] = 1
    
    hist_frame_array = np.asarray(hist_frame)
    temp_frame_array = np.asarray(temp_frame)
    assert hist_time==temp_time
    filename = path #  Directory of files to be generated
    filename += str(index)
    melt_percentage = overall_melt_percentage_list[index]
    index += 1
    filename += ".jpg"
    fig = plt.figure(frameon=False)
    #plt.title(str(hist_time))
    gs1 = gridspec.GridSpec(2, 1)
    gs1.update(left=0.1, right=0.68, wspace=0.05)
    title = 'time: ' + '%.1f' % (hist_time) + 'ns'
    title += (' melt%: ' + '%.2f' % melt_percentage)
    
    # plt.scatter(boundary_x_list, boundary_y_list, color='b', s=5)
    ax1 = fig.add_subplot(gs1[0,0])
    _2d_array = np.array(temp_frame_array[:,0,:])
    # print _2d_array.shape
    img = ax1.imshow(_2d_array, cmap="hot")
    
    _2d_array = np.array(hist_frame_array[:,0,:])
    ax1.set_xlabel('Node Number')
    ax1.set_ylabel('Node Number')
    ax1.imshow(_2d_array,clim=(0,1),cmap=plt.cm.gray, alpha=0.3, aspect=1)
    #plt.colorbar(img, ax2,orientation='horizontal')
    
    ax2 = fig.add_subplot(gs1[1,0])
    _2d_array = np.array(temp_frame_array[:,-1,:])
    # print _2d_array.shape
    img = ax2.imshow(_2d_array, cmap="hot")
    
    _2d_array = np.array(hist_frame_array[:,-1,:])
    ax2.set_xlabel('Node Number')
    ax2.set_ylabel('Node Number')
    ax2.imshow(_2d_array,clim=(0,1),cmap=plt.cm.gray, alpha=0.3, aspect=1)
    #plt.colorbar(img, ax2,orientation='horizontal')
    
    gs2 = gridspec.GridSpec(4, 1)
    gs2.update(left=0.75, right=0.95, wspace=0.01)
    
    ax3 = fig.add_subplot(gs2[0,0])
    ax3.plot(profile_timestamp_list, profile_intensity_list, 'k')
    ax3.set_xlim(report_timestamp_list[0], report_timestamp_list[-1])
    ax3.axvline(hist_time, c='k', ls='--')
    ax3.set_title('laser profile')
    for label in ax3.get_xticklabels(which='both'):
        label.set_visible(False)
        
    ax4 = fig.add_subplot(gs2[1,0])
    ax4.plot(report_timestamp_list, top_melt_percentage_list, 'g')
    ax4.set_xlim(report_timestamp_list[0], report_timestamp_list[-1])
    ax4.axvline(hist_time, c='k', ls='--')
    ax4.set_title('top melt%')
    for label in ax4.get_xticklabels(which='both'):
        label.set_visible(False) 
        
    ax5 = fig.add_subplot(gs2[2,0])
    ax5.plot(report_timestamp_list, bottom_melt_percentage_list, 'b')
    ax5.set_xlim(report_timestamp_list[0], report_timestamp_list[-1])
    ax5.axvline(hist_time, c='k', ls='--')
    ax5.set_title('bottom melt%')
    for label in ax5.get_xticklabels(which='both'):
        label.set_visible(False)
        
    ax6 = fig.add_subplot(gs2[3,0])
    ax6.plot(report_timestamp_list, overall_melt_percentage_list, 'r')
    ax6.set_xlim(report_timestamp_list[0], report_timestamp_list[-1])
    ax6.axvline(hist_time, c='k', ls='--')
    ax6.set_title('overall melt%')
    ax6.set_xlabel('time [ns]')
        
    fig.savefig(filename, dpi=500)