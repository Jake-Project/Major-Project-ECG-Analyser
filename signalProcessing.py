# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 17:39:54 2019

@author: rocke
"""

# To plot Graphs of data
import matplotlib.pyplot as plt
import os # Needed for folders



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
            total += float(ecgDataInstance[x]) # Add all of the data together and cast to float
            # print(total)
        
        averagedSignal = total / 9
        # print("Averaged Signal: " + str(averagedSignal))
        return averagedSignal
      
    # Function to calculate the cubic spline interpolation of the running average sections of the signal
    def calculateCubicInterpolation(self, averagedSignalData, singularMeanOfData, runningMeanDatapoints, folderLocation, fileName):
        print("Calculating the Cubic Interpolation of the running mean sections")
        
        y = []
       
        # For the amount of data points in our code - TODO This must be changed to the lenght of meanOfData (Here and below)
        for x in range(1, len(singularMeanOfData) + 1):
            y.append(x)
        
        print(len(singularMeanOfData))
        print(len(y))
        # X is horizontal (The data point included in the mean of data)
        # Y is vertical (The mean of data that we wish to look at)
        # This returns the interpolation function which we need to make use of
        cubicInterpolatedRepresentation = interp1d(y, singularMeanOfData, 'cubic')
        
        xnew = np.arange(1, 15, 0.00233)
        ynew = cubicInterpolatedRepresentation(xnew) 
        
        print('ynew = ' + str(len(ynew)))
        print(type(ynew))
        print(str(ynew))
        plt.plot(runningMeanDatapoints, 'o', ynew, '--')
        plt.legend(['Running Average Sections', 'Cubic Interpolation Of Running Average Sections'], loc='best')
        
        folderToSaveTo = folderLocation +'/Graphs/Cubic Interpolation Paired With Running Average Sections/'
        
        # Make sure directory exists to save file to
        self.saveGraph(folderToSaveTo, fileName+'.png')
        
        #TODO CHANGE NAME OF XNEW YNEW
        plt.plot(averagedSignalData)
        plt.plot(ynew)
        #plt.plot(averagedSignalData, 'o', ynew, '--')
        #plt.legend(['Averaged Signal Data', 'Cubic Interpolation Of Running Average Sections'], loc='best')
        
        folderToSaveTo = folderLocation +'/Graphs/Cubic Interpolation Paired With Averaged Signal Data/'
        
        # Make sure directory exists to save file to
        Graph.saveGraph(folderToSaveTo, fileName+'.png')
        
        # Function to find zero crossings for the averaged signal of the dataset using the 
        self.findZeroCrossings(averagedSignalData, 0, ynew, folderLocation, fileName)
        
        return ynew # TODO WHAT IS yNEW?????
    
    
    # Method that removes the drift from the averaged ECG signal.
    # Function that will eliminate baseline drift of the biological ECG signal
    def removeDrift(self, averagedEcgData, runningMeanDatapoints, folderLocation, fileName):
        newData = []
        print('Length of averaged data = ' + str(len(averagedEcgData)) + '. Length of running mean datapoints' + str(len(runningMeanDatapoints)))
        counter = 0
        
        # THis line is a copy - Make it yours
        runningMeanDatapoints = runningMeanDatapoints[:len(runningMeanDatapoints)-9]

        for data in runningMeanDatapoints:
            
            newData.append(averagedEcgData[counter] - self.distance(0, data))
            counter += 1
    
        plt.plot(newData)
        folderToSaveTo = folderLocation +'/Graphs/BSHDSAJHDJA/'
        self.saveGraph(folderToSaveTo, fileName+'.png')
    
    
    #__init__.py
    
    


class QrsDetection:
    
    # Function to detect QRS Complex
    def findQrsComplex(self, graphicsView):
        print("bladlsajdlksajldksajkofjlksklfjlkfja")
        signalPeaks = signal.find_peaks(ecgDataset, height=0, distance=200)
        print(signalPeaks[0])
        signalPeaksData = signalPeaks[0]
        peaks = list() #TODO Do not need this if we are using indices to find peaks.
        
        ecgDatasetToPlot = []
        ecgDatasetToPlot.clear()
        ecgDatasetToPlot = ecgDataset # Temporary dataset to plot
        
        # Get data from index where we have found a peak because find_peaks gives us the index of peaks and not the actual peaks
        for dataIndex in signalPeaksData:
    
            peaks.append(ecgDataset[dataIndex])
            #print(ecgDataset[dataIndex])
            
            # Append peaks to ecg dataset to be shown. If this is left as is TODO remove peaks
            ecgDatasetToPlot.append(ecgDataset[dataIndex])
        
        
        self.graphicsView.clear() #TODO Need to make a buffer for the data that is stored on the array that i show
        #self.graphicsView.plot(peaks)
        self.graphicsView.plot(ecgDatasetToPlot)
    
      # TODO This probably wont work
      # Not a robust method. Will not work for people with faster heartrates or extremely low heartrate. Dependant on the distance variable above
      # 600hz frequency.
        heartRate = len(signalPeaksData) * 6
      
        print("Heart Rate Is: " + str(heartRate))
        
        
        
        
class Graph:
    
    # Function to make a directory in python to save the graphs to     
    def saveGraph(self, folderToSaveTo, fileName):
        try:
            os.mkdir(folderToSaveTo)
            print('The Directory: ' + folderToSaveTo + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folderToSaveTo + ' Already Exists. Saving Data')
        
        # Set X and Y Labels on the plot
        plt.title('Some Graph', fontsize = 20)
        plt.xlabel('Time in 600ths of a second', fontsize = 14)
        plt.ylabel('Amplitude in Mv (Millivolts)', fontsize = 14)
        
        plt.show()
        
        # Save and clear the plot
        plt.savefig(folderToSaveTo + fileName)
        plt.cla() # Clear the plot
        
           

    #__init__.py