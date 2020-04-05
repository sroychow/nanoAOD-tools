#!/usr/bin/env python
import os, sys
import ROOT
import argparse
import subprocess

ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.muonScaleResProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
from PhysicsTools.NanoAODTools.postprocessing.ztojpsig.preSelection import *

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
parser.add_argument('-runPeriod', '--runPeriod',type=str, default="B",    help="")
parser.add_argument('-genOnly',    '--genOnly',type=int, default=0,    help="")
parser.add_argument('-trigOnly',    '--trigOnly',type=int, default=0,    help="")
args = parser.parse_args()
isMC      = args.isMC
crab      = args.crab
passall   = args.passall
dataYear  = args.dataYear
maxEvents = args.maxEvents
runPeriod = args.runPeriod
genOnly   = args.genOnly
trigOnly  = args.trigOnly
 
print "isMC =", bcolors.OKGREEN, isMC, bcolors.ENDC, \
    "genOnly =", bcolors.OKGREEN, genOnly, bcolors.ENDC, \
    "crab =", bcolors.OKGREEN, crab, bcolors.ENDC, \
    "passall =", bcolors.OKGREEN, passall,  bcolors.ENDC, \
    "dataYear =",  bcolors.OKGREEN,  dataYear,  bcolors.ENDC, \
    "maxEvents =", bcolors.OKGREEN, maxEvents, bcolors.ENDC 

if genOnly and not isMC:
    print "Cannot run with --genOnly=1 option and data simultaneously"
    exit(1)
if trigOnly and not isMC:
    print "Cannot run with --trigOnly=1 option and data simultaneously"
    exit(1)

# run with crab
if crab:
    from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

################################################ MET
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
    
################################################PREFIRE Weights
jetROOT='L1prefiring_jetpt_2016BtoH'
photonROOT='L1prefiring_photonpt_2016BtoH'

if dataYear == 2017: 
    jetROOT='L1prefiring_jetpt_2017BtoF'
    photonROOT='L1prefiring_photonpt_2017BtoF'

prefireCorr= lambda : PrefCorr(jetroot=jetROOT + '.root', jetmapname=jetROOT, photonroot=photonROOT + '.root', photonmapname=photonROOT)
################################################

##This is temporary for testing purpose
#input_dir = "/eos/user/s/sroychow/jpsi/nanoInput/"
input_dir = "/eos/cms/store/"

"""
/eos/user/s/sroychow/jpsi/nanoInput/ZGTo2MuG_MMuM:
A897EC1C-6A36-4149-BC29-6EE7BE5DC1E7.root

/eos/user/s/sroychow/jpsi/nanoInput/ZToJPsiGamma:
8EEB3BA0-9E04-AC44-AA78-ED82C143F4E3.root
"""


ifileMC = ""
if dataYear==2016:#has to be changed
    ifileMC="ZToJPsiGamma/8EEB3BA0-9E04-AC44-AA78-ED82C143F4E3.root"
elif dataYear==2017:
    ifileMC = "ZToJPsiGamma/8EEB3BA0-9E04-AC44-AA78-ED82C143F4E3.root"
    #ifileMC = "ZGTo2MuG_MMuM/A897EC1C-6A36-4149-BC29-6EE7BE5DC1E7.root"
elif dataYear==2018:#has to be chanched
    ifileMC = "mc/RunIIAutumn18NanoAODv5/WJetsToLNu_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/Nano1June2019_102X_upgrade2018_realistic_v19-v1/100000/FEF8F001-02FD-E449-B1FC-67C8653CDCEC.root"

ifileDATA = ""
if dataYear==2016:
    #ifileDATA = "data/Run2016D/DoubleEG/NANOAOD/Nano14Dec2018-v1/280000/481DA5C0-DF96-5640-B5D1-208F52CAC829.root"
    if not isMC: input_dir = 'root://xrootd.ba.infn.it//store/'
    ifileDATA = "data/Run2016D/SingleMuon/NANOAOD/Nano1June2019-v1/40000/FBA773A7-6C8A-FA4A-AAB2-939609D9B339.root"
elif dataYear==2017:
    #ifileDATA = "data/Run2017E/DoubleMuon/NANOAOD/31Mar2018-v1/710000/A452D873-4B6E-E811-BE23-FA163E60E3B4.root"
    ifileDATA = "data/Run2017B/MuonEG/NANOAOD/Nano25Oct2019-v1/240000/14D82EAF-5DAC-274B-BA8E-6A761DB9B259.root"
elif dataYear==2018:
    #ifileDATA = "data/Run2018D/SingleMuon/NANOAOD/14Sep2018_ver2-v1/110000/41819B10-A73F-BC4A-9CCC-FD93D80D5465.root"
    ifileDATA = "data/Run2018B/DoubleMuon/NANOAOD/Nano1June2019-v1/40000/20FCA3B4-6778-7441-B63C-307A21C7C2F0.root"

input_files = []
modules = []

if isMC:
    input_files.append( input_dir+ifileMC )
    if (not genOnly and not trigOnly):
        modules = [puWeightProducer(),
                   preSelection(isMC=isMC, passall=passall, dataYear=dataYear), 
                   prefireCorr(),
                   muonScaleRes(),
                   #jmeCorrections()
                   ]
else:
    input_files.append( input_dir+ifileDATA )
    modules = [preSelection(isMC=isMC, passall=passall, dataYear=dataYear), 
               muonScaleRes(),
               #jmeCorrections()
               ]
treecut = ("Entry$<" + str(maxEvents) if maxEvents > 0 else None)
kd_file = "keep_and_drop"
if isMC:
    kd_file += "_MC"
    #if genOnly: kd_file+= "GenOnly"
    #elif trigOnly: kd_file+= "TrigOnly"
else:
    kd_file += "_DATA"
kd_file += ".txt"

print "Keep drop file used:", kd_file

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
os.system("ls -lR")
