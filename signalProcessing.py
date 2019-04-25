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
    def calculateRunningMean(averagedSignalData):
        
        # Array to hold the running mean datapoints
        runningMeanDatapoints = []
        
        # Variables to calculate the mean
        ecgRunningMean = 0.0
        ecgRunningMeanCounter = 0
        
        # Amount of signals for mean to be calculated on (Should be divisible by 6000)
        runningMeanMaxDatapoints = 400
        
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
        
        folderToSaveTo = folderLocation +'/Graphs/Cubic Interpolation Paired With Averaged Signal Data/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        # Function to find zero crossings for the averaged signal of the dataset using the 
        Util.findZeroCrossings(averagedSignalData, 0, ynew, folderLocation, fileName)
        
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
        
        folderToSaveTo = folderLocation +'/Graphs/Averaged ECG Data (Drift Removed Vs No Processing)/'
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        return ecgSignalWithDriftRemoved
    
    #__init__.py
    
    


class QrsDetection:
    
    # Function to detect peaks in the data.
    # Heart Rate is then calculated from these peaks and is saved into an Excel file
    def findQrsComplex(averagedEcgData, folderLocation, fileName):
        # Returns 2 arrays. One containing the location of the peaks in the array
        # The other containing the value of the peak
        signalPeaks = signal.find_peaks(averagedEcgData, height=200, distance=200)
        print(signalPeaks[0])
        print(signalPeaks[1]['peak_heights'])
        
        
        # Frequency of Welch Allyn System is 600Hz and it runs clinical ECG's for 10 seconds.
        # To get a minute, this needs to be multiplied by 6
        heartRate = len(signalPeaks[0]) * 6
        
        # Calculates the Heart Rate zone of the participant (Uses 25 year old for calculation)
        heartRateZone = Util.calculateHeartRateZone(heartRate)
        print("Participants Heart Rate Is Equal To " + str(heartRate) + " And Their Heart Rate Zone Is " + heartRateZone)
        
        # Save heart rate data to file for user
        Util.saveToCsv(folderLocation +'/Results/')
        
        # Adding the averagedEcgData to the graph
        plt.plot(averagedEcgData, '-', signalPeaks[0], signalPeaks[1]['peak_heights'], 'o')
        plt.legend(['ECG Signal', 'R-Peaks'], loc='best')
        plt.title('R-Peaks Plotted Against ECG Data', fontsize = 20)
        plt.text(0.5, 0.5, 'Heart Rate = ' + str(heartRate))
        
        folderToSaveTo = folderLocation +'/Graphs/fdfdsdadga/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folderToSaveTo, fileName+'.png') 
        
        return signalPeaks
    
class Fft:
    
    # Calculate the FFT using the averaged ECG Data
    def calculateFft(averagedEcgData, runningMeanDatapoints, folderLocation, fileName):
        averageEcgFft = np.fft.fft(np.array(averagedEcgData).flatten())
        # TODO can remove this as well later possibly
        folderToSaveTo = folderLocation +'/Graphs/Averaged Signals With FFT/'
        plt.plot(averageEcgFft)
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        folderToSaveTo = folderLocation +'/Graphs/Averaged Signals With FFT FREQ/'
        # TODO - remove me. This line below is a direct copy for testing
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
        plt.plot(filtered_sig)
        plt.plot(runningMeanDatapoints)
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
        Fft.calculateFft(averagedEcgData, runningMeanDatapoints, folderLocation, fileName)
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
    def saveToCsv(folderToSaveTo):
        # Try to make a folder (Stops errors)
        try:
            os.mkdir(folderToSaveTo)
            print('The Directory: ' + folderToSaveTo + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folderToSaveTo + ' Already Exists. Saving Data')
            
        
        
    
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