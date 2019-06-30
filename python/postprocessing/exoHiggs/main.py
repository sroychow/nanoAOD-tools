#!/usr/bin/env python
import os, sys
import ROOT
import argparse
import subprocess

ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.muonScaleResProducer import *
#from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSFProducer_v2 import *

from PhysicsTools.NanoAODTools.postprocessing.exoHiggs.preSelection import *
from PhysicsTools.NanoAODTools.postprocessing.exoHiggs.triggerSelection import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

parser = argparse.ArgumentParser("")
parser.add_argument('-jobNum',    '--jobNum',   type=int, default=1,      help="")
parser.add_argument('-crab',      '--crab',     type=int, default=0,      help="")
parser.add_argument('-passall',   '--passall',  type=int, default=0,      help="")
parser.add_argument('-isMC',      '--isMC',     type=int, default=1,      help="")
parser.add_argument('-maxEvents', '--maxEvents',type=int, default=-1,	  help="")
parser.add_argument('-dataYear',  '--dataYear', type=int, default=2016,   help="")
parser.add_argument('-jesUncert', '--jesUncert',type=str, default="Total",help="")
parser.add_argument('-redojec',   '--redojec',  type=int, default=0,      help="")
parser.add_argument('-runPeriod', '--runPeriod',type=str, default="B",    help="")
args = parser.parse_args()
isMC      = args.isMC
crab      = args.crab
passall   = args.passall
dataYear  = args.dataYear
maxEvents = args.maxEvents
runPeriod = args.runPeriod
redojec   = args.redojec
jesUncert = args.jesUncert
 
print "isMC =", bcolors.OKGREEN, isMC, bcolors.ENDC, \
    "crab =", bcolors.OKGREEN, crab, bcolors.ENDC, \
    "passall =", bcolors.OKGREEN, passall,  bcolors.ENDC, \
    "dataYear =",  bcolors.OKGREEN,  dataYear,  bcolors.ENDC, \
    "maxEvents =", bcolors.OKGREEN, maxEvents, bcolors.ENDC 

# run with crab
if crab:
    from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

################################################ JEC
"""print "JECTag =", bcolors.OKGREEN, jecTag,  bcolors.ENDC, \
    "jesUncertainties =", bcolors.OKGREEN, jmeUncert,  bcolors.ENDC, \
    "redoJec =", bcolors.OKGREEN, redojec,  bcolors.ENDC
"""
jmeCorrections = jetmetUncertainties2016 if isMC else jetRecalib2016BCD 
################################################ MET

################################################ PU
#pu reweight modules
puWeightProducer = puWeight_2016
if dataYear==2017:
    puWeightProducer = puWeight_2017
elif dataYear==2018:
    puWeightProducer = puWeight_2018

################################################ Muons
#Rochester correction for muons
muonScaleRes = muonScaleRes2016
if dataYear==2017:
    muonScaleRes = muonScaleRes2017
elif dataYear==2018:
    muonScaleRes = muonScaleRes2018
    #print bcolors.OKBLUE, "No module %s will be run" % "muonScaleRes", bcolors.ENDC
    
################################################ GEN

##This is temporary for testing purpose
input_dir = "/eos/cms/store/"

ifileMC = ""
if dataYear==2016:
    ifileMC = "mc/RunIISummer16NanoAODv3/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v2/00000/7667A3B0-2509-E911-B82E-FA163E64DEEE.root"
elif dataYear==2017:#not correct
    ifileMC = "mc/RunIIFall17NanoAODv4/DYJetsToLL_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/20000/41874784-9F25-7C49-B4E3-6EECD93B77CA.root"    
elif dataYear==2018:
    ifileMC = "mc/RunIIAutumn18NanoAODv4/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/270000/320474A7-2A79-E042-BD91-BD48021177A2.root"

ifileDATA = ""
if dataYear==2016:
    ifileDATA = "data/Run2016B_ver2/SingleMuon/NANOAOD/Nano1June2019_ver2-v1/240000/1103C280-826D-E346-9750-BDB64D295F1A.root"
elif dataYear==2017:#not correct
    ifileDATA = "data/Run2017E/DoubleMuon/NANOAOD/31Mar2018-v1/710000/A452D873-4B6E-E811-BE23-FA163E60E3B4.root"
elif dataYear==2018:#not correct
    ifileDATA = "data/Run2018D/SingleMuon/NANOAOD/14Sep2018_ver2-v1/110000/41819B10-A73F-BC4A-9CCC-FD93D80D5465.root"

input_files = []
modules = []

if isMC:
    input_files.append( input_dir+ifileMC )
    modules = [    triggerModule(),
                   puWeightProducer(), 
                   preSelection(isMC=isMC, passall=passall, dataYear=dataYear),  
                   jmeCorrections(),
              ]
    # add before recoZproducer
    if muonScaleRes!=None: modules.insert(3, muonScaleRes())
else:
    input_files.append( input_dir+ifileDATA )
    modules = [
                triggerModule(), 
		preSelection(isMC=isMC, passall=passall, dataYear=dataYear)
              ]
    # add before recoZproducer
    if jmeCorrections!=None: modules.insert(2,jmeCorrections())
    # add before recoZproducer
    if muonScaleRes!=None:   modules.insert(2, muonScaleRes())

treecut = ("Entry$<" + str(maxEvents) if maxEvents > 0 else None)
kd_file = "keep_and_drop_MC.txt" if isMC else "keep_and_drop_DATA.txt"

p = PostProcessor(outputDir=".",  
                  inputFiles=(input_files if crab==0 else inputFiles()),
                  cut=treecut,      
                  modules=modules,
                  provenance=True,
                  outputbranchsel=kd_file,
                  fwkJobReport=(False if crab==0 else True),
                  jsonInput=(None if crab==0 else runsAndLumis())
                  )
p.run()
print "DONE"
os.system("ls -lRt")
