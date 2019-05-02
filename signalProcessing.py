# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 17:39:54 2019
@author: rocke

This file contains all of the classes and function for further processing the signal
after the average of the 8 leads has been created and the baseline drift has been removed
The final stage of this file is to attempy to find the PQRST sections
"""

import matplotlib.pyplot as plt # To plot Graphs of data
import os # Needed for folders
import numpy as np
import math
import scipy.signal as signal # For peak detection


class PeakValleyDetection:
    
    # TODO - Try and use signal_peaks inside of this to try to calculate if the r peaks stayed the same...
    # To try and find P, T Peaks (Will also re-find r peaks)
    # Looks for peaks based on individual beats and saves this to an array to show as whole ECG again
    # Will not find individuals P and T sections if they have certain heart disorders. 
    def findPeaks(averaged_ecg_data, start_end_of_beats, folder_location, file_name):
        
        p_segment_indexs = []
        p_segment_peaks = [] 
        r_segment_indexs = []
        r_segment_peaks = []
        t_segment_indexs = []
        t_segment_peaks = []
        
        # To hold the last place indexed
        last_index = 0
        
        # FOR naming graphs
        counter = 0
        
        # Get the mean to find the height we are looking for the peaks at
        mean_of_data = Util.calculateMeanOfData(averaged_ecg_data)
        
        # Slice Array with point A and B (Start and end of the beat) and try to find 3 peaks
        for index in start_end_of_beats:
            # If index == 0, skip
            if index != 0:
                # Finding peaks which have a width of 3 and are at a distance of 30 datapoints away from each other
                signal_peaks = signal.find_peaks(averaged_ecg_data[last_index:index], height=mean_of_data[0], width=3, distance = 30)
                
                # Counter to keep track of signal_peaks[0] compared to signal_peaks[1]['peak_heights']
                signal_peaks_counter = 0
                
                # Because we sliced the array, the index's are incorrect. We need to add the original index to the numbers first
                # We will append to the array at the same time
               # for slicedIndex in signal_peaks[0]:
                   # prtSectionIndexs.append(last_index + slicedIndex)
                
                p_segment = 0
                p_segment_index = 0
                q_segment = 0
                q_segment_index = 0
                r_segment = 0
                r_segment_index = 0
                s_segment = 0
                s_segment_index = 0
                t_segment = 0
                t_segment_index = 0
                    
                # Apply a filter to sort the peaks (Based on height)
                for section_peaks in signal_peaks[1]['peak_heights']:
                    # r peaks are always above 400. Peaks are returned in order. Cannot be after t_segment. Cannot have duplicates as heart beat should have this in the middle
                    if section_peaks >= 400 and t_segment == 0 and r_segment == 0: 
                        print("Appending r Peak")
                        # Set r segment height and position
                        r_segment = section_peaks
                        r_segment_index = signal_peaks[0][signal_peaks_counter]
                        # Add r segment to array for whole ecg
                        r_segment_peaks.append(r_segment)
                        # Need to add last index because this is only 1 heartbeat out of the whole ecg
                        r_segment_indexs.append(last_index + r_segment_index)
                        
                        # TODO New as of 04:21 - 02/05/29
                        
                        # Index of the current r Peak
                        r_peak_index = signal_peaks[0][signal_peaks_counter]
                        print("R PEAK INDEX ! " + r_peak_index)
                        ecg_data_heartbeat_slice = averaged_ecg_data[last_index:index]
                        
                        s_segment_parts = PeakValleyDetection.findValleys(mean_of_data, r_peak_index, ecg_data_heartbeat_slice, signal_peaks, signal_peaks_counter, folder_location, file_name + " BEAT " + str(counter + 1))
                        s_segment = s_segment_parts[0]
                        s_segment_index = s_segment_parts[1]
                        # TODO VERY IMPORTANT! REMEMBER THAT THE Q SECTION IS FLIPPED AND MUST BE FLIPPED BACK ;)
                        
                        
                        # Experimental 2:40 am 27/04 TODO
                        # Use r as a basis to find q and s
                        # r is always found :)
                        # My own valley finding algorithm (From r peaks)
                        
                        # TODO - turn this into a find valley function and call it - SImples
                        # Set it up to be less than the mean of data to start with (thats the beggining threshold anyway)
                        s_segment_to_test = mean_of_data[0]
                        data_to_search_in = averaged_ecg_data[last_index:index]
                        break_counter = 0
                        # TODO BAD WAY TO DO THIS. FIND START OF r PROPERLY! DONT BE A MORON.
                        todo = int(len(data_to_search_in) / 2)
                        todo = signal_peaks[0][signal_peaks_counter]
                        
                        s_segment_search_counter = 0
                        # Find index of r peak to start search
                        for s_segment_search in data_to_search_in[todo : ]:
                            # S Segment will always be below mean_of_data
                            if s_segment_search < mean_of_data[0]:
                                # Get positive number (if negative then it will be double negative so will turn positive)
                                if (s_segment_search) - (s_segment_to_test) < 0:
                                    s_segment_to_test = s_segment_search
                                    s_segment_search_counter += 1
                                elif break_counter != 1:
                                    # I think we found the S Segment
                                    # TODO For testing purposes only
                                    s_segment = s_segment_to_test
                                    s_segment_index = todo + s_segment_search_counter
                                    break_counter = 1
                                    #print('s_segment_search (' + str(s_segment_search) + ') - s_segment_to_test (' + str(s_segment_to_test) + ') = ' + str((s_segment_search) - (s_segment_to_test)))
                                    plt.plot(data_to_search_in, '-', todo + s_segment_search_counter, s_segment_to_test, 'ro')
                                    plt.legend(['ECG Signal', 'P Peak'], loc='best')
                                    plt.text(0.5, 0.5, 'Peak Detection Cutoff Height = ' + str(mean_of_data[0]))
                                    plt.title('Single Beat PRT-Peaks Plotted Against ECG Data', fontsize = 20)
                                    folder_to_save_to = folder_location +'/Graphs/Hopefully the S Segment/'
                                    # Make sure directory exists to save file to
                                    Util.saveGraph(folder_to_save_to, file_name + " BEAT " + str(counter + 1)) 
                 
                            # Counter needs incrementing anyway
                            else:
                                s_segment_search_counter += 1
                        
                        q_segment_to_test = mean_of_data[0]
                        array_ready_for_reverse = averaged_ecg_data[last_index:index]
                        data_to_search_in = array_ready_for_reverse[::-1]
                        break_counter = 0
                        # TODO BAD WAY TO DO THIS. FIND START OF r PROPERLY! DONT BE A MORON.
                        todo = signal_peaks[0][signal_peaks_counter]
                        
                        q_segment_search_counter = 0
                        # Find index of r peak to start search
                        for q_segment_search in data_to_search_in[todo : ]:
                            # S Segment will always be below mean_of_data
                            if q_segment_search < mean_of_data[0]:
                                # Get positive number (if negative then it will be double negative so will turn positive)
                                if (q_segment_search) - (q_segment_to_test) < 0:
                                    q_segment_to_test = q_segment_search
                                    q_segment_search_counter += 1
                                elif break_counter != 1:
                                    # I think we found the S Segment
                                    # TODO For testing purposes only
                                    q_segment = q_segment_to_test
                                    q_segment_index = len(data_to_search_in) - (todo + q_segment_search_counter)
                                    break_counter = 1
                                    #print('q_segment_search (' + str(q_segment_search) + ') - q_segment_to_test (' + str(q_segment_to_test) + ') = ' + str((q_segment_search) - (q_segment_to_test)))
                                    plt.plot(data_to_search_in, '-', todo + q_segment_search_counter, q_segment_to_test, 'ro')
                                    plt.legend(['ECG Signal', 'P Peak'], loc='best')
                                    plt.text(0.5, 0.5, 'Peak Detection Cutoff Height = ' + str(mean_of_data[0]))
                                    plt.title('Single Beat PRT-Peaks Plotted Against ECG Data', fontsize = 20)
                                    folder_to_save_to = folder_location +'/Graphs/Hopefully the Q Segment/'
                                    # Make sure directory exists to save file to
                                    Util.saveGraph(folder_to_save_to, file_name + " BEAT " + str(counter + 1)) 
                 
                            # Counter needs incrementing anyway
                            else:
                                q_segment_search_counter += 1
                                
                    # t peak has to come after r peak - r peak is always found. Only allow if rpeak != 0
                    elif section_peaks < 400 and r_segment != 0: 
                        print("Appending t Peak")
                        # Set t segment height and position
                        t_segment = section_peaks
                        t_segment_index = signal_peaks[0][signal_peaks_counter]
                        # Add t segment to array for whole ecg
                        t_segment_peaks.append(t_segment)
                        # Need to add last index because this is only 1 heartbeat out of the whole ecg
                        t_segment_indexs.append(last_index + t_segment_index)
                    # p peak has to come before r segment.
                    elif section_peaks < 400 and r_segment == 0:
                        print("Appending p Peak")
                        # Set p segment height and position
                        p_segment = section_peaks
                        p_segment_index = signal_peaks[0][signal_peaks_counter]
                        # Add p segment to array for whole ecg
                        p_segment_peaks.append(p_segment)
                        # Need to add last index because this is only 1 heartbeat out of the whole ecg
                        p_segment_indexs.append(last_index + p_segment_index)
                    
                    # Look for peaks around next R Peak
                    signal_peaks_counter += 1
                #prsSectionPeaks.extend(signal_peaks[1]['peak_heights'])
                
                # For testing only - Remove if not neede for plot TODO
                x = []
                y = []
                c = 0
                for d in averaged_ecg_data:
                    x.append(c)
                    c+=1
                # TODO For testing purposes only
                plt.plot(averaged_ecg_data[last_index:index], '-', x[q_segment_index:s_segment_index], averaged_ecg_data[q_segment_index:s_segment_index], 'y-', p_segment_index, p_segment, 'ro', q_segment_index, q_segment, 'co', r_segment_index, r_segment, 'bo', s_segment_index, s_segment, 'mo', t_segment_index, t_segment, 'go')
                plt.legend(['ECG Signal', 'QRS Segment', 'P Peak', 'Q Valley', 'R Peak', 'S Valley', 'T Peak'], loc='best')
                plt.text(0.5, 0.5, 'Peak Detection Cutoff Height = ' + str(mean_of_data[0]))
                plt.title('Single Beat PRT-Peaks Plotted Against ECG Data', fontsize = 20)
                folder_to_save_to = folder_location +'/Graphs/Part 5 - Individual Heart Beats Plotted Against PRT-Peaks/'
                # Make sure directory exists to save file to
                Util.saveGraph(folder_to_save_to, file_name + " BEAT " + str(counter + 1)) 
                counter += 1
                
                # Change the last index to be the current index
                last_index = index
        
        # Adding the averaged_ecg_data to the graph
        plt.plot(averaged_ecg_data, '-', p_segment_indexs, p_segment_peaks, 'ro', r_segment_indexs, r_segment_peaks, 'bo', t_segment_indexs, t_segment_peaks, 'go')
        plt.legend(['ECG Signal', 'P Peak', 'R Peak', 'T Peak'], loc='best')
        plt.title('PRT-Peaks Plotted Against ECG Data', fontsize = 20)
        
        folder_to_save_to = folder_location +'/Graphs/Part 6 - PRT-Peaks Plotted Against Averaged ECG Signal With Biological Drift Removed/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folder_to_save_to, file_name) 
    
    
    # A function to find the Q and S valleys which reside at the bottom of the R peak in the QRS Complex
    def findValleys(mean_of_data, r_peak_index, ecg_data_heartbeat_slice, signal_peaks, signal_peaks_counter, folder_location, file_name):
        print("TODO")
        
        #segment_test_number is equal to the mean of the data initially
        segment_test_number = mean_of_data[0]
        break_counter = 0
        
        segment_search_counter = 0
        # Find index of r peak and go to the end of the data to start the search
        # TODO, can i not just pass this value if the "Todo value is fixed rather than sending hearbeat_slice as it is?
        for segment_search in ecg_data_heartbeat_slice[r_peak_index : ]:
            # Q and S Segments should always be below mean_of_data
            if segment_search < mean_of_data[0]:
                # Get positive number (if negative then it will be double negative so will turn positive)
                if (segment_search) - (segment_test_number) < 0:
                    segment_test_number = segment_search
                    segment_search_counter += 1
                elif break_counter != 1:
                        # I think we found the S Segment # TODO issues from here . need to return this data somehow
                        # TODO For testing purposes only
                        segment = segment_test_number
                        segment_index = r_peak_index + segment_search_counter
                        break_counter = 1
                        #print('s_segment_search (' + str(s_segment_search) + ') - segment_test_number (' + str(segment_test_number) + ') = ' + str((s_segment_search) - (s_segment_to_test)))
                        plt.plot(ecg_data_heartbeat_slice, '-', r_peak_index + segment_search_counter, segment_test_number, 'ro')
                        plt.legend(['ECG Signal', 'P Peak'], loc='best')
                        plt.text(0.5, 0.5, 'Peak Detection Cutoff Height = ' + str(mean_of_data[0]))
                        plt.title('Single Beat PRT-Peaks Plotted Against ECG Data', fontsize = 20)
                        folder_to_save_to = folder_location +'/Graphs/Hopefully the S Segment/'
                        # Make sure directory exists to save file to
                        # TODO - call with the counter part already added...
                        Util.saveGraph(folder_to_save_to, file_name) 
                        
                        # Return the segment that was found and it's index
                        return [segment, segment_index]
                # Counter needs incrementing anyway
                else:
                    segment_search_counter += 1
                        
    
    
    # Function to detect peaks in the data.
    # Heart Rate is then calculated from these peaks and is saved into an Excel file
    def findQrsComplex(averaged_ecg_data, folder_location, file_name):
        # Returns 2 arrays. One containing the location of the peaks in the array
        # The other containing the value of the peak # TODO - Shouldnt this height be higher? Probably more like 400? # SHOULD DISTANCE BE 30? (200bpm over 6000 samples = 30) - REFERENCED AS 30 in report
        signal_peaks = signal.find_peaks(averaged_ecg_data, height=200, distance=200)
        print(signal_peaks[0])
        print(signal_peaks[1]['peak_heights'])
        
        # Setup an array with data inside to save to a file
        heart_rate_data_to_save = [[0 for x in range(2)] for y in range(2)] # Initializes array as 2x2 
        heart_rate_data_to_save[0][0] = "Heart Rate"
        heart_rate_data_to_save[0][1] = "Heart Rate Zone"
        
        # Frequency of Welch Allyn System is 600Hz and it runs clinical ECG's for 10 seconds.
        # To get a minute, this needs to be multiplied by 6
        heart_rate = len(signal_peaks[0]) * 6
        # Adding the heartrate to the array
        heart_rate_data_to_save[1][0] = str(heart_rate)
        
        #TODO change Mv on graphs to mV
        
        # Calculates the Heart Rate zone of the participant (Uses 25 year old for calculation)
        heart_rate_zone = Util.calculateHeartRateZone(heart_rate)
        # Adding Heart Rate Zone to array
        heart_rate_data_to_save[1][1] = heart_rate_zone
        print("Participants Heart Rate Is Equal To " + str(heart_rate) + " And Their Heart Rate Zone Is " + heart_rate_zone)
        
        # Save heart rate data to file for user
        Util.saveToCsv(heart_rate_data_to_save, folder_location +'/Results/', file_name + ' Heartrate Results')
        
        # Adding the averaged_ecg_data to the graph
        plt.plot(averaged_ecg_data, '-', signal_peaks[0], signal_peaks[1]['peak_heights'], 'o')
        plt.legend(['ECG Signal', 'R-Peaks'], loc='best')
        plt.title('R-Peaks Plotted Against ECG Data', fontsize = 20)
        plt.text(0.5, 0.5, 'Heart Rate = ' + str(heart_rate))
        
        folder_to_save_to = folder_location +'/Graphs/Part 3 - (R-Peaks Plotted Against Averaged ECG Data With Biological Drift Removed)/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folder_to_save_to, file_name) 
        
        return signal_peaks
    
    
    
class Fft:
    
    # TODO - Do i need running mean datapoints here?
    # Calculate the FFT using the averaged ECG Data
    def calculateFft(averaged_ecg_data, running_mean_datapoints, folder_location, file_name):
        
        # Calculates discrete fourier transform using FFT (fast fourier transform)
        average_ecg_fft = np.fft.fft(averaged_ecg_data)
        
        # This gets the Discrete fourier transforms frequencies
        freq = np.fft.fftfreq(len(averaged_ecg_data))
        
        print('freq = ' + str(freq))
        
        # Below block is copied from here http://scipy-lectures.org/intro/scipy/auto_examples/plot_fftpack.html
        power = np.abs(average_ecg_fft)        
        pos_mask = np.where(freq > 0)
        freqs = freq[pos_mask]
        peak_freq = freqs[power[pos_mask].argmax()]
        average_ecg_fft[np.abs(freq) < peak_freq] = 0
        filtered_sig = np.fft.ifft(average_ecg_fft)
        print("FFT WITH MATH = " + str(average_ecg_fft))
        
        folder_to_save_to = folder_location +'/Graphs/Part 8 - Averaged ECG Data (Drift Removed) As FFT FREQ/'
        plt.plot(average_ecg_fft)
        Util.saveGraph(folder_to_save_to, file_name)
        
        folder_to_save_to = folder_location +'/Graphs/Part 9 - Averaged ECG Data (Drift Removed) As FFT FREQ/'
        plt.plot(filtered_sig)
        Util.saveGraph(folder_to_save_to, file_name)
        
        #plots the freq against the length
        #plt.plot(freq, np.abs(average_ecg_fft))
        #self.saveGraph(folder_to_save_to, file_name)        
        
        
        
class Util:
    
    # Function to make a directory using python to save the graphs to.   
    def saveGraph(folder_to_save_to, file_name):
        try:
            os.mkdir(folder_to_save_to)
            print('The Directory: ' + folder_to_save_to + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folder_to_save_to + ' Already Exists. Saving Data')
        
        # Set X and Y Labels on the plot
        plt.xlabel('Time in 600ths of a second', fontsize = 14)
        plt.ylabel('Amplitude in Mv (Millivolts)', fontsize = 14)
        
        plt.show()
        
        # Save and clear the plot
        # bbox_inches = "tight" is to make sure that the whole of the graph fits within the image
        plt.savefig(folder_to_save_to + file_name + '.png', bbox_inches = "tight")
        plt.cla() # Clear the plot
    
    
    # Method to find the individual beats 
    def findIndividualBeats(averaged_ecg_data, signal_peaks, folder_location, file_name):
        
        # Array to hold the datapoints index's inbetween the peaks - Meaning the end of one beat and the start of the next
        start_of_beat_array = []
        
        # Counter for r sections iterated through
        r_section_counter = 0
        
        # To remember the last section which we visited
        previous_section = 0
        
        # For the amount of peaks that we have, calculate midway point between peaks
        for signal_location in signal_peaks[0]:
            # Add '0' to array because we need to start here (first peak doesnt have an obvious midpoint before it)
            if r_section_counter == 0:
                start_of_beat_array.append(0)
                
                # Set the current section as the previous section
                previous_section = signal_location
                # Add 1 to the counter
                r_section_counter += 1
                
            # Find the midway point between this peak and the last peak and append to array.
            else:
                # Find difference between numbers and then divide by 2 and round up
                midway_point_difference = int(round((signal_location - previous_section) / 2))
                start_of_beat_array.append(signal_location - midway_point_difference)
                
                # if this is the last peak we can add 6000 to array because there are no obvious mid points past this location
                if r_section_counter == len(signal_peaks[0]) - 1:
                    start_of_beat_array.append(len(averaged_ecg_data) - 1)
                
                # Set the current section as the previous section
                previous_section = signal_location
                
                # Set the current section as the previous section
                previous_section = signal_location
                # Add 1 to the counter
                r_section_counter += 1
        
        print("This is the midway Peaks array" + str(start_of_beat_array))
        
        # Find data points at location given by the midwayPeaksArray in order to generate graph
        mid_r_section_values = []
        for index in start_of_beat_array:
            mid_r_section_values.append(averaged_ecg_data[index])
        
        plt.plot(averaged_ecg_data, '-', start_of_beat_array, mid_r_section_values, 'o')
        plt.legend(['Averaged ECG Data - Drift Removed', 'Heart Beat Section Points'], loc='best')
        
        folder_to_save_to = folder_location +'/Graphs/Part 4 - Averaged ECG Data With Drift Removed Plotted With Individual Heart Beat Cuts/'
        Util.saveGraph(folder_to_save_to, file_name)
        
        return start_of_beat_array
        
    
    # Function to find zero crossings in data set
    def findZeroCrossings(averaged_ecg_data, mean_of_data, running_mean_datapoints, folder_location, file_name):
        print("Finding Zero Crossings")
        
        last_data_point = mean_of_data
        
        data_under = 0
        data_over = 0
        
        # To colour the zero crossings differently
        zero_crossings_counter = 0
        zero_crossings_plot_array = []
        
        for data_point in averaged_ecg_data:
            
            zero_crossings_counter += 1
            zero_crossings_plot_array.append(data_point)
            
            # If data has gone above crossing point
            if data_point >= running_mean_datapoints[zero_crossings_counter-1] and last_data_point < running_mean_datapoints[zero_crossings_counter-1]:
                data_over += 1
                
                plt.plot(zero_crossings_plot_array, 'b')
                zero_crossings_plot_array.clear()
                data_over_array = [np.nan] * zero_crossings_counter
                zero_crossings_plot_array.extend(data_over_array)
                
            # If data has gone below crossing point    
            elif data_point < running_mean_datapoints[zero_crossings_counter-1] and last_data_point > running_mean_datapoints[zero_crossings_counter-1]:
                data_under += 1
                # TODO - Testing 
                plt.plot(zero_crossings_plot_array, 'r')
                zero_crossings_plot_array.clear()
                data_under_array = [np.nan] * zero_crossings_counter
                zero_crossings_plot_array.extend(data_under_array)
                
                
                
            last_data_point = data_point # Set last datapoint to this data point
        
        print('Data Over = ' + str(data_over) + ' And Data Under = ' + str(data_under))
        
        # plt.plot(averaged_ecg_data) # Plot ecg data
        
        # Is this needed?
        y = []
       
        for x in range(1, 6001):
            y.append(x)
        
        # blah = interp1d(running_mean_datapoints, y, kind='cubic')
        
        plt.plot(running_mean_datapoints)
        
        # To add the mean of the data to the graph
        plt.plot(np.repeat(mean_of_data, len(averaged_ecg_data)))
        
        folder_to_save_to = folder_location +'/Graphs/ECG Data plotted against Moving Point Average/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folder_to_save_to, file_name)
        
        #Probably remove from here and put elsewhere......
        #Fft.calculateFft(averaged_ecg_data, running_mean_datapoints, folder_location, file_name)
        #for csvData in ecgData:
         #   print("Data = " + str(ecgData))
        
        
    # Function to find the distance between two numbers
    def findDistance(point_one, point_two):
        # If the two points are exactly the same, return 0
        if (point_one == point_two):
            return 0
        
        # If both pointOne and pointTwo are above or below 0
        elif ((point_one > 0) and (point_two > 0)) or ((point_one < 0) and (point_two < 0)):
            # absolute turns negative number into positive numbers
            # If point one is greater than point two, Find the absolute value of pointOne - pointTwo 
            # and return it as a negative
            if (point_one > point_two):
                return -(abs(abs(point_one) - abs(point_two)))
            # If pointTwo is greater than pointOne, do the same but return as a positive
            else:
                return (abs(abs(point_one) - abs(point_two)))
        
        # If one point is above zero but the other point is below zero
        else:
            # Return the two points added together with the signature of point 2
            return math.copysign((abs(point_one) + abs(point_two)),point_two)
        
        
    # Formats and saves data to a CSV File
    def saveToCsv(data_to_save, folder_to_save_to, file_name):
        # Try to make a folder (Stops errors)
        try:
            os.mkdir(folder_to_save_to)
            print('The Directory: ' + folder_to_save_to + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folder_to_save_to + ' Already Exists. Saving Data')
        
        # Allow for file to be saved
        np.savetxt(folder_to_save_to + file_name + ".csv", data_to_save, delimiter=",", fmt='%s')
        
    
    # Function to make sure that the three folders (Graphs, Results and CSV Formatted) are created.
    # If these are not generated, an error is thrown. This is called right at the start of the program
    def createMainFolders(folder_to_generate_in):
        # Try to make all three folders
        # Graphs folder
        try:
            os.mkdir(folder_to_generate_in + "/Graphs/")
            print('The Directory: ' + folder_to_generate_in + '/Graphs/ Has Been Created.')
        except:
            print('The Directory: ' + folder_to_generate_in + '/Graphs/ Already Exists.')
        # Results folder
        try:
            os.mkdir(folder_to_generate_in + "/Results/")
            print('The Directory: ' + folder_to_generate_in + '/Results/ Has Been Created.')
        except:
            print('The Directory: ' + folder_to_generate_in + '/Results/ Already Exists.')
        # 
        try:
            os.mkdir(folder_to_generate_in + "/CSV Formatted/")
            print('The Directory: ' + folder_to_generate_in + '/CSV Formatted/ Has Been Created.')
        except:
            print('The Directory: ' + folder_to_generate_in + '/CSV Formatted/ Already Exists.')
        
        
    # Function that just calculates the mean of data.
    # Returns an array with 6000 datapoints of the mean of data for plotting on a graph
    def calculateMeanOfData(averaged_ecg_data):
        
        ecg_mean = 0.0
        ecg_mean_counter = 0
        
        for data in averaged_ecg_data:
            ecg_mean += data
            ecg_mean_counter += 1
            
        mean_of_data = [ecg_mean / ecg_mean_counter] * 6000
        print("Mean of averaged_ecg_data = " + str(mean_of_data[0]))
        
        return mean_of_data
    
    # TODO Explain how this only shows heart rate zones for a 25 year old (Will not work for other ages)
    # Even then its a guestimate. 
    # TODO - EXCERCISE ZONES TAKEN FROM HERE - https://commons.wikimedia.org/wiki/File:Exercise_zones.png
    # Calculates Heart Rate Zone
    def calculateHeartRateZone(heart_rate):
        
        heart_rate_zone = ""
        
        if heart_rate <= 80:
            heart_rate_zone = "Resting"
        elif heart_rate > 80 and heart_rate <= 98:
            heart_rate_zone = "Walking/Moving"
        elif heart_rate > 98 and heart_rate <= 117:
            heart_rate_zone = "Maintenance/Warm Up"
        elif heart_rate > 117 and heart_rate <= 137:
            heart_rate_zone = "Weight Control (Fitness/Fat Burn)"
        elif heart_rate > 137 and heart_rate <= 156:
            heart_rate_zone = "Aerobic Zone (Cardio Training/Endurance)"
        elif heart_rate > 156 and heart_rate <= 176:
            heart_rate_zone = "Anaerobic Zone"
        elif heart_rate > 176 and heart_rate <= 195:
            heart_rate_zone = "VO2 Max (Maximum Effort)"
            
        return heart_rate_zone
    #__init__.py