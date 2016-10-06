from __future__ import division
import math
import scipy.io as sio
import os#, subprocess
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints'] = 1

def getFrequencies(mapData):
    frequencies = mapData['map0'][0,0].f[0]
    return frequencies

def getStartTimes(mapData):
    startTimes = mapData['map0'][0,0].segstarttime[0]
    return startTimes

def getClusterData(stoch_outFile):
    try:
        stoch_outData = sio.loadmat(stoch_outFile)
        #clusterData = stoch_outData['stoch_out'][0,0].cluster[0,0].reconMax
        clusterData = stoch_outData['stoch_out']['cluster'][0,0]['reconMax'][0,0]
    except:
        output_dir = ""
        if "/" in stoch_outFile:
            temp_dir = stoch_outFile[::-1]
            temp_dir = temp_dir[temp_dir.index('/'):]
            output_dir = temp_dir[::-1]
        maxClusterFile = glueFileLocation(output_dir, "max_cluster.txt")
        with open(maxClusterFile, "r") as infile:
            clusterData = [[float(y) for y in x.split(',')] for x in infile]
        #matlabExecutablePath = "/home/quitzow/GIT/Development_Branches/pyCondorSTAMP/readSaveMatrix"
        #matlabExecutablePath = "/home/quitzow/GIT/Development_Branches/MatlabExecutableDuctTape/readSaveArray"
        #print("attempting to read " + stoch_outFile)
        #tempOutput = subprocess.Popen([matlabExecutablePath, stoch_outFile, outputFile, 'stoch_out', 'cluster,reconMax', ','], stdout = subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        #if tempOutput[1]:
        #    print(tempOutput[1])
        #    raw_input("press enter to continue")
        #    clusterData = None
        #else:
        #    clusterData = getClusterDataOther(outputFile)
    return clusterData

"""def getClusterData(stoch_outFile):
    \"""print(stoch_outData['stoch_out'][0,0])
    print(stoch_outData['stoch_out'][0,0].cluster[0,0])
    print(stoch_outData['stoch_out'][0,0].cluster[0,0].reconMax[0,0])
    print(stoch_outData['stoch_out'][0,0].cluster[0,0].reconMax[0])
    print(stoch_outData['stoch_out'][0,0]._fieldnames)
    print(stoch_outData['stoch_out'][0,0].cluster[0,0]._fieldnames)
    print(stoch_outData['stoch_out'][0,0].cluster[0,0].reconMax)
    print(len(stoch_outData['stoch_out'][0,0].cluster[0,0].reconMax[0]))
    print(stoch_outData['stoch_out'][0,0].cluster[0,0].reconMax._fieldnames)
    print(stoch_outData['stoch_out'][0,0].cluster[0,0].reconMax[0]._fieldnames)
    print(stoch_outData['stoch_out'][0,0].cluster[0,0].reconMax[0,0]._fieldnames)\"""
    try:
        stoch_outData = sio.loadmat(stoch_outFile)
        clusterData = stoch_outData['stoch_out'][0,0].cluster[0,0].reconMax
    except:
        output_dir = ""
        if "/" in stoch_outFile:
            temp_dir = stoch_outFile[::-1]
            temp_dir = temp_dir[temp_dir.index('/'):]
            output_dir = temp_dir[::-1]
        outputFile = output_dir + "pythonClusterTemp.mat"
        #matlabExecutablePath = "/home/quitzow/GIT/Development_Branches/pyCondorSTAMP/readSaveMatrix"
        matlabExecutablePath = "/home/quitzow/GIT/Development_Branches/MatlabExecutableDuctTape/readSaveArray"
        print("attempting to read " + stoch_outFile)
        tempOutput = subprocess.Popen([matlabExecutablePath, stoch_outFile, outputFile, 'stoch_out', 'cluster,reconMax', ','], stdout = subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if tempOutput[1]:
            print(tempOutput[1])
            raw_input("press enter to continue")
            clusterData = None
        else:
            clusterData = getClusterDataOther(outputFile)
    return clusterData"""

def getClusterDataOther(stoch_outFile):
    stoch_outData = sio.loadmat(stoch_outFile)
    clusterData = stoch_outData['output']
    return clusterData

"""
def getClusterDataOther(stoch_outFile):
    stoch_outData = sio.loadmat(stoch_outFile)
    clusterData = stoch_outData['output'][0,0]
    return clusterData
"""

def getClusterInfo(stochFile, mapFile):
    mapData = sio.loadmat(mapFile)
    frequencies = getFrequencies(mapData)
    startTimes = getStartTimes(mapData)
    clusterData = getClusterData(stochFile)
    #print(clusterData)
    max_rows = [max(row) for row in clusterData]
    max_cols = [max([x[col] for x in clusterData]) for col in range(len(clusterData[0]))]
    #print(len(max_rows))
    #print(len(max_cols))
    clusterRows = [num for num, val in enumerate(max_rows) if val > 0]
    clusterCols = [num for num, val in enumerate(max_cols) if val > 0]
    tempDict = {}
    #print(clusterRows)
    #print(frequencies)
    #print(clusterCols)
    tempDict["frequencies"] = [frequencies[x] for x in clusterRows]
    tempDict["startTimes"] = [startTimes[x] for x in clusterCols]
    try:
        tempDict["clusterData"] = [[clusterData[x, y] for y in clusterCols] for x in clusterRows]
    except:
        tempDict["clusterData"] = [[clusterData[x][y] for y in clusterCols] for x in clusterRows]
    plotData = constructClusterPlotData(tempDict)
    #print(plotData)
    return plotData

def constructClusterPlotData(tempDict):
    data = [[],[]]
    #print(tempDict["clusterData"])
    #print(tempDict["clusterData"][0][0])
    #print(tempDict["clusterData"][0][0]> 0)
    for rowIndex, rowVal in enumerate(tempDict["frequencies"]):
        for colIndex, colVal in enumerate(tempDict["startTimes"]):
            #print(rowIndex)
            #print(len(tempDict["startTimes"]))
            #print(len(tempDict["clusterData"]))
            #print(tempDict["clusterData"])
            #print(tempDict["clusterData"][rowIndex])
            #print(tempDict["clusterData"][rowIndex][colIndex])
            ##print(rowIndex)
            #print(colIndex)
            #print(tempDict["clusterData"][rowIndex][colIndex])
            #print(tempDict["clusterData"][rowIndex][colIndex]>0)
            if tempDict["clusterData"][rowIndex][colIndex] > 0:
                data[0] += [rowVal]
                data[1] += [colVal]
    #            print(rowVal)
    #            print(colVal)
    #print(data)
    #print(tempDict[0])
    return data

print("WARNING: Script is currently not set up to handle directories with multiple files with the name base.")
def returnMatrixFilePath(nameBase, directory):
    files = [x for x in os.listdir(directory) if nameBase in x]
    if len(files) != 1:
        print("WARNING: Number of files in " + directory + " with name base " + nameBase + " is not equal to one. Number of files is " + str(len(files)) + ". Selecting first occurance for rest of script.")
    if len(files) == 0:
        filePath = None
    else:
        filePath = directory + "/" + files[0]
    return filePath

def glueFileLocation(directory, filename):
    output = None
    if directory[-1] == "/":
        if filename[0] == "/":
            output = directory + filename[1:]
        else:
            output = directory + filename
    else:
        if filename[0] == "/":
            output = directory + filename
        else:
            output = directory + "/" + filename
    return output

def readFile(file_name, delimeter = None):
    with open(file_name, "r") as infile:
        content = [x.split(delimeter) for x in infile]
    return content

def saveClusterPlot(directory, data, burstegard = False):
    if not os.path.exists(directory + "/cluster_focus_plot.png"):
        plt.grid(b=True, which='minor',color='0.85',linestyle='--')
        plt.grid(b=True, which='major',color='0.75',linestyle='-')
        #print(data)
        if burstegard:
            plt.plot(data[1], data[0],'b.')#, label = "SNR distribution")
        else:
            plt.plot(data[1], data[0],'b.-')#, label = "SNR distribution")
        #plt.plot(all_snrs, all_percentage, 'ro', label = "FAP = " + str(100*rank) + "%\nSNR = " + str(specificSNR))
        #plt.yscale('log')
        #plt.xscale('log')
        plt.xlabel("Time [GPS]")
        #plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
        #plt.ylabel('Strain [Counts / sqrt(Hz)]')
        plt.ylabel("Frequency [Hz]")
        plt.ylim([0,2500])
        #if max(data[0]) - min(data[0]) < 10:
        #    plt.ylim = ([min(data[0]) - 5], max(data[0]) + 5)
        #plt.ylim([0,100])
        #plt.title("")
        #legend = plt.legend(prop={'size':6})#, framealpha=0.5)
        #legend.get_frame().set_alpha(0.5)
        #plt.show()
        plt.savefig(directory + "/cluster_plot", bbox_inches = 'tight')
        plt.clf()

        plt.grid(b=True, which='minor',color='0.85',linestyle='--')
        plt.grid(b=True, which='major',color='0.75',linestyle='-')
        #print(data)
        if burstegard:
            plt.plot(data[1], data[0],'b.')#, label = "SNR distribution")
        else:
            plt.plot(data[1], data[0],'b.-')#, label = "SNR distribution")
        #plt.plot(all_snrs, all_percentage, 'ro', label = "FAP = " + str(100*rank) + "%\nSNR = " + str(specificSNR))
        #plt.yscale('log')
        #plt.xscale('log')
        plt.xlabel("Time [GPS]")
        #plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
        #plt.ylabel('Strain [Counts / sqrt(Hz)]')
        plt.ylabel("Frequency [Hz]")
        #plt.ylim([0,2500])
        if max(data[0]) - min(data[0]) < 10:
            plt.ylim([min(data[0]) - 5, max(data[0]) + 5])
        #plt.ylim([0,100])
        #plt.title("")
        #legend = plt.legend(prop={'size':6})#, framealpha=0.5)
        #legend.get_frame().set_alpha(0.5)
        #plt.show()
        plt.savefig(directory + "/cluster_focus_plot", bbox_inches = 'tight')
        plt.clf()

def plotClusterInfo(stochFile, mapFile, directory, burstegard = False):
    if mapFile == None or stochFile == None:
        print("Missing mapFile or stochFile in " + directory)
        return False
    else:
        data = getClusterInfo(stochFile, mapFile)
        saveClusterPlot(directory, data, burstegard)
        print("Plot saved in " + directory)
        return True

def getPixelInfo(directory, deltaTfile, overlapFile):
    mat_file = [x for x in os.listdir(directory) if 'bknd' in x]
    mat_path = glueFileLocation(directory, mat_file[0])
    mat_data = sio.loadmat(mat_path)
    deltaT_data = mat_data['stoch_out']['params'][0,0]['segmentDuration'][0,0][0,0]
    overlap_data = mat_data['stoch_out']['params'][0,0]['doOverlap'][0,0][0,0]
    data = [deltaT_data, overlap_data]
    """try:
        mat_file = [x for x in os.listdir(directory) if 'bknd' in x]
        mat_path = glueFileLocation(directory, mat_file[0])
        mat_data = sio.loadmat(mat_path)
        deltaT_data = mat_data['stoch_out']['params'][0,0]['segmentDuration'][0,0][0,0]
        overlap_data = mat_data['stoch_out']['params'][0,0]['doOverlap'][0,0][0,0]
        data = [deltaT_data, overlap_data]
    except:
        with open(directory + "/" + deltaTfile, "r") as infile:
            deltaT_data = [[float(y) for y in x.split(',')] for x in infile]
        with open(directory + "/" + overlapFile, "r") as infile:
            overlap_data = [[float(y) for y in x.split(',')] for x in infile]
        data = [deltaT_data[0][0], overlap_data[0][0]]"""
    return data

def getFrequencyInfo(directory, frequencyFile, deltaFfile):
    try:
        mat_file = [x for x in os.listdir(directory) if 'bknd' in x]
        mat_path = glueFileLocation(directory, mat_file[0])
        mat_data = sio.loadmat(mat_path)
        f_min = mat_data['stoch_out']['params'][0,0]['fmin'][0,0][0,0]
        f_max = mat_data['stoch_out']['params'][0,0]['fmax'][0,0][0,0]
        frequency_window = [f_min, f_max]
        delta_F = mat_data['stoch_out']['params'][0,0]['deltaF'][0,0][0,0]
        data = [frequency_window, delta_F]
    except:
        with open(directory + "/" + frequencyFile, "r") as infile:
            frequencyData = [[float(y) for y in x.split(',')] for x in infile]
        with open(directory + "/" + deltaFfile, "r") as infile:
            deltaFdata = [[float(y) for y in x.split(',')] for x in infile]
        data = [frequencyData[0], deltaFdata[0][0]]
    return data

def getClusterInfo_v2(stochFile, pixelInfo, frequencyInfo):
    #mapData = sio.loadmat(mapFile)
    #frequencies = getFrequencies(mapData)
    #startTimes = getStartTimes(mapData)
    frequencies = [x * frequencyInfo[1] for x in range(int(frequencyInfo[0][0]/frequencyInfo[1] + 0.5), int(frequencyInfo[0][1]/frequencyInfo[1] + 0.5))] + [frequencyInfo[0][1]]
    clusterData = getClusterData(stochFile)
    if pixelInfo[1]:
        startTimes = [x * pixelInfo[0]/2 for x in range(len(clusterData[0]))]
    else:
        startTimes = [x * pixelInfo[0] for x in range(len(clusterData[0]))]
    #print(clusterData)
    max_rows = [max(row) for row in clusterData]
    max_cols = [max([x[col] for x in clusterData]) for col in range(len(clusterData[0]))]
    #print(len(max_rows))
    #print(len(max_cols))
    clusterRows = [num for num, val in enumerate(max_rows) if val > 0]
    clusterCols = [num for num, val in enumerate(max_cols) if val > 0]
    tempDict = {}
    #print(clusterRows)
    #print(frequencies)
    #print(clusterCols)
    tempDict["frequencies"] = [frequencies[x] for x in clusterRows]
    tempDict["startTimes"] = [startTimes[x] for x in clusterCols]
    try:
        tempDict["clusterData"] = [[clusterData[x, y] for y in clusterCols] for x in clusterRows]
    except:
        tempDict["clusterData"] = [[clusterData[x][y] for y in clusterCols] for x in clusterRows]
    plotData = constructClusterPlotData(tempDict)
    #print(plotData)
    return plotData

def plotClusterInfo_v2(stochFile, pixelInfo, frequencyInfo, directory, burstegard = False):
    data = getClusterInfo_v2(stochFile, pixelInfo, frequencyInfo)
    saveClusterPlot(directory, data, burstegard)
    print("Plot saved in " + directory)
    return True
