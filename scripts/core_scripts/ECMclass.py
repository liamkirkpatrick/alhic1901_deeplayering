#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 22:31:42 2024

@author: Liam
"""

#%% Import packages

import pandas as pd
import numpy as np
import math
from tqdm import tqdm


#%% User inputs

path_to_data = '../../data/ecm/'
metadata = 'metadata.csv'

#%% Define ECM Class

class ECM:
    
    def __init__(self,core,section,face,ACorDC,path_to_data='ecm/raw/',metadata=metadata):
        
        # open metadata csv
        meta = pd.read_csv(path_to_data+metadata)
        row = meta.loc[meta['core']==core]
        row = row.loc[row['section']==section]
        row = row.loc[row['face']==face]
        row = row.loc[row['ACorDC']==ACorDC]
        
        # assign core components
        self.time = row['time'].values[0]
        self.y_left = row['Y_left'].values[0]
        self.y_right = row['Y_right'].values[0]
        self.core = row['core'].values[0]
        self.section = row['section'].values[0]
        self.face = row['face'].values[0]
        self.ACorDC = row['ACorDC'].values[0]
        
        # open core csv
        fname = self.core+'-'+self.section+'-'+self.face+'-'+self.ACorDC+'.csv'
        raw = pd.read_csv(path_to_data+fname)
        
        # assign vectors
        self.meas = raw['meas'].to_numpy()
        self.y = raw['Y_dimension(mm)'].to_numpy()
        self.button = raw['Button'].to_numpy()
        self.depth = raw['True_depth(m)'].to_numpy()
        self.y_vec = np.unique(self.y)
        if 'button_raw' in raw.columns:
            self.button_raw = raw['button_raw'].to_numpy()
        self.y_space = self.y_vec[1] - self.y_vec[0]
            
        # remove tracks that are incomplete
        lenth = []
        approx_length = max(self.depth) - min(self.depth)
        for y in self.y_vec:
            idx = self.y==y
            track_length = max(self.depth[idx]) - min(self.depth[idx])

            # remove tracks not within 1cm of overall length
            if abs(approx_length - track_length) > 0.01:
                self.meas = self.meas[np.invert(idx)]
                self.y = self.y[np.invert(idx)]
                self.button = self.button[np.invert(idx)]
                self.depth = self.depth[np.invert(idx)]
                self.y_vec = self.y_vec[self.y_vec!=y]
                if 'button_raw' in raw.columns:
                    self.button_raw = self.button_raw[np.invert(idx)]
        
        # assign status
        self.issmoothed = False
        
    def smooth(self,window):
        # takes as input smoothing window (in mm)
        
        # convert window to m
        window=window/1000
        
        # get spacing between points
        vec = self.depth[self.y==self.y_vec[0]]
        dist = []
        for i in range(len(vec)-1):
            dist.append(vec[i+1]-vec[i])
        
        # make vector of depths to interpolate onto
        dvecmin = min(self.depth) + 2*window/3
        dvecmax = max(self.depth) - 2*window/3
        dvec_num = math.floor((dvecmax-dvecmin) / abs(np.mean(dist)))
        depth_vec = np.linspace(dvecmin,dvecmax,dvec_num)
        #self.dvec = np.flip(depth_vec)
        
        # make empty smooth vectors
        depth_smooth = []
        meas_smooth = []
        button_smooth = []
        y_smooth = []
        
        # loop through all tracks
        for y in self.y_vec:
            
            # index within track
            idx = self.y == y
            
            dtrack = self.depth[idx]
            mtrack = self.meas[idx]
            btrack = self.button[idx]
            
            # loop through all depths
            for d in depth_vec:
                
                # find index of all points within window of this depth
                didx = (dtrack >= d-window/2) * (dtrack <= d+window/2)
                
                # save values
                depth_smooth.append(d)
                meas_smooth.append(np.median(mtrack[didx]))
                y_smooth.append(y)
                if sum(btrack[didx])>0:
                    button_smooth.append(1)
                else:
                    button_smooth.append(0)
                
        # save smooth values
        self.depth_s = np.flip(np.array(depth_smooth))
        self.meas_s = np.flip(np.array(meas_smooth))
        self.button_s = np.flip(np.array(button_smooth))
        self.y_s = np.flip(np.array(y_smooth))
        
        self.issmoothed = True
        
    def rem_ends(self,clip):
        
        # convert clip to m
        clip = clip/1000
        
        # find index within clip
        dmin = min(self.depth)
        dmax = max(self.depth)
        idx = (self.depth>=dmin+clip) * (self.depth<=dmax-clip)
        
        self.meas = self.meas[idx]
        self.y = self.y[idx]
        self.button = self.button[idx]
        self.depth = self.depth[idx]
        
        
        # check if smooth exists
        if hasattr(self,'y_s'):
            
            # find index within clip
            dmin = min(self.depth_s)
            dmax = max(self.depth_s)
            idx = (self.depth_s>=dmin+clip) * (self.depth_s<=dmax-clip)
            
            self.meas_s = self.meas_s[idx]
            self.y_s = self.y_s[idx]
            self.button_s = self.button_s[idx]
            self.depth_s = self.depth_s[idx]
            
    
    # normalize outside magnitude to match inner tracks
    def norm_outside(self):
                
        # calculate average accross main track
        norm_idx1 = self.y>self.y_vec[0]
        norm_idx2 = self.y<self.y_vec[-1]
        norm_idx = norm_idx1*norm_idx2
        norm = np.mean(self.meas[norm_idx])
        
        # now loop through each outside track
        for ytrack in [self.y_vec[0],self.y_vec[-1]]:
            track_idx = self.y == ytrack
            track_ave = np.mean(self.meas[track_idx])
            self.meas[track_idx] = self.meas[track_idx] * norm / track_ave
            if self.issmoothed:
                strack_idx = self.y_s == ytrack
                self.meas_s[strack_idx] = self.meas_s[strack_idx] * norm / track_ave
                
            print(norm/track_ave)
            
    # normalize all tracks
    def norm_all(self):
        
        # loop through all tracks
        for ytrack in self.y_vec:
            
            button_idx = self.button == 0
            track_idx = self.y == ytrack
            trackave = np.mean(self.meas[track_idx*button_idx])
            self.meas[track_idx] = self.meas[track_idx] / trackave
            
            # normalize smooth track if it exists
            if self.issmoothed:
                
                sbutton_idx = self.button_s == 0
                strack_idx = self.y_s == ytrack
                strackave = np.mean(self.meas_s[strack_idx*sbutton_idx])
                self.meas_s[strack_idx] = self.meas_s[strack_idx] / strackave

    def add_3d_to_face(self,x,y):
        
        self.x_3d = x
        self.y_3d = y


class core_section:

    def __init__(self,section,core,ACorDC,data,sections,faces,cores,ACorDCs):

        # find data
        t = next((d for d, sec, f, c, acdc in zip(data, sections, faces,cores,ACorDCs) if sec == section and f == 't' and c == core and acdc == ACorDC), None)
        r = next((d for d, sec, f, c, acdc in zip(data, sections, faces,cores,ACorDCs) if sec == section and f == 'r' and c == core and acdc == ACorDC), None)
        l = next((d for d, sec, f, c, acdc in zip(data, sections, faces,cores,ACorDCs) if sec == section and f == 'l' and c == core and acdc == ACorDC), None)
        o = next((d for d, sec, f, c, acdc in zip(data, sections, faces,cores,ACorDCs) if sec == section and f == 'o' and c == core and acdc == ACorDC), None)

        # assign metadata
        self.core = core
        self.section = section
        self.ACorDC = ACorDC

        # assign faces if they exist
        if t is None:
            print(f"No data found for top face of section {section} in core {core}")
        else:
            self.top = t
        if l is None:
            print(f"No data found for left face of section {section} in core {core}")
        else:
            self.left = l
        if r is None:
            print(f"No data found for right face of section {section} in core {core}")
        else:
            self.right = r
        if o is None:
            print(f"No data found for opposite face of section {section} in core {core}")
        else:
            self.opposite = o

    def get_angles(self,angle):

        # pull out angles
        angle_row = angle.loc[angle['section'] == self.section]
        self.top_angle = angle_row['top_angle'].values[0]
        self.left_angle = angle_row['left_angle'].values[0]
        self.right_angle = angle_row['right_angle'].values[0]
        self.side_angle = angle_row['side_angle'].values[0]

    def add_3d_coords(self,top_loc='wide'):

        # TOP
        if not hasattr(self, 'top'):
            print("The 'top' face does not exist for this core section.")
        else:
            y_t = self.top.y_s * 0
            if top_loc == 'wide':
                x_t_0 = (self.top.y_right+self.top.y_left)/2
            elif top_loc == 'tr':
                x_t_0 = 0
            x_t = (self.top.y_s - x_t_0) * -1
            self.top.add_3d_to_face(x_t/1000,y_t/1000)
        
        # LEFT
        if not hasattr(self, 'left'):
            print("The 'left' face does not exist for this core section.")
        else:
            x_l = self.left.y_s * 0
            y_l = (self.left.y_s - self.left.y_right) * -1
            self.left.add_3d_to_face(x_l/1000,y_l/1000)

        # RIGHT
        if not hasattr(self, 'right'):
            print("The 'right' face does not exist for this core section.")
        else:
            x_r = self.right.y_s * 0
            y_r = (self.right.y_s -  self.right.y_left)
            self.right.add_3d_to_face(x_r/1000,y_r/1000)

        # Opposite
        if not hasattr(self, 'opposite'):
            print("The 'opposite' face does not exist for this core section.")
        else:
            y_o = self.opposite.y_s * 0
            x_o_0 = (self.opposite.y_right+self.opposite.y_left)/2
            x_o = (self.opposite.y_s - x_o_0)
            self.opposite.add_3d_to_face(x_o/1000,y_o/1000)

    def to_df(self):

        # create empty dataframe
        df_full = pd.DataFrame()

        faces = []
        if  hasattr(self, 'opposite'):
            faces.append(self.opposite)
        if hasattr(self, 'top'):
            faces.append(self.top)
        if hasattr(self, 'left'):
            faces.append(self.left)
        if hasattr(self, 'right'):
            faces.append(self.right)

        # loop through faces
        for f in faces:
            
            # create empty dataframe
            df = pd.DataFrame()

            # add top data
            df['mid_depth'] = f.depth_s
            df['top_depth'] = f.depth_s
            df['bottom_depth'] = f.depth_s
            if self.ACorDC == 'AC':
                df['AC_ecm'] = f.meas_s
            else:
                df['DC_ecm'] = f.meas_s
            df['effective_center_x'] = f.x_3d
            df['effective_center_y'] = f.y_3d
            df['x_lo'] = f.x_3d
            df['x_hi'] = f.x_3d
            df['y_lo'] = f.y_3d
            df['y_hi'] = f.y_3d

            # add section and face
            df['section'] = self.section
            df['stick'] = f.face
            df['core'] = self.core

            # add df to df_full
            df_full = pd.concat([df_full,df],ignore_index=True)

        return df_full

    # def to_df(self):

    #     # create empty dataframe
    #     df_full = pd.DataFrame()

    #     faces = []
    #     if  hasattr(self, 'opposite'):
    #         faces.append(self.opposite)
    #     if hasattr(self, 'top'):
    #         faces.append(self.top)
    #     if hasattr(self, 'left'):
    #         faces.append(self.left)
    #     if hasattr(self, 'right'):
    #         faces.append(self.right)

    #     # loop through faces
    #     for f in faces:
            
    #         # create empty dataframe
    #         df = pd.DataFrame()

    #         # add top data
    #         df['mid_depth'] = f.depth_s
    #         df['top_depth'] = f.depth_s
    #         df['bottom_depth'] = f.depth_s
    #         if self.ACorDC == 'AC':
    #             df['AC_ecm'] = f.meas_s
    #         else:
    #             df['DC_ecm'] = f.meas_s
    #         df['effective_center_x'] = f.x_3d
    #         df['effective_center_y'] = f.y_3d
    #         df['x_lo'] = f.x_3d
    #         df['x_hi'] = f.x_3d
    #         df['y_lo'] = f.y_3d
    #         df['y_hi'] = f.y_3d

    #         # add section and face
    #         df['section'] = self.section
    #         df['stick'] = f.face
    #         df['core'] = self.core

    #         # add df to df_full
    #         df_full = pd.concat([df_full,df],ignore_index=True)

    #     return df_full
    

#%% Test

if __name__ == "__main__":

    # TEST ECM
    
    #test = ECM('alhic2201','10_1','t','AC')
    test = ECM('alhic1901','228_4','t','AC')
    
    test.smooth(1)
    
    test.rem_ends(1)
    
    test.smooth(1)
    
    #test.norm_outside()
    
    test.norm_all()

    window = 1
    meta = pd.read_csv(path_to_data+metadata)
    # TEST SECTION 
    data = []
    cores = []
    sections = []
    faces = []
    ACorDCs = []
    for index, row in tqdm(meta.iterrows(), total=len(meta), desc="Processing data"):
        
        core = row['core']
            
        section = row['section']
        face = row['face']
        ACorDC = row['ACorDC']

        data_item = ECM(core,section,face,ACorDC)
        print("Reading "+core+", section "+section+'-'+face+'-'+ACorDC)
        
        data_item.rem_ends(15)
        data_item.smooth(window)
        data.append(data_item)
        
        cores.append(core)
        sections.append(section)
        faces.append(face)
        ACorDCs.append(ACorDC)

    s228_4 = core_section('228_4','alhic1901','AC',data,sections,faces,cores,ACorDCs)
    print("Core section success")
    
    s228_4.add_3d_coords()
    print("3D coordinates success")

    df = s228_4.to_df()
    print(df.head)
    print("Dataframe success")


    
# %%
