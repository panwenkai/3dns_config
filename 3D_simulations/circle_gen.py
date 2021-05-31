from PIL import Image
import numpy as np
import scipy
from scipy import interpolate

i_nodes = 120
k_nodes = 120
j_nodes = 10

radius = 30  # in terms of number of nodes
node_size = 5


def copy_template_file(template_file, target_file):
    for line in template_file:
        target_file.write(line)
    pass

def copy_overlay_file(overlay_template_file, target_file, loc_i, loc_j_start, loc_j_end, loc_k, grain_index):
    for line in overlay_template_file:
        if line.find('OVERLAY_LOCATIONS_I') != -1:
            line = line.replace("...", str(loc_i))
        elif line.find('OVERLAY_LOCATIONS_K') != -1:
            line = line.replace("...", str(loc_k))
        elif line.find('OVERLAY_LOCATIONS_J') != -1:
            line = line.replace("...", str(loc_j_start)+'..'+str(loc_j_end))
        elif line.find('OVERLAY_GRAIN_INDEX') != -1:
            line = line.replace("...", str(grain_index))
        target_file.write(line)
    pass
 
target_filename = "C://Users//WenkaiPan//Desktop//3dns//x64//Release//circle.sim"
template_filename = 'C://Users//WenkaiPan//Desktop//3dns//Release//circle_3D_template.txt'
overlay_template_filename = 'C://Users//WenkaiPan//Desktop//3dns//Release//circle_overlay_template.txt'

template_file = open(template_filename)
target_file = open(target_filename, 'w')

copy_template_file(template_file, target_file)

template_file.close()

center_i = i_nodes / 2.0
center_k = k_nodes / 2.0
                                

                                
for i in range(i_nodes):
    for k in range(k_nodes):
        i_loc = i + 0.5
        k_loc = k + 0.5
        distance = np.sqrt((i_loc-center_i)**2+(k_loc-center_k)**2)
        overlay_template = open(overlay_template_filename)
        j_start = 0
        j_end = 9
        if distance <= radius:
            copy_overlay_file(overlay_template, target_file, i, j_start, j_end, k, 1)
        else:
            pass
                                
        overlay_template.close()
target_file.close()