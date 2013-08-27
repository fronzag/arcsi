"""
Module that contains the ARCSIResampleSpectralResponseFuncs Class.
"""

############################################################################
#  arcsispecresponsefuncs.py
#
#  Copyright 2013 ARCSI.
#
#  ARCSI: 'Atmospheric and Radiometric Correction of Satellite Imagery'
#
#  ARCSI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARCSI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARCSI.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Purpose:  A class for resampling spectral response functions for 
#           remote sensing sensors.
#
# Author: Pete Bunting
# Email: pfb@aber.ac.uk
# Date: 15/07/2013
# Version: 1.0
#
# History:
# Version 1.0 - Created.
#
############################################################################

# Import the numpy library
import numpy
# Import the ARCSI utilities class
from arcsiutils import ARCSIUtils
# Import the ARCSI exception class
from arcsiexception import ARCSIException
# Import the python maths module. 
import math
# Import python system library
import sys
# Import the python Argument parser
import argparse

class ARCSIResampleSpectralResponseFuncs (object):
    """
    A class which resamples spectral response functions.
    """
    
    def readSpectralResponseFunc(self, inFile, seperator, ignoreLines, waveCol, respCol):
        specResp = list()
        try:
            specFile = open(inFile, 'r')
            lineCount = 0
            for line in specFile:
                if lineCount >= ignoreLines:
                    line = line.strip()
                    if line:
                        lineVals = line.split(seperator)
                        if (len(lineVals) <= waveCol) or (len(lineVals) <= respCol):
                            raise ARCSIException("")
                        waveVal = float(lineVals[waveCol].strip())
                        respVal = float(lineVals[respCol].strip())
                        specResp.append([waveVal,respVal])
                lineCount += 1
            specFile.close()
        except ARCSIException as e:
            raise e
        except Exception as e:
            raise e
        return numpy.array(specResp)
    

    
    def resampleSpectralResponseFunction(self, outputFile, respFuncs, sampling, method):
        minWv = respFuncs[0][0]
        maxWv = respFuncs[len(respFuncs)-1][0]
        
        rangeWv = int(maxWv - minWv)+1
        
        numOfSamples = int(math.ceil(float(rangeWv)/float(sampling)))
        try:
            outFile = open(outputFile, 'w')
            
            wv = minWv
            for i in range(numOfSamples):
                line = str(wv) + str(",")
                                
                rfDist = 0
                minDist = 0
                minDistRF = None
                minDistIdx = 0
                first = True
                for j in range(len(respFuncs)):
                    rfDist = math.fabs(wv - respFuncs[j][0])
                    if first:
                        minDist = rfDist
                        minDistRF = respFuncs[j]
                        minDistIdx = j
                        first = False
                    else:
                        if rfDist < minDist:
                            minDist = rfDist
                            minDistRF = respFuncs[j]
                            minDistIdx = j
                if method == 'NearNeighbour':
                    line = line + str(minDistRF[1])
                else:
                    raise ARCSIException("Method of resampling is not reconised.")
                
                print line
                line = line + str("\n")
                outFile.write(line)
                wv = wv + sampling
            outFile.close()
        except ARCSIException as e:
            raise e
        except Exception as e:
            raise e
    
    def run(self, outputFile, inputFile, seperator, ignoreLines, wvCol, respCol, sampling, method):
        respFunc = self.readSpectralResponseFunc(inputFile, seperator, ignoreLines, wvCol, respCol)
        self.resampleSpectralResponseFunction(outputFile, respFunc, sampling, method)

if __name__ == '__main__':
    """
    The command line user interface to ARCSI Response Function tool.
    """
    parser = argparse.ArgumentParser(prog='arcsispecresponsefuncs',
                                    description='''ARCSI command for resampling
                                                   spectral response functions.''',
                                    epilog='''Different tools require the spectral
                                              response function to a different resampling
                                              (for example 6S requires a sampling of 2.5nm).
                                              This tool allows a provided spectral response
                                              function to be resampled.''')
    # Request the version number.
    parser.add_argument('-v', '--version', action='version', version='%(prog)s Version 0.1a')
    # Define the argument for specifying the input spectral response file.
    parser.add_argument("-o", "--output", type=str, 
                        help='''A file to where the resampled spectral response functions will
                        be outputted as a comma seperated file.''')
    # Define the argument for specifying the input spectral response file.
    parser.add_argument("-i", "--input", type=str, 
                        help='''A seperated (--sep) text file defining the
                        wavelength (nm) and normalised spectral response
                        function.''')
    # Define the argument for specifying input seperator.
    parser.add_argument("-s", "--sep", type=str,
                        help='''The seperator used to split the columns within the input
                        file. The default is space seperated where consecutive spaces 
                        are ignored.''')
    # Define the argument for specifying the number of lines to ignore.
    parser.add_argument("--ignore", type=int, default="0",
                        help='''Number of lines at the beginning of the file
                        which should be ignored.''')
    # Define the argument for specifying the column for the wavelength.
    parser.add_argument("--wvcol", type=int, default="0",
                        help='''The wavelength column within the input file (starting at 0).''')
    # Define the argument for specifying the column for the response function.
    parser.add_argument("--rcol", type=int, default="1",
                        help='''The response function column within the input file (starting at 0).''')
    # Define the argument for specifying the column for the response function.
    parser.add_argument("--sample", type=float, default="1",
                        help='''The sampling of the output file.''')
    # Define the argument which specifies the standard aersol profile to use.
    parser.add_argument("--method", type=str, default="NearNeighbour", choices=['NearNeighbour', 'Linear'],
                        help='''Specify the method of resampling. Choises are NearNeighbour, Linear.''')

    # Call the parser to parse the arguments.
    args = parser.parse_args()
    
    if args.input == None:
        print("An input file was not specified.")
        sys.exit()
    
    if args.output == None:
        print("An output file was not specified.")
        sys.exit()
    
    arcsiObj = ARCSIResampleSpectralResponseFuncs()
    
    arcsiObj.run(args.output, args.input, args.sep, args.ignore, args.wvcol, args.rcol, args.sample, args.method)
        
        
        
        
        
        
        
        
        
        
        
        