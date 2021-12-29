# Copyright 2021 TPS 13A team
########################################################################
# merge is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# merge is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with merge.  If not, see <https://www.gnu.org/licenses/>.      #
########################################################################

import os
import numpy as np
import argparse

#data is trimmed at this point
def readin1d(experimentDirectory, file, trim):
    with open(experimentDirectory+ '/' + file,'r') as f:
        lines = f.readlines()
    lines = lines[:len(lines)-trim]
    
    data = {"q" : [], "I" : [], "err" : []}
    for line in lines:
        if len(line.split()) == 3:    # length 2 is header
            data["q"].append(float(line.split()[0]))
            data["I"].append(float(line.split()[1]))
            data["err"].append(float(line.split()[2]))
    
    return data

def save_merged(experimentDirectory,save_name, new_data):
    with open(experimentDirectory + "/" + save_name, 'w') as f:
        np.savetxt(f, np.transpose([new_data["q"], new_data["I"], new_data["err"]]),fmt='%1.6e',delimiter='    ')
    return

# find overlap assums highest q 9M data is the last point and lowest q 1M data is first point (already trimmed)
def find_overlap(q_data9M, q_data1M):

    overlap_1M_indices = []
    overlap_9M_indices = []
    for i_q1M, v_q1M in enumerate(q_data1M):
        if float(v_q1M) < float(q_data9M[-1]):
            overlap_1M_indices.append(i_q1M)

    for i_q9M, v_q9M in enumerate(q_data9M):
        if v_q9M >= q_data1M[1]:
            overlap_9M_indices.append(i_q9M)
    print(q_data9M[-1])
    print(overlap_1M_indices)
    print(overlap_9M_indices)
    return overlap_1M_indices, overlap_9M_indices

def calc_scale_factor(data9M, data1M, overlap_1M_indices, overlap_9M_indices):
    Idat_9M = np.array(data9M["I"])
    Idat_1M = np.array(data1M["I"])
    scale_factor = np.divide( np.mean(Idat_9M[overlap_9M_indices]),np.mean(Idat_1M[overlap_1M_indices]))
    print(scale_factor)
    return scale_factor

def merge(data9M, data1M, scale1M):
    # scale 1M data
    data1M["I"] =  np.multiply(data1M["I"], scale1M).tolist() # have to turn back to list to concatinate below...
    data1M["err"] =  np.multiply(data1M["err"], scale1M).tolist()

    new_data = {"q" : [], "I" : [], "err" : []}
    new_data_q = np.array(data9M["q"] + data1M["q"])
    new_data_I = np.array(data9M["I"] + data1M["I"]) 
    new_data_err = np.array(data9M["err"] + data1M["err"]) 
    sort_index = np.argsort(new_data_q)    
    new_data["q"] = new_data_q[sort_index].tolist()
    new_data["I"] = new_data_I[sort_index].tolist()
    new_data["err"] = new_data_err[sort_index].tolist()
    return new_data

def main():
    parser = argparse.ArgumentParser(description='Merge 1d .dat file data from 9M and 1M detectors.')
    parser.add_argument('--directory', action='store', help='directory where the experiment is, if none default is cwd [default= None]', type=str, default= None)
    parser.add_argument('--file_9M', action='store', help='Name of 9M data file',type=str, default='data9M.dat')
    parser.add_argument('--file_1M', action='store', help='Name of 1M data file',type=str, default='data1M.dat')
    parser.add_argument('--trim_9M', action='store', help='number points to trim from END of 9M data [default=0]',type=int, default=0)
    parser.add_argument('--trim_1M', action='store', help='number points to trim from START of 1M data [default=0]',type=int, default=0)
    parser.add_argument('--save_name', action='store', help='name of column .dat file to save [default=data].',type=str, default='data')
    parser.add_argument('--scale_1M', action='store', help='scale factor for 1M I(q) data [default=1].',type=float, default=1)
    parser.add_argument('--calc_scale', action='store_true', help='If --calc_scale the scale factor will be calculated' )
    args = parser.parse_args()


    if args.directory is None:
        experimentDirectory = os.getcwd()
    else:    
        experimentDirectory = args.directory

    save_name = args.save_name
    file9M = args.file_9M
    file1M = args.file_1M
    scale1M = args.scale_1M
    trim9M = args.trim_9M
    trim1M = args.trim_1M
    calc_scale = args.calc_scale

    data9M = readin1d(experimentDirectory, file9M, trim9M)
    data1M = readin1d(experimentDirectory, file1M, trim1M)
    if calc_scale and scale1M != 1.0:
        print("Both calc scale factor and a value for the scale factor were give \nDefulting to use the given scale factor and NOT caculate it")
        overlap_1M, overlap_9M = find_overlap(data9M["q"], data1M["q"])
        scale1M = calc_scale_factor(data9M, data1M, overlap_1M, overlap_9M)
    elif calc_scale:
        overlap_1M, overlap_9M = find_overlap(data9M["q"], data1M["q"])
        scale1M = calc_scale_factor(data9M, data1M, overlap_1M, overlap_9M)

    new_data = merge(data9M, data1M, scale1M)
    save_merged(experimentDirectory,save_name, new_data)


if __name__ == "__main__":
    main()