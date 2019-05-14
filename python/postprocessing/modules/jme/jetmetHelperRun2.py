#!/usr/bin/env python
import os, sys
import subprocess

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *

# JEC for MET
jecTagsMC = {'2016' : 'Summer16_07Aug2017_V11_MC', 
             '2017' : 'Fall17_17Nov2017_V32_MC', 
             '2018' : 'Autumn18_V8_MC'}

jecTagsDATA = { '2016B' : 'Summer16_07Aug2017BCD_V11_DATA', 
                '2016C' : 'Summer16_07Aug2017BCD_V11_DATA', 
                '2016D' : 'Summer16_07Aug2017BCD_V11_DATA', 
                '2016E' : 'Summer16_07Aug2017EF_V11_DATA', 
                '2016F' : 'Summer16_07Aug2017EF_V11_DATA', 
                '2016G' : 'Summer16_07Aug2017GH_V11_DATA', 
                '2016H' : 'Summer16_07Aug2017GH_V11_DATA', 
                '2016H' : 'Summer16_07Aug2017GH_V11_DATA', 
                '2017B' : 'Fall17_17Nov2017B_V32_DATA', 
                '2017C' : 'Fall17_17Nov2017C_V32_DATA', 
                '2017D' : 'Fall17_17Nov2017DE_V32_DATA', 
                '2017E' : 'Fall17_17Nov2017DE_V32_DATA', 
                '2017F' : 'Fall17_17Nov2017F_V32_DATA', 
                '2018A' : 'Autumn18_RunA_V8_DATA',
                '2018B' : 'Autumn18_RunB_V8_DATA',
                '2018C' : 'Autumn18_RunC_V8_DATA',
                '2018D' : 'Autumn18_RunD_V8_DATA',
                } 

jerTagsMC = {'2016' : 'Summer16_25nsV1_MC',
             '2017' : 'Fall17_V3_MC',
             '2018' : 'Fall17_V3_MC'
            }

jerTagsDATA = {'2016' : 'Summer16_25nsV1_DATA',
             '2017' : 'Fall17_V3_DATA',
             '2018' : 'Fall17_V3_DATA'
            }

def createJMECorrector(isMC=True, dataYear=2016, runPeriod="B", jesUncert="Total", redojec=True, saveJets=False, crab=False):
    
    jecTag = jecTagsMC[str(dataYear)] if isMC else jecTagsDATA[str(dataYear) + runPeriod]

    jmeUncert = [x for x in jesUncert.split(",")]

    jerTag_ = jerTagsMC[str(dataYear)] if isMC else jerTagsDATA[str(dataYear)]

    print 'JEC=', jecTag, '\t JER=', jerTag_
    #untar the zipped jec files when submitting crab jobs
    if crab :
        jesDatadir = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoAODTools/data/jme/"
        jesInputFile = jesDatadir + jecTag + ".tar.gz"
        if os.path.isfile(jesInputFile):
            print "Using JEC files from: %s" % jesInputFile
            subprocess.call(['tar', "-xzvf", jesInputFile, "-C", jesDatadir])
        else:
            print "JEC file %s does not exist" % jesInputFile
        jerInputFile = jesDatadir + jerTag_ + ".tar.gz"
        if os.path.isfile(jerInputFile):
            print "Using JER files from: %s" % jerInputFile
            subprocess.call(['tar', "-xzvf", jerInputFile, "-C", jesDatadir])
        else:
            print "JER file %s does not exist" % jerInputFile
    jmeCorrections = None
    #jme corrections
    if isMC:
        jmeCorrections = lambda : jetmetUncertaintiesProducer(era=str(dataYear), globalTag=jecTag, jesUncertainties=jmeUncert, \
                                                                  redoJEC=redojec, saveJets = saveJets, jerTag=jerTag_)
    else:
        if redojec:
            jmeCorrections = lambda : jetRecalib(globalTag=jecTag, saveJets = saveJets)
    return jmeCorrections
