

def getDefaultCommonParams():

    return {
        "preproc" : {
                     'ShiftTime1': 1,
                     'ShiftTime2': 0,
                     'alphaBetaFile1': None,
                     'alphaBetaFile2': None,
                     'alphaExp': 0,
                     'batch': True,
                     'betaParam1': 5,
                     'betaParam2': 5,
                     'bufferSecs1': 2,
                     'bufferSecs2': 2,
                     'calCavGainFile1': None,
                     'calCavGainFile2': None,
                     'calResponseFile1': None,
                     'calResponseFile2': None,
                     'deltaF': 1,
                     'doBadGPSTimes': False,
                     'doDetectorNoiseSim': False,
                     'doFreqMask': False,
                     'doHighPass1': True,
                     'doHighPass2': True,
                     'doOverlap': True,
                     'doShift1': True,
                     'doShift2': False,
                     'doSidereal': False,
                     'fRef': 100,
                     'fhigh': 2500,
                     'flow': 40,
                     'frameDuration1': -1,
                     'frameDuration2': -1,
                     'freqsToRemove': "",
                     'hannDuration1': 1,
                     'hannDuration2': 1,
                     'heterodyned': False,
                     'highPassFreq1': 32,
                     'highPassFreq2': 32,
                     'highPassOrder1': 6,
                     'highPassOrder2': 6,
                     'ifo1': 'H1',
                     'ifo2': 'L1',
                     'ignoreMidSegment': True,
                     'mapsize': 200,
                     'maxDSigRatio': 1.2,
                     'minDSigRatio': 0.8,
                     'minDataLoadLength': 500,
                     'nBinsToremove': "",
                     'nResample1': 10,
                     'nResample2': 10,
                     'numSegmentsPerInterval': 9,
                     'outputfilename': 'map',
                     'pp_seed': -1,
                     'relativeInjectionStart': 10,
                     'resampleRate1': 8192,
                     'resampleRate2': 8192,
                     'sampleRate': 16384,
                     'segmentDuration': 4,
                     'simOmegaRef': 0,
                     'stampinj': False,
                     'stochmap': True,
                     'storemats': True,
                     

            
    
        },
        "anteproc_h" : {
            "stamp" : {
            }
    
        },
    
        "anteproc_l" : {
            "stamp" : {
            }
    
        },
    
        "grandStochtrack" : {"fmin": 40,
                            "fmax": 2500,
                            "saveMat": False,
                            "savePlots": True,
                            "seed": -1,
                            "jobNumber": 1,
                            "doGPU": False,
                            "doParallel": False,
                            
        
            "stochtrack" : {
                "T": 10000,
                "F": 3000,
                "mindur": 25,
                "demo": False,
                "doStampFreqMask": True,
                "doPixelCut": 1,
                "pixel_threshold": 10,
                "norm": "npix",
                "flexibleTmap": 1,
                "TmapButter": 1,
                "StampFreqsToRemove": [57, 58, 59, 60, 61, 62, 63, 119, 120, 121],

                "singletrack" : {
                }

            },
            "glitch": {"doCut": False,
                "numBands": 3,
                "doCoincidentCut": 0,
                "doCut": 1,
                "
            },
            "burstegard": {"NCN": 80,
                            "NR": 2,
                            "pixelThreshold": 0.75,
                            "tmetric": 1,
                            "fmetric": 1,
                            "debug": 0,
                            "weightedSNR": 1,
                            "super": 0,
                            "findtrack": 0,
                            "rr": 35      
            }
    
        }
    
    }
    
    