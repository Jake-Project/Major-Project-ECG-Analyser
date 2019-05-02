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
    
    # To try and find P, T Peaks (Will also re-find r peaks)
    # Looks for peaks based on individual beats that have been taken as a slice out of the signal array 
    # and saves this to the array to show as whole ECG again
    # Looks for Q and S valleys based off of the R Peak 
    def findPeaks(averaged_ecg_data, start_end_of_beats, folder_location, file_name):
        
        p_segment_indexs = []
        p_segment_peaks = [] 
        q_segment_indexs = []
        q_segment_peaks = []
        r_segment_indexs = []
        r_segment_peaks = []
        s_segment_indexs = []
        s_segment_peaks = []
        t_segment_indexs = []
        t_segment_peaks = []
        
        # To hold the last place indexed
        last_index = 0
        
        # For naming graphs
        counter = 0
        
        # Get the mean to find the height we are looking for the peaks at
        mean_of_data = Util.calculateMeanOfData(averaged_ecg_data)
        
        # Slice Array with point A and B (Start and end of the beat) and try to find 3 peaks
        for index in start_end_of_beats:
            # If index == 0, skip
            if index != 0:
                # Finding peaks which have a width of 3 and are at a distance of 30 datapoints away 
                # from each other
                signal_peaks = signal.find_peaks(averaged_ecg_data[last_index:index], height=mean_of_data[0], 
                                                 width=3, distance = 30)
                
                # Counter to keep track of signal_peaks[0] compared to signal_peaks[1]['peak_heights']
                signal_peaks_counter = 0
                
                # Because we sliced the array, the index's are incorrect. We need to add the original index 
                # to the numbers first. We will append to the array at the same time
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
                    # r peaks are always above 400. Peaks are returned in order. Cannot be after t_segment. 
                    # Cannot have duplicates as heart beat should have this in the middle
                    if section_peaks >= 400 and t_segment == 0 and r_segment == 0: 
                        print("Appending r Peak")
                        # Set r segment height and position
                        r_segment = section_peaks
                        r_segment_index = signal_peaks[0][signal_peaks_counter]
                        # Add r segment to array for whole ecg
                        r_segment_peaks.append(r_segment)
                        # Need to add last index because this is only 1 heartbeat out of the whole ecg
                        r_segment_indexs.append(last_index + r_segment_index)
                        
                        # Index of the current r Peak - We know this because its just been saved as this
                        r_peak_index = signal_peaks[0][signal_peaks_counter]
                    
                        ecg_data_heartbeat_slice = averaged_ecg_data[last_index:index]
                        
                        # Call a valley finding algorithm to find the s segment
                        s_segment_parts = PeakValleyDetection.findValleys(mean_of_data, r_peak_index, 
                                                                          ecg_data_heartbeat_slice, 
                                                                          signal_peaks, signal_peaks_counter, 
                                                                          folder_location + '/Graphs/Part 8 - Singular Heart Beats With S Valleys/', 
                                                                          file_name + " BEAT " + str(counter + 1))
                        # May return None if nothing is found
                        # Save data to array for graph
                        if s_segment_parts != None:
                            s_segment = s_segment_parts[0]
                            s_segment_peaks.append(s_segment)
                            s_segment_index = s_segment_parts[1]
                            # Need to append the overall counter as this is just a slice of the signal
                            s_segment_indexs.append(s_segment_index + last_index)
                        
                        # Call a valley finding algorithm to find the q segment
                        # This data is flipped around so that the same function can be used 
                        # as the q section is before the r section
                        ecg_data_heartbeat_slice = averaged_ecg_data[last_index:index]
                        ecg_data_heartbeat_slice_reversed = ecg_data_heartbeat_slice[::-1]
                        q_segment_parts = PeakValleyDetection.findValleys(mean_of_data, r_peak_index, 
                                                                          ecg_data_heartbeat_slice_reversed, 
                                                                          signal_peaks, signal_peaks_counter, 
                                                                          folder_location + '/Graphs/Part 9 - Singular Heart Beats With Q Valleys/', 
                                                                          file_name + " BEAT " + str(counter + 1))
                        
                        # May return None if nothing is found
                        if q_segment_parts != None:
                            # Because the array was reversed, the index needs to be inverted
                            # Save to array for graph
                            q_segment = q_segment_parts[0]
                            q_segment_peaks.append(q_segment)
                            q_segment_index = len(ecg_data_heartbeat_slice) - q_segment_parts[1]
                            # Need to append the overall counter as this is just a slice of the signal
                            q_segment_indexs.append(q_segment_index + last_index)
                            
                            print("q_segment: " + str(q_segment))
                            print("q_segment_index: " + str(q_segment_index))
                    
                    # t peak has to come after r peak - r peak is always found. Only allow if rpeak != 0
                    elif section_peaks < 400 and r_segment != 0 and t_segment == 0: 
                        print("Appending t Peak")
                        # Set t segment height and position
                        t_segment = section_peaks
                        t_segment_index = signal_peaks[0][signal_peaks_counter]
                        # Add t segment to array for whole ecg
                        t_segment_peaks.append(t_segment)
                        # Need to add last index because this is only 1 heartbeat out of the whole ecg
                        t_segment_indexs.append(last_index + t_segment_index)
                        
                    # p peak has to come before r segment.
                    elif section_peaks < 400 and r_segment == 0 and p_segment == 0:
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
                
                # For plotting the array
                x = []
                c = 0
                for d in averaged_ecg_data:
                    x.append(c)
                    c+=1
                    
                # Plotting all 5 segments as individual heartbeats to a graph
                plt.plot(averaged_ecg_data[last_index:index], '-', p_segment_index, p_segment, 
                         'ro', q_segment_index, q_segment, 'co', r_segment_index, r_segment, 'bo', 
                         s_segment_index, s_segment, 'mo', t_segment_index, t_segment, 'go')
                
                # Setting the legend for the plot
                plt.legend(['ECG Signal', 'P Peak', 'Q Valley', 'R Peak', 'S Valley', 'T Peak'], 
                           loc='best')
                # Setting the plot title
                plt.title('Single Beat PQRST-Peaks Plotted Against ECG Data', fontsize = 20)
                folder_to_save_to = folder_location +'/Graphs/Part 10 - Individual Heart Beats Plotted Against Found PQRST Sections/'
                # Make sure directory exists to save file to and save the file
                Util.saveGraph(folder_to_save_to, file_name + " BEAT " + str(counter + 1)) 
                
                # Incriment the counter for the name
                counter += 1
                # Change the last index to be the current index
                last_index = index
        
        # Adding the averaged_ecg_data to the graph with all found PQRST Sections
        plt.plot(averaged_ecg_data, '-', p_segment_indexs, p_segment_peaks, 'co', q_segment_indexs, 
                 q_segment_peaks, 'ro', r_segment_indexs, r_segment_peaks, 'bo', s_segment_indexs, 
                 s_segment_peaks, 'mo', t_segment_indexs, t_segment_peaks, 'go')
        # Adding the legend 
        plt.legend(['ECG Signal', 'P Peak', 'Q Valley', 'R Peak', 'S Valley', 'T Peak'], loc='best')
        # Adding the title
        plt.title('PRT-Peaks Plotted Against ECG Data', fontsize = 20)
        
        folder_to_save_to = folder_location +'/Graphs/Part 11 - PQRST Sections Plotted Against Processed Averaged ECG Signal/'
        
        # Make sure directory exists to save file to and save the graph
        Util.saveGraph(folder_to_save_to, file_name) 
        
        # Calculate the PQRST sections in seconds rather than samples and save to Excel + graph
        Util.pqrstToSeconds(p_segment_indexs, q_segment_indexs, r_segment_indexs, s_segment_indexs, 
                              t_segment_indexs, folder_location, file_name) 
    
    # A function to find the Q and S valleys which reside at the bottom of the R peak in the QRS Complex
    def findValleys(mean_of_data, r_peak_index, ecg_data_heartbeat_slice, signal_peaks, signal_peaks_counter, 
                    folder_location, file_name):
        
        # segment_test_number is equal to the mean of the data initially
        # This changes to be the most recent data that we are testing
        segment_test_number = mean_of_data[0]
        # Stops the if statement from running after valley has been found
        break_counter = 0
        
        segment_search_counter = 0
        
        # Find index of r peak inside of the dataset and use data between here and the end for the search
        for segment_search in ecg_data_heartbeat_slice[r_peak_index : ]:
            # Q and S Segments should always be below mean_of_data
            if segment_search < mean_of_data[0]:
                # Get positive number (if negative then it will be double negative so will turn positive)
                if (segment_search) - (segment_test_number) < 0:
                    segment_test_number = segment_search
                    segment_search_counter += 1
                elif break_counter != 1:
                        # We found the Q or S Segment
                        # Set the segment and it's index
                        segment = segment_test_number
                        segment_index = r_peak_index + segment_search_counter
                        # Stop this elif  from being called again
                        break_counter = 1
                        # Plot the individual heartbeat and the valley (segment) that was found
                        plt.plot(ecg_data_heartbeat_slice, '-', segment_index, segment, 'ro')
                        plt.legend(['ECG Signal', 'Valley'], loc='best')
                        plt.text(0.5, 0.5, 'Peak Detection Cutoff Height = ' + str(mean_of_data[0]))
                        plt.title('Single Beat PRT-Peaks Plotted Against ECG Data', fontsize = 20)
                        
                        # Make sure directory exists to save file to and save graph
                        Util.saveGraph(folder_location, file_name) 
                                                
                        # Return the segment that was found and it's index
                        return [segment, segment_index]
            # Move on to the next datapoint because we are not below mean yet and increment counter
            else:
                segment_search_counter += 1
    
    
    # Function to detect r-peaks in the data.
    # Heart Rate is then calculated from these peaks and is saved into an Excel file
    # R-Peaks are returned to calculate individual beats
    def findHeartRate(averaged_ecg_data, folder_location, file_name):
        # Returns 2 arrays. One containing the location of the peaks in the array
        # The other containing the value of the peak 
        signal_peaks = signal.find_peaks(averaged_ecg_data, height=400, distance=200)
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
        
        # Calculates the Heart Rate zone of the participant (Uses 25 year old for calculation)
        heart_rate_zone = Util.calculateHeartRateZone(heart_rate)
        # Adding Heart Rate Zone to array
        heart_rate_data_to_save[1][1] = heart_rate_zone
        print("Participants Heart Rate Is Equal To " + str(heart_rate) + " And Their Heart Rate Zone Is " + heart_rate_zone)
        
        # Save heart rate data to file for user
        Util.saveToCsv(heart_rate_data_to_save, folder_location +'/Results/', file_name + ' Heartrate Results')
        
        # Adding the averaged_ecg_data to the graph against r-peaks
        plt.plot(averaged_ecg_data, '-', signal_peaks[0], signal_peaks[1]['peak_heights'], 'o')
        plt.legend(['ECG Signal', 'R-Peaks'], loc='best')
        plt.title('R-Peaks Plotted Against ECG Data', fontsize = 20)
        # Add heartrate to graph
        plt.text(0.5, 0.5, 'Heart Rate = ' + str(heart_rate))
        
        folder_to_save_to = folder_location +'/Graphs/Part 6 - (R-Peaks Plotted Against Averaged ECG Data With Biological Drift Removed)/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folder_to_save_to, file_name) 
        
        return signal_peaks
    
    
    
class Fft:
    
    # Calculate the FFT using the averaged ECG Data
    # Take the FFT data and filter out negatives
    # Block of code taken from http://scipy-lectures.org/intro/scipy/auto_examples/plot_fftpack.html
    # This block has been understood and annotated. The block will start from "# Below Block Is Copied"
    # and run until "#End of copied block"
    # Attempted different filters but all caused more noise.
    def calculateFft(averaged_ecg_data, running_mean_datapoints, folder_location, file_name):
        
        # Calculates discrete fourier transform using FFT (fast fourier transform)
        average_ecg_fft = np.fft.fft(averaged_ecg_data)
        
        # This gets the Discrete fourier transforms frequencies
        freq = np.fft.fftfreq(len(averaged_ecg_data))
        
        #print('freq = ' + str(freq))
        
        # Below Block Is Copied 
        # Get the absolute values for the frequencies which have been found
        power = np.abs(average_ecg_fft)        
        # Returns element where the frequency is greater than 0
        pos_mask = np.where(freq > 0)
        # Returns frequencies found from pos_mask
        freqs = freq[pos_mask]
        # Looks for frequencies that are only positive
        peak_freq = freqs[power[pos_mask].argmax()]
        # Removes frequencies which are less than the peak_freq
        average_ecg_fft[np.abs(freq) < peak_freq] = 0
        # End of copied block
        
        #Converts the frequencies back to timeseries data
        filtered_ecg_signal = np.fft.ifft(average_ecg_fft)
        
        # Saves the none-filtered FFT
        plt.title('Averaged ECG Signal As FFT Frequencies', fontsize = 20)
        folder_to_save_to = folder_location +'/Graphs/Part 3 - Averaged ECG Data (Drift Removed) As FFT Frequencies/'
        plt.plot(average_ecg_fft)
        Util.saveGraph(folder_to_save_to, file_name)
        
        # Saves the filtered FFT
        folder_to_save_to = folder_location +'/Graphs/Part 4 - Averaged ECG Data (Drift Removed) As FFT filtered ECG Signal/'
        plt.title('FFT Filtered Averaged ECG Signal', fontsize = 20)
        plt.plot(filtered_ecg_signal)
        Util.saveGraph(folder_to_save_to, file_name)
        
        # Returns the filtered ecg signal       
        return filtered_ecg_signal
        
        
# A class that contains useful functions that are used throughout the program in multiple classes
class Util:
    
    # Function to make a directory using python to save the graphs to.   
    def saveGraph(folder_to_save_to, file_name):
        # Attempt to make the folder
        try:
            os.mkdir(folder_to_save_to)
            print('The Directory: ' + folder_to_save_to + ' Has Been Created. Saving Data')
        # The folder already exists
        except:
            print('The Directory: ' + folder_to_save_to + ' Already Exists. Saving Data')
        
        # Set X and Y Labels on the plot
        plt.xlabel('Time in 600ths of a second', fontsize = 14)
        plt.ylabel('Amplitude in mV (Millivolts)', fontsize = 14)
        
        plt.show()
        
        # Save the plot
        # bbox_inches = "tight" is to make sure that the whole of the graph fits within the image
        plt.savefig(folder_to_save_to + file_name + '.png', bbox_inches = "tight")
        plt.cla() # Clear the plot
    
    
    # Method to find the individual beats
    # Takes R-Peaks and finds the datapoints inbetween the next and previous R-Peak.
    # Slices at these datapoints and returns where they are
    def findIndividualBeats(averaged_ecg_data, signal_peaks, folder_location, file_name):
        
        # Array to hold the datapoints index's inbetween the peaks - 
        # Meaning the end of one beat and the start of the next
        start_of_beat_array = []
        
        # Counter for r sections iterated through
        r_section_counter = 0
        
        # To remember the last section which we visited
        previous_section = 0
        
        # For the amount of peaks that we have, calculate midway point between peaks
        for signal_location in signal_peaks[0]:
            # Add '0' to array because we need to start here 
            # (first peak doesnt have an obvious midpoint before it)
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
                
                # if this is the last peak we can add 6000 to array because there are no obvious mid points 
                # past this location
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
        
        # Plot the splits on a graph
        plt.title('Averaged ECG Data and Heartbeat Splitting Points', fontsize = 20)
        plt.plot(averaged_ecg_data, '-', start_of_beat_array, mid_r_section_values, 'o')
        plt.legend(['Averaged ECG Data - Drift Removed', 'Heart Beat Section Points'], loc='best')
        
        folder_to_save_to = folder_location +'/Graphs/Part 7 - Averaged ECG Data With Drift Removed Plotted With Individual Heart Beat Cuts/'
        Util.saveGraph(folder_to_save_to, file_name)
        
        return start_of_beat_array
        
    
    # Function to find zero crossings in data set
    # Not used anymore. Attempted to use this to help in this software.
    # Could be used for illustration purposes to show the split in the graph but can do this in other ways now.
    # Such as the drift removal graph which shows the change in data when drift is removed
    def findZeroCrossings(averaged_ecg_data, mean_of_data, running_mean_datapoints, folder_location, file_name):
        print("Finding Zero Crossings")
        
        # Last data point that is checked
        last_data_point = mean_of_data [0]
        
        # Amount of datapoints found over and under
        data_under = 0
        data_over = 0
        
        # To colour the zero crossings differently
        zero_crossings_counter = 0
        zero_crossings_plot_array = []
        
        # Iterate through the data
        for data_point in averaged_ecg_data:
            
            # Add 1 to the counter
            zero_crossings_counter += 1
            # Append the data
            zero_crossings_plot_array.append(data_point)
            
            # If data has gone above crossing point
            if data_point >= running_mean_datapoints[zero_crossings_counter-1] and last_data_point < running_mean_datapoints[zero_crossings_counter-1]:
                # Add one to the counter
                data_over += 1
                
                # Plot on the graph
                plt.plot(zero_crossings_plot_array, 'b')
                #Clear the array because it has gone over the mean
                zero_crossings_plot_array.clear()
                data_over_array = [np.nan] * zero_crossings_counter
                zero_crossings_plot_array.extend(data_over_array)
                
            # If data has gone below crossing point    
            elif data_point < running_mean_datapoints[zero_crossings_counter-1] and last_data_point > running_mean_datapoints[zero_crossings_counter-1]:
                # add one to the counter
                data_under += 1
                # Plot on the graph
                plt.plot(zero_crossings_plot_array, 'r')
                # Clear the array because it has gone under the mean
                zero_crossings_plot_array.clear()
                data_under_array = [np.nan] * zero_crossings_counter
                # Extend the array for a graph
                zero_crossings_plot_array.extend(data_under_array)
                
                
                
            last_data_point = data_point # Set last datapoint to this data point
        
        print('Data Over = ' + str(data_over) + ' And Data Under = ' + str(data_under))

        # Plot the running mean        
        plt.plot(running_mean_datapoints)
        
        # To add the mean of the data to the graph
        plt.plot(np.repeat(mean_of_data, len(averaged_ecg_data)))
        
        folder_to_save_to = folder_location +'/Graphs/ECG Data plotted against Moving Point Average/'
        
        # Make sure directory exists to save file to and save the graph
        Util.saveGraph(folder_to_save_to, file_name)
        
        
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
        # If folder already exists
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
        
        # Create variables to hold total and the counter
        ecg_mean = 0.0
        ecg_mean_counter = 0
        
        # Get total and increment counter
        for data in averaged_ecg_data:
            ecg_mean += data
            ecg_mean_counter += 1
        
        # Calculate mean and add to array
        mean_of_data = [ecg_mean / ecg_mean_counter] * 6000
        print("Mean of averaged_ecg_data = " + str(mean_of_data[0]))
        
        # Return array
        return mean_of_data
    
    # Excercise zone chart used as the main basis - https://commons.wikimedia.org/wiki/File:Exercise_zones.png
    # Calculates Heart Rate Zone (Based on a 25 year old due to my age)
    def calculateHeartRateZone(heart_rate):
        
        # Sets an empty string for the heartrate zone
        heart_rate_zone = ""
        
        # Uses heartrate to calculate which zone the person is in (based on a 25 year old)
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
            
        # Returns the zone
        return heart_rate_zone
    
    
    # Function that finds the PQRST sections in seconds rather than samples. 
    # This data is then saved to a CSV file
    # Amplitude is not saved, only the time at which the segment occured
    def pqrstToSeconds(p_segment_indexs, q_segment_indexs, r_segment_indexs, s_segment_indexs, t_segment_indexs, 
                         folder_to_save_to, file_name): 
        
        # Initializes a multidimensional array
        # If a heart is beating at  200 bpm, the max beats in 1/6th of a minute is 33.3 Make array size 40
        pqrst_data_to_save = [[0 for x in range(5)] for y in range(40)] # Initializes array as 40x5 
        
        # Save the column names
        pqrst_data_to_save[0][0] = "P Waves (Seconds)"
        pqrst_data_to_save[0][1] = "Q Waves (Seconds)"
        pqrst_data_to_save[0][2] = "R Waves (Seconds)"
        pqrst_data_to_save[0][3] = "S Waves (Seconds)"
        pqrst_data_to_save[0][4] = "T Waves (Seconds)"
        
        # For each point that was found
        p_wave_counter, q_wave_counter, r_wave_counter, s_wave_counter, t_wave_counter = [1, 1, 1, 1, 1]
        # Find time in seconds for p waves
        # Welch Allyn system uses 600hz. This means 600 times a second. 
        # To find out how many milliseconds has passed, we divide the index by 600
        for p_index in p_segment_indexs:
            if p_index != 0: # Stops 0's from being added to the csv file
                pqrst_data_to_save[p_wave_counter][0] = str(p_index / 600)
                p_wave_counter +=1
        # For q waves  
        for q_index in q_segment_indexs:
            if q_index != 0:
                pqrst_data_to_save[q_wave_counter][1] = str(q_index / 600)
                q_wave_counter +=1
        # For r waves   
        for r_index in r_segment_indexs:
            if r_index != 0:
                pqrst_data_to_save[r_wave_counter][2] = str(r_index / 600)
                r_wave_counter +=1
        # For S waves    
        for s_index in s_segment_indexs:
            if s_index != 0:
                pqrst_data_to_save[s_wave_counter][3] = str(s_index / 600)
                s_wave_counter +=1
        # For t waves      
        for t_index in t_segment_indexs:
            if t_index != 0:
                pqrst_data_to_save[t_wave_counter][4] = str(t_index / 600)
                t_wave_counter +=1
        
        # Save total waves found for each section
        # R is most reliably found - Use r counter to set where to save this data
        counter_array = [p_wave_counter, q_wave_counter, r_wave_counter, s_wave_counter, t_wave_counter]
        print("Counter array = " + str(counter_array))
        # Save the waves in their proper rows
        for i in range(5):
            pqrst_data_to_save[r_wave_counter + 4][i] = "Total Found"
            pqrst_data_to_save[r_wave_counter + 5][i] = str(counter_array[i] - 1)
            
        # Remove any zeros from array which were created upon initialization
        for x in range(5):
            for y in range(40):
                if pqrst_data_to_save[y][x] == 0:
                    pqrst_data_to_save[y][x] = ""
            
        # Save heart PQRST data to file for user
        Util.saveToCsv(pqrst_data_to_save, folder_to_save_to +'/Results/', file_name + ' PQRST Sections In Seconds')
        print("Saved file: " + folder_to_save_to + "/Results/" + file_name + " PQRST Sections In Seconds")
    #__init__.py