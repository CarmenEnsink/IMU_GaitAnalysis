# -*- coding: utf-8 -*-
"""
Script to read c3d markerdata

Version:
    2022-01-20: C.J. Ensink - add analog data
    2022-12-23: Bart Nienhuis
"""

import c3d
# from VICON_functions import c3d
import numpy as np
# import tkinter as tk
# from tkinter import filedialog

# # diverse modules om te kunnen plotten  
# import matplotlib.pyplot as plt
# from matplotlib.textpath import TextPath
# from matplotlib.patches import Rectangle, PathPatch
# import mpl_toolkits.mplot3d.art3d as art3d
# from matplotlib.transforms import Affine2D

def readmarkerdata (filepath, **kwargs):
    
    # definieeer een reader opject welke velden er zijn kun je terug vinden en de c3d.py file
    reader = c3d.Reader(open(filepath, 'rb'))

    #  voorbeeld: lees het aantal analoge frames per marker frame.  Analog sample frequentie is vaak 1000 Hz 
    #  deze waarde is dat 10 als de marker sample frequentie 100 Hz is  
    # analog_per_frame=reader.header.analog_per_frame
    # print(analog_per_frame)

    # De marker labels zitten in een apparte groep in de c3D file deze kun uitlezen m.b.v. het point_labels veld 
    # De volgorde van de labels is dezelfde als de volgorde in de markerdata.
    markerlabels=reader.point_labels
    # print(labels)
    
    # Check of er anologe data (forceplates) aanwezig is.
    try:
        analog_labels = list(reader.analog_labels)
        # analog_labels=(reader.groups['ANALOG'].params['LABELS'].bytes).decode("utf-8")
    except (KeyError, AttributeError) as error:
        analog_labels = list(['None Available'])
    
    # Verwijder de hele rij met spaties uit de labelnaam
    for i in range(0,len(analog_labels)):
        analog_labels[i] = analog_labels[i].replace(" ","")
    # analoglabels=[]
    # dotloc = np.array([],dtype=int)
    # for label in range(0,len(analog_labels)):
    #     for char in range(0,len(analog_labels[label])):
    #         if analog_labels[label][char] == '.':
    #             dotloc = np.append(dotloc, char)
        
    # for i in range(0,len(dotloc)):
    #     lastuppercase_beforedot = [idx for idx in range(0,dotloc[i]) if analog_labels[i][idx].isupper()][-1]
    #     try:
    #         firstspace_afterdot = [idx for idx in range(dotloc[i],len(analog_labels[i])) if analog_labels[i][idx] == " "][1]
    #     except IndexError:
    #         firstspace_afterdot = len(analog_labels[i])
        
    #     # if dotloc[i] < dotloc[-1]:
    #     #     if firstspace_afterdot > dotloc[i+1]:
    #     #         firstspace_afterdot = [idx for idx in range(dotloc[i],len(analog_labels[i])) if analog_labels[i][idx].isupper()][1]
                
    #     label = analog_labels[i][lastuppercase_beforedot : firstspace_afterdot]
    #     analoglabels.append(label)

    # Dit zijn de lists waarin de makerdata en analog_data  worden ingelezen
    markerdata_list=[]
    analog_data_list=[]
    analog_per_frame = reader.header.analog_per_frame
    analog_count = reader.header.analog_count

    for i, points, analog in reader.read_frames():
    #            frames : sequence of (frame number, points, analog)
    #            This method generates a sequence of (frame number, points, analog)
    #            tuples, one tuple per frame. The first element of each tuple is the
    #            frame number. The second is a numpy array of parsed, 5D point data
    #            and the third element of each tuple is a numpy array of analog
    #            values that were recorded during the frame. (Often the analog data
    #            are sampled at a higher frequency than the 3D point data, resulting
    #            in multiple analog frames per frame of point data.)
    #
    #            The first three columns in the returned point data are the (x, y, z)
    #            coordinates of the observed motion capture point. The fourth column
    #            is an estimate of the error for this particular point, and the fifth
    #            column is the number of cameras that observed the point in question.
    #            Both the fourth and fifth values are -1 if the point is considered
    #            to be invalid.
          
        points2=points[:,0:3] # lees alleen de x,y,z, cordinaat 
        markerdata_list.append(points2.T)

        #  LET OP voor de analoge moet de matrix gereshaped worden en dat hangt af van het aantal analoge kanalen in de C3D file
        try:
            # analog_data_list.append(analog.reshape(analog_per_frame, int(analog_count/analog_per_frame)))
            analog_data_list.append(np.transpose(analog))
        except ZeroDivisionError:
            # print('No analog data available')
            continue
        except:
            # print('Failed to read analog data')
            continue
        
        
    
    # maak van de twee list numpy array
    marker_data=np.stack(markerdata_list, axis=2)
    try:
        analog_data=np.vstack(analog_data_list)   
    except ValueError: # Empty analog_data_list
        analog_data=np.array([]) 
    
    markerdata = dict()
    # Sla merkerdata op onder label naam
    for i in range(0, len(markerlabels)):
            marker_x = marker_data[0,i,:]
            marker_y = marker_data[1,i,:]
            marker_z = marker_data[2,i,:]
            # vars()[labels[i].split(' ')[0]] = np.transpose(np.array([marker_x, marker_y,marker_z]))
            markerdata[markerlabels[i].split(' ')[0]] = np.transpose(np.array([marker_x, marker_y,marker_z]))
    
    analogdata=dict()
    try:
        for i in range(0,len(analog_labels)):
            analogdata[analog_labels[i]] = analog_data[:,i]
    except IndexError:
        analogdata[analog_labels[i]] = np.array([])
    
    # ParameterGroup = reader.groups #['EVENT']
    fs_markerdata = reader.header.frame_rate #100
    
    opt = False
    for key, value in kwargs.items():
        if key == 'analogdata' and value == True:
            opt = True
        elif key == 'analogdata' and value == False:
            opt = False
    
    if opt == True:
        return markerdata, fs_markerdata, analogdata #ParameterGroup, 
    elif opt == False:
        return markerdata, fs_markerdata #ParameterGroup, 
        
    # fig1 = plt.figure()
    # ax3 = fig1.add_subplot(111, projection='3d') 
    # #
    # marker1_x = marker_data[0,0,:]
    # marker1_y = marker_data[1,0,:]
    # marker1_z = marker_data[2,0,:]

    # marker2_x = marker_data[0,1,:]
    # marker2_y = marker_data[1,1,:]
    # marker2_z = marker_data[2,1,:]
    
    # marker3_x = marker_data[0,2,:]
    # marker3_y = marker_data[1,2,:]
    # marker3_z = marker_data[2,2,:]
        
    # # plot de drie markers in een 3D plot
    # ax3.scatter(marker1_x,marker1_y,marker1_z, c='r', marker='o')   
    # ax3.scatter(marker2_x,marker2_y,marker2_z, c='g', marker='o')      
    # ax3.scatter(marker3_x,marker3_y,marker3_z, c='m', marker='o')      


    # ## Position graph x, y z
    # plt.style.use('classic')
    # plt.rcParams['font.size'] =8.0
    # example_3D_plot, axarr=plt.subplots(3, sharex=True)
    # example_3D_plot.subplots_adjust(hspace=0.4)
    
    # l1,=axarr[0].plot(marker1_x)
    # axarr[0].set_title('X')
    # axarr[0].set_ylabel('mm')
    # l2,=axarr[1].plot(marker1_y)
    # axarr[1].set_title('Y')
    # axarr[1].set_ylabel('mm')
    # l3,=axarr[2].plot(marker1_z)
    # axarr[2].set_title('Z')
    # axarr[2].set_ylabel('mm')
    
    # plt.show()