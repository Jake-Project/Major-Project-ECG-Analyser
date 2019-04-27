# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 17:39:54 2019

@author: rocke
"""

# To plot Graphs of data
import matplotlib.pyplot as plt
import os # Needed for folders
from scipy.interpolate import interp1d
import numpy as np
import math


# For peak detection
import scipy.signal as signal

# Class that finds the average of all of the ECG leads
# The class allows for:
#   The average of all 8 signals to be found 
#   The moving average of the signal to be calculated
#   The cubic interpolation of that moving average for a smooth moving average signal rather than square
#   The signal average to have the drift removed which makes the data more uniform
class AverageEcgLeads:
    
    # Function that returns the averaged signal to append to the data
    def createAveragedSignal(charString):
        # print('This is the char array ' + str(charString))
        total = 0.00
        ecgDataInstance = charString.split(",") # Split by the commas and retrieve data as an array to iterate through
        for x in range(1, 9): # Do not include first position in array because this data is not needed
            total += float(ecgDataInstance[x]) # Cast to float and add all of the data together
            # print(total)
        
        averagedSignal = total / 9
        # print("Averaged Signal: " + str(averagedSignal))
        return averagedSignal
    
    # Function that just calculates the mean of data.
    # Returns an array with 6000 datapoints for plotting on a graph
    def calculateMeanOfData(averagedEcgData):
        
        ecgMean = 0.0
        ecgMeanCounter = 0
        
        for data in averagedEcgData:
            ecgMean += data
            ecgMeanCounter += 1
            
        meanOfData = [ecgMean / ecgMeanCounter] * 6000
        print("Mean of averagedEcgData = " + str(meanOfData[0]))
        
        return meanOfData
        
    # Method that takes a mean after n amount of signals have been iterated through
    # This data can then be used with cubic interpolation to create a smooth curve which represents a running mean
    # Amount of signals for mean to be calculated on (runningMeanMaxDatapoints) Should be divisible by 6000
    def calculateRunningMean(averagedSignalData, runningMeanMaxDatapoints):
        
        # Array to hold the running mean datapoints
        runningMeanDatapoints = []
        
        # Variables to calculate the mean
        ecgRunningMean = 0.0
        ecgRunningMeanCounter = 0
        
        # TODO THIS FUNCTION COULD FILL IN THE GAPS USING CUBIC INTERPOLATION!!!!! :D
        
        # Run through all of the data in the averaged signal
        for data in averagedSignalData:
            # Add 1 to the counter and add the averaged signal    
            ecgRunningMean += data
            ecgRunningMeanCounter += 1
        
            # If we have enough datapoints, save the data to the array and reset the counter                
            if ecgRunningMeanCounter == runningMeanMaxDatapoints:
                runningMeanDatapoints.append(ecgRunningMean/ecgRunningMeanCounter)
                ecgRunningMean = 0.0
                ecgRunningMeanCounter = 0
      
        return runningMeanDatapoints
        
    # Function to calculate the cubic spline interpolation of the running average sections of the signal
    def calculateCubicInterpolation(averagedSignalData, runningMeanDatapoints, folderLocation, fileName):
        print("Calculating the Cubic Interpolation of the running mean sections")
        
        y = []
       
        # For the amount of data points in our code - TODO This must be changed to the lenght of meanOfData (Here and below)
        for x in range(1, len(runningMeanDatapoints) + 1):
            y.append(x)
        
        print(len(runningMeanDatapoints))
        print(len(y))
        # X is horizontal (The data point included in the mean of data)
        # Y is vertical (The mean of data that we wish to look at)
        # This returns the interpolation function which we need to make use of
        cubicInterpolatedRepresentation = interp1d(y, runningMeanDatapoints, 'cubic')
        
        xnew = np.arange(1, 15, 0.00233)
        ynew = cubicInterpolatedRepresentation(xnew) 
        
        #TODO CHANGE NAME OF XNEW YNEW
        plt.plot(averagedSignalData)
        plt.plot(ynew)
        #plt.plot(averagedSignalData, 'o', ynew, '--')
        #plt.legend(['Averaged Signal Data', 'Cubic Interpolation Of Running Average Sections'], loc='best')
        
        folderToSaveTo = folderLocation +'/Graphs/Part 1 - (Running Mean Cubic Interpolation Paired With Averaged Signal Data)/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        # Function to find zero crossings for the averaged signal of the dataset using the 
        Util.findZeroCrossings(averagedSignalData, 0, ynew, folderLocation, fileName)
        
        return ynew # TODO WHAT IS yNEW?????
      
    # TODO JAKE REMOVE THIS IF NOT NEEDED (THIS IS TO TEST IF WE CAN GET THE AVERAGED DATA CUBICLY INTERPOLATED)
      # Function to calculate the cubic spline interpolation of the running average sections of the signal
    def calculateCubicInterpolationNumberTwo(averagedSignalData, runningMeanDatapoints, folderLocation, fileName):
        print("Calculating the Cubic Interpolation of the running mean sections")
        
        
        y = []
       
        # For the amount of data points in our code - TODO This must be changed to the lenght of meanOfData (Here and below)
        for x in range(1, len(runningMeanDatapoints) + 1):
            y.append(x)
        
        # X is horizontal (The data point included in the mean of data)
        # Y is vertical (The mean of data that we wish to look at)
        # This returns the interpolation function which we need to make use of
        cubicInterpolatedRepresentation = interp1d(y, runningMeanDatapoints, 'linear')
        
        xnew = np.arange(1, 600, 0.1)
        ynew = cubicInterpolatedRepresentation(xnew)
        
        #TODO CHANGE NAME OF XNEW YNEW
        plt.plot(averagedSignalData, 'r-')
        plt.plot(ynew, 'b-')
        #plt.plot(averagedSignalData, 'o', ynew, '--')
        #plt.legend(['Averaged Signal Data', 'Cubic Interpolation Of Running Average Sections'], loc='best')
        
        folderToSaveTo = folderLocation +'/Graphs/Part 7 - (HAHA)/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        # Function to find zero crossings for the averaged signal of the dataset using the 
        #Util.findZeroCrossings(averagedSignalData, 0, ynew, folderLocation, fileName)
        
        return ynew # TODO WHAT IS yNEW?????
    
    # Method that removes the drift from the averaged ECG signal.
    # Function that will eliminate baseline drift of the biological ECG signal
    def removeDrift(averagedEcgData, runningMeanDatapoints, meanOfDataBeforeDriftRemoval, folderLocation, fileName):
        ecgSignalWithDriftRemoved = []
        print('Length of averaged data = ' + str(len(averagedEcgData)) + '. Length of running mean datapoints' + str(len(runningMeanDatapoints)))
        counter = 0
        
        # THis line is a copy - Make it yours
        runningMeanDatapoints = runningMeanDatapoints[:len(runningMeanDatapoints)-9]

        for data in runningMeanDatapoints:
            
            ecgSignalWithDriftRemoved.append(averagedEcgData[counter] - Util.distance(0, data))
            counter += 1
        
        meanOfDataNow = AverageEcgLeads.calculateMeanOfData(ecgSignalWithDriftRemoved)
        
        plt.plot(ecgSignalWithDriftRemoved, '-', meanOfDataBeforeDriftRemoval, '-', meanOfDataNow, '-', averagedEcgData, '-')
        plt.legend(['Averaged ECG Data - Drift Removed', 'Mean Of Data Before Drift Removal', 'Mean Of Data Now', 'Averaged ECG Data - No Processing'], loc='best')
        
        # Gives gaps inbetween subplots
        plt.tight_layout()
        
        folderToSaveTo = folderLocation +'/Graphs/Part 2 - (Averaged ECG Data (Drift Removed Vs No Processing)/'
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        return ecgSignalWithDriftRemoved
    
    #__init__.py
    
    


class PeakDetection:
    
    # TODO - Try and use signalPeaks inside of this to try to calculate if the r peaks stayed the same...
    # To try and find P, T Peaks (Will also refind r peaks)
    # Looks for peaks based on individual beats and saves this to an array to show as whole ECG again
    # Will not work on individuals with unusual rhythms as the p and t will be off
    def findPeaks(averagedEcgData, startEndOfBeats, folderLocation, fileName):
        
        pSegmentIndexs = []
        pSegmentPeaks = [] 
        rSegmentIndexs = []
        rSegmentPeaks = []
        tSegmentIndexs = []
        tSegmentPeaks = []
        
        # To hold the last place indexed
        lastIndex = 0
        
        # FOR TESTING TODO
        counter = 0
        
        # Get the mean to find the height we are looking for the peaks at
        meanOfData = AverageEcgLeads.calculateMeanOfData(averagedEcgData)
        
        # Slice Array with point A and B (Start and end of the beat) and try to find 3 peaks
        for index in startEndOfBeats:
            # If index == 0, skip
            if index != 0:
                # TODO - need to write distance function to calculate the distance because this will  change! # Distance was at 100 IMPORTANT DISTANCE MAY BE IMPORTANT)
                signalPeaks = signal.find_peaks(averagedEcgData[lastIndex:index], height=meanOfData[0], width=3, distance = 30)
                
                # Counter to keep track of signalPeaks[0] compared to signalPeaks[1]['peak_heights']
                signalPeaksCounter = 0
                
                # Because we sliced the array, the index's are incorrect. We need to add the original index to the numbers first
                # We will append to the array at the same time
               # for slicedIndex in signalPeaks[0]:
                   # prtSectionIndexs.append(lastIndex + slicedIndex)
                
                pSegment = 0
                pSegmentIndex = 0
                rSegment = 0
                rSegmentIndex = 0
                sSegment = 0
                sSegmentIndex = 0
                qSegment = 0
                qSegmentIndex = 0
                tSegment = 0
                tSegmentIndex = 0
                    
                # Apply a filter to sort the peaks (Based on height)
                for sectionPeaks in signalPeaks[1]['peak_heights']:
                    # r peaks are always above 400. Peaks are returned in order. Cannot be after tSegment. Cannot have duplicates as heart beat should have this in the middle
                    if sectionPeaks >= 400 and tSegment == 0 and rSegment == 0: 
                        print("Appending r Peak")
                        # Set r segment height and position
                        rSegment = sectionPeaks
                        rSegmentIndex = signalPeaks[0][signalPeaksCounter]
                        # Add r segment to array for whole ecg
                        rSegmentPeaks.append(rSegment)
                        # Need to add last index because this is only 1 heartbeat out of the whole ecg
                        rSegmentIndexs.append(lastIndex + rSegmentIndex)
                        
                         # Experimental 2:40 am 27/04 TODO
                        # Use r as a basis to find q and s
                        # r is always found :)
                        # My own valley finding algorithm (From r peaks)
                        
                        # TODO - FLIP ARRAY AROUND AND LOOK FOR Q
                        # TODO - turn this into a find valley function and call it - SImples
                        # TODO - remove this from here. It will take years otherwise
                        # Set it up to be less than the mean of data to start with (thats the beggining threshold anyway)
                        sSegmentToTest = meanOfData[0]
                        dataToSearchIn = averagedEcgData[lastIndex:index]
                        breakCounter = 0
                        # TODO BAD WAY TO DO THIS. FIND START OF r PROPERLY! DONT BE A MORON.
                        todo = int(len(dataToSearchIn) / 2)
                        todo = signalPeaks[0][signalPeaksCounter]
                        
                        sSegmentSearchCounter = 0
                        # Find index of r peak to start search
                        for sSegmentSearch in dataToSearchIn[todo : ]:
                            # S Segment will always be below meanOfData
                            if sSegmentSearch < meanOfData[0]:
                                # Get positive number (if negative then it will be double negative so will turn positive)
                                if (sSegmentSearch) - (sSegmentToTest) < 0:
                                    sSegmentToTest = sSegmentSearch
                                    sSegmentSearchCounter += 1
                                elif breakCounter != 1:
                                    # I think we found the S Segment
                                    # TODO For testing purposes only
                                    sSegment = sSegmentToTest
                                    sSegmentIndex = todo + sSegmentSearchCounter
                                    breakCounter = 1
                                    print('sSegmentSearch (' + str(sSegmentSearch) + ') - sSegmentToTest (' + str(sSegmentToTest) + ') = ' + str((sSegmentSearch) - (sSegmentToTest)))
                                    plt.plot(dataToSearchIn, '-', todo + sSegmentSearchCounter, sSegmentToTest, 'ro')
                                    plt.legend(['ECG Signal', 'P Peak'], loc='best')
                                    plt.text(0.5, 0.5, 'Peak Detection Cutoff Height = ' + str(meanOfData[0]))
                                    plt.title('Single Beat PRT-Peaks Plotted Against ECG Data', fontsize = 20)
                                    folderToSaveTo = folderLocation +'/Graphs/Hopefully the S Segment/'
                                    # Make sure directory exists to save file to
                                    Util.saveGraph(folderToSaveTo, fileName + " BEAT " + str(counter + 1) + '.png') 
                 
                            # Counter needs incrementing anyway
                            else:
                                sSegmentSearchCounter += 1
                        
                        qSegmentToTest = meanOfData[0]
                        arrayReadyForReverse = averagedEcgData[lastIndex:index]
                        dataToSearchIn = arrayReadyForReverse[::-1]
                        breakCounter = 0
                        # TODO BAD WAY TO DO THIS. FIND START OF r PROPERLY! DONT BE A MORON.
                        todo = signalPeaks[0][signalPeaksCounter]
                        
                        qSegmentSearchCounter = 0
                        # Find index of r peak to start search
                        for qSegmentSearch in dataToSearchIn[todo : ]:
                            # S Segment will always be below meanOfData
                            if qSegmentSearch < meanOfData[0]:
                                # Get positive number (if negative then it will be double negative so will turn positive)
                                if (qSegmentSearch) - (qSegmentToTest) < 0:
                                    qSegmentToTest = qSegmentSearch
                                    qSegmentSearchCounter += 1
                                elif breakCounter != 1:
                                    # I think we found the S Segment
                                    # TODO For testing purposes only
                                    qSegment = qSegmentToTest
                                    qSegmentIndex = len(dataToSearchIn) - (todo + qSegmentSearchCounter)
                                    breakCounter = 1
                                    print('qSegmentSearch (' + str(qSegmentSearch) + ') - qSegmentToTest (' + str(qSegmentToTest) + ') = ' + str((qSegmentSearch) - (qSegmentToTest)))
                                    plt.plot(dataToSearchIn, '-', todo + qSegmentSearchCounter, qSegmentToTest, 'ro')
                                    plt.legend(['ECG Signal', 'P Peak'], loc='best')
                                    plt.text(0.5, 0.5, 'Peak Detection Cutoff Height = ' + str(meanOfData[0]))
                                    plt.title('Single Beat PRT-Peaks Plotted Against ECG Data', fontsize = 20)
                                    folderToSaveTo = folderLocation +'/Graphs/Hopefully the Q Segment/'
                                    # Make sure directory exists to save file to
                                    Util.saveGraph(folderToSaveTo, fileName + " BEAT " + str(counter + 1) + '.png') 
                 
                            # Counter needs incrementing anyway
                            else:
                                qSegmentSearchCounter += 1
                                
                    # t peak has to come after r peak - r peak is always found. Only allow if rpeak != 0
                    elif sectionPeaks < 400 and rSegment != 0: 
                        print("Appending t Peak")
                        # Set t segment height and position
                        tSegment = sectionPeaks
                        tSegmentIndex = signalPeaks[0][signalPeaksCounter]
                        # Add t segment to array for whole ecg
                        tSegmentPeaks.append(tSegment)
                        # Need to add last index because this is only 1 heartbeat out of the whole ecg
                        tSegmentIndexs.append(lastIndex +tSegmentIndex)
                    # p peak has to come before r segment.
                    elif sectionPeaks < 400 and rSegment == 0:
                        print("Appending p Peak")
                        # Set p segment height and position
                        pSegment = sectionPeaks
                        pSegmentIndex = signalPeaks[0][signalPeaksCounter]
                        # Add p segment to array for whole ecg
                        pSegmentPeaks.append(pSegment)
                        # Need to add last index because this is only 1 heartbeat out of the whole ecg
                        pSegmentIndexs.append(lastIndex + pSegmentIndex)
                        
                    signalPeaksCounter += 1
                #prsSectionPeaks.extend(signalPeaks[1]['peak_heights'])
                
                # For testing only - Remove if not neede for plot TODO
                x = []
                y = []
                c = 0
                for d in averagedEcgData:
                    x.append(c)
                    c+=1
                # TODO For testing purposes only
                plt.plot(averagedEcgData[lastIndex:index], '-', x[qSegmentIndex:sSegmentIndex], averagedEcgData[qSegmentIndex:sSegmentIndex], 'y-', pSegmentIndex, pSegment, 'ro', qSegmentIndex, qSegment, 'co', rSegmentIndex, rSegment, 'bo', sSegmentIndex, sSegment, 'mo', tSegmentIndex, tSegment, 'go')
                plt.legend(['ECG Signal', 'QRS Segment', 'P Peak', 'Q Valley', 'R Peak', 'S Valley', 'T Peak'], loc='best')
                plt.text(0.5, 0.5, 'Peak Detection Cutoff Height = ' + str(meanOfData[0]))
                plt.title('Single Beat PRT-Peaks Plotted Against ECG Data', fontsize = 20)
                folderToSaveTo = folderLocation +'/Graphs/Part 5 - Individual Heart Beats Plotted Against PRT-Peaks/'
                # Make sure directory exists to save file to
                Util.saveGraph(folderToSaveTo, fileName + " BEAT " + str(counter + 1) + '.png') 
                counter += 1
                
                # Change the last index to be the current index
                lastIndex = index
        
        # Adding the averagedEcgData to the graph
        plt.plot(averagedEcgData, '-', pSegmentIndexs, pSegmentPeaks, 'ro', rSegmentIndexs, rSegmentPeaks, 'bo', tSegmentIndexs, tSegmentPeaks, 'go')
        plt.legend(['ECG Signal', 'P Peak', 'R Peak', 'T Peak'], loc='best')
        plt.title('PRT-Peaks Plotted Against ECG Data', fontsize = 20)
        
        folderToSaveTo = folderLocation +'/Graphs/Part 6 - PRT-Peaks Plotted Against Averaged ECG Signal With Biological Drift Removed/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folderToSaveTo, fileName+'.png') 
    
    # TODO - LOOK AT THE HEARTBEAT SECTION FINDING PART. THERE IS A PICTURE SAVED IN GRAPHS. IMPORTANT
    # THIS METHOD BREAKS DOWN AND CEASES TO WORK IF THE HEARTRATE SPEEDS UP OR DOWN TOO MUCH
    # Function to detect peaks in the data.
    # Heart Rate is then calculated from these peaks and is saved into an Excel file
    def findQrsComplex(averagedEcgData, folderLocation, fileName):
        # Returns 2 arrays. One containing the location of the peaks in the array
        # The other containing the value of the peak
        signalPeaks = signal.find_peaks(averagedEcgData, height=200, distance=200)
        print(signalPeaks[0])
        print(signalPeaks[1]['peak_heights'])
        
        # Setup an array with data inside to save to a file
        heartRateDataToSave = [[0 for x in range(2)] for y in range(2)] # Initializes array as 2x2 
        heartRateDataToSave[0][0] = "Heart Rate"
        heartRateDataToSave[0][1] = "Heart Rate Zone"
        
        # Frequency of Welch Allyn System is 600Hz and it runs clinical ECG's for 10 seconds.
        # To get a minute, this needs to be multiplied by 6
        heartRate = len(signalPeaks[0]) * 6
        # Adding the heartrate to the array
        heartRateDataToSave[1][0] = str(heartRate)
        
        # Calculates the Heart Rate zone of the participant (Uses 25 year old for calculation)
        heartRateZone = Util.calculateHeartRateZone(heartRate)
        # Adding Heart Rate Zone to array
        heartRateDataToSave[1][1] = heartRateZone
        print("Participants Heart Rate Is Equal To " + str(heartRate) + " And Their Heart Rate Zone Is " + heartRateZone)
        
        # Save heart rate data to file for user
        Util.saveToCsv(heartRateDataToSave, folderLocation +'/Results/', fileName + ' Results.csv')
        
        # Adding the averagedEcgData to the graph
        plt.plot(averagedEcgData, '-', signalPeaks[0], signalPeaks[1]['peak_heights'], 'o')
        plt.legend(['ECG Signal', 'R-Peaks'], loc='best')
        plt.title('R-Peaks Plotted Against ECG Data', fontsize = 20)
        plt.text(0.5, 0.5, 'Heart Rate = ' + str(heartRate))
        
        folderToSaveTo = folderLocation +'/Graphs/Part 3 - (R-Peaks Plotted Against Averaged ECG Data With Biological Drift Removed)/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folderToSaveTo, fileName+'.png') 
        
        return signalPeaks
    
class Fft:
    
    # TODO - Do i need running mean datapoints here?
    # Calculate the FFT using the averaged ECG Data
    def calculateFft(averagedEcgData, runningMeanDatapoints, folderLocation, fileName):
        
        # Calculates discrete fourier transform using FFT (fast fourier transform)
        averageEcgFft = np.fft.fft(averagedEcgData)
        
        # This gets the Discrete fourier transforms frequencies
        freq = np.fft.fftfreq(len(averagedEcgData))
        
        print('freq = ' + str(freq))
        print(len(freq))
        
        # Below block is copied from here http://scipy-lectures.org/intro/scipy/auto_examples/plot_fftpack.html
        power = np.abs(averageEcgFft)        
        pos_mask = np.where(freq > 0)
        freqs = freq[pos_mask]
        peak_freq = freqs[power[pos_mask].argmax()]
        averageEcgFft[np.abs(freq) < peak_freq] = 0
        filtered_sig = np.fft.ifft(averageEcgFft)
        print("FFT WITH MATH = " + str(averageEcgFft))
        
        folderToSaveTo = folderLocation +'/Graphs/Part 8 - Averaged ECG Data (Drift Removed) As FFT FREQ/'
        plt.plot(averageEcgFft)
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        folderToSaveTo = folderLocation +'/Graphs/Part 9 - Averaged ECG Data (Drift Removed) As FFT FREQ/'
        plt.plot(filtered_sig)
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        #plots the freq against the length
        #plt.plot(freq, np.abs(averageEcgFft))
        #self.saveGraph(folderToSaveTo, fileName+'.png')        
        
        
class Util:
    
    # Function to make a directory in python to save the graphs to     
    def saveGraph(folderToSaveTo, fileName):
        try:
            os.mkdir(folderToSaveTo)
            print('The Directory: ' + folderToSaveTo + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folderToSaveTo + ' Already Exists. Saving Data')
        
        # Set X and Y Labels on the plot
        plt.xlabel('Time in 600ths of a second', fontsize = 14)
        plt.ylabel('Amplitude in Mv (Millivolts)', fontsize = 14)
        
        plt.show()
        
        # Save and clear the plot
        plt.savefig(folderToSaveTo + fileName)
        plt.cla() # Clear the plot
    
    
    # TODO THIS IS FLAWED SOMEHOW. LOOK AT IMPORTANT PHOTO WHICH HAS BEEN SAVED (MARKED IMPORTANT)
    # THIS HAPPENED WHEN USING RUNNING AVERAGE ON ECG SIGNAL AND THEN RUNNING THAT THROUGH THIS METHOD
    # Method to find the individual beats 
    def findIndividualBeats(averagedEcgData, signalPeaks, folderLocation, fileName):
        
        # Array to hold the datapoints index's inbetween the peaks - Meaning the end of one beat and the start of the next
        startOfBeatArray = []
        
        # Counter for r sections iterated through
        rSectionCounter = 0
        
        # To remember the last section which we visited
        previousSection = 0
        
        # For the amount of peaks that we have, calculate midway point between peaks
        for signalLocation in signalPeaks[0]:
            # Add '0' to array because we need to start here (first peak doesnt have an obvious midpoint before it)
            if rSectionCounter == 0:
                startOfBeatArray.append(0)
                
                # Set the current section as the previous section
                previousSection = signalLocation
                # Add 1 to the counter
                rSectionCounter += 1
                
            # Find the midway point between this peak and the last peak and append to array.
            else:
                # Find difference between numbers and then divide by 2 and round up
                midwayPointDifference = int(round((signalLocation - previousSection) / 2))
                startOfBeatArray.append(signalLocation - midwayPointDifference)
                
                # if this is the last peak we can add 6000 to array because there are no obvious mid points past this location
                if rSectionCounter == len(signalPeaks[0]) - 1:
                    startOfBeatArray.append(len(averagedEcgData) - 1)
                
                # Set the current section as the previous section
                previousSection = signalLocation
                
                # Set the current section as the previous section
                previousSection = signalLocation
                # Add 1 to the counter
                rSectionCounter += 1
        
        print("This is the midway Peaks array" + str(startOfBeatArray))
        
        # Find data points at location given by the midwayPeaksArray in order to generate graph
        midRSectionValues = []
        for index in startOfBeatArray:
            midRSectionValues.append(averagedEcgData[index])
        
        plt.plot(averagedEcgData, '-', startOfBeatArray, midRSectionValues, 'o')
        plt.legend(['Averaged ECG Data - Drift Removed', 'Heart Beat Section Points'], loc='best')
        
        # Gives gaps inbetween subplots
        plt.tight_layout()
        
        folderToSaveTo = folderLocation +'/Graphs/Part 4 - Averaged ECG Data With Drift Removed Plotted With Individual Heart Beat Cuts/'
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        return startOfBeatArray
        
    
    # Function to find zero crossings in data set
    def findZeroCrossings(averagedEcgData, meanOfData, runningMeanDatapoints, folderLocation, fileName):
        print("Finding Zero Crossings")
        
        lastDataPoint = meanOfData
        
        dataUnder = 0
        dataOver = 0
        
        # To colour the zero crossings differently
        zeroCrossingCounter = 0
        zeroCrossingPlotArray = []
        
        for dataPoint in averagedEcgData:
            
            # TODO maybe remove this
            zeroCrossingCounter += 1
            zeroCrossingPlotArray.append(dataPoint)
            
            # If data has gone above crossing point
            if dataPoint >= runningMeanDatapoints[zeroCrossingCounter-1] and lastDataPoint < runningMeanDatapoints[zeroCrossingCounter-1]:
                dataOver += 1
                # TODO - Testing
                plt.plot(zeroCrossingPlotArray, 'b')
                zeroCrossingPlotArray.clear()
                toDoWillyWonka = [np.nan] * zeroCrossingCounter
                zeroCrossingPlotArray.extend(toDoWillyWonka)
                
            # If data has gone below crossing point    
            elif dataPoint < runningMeanDatapoints[zeroCrossingCounter-1] and lastDataPoint > runningMeanDatapoints[zeroCrossingCounter-1]:
                dataUnder += 1
                # TODO - Testing 
                plt.plot(zeroCrossingPlotArray, 'r')
                zeroCrossingPlotArray.clear()
                toDoWillyWonka = [np.nan] * zeroCrossingCounter
                zeroCrossingPlotArray.extend(toDoWillyWonka)
                
                
                
            lastDataPoint = dataPoint # Set last datapoint to this data point
        
        print('Data Over = ' + str(dataOver) + ' And Data Under = ' + str(dataUnder))
        
        # plt.plot(averagedEcgData) # Plot ecg data
        
        # Is this needed?
        y = []
       
        for x in range(1, 6001):
            y.append(x)
        
        # blah = interp1d(runningMeanDatapoints, y, kind='cubic')
        
        plt.plot(runningMeanDatapoints)
        
        # To add the mean of the data to the graph
        plt.plot(np.repeat(meanOfData, len(averagedEcgData)))
        
        folderToSaveTo = folderLocation +'/Graphs/ECG Data plotted against Moving Point Average/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        #Probably remove from here and put elsewhere......
        #Fft.calculateFft(averagedEcgData, runningMeanDatapoints, folderLocation, fileName)
        #for csvData in ecgData:
         #   print("Data = " + str(ecgData))
        
     # TODO this is totally someone elses function. If it needs keeping then it needs to be deleted and rewritten
    def distance(a, b):
        if (a == b):
            return 0
        elif (a < 0) and (b < 0) or (a > 0) and (b > 0):
            if (a < b):
                return (abs(abs(a) - abs(b)))
            else:
                return -(abs(abs(a) - abs(b)))
        else:
            return math.copysign((abs(a) + abs(b)),b)
           
    # Formats and saves data to a CSV File
    def saveToCsv(dataToSave, folderToSaveTo, fileName):
        # Try to make a folder (Stops errors)
        try:
            os.mkdir(folderToSaveTo)
            print('The Directory: ' + folderToSaveTo + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folderToSaveTo + ' Already Exists. Saving Data')
        
        # Allow for file to be saved
        np.savetxt(folderToSaveTo + fileName, dataToSave, delimiter=",", fmt='%s')
        
    
    # TODO Explain how this only shows heart rate zones for a 25 year old (Will not work for other ages)
    # Even then its a guestimate. 
    # TODO - EXCERCISE ZONES TAKEN FROM HERE - https://commons.wikimedia.org/wiki/File:Exercise_zones.png
    # Calculates Heart Rate Zone
    def calculateHeartRateZone(heartRate):
        
        heartRateZone = ""
        
        if heartRate <= 80:
            heartRateZone = "Resting"
        elif heartRate > 80 and heartRate <= 98:
            heartRateZone = "Walking/Moving"
        elif heartRate > 98 and heartRate <= 117:
            heartRateZone = "Maintenance/Warm Up"
        elif heartRate > 117 and heartRate <= 137:
            heartRateZone = "Weight Control (Fitness/Fat Burn)"
        elif heartRate > 137 and heartRate <= 156:
            heartRateZone = "Aerobic Zone (Cardio Training/Endurance)"
        elif heartRate > 156 and heartRate <= 176:
            heartRateZone = "Anaerobic Zone"
        elif heartRate > 176 and heartRate <= 195:
            heartRateZone = "VO2 Max (Maximum Effort)"
            
        return heartRateZone
    #__init__.py