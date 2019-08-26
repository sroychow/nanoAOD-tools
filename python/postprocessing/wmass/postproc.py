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
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.muonScaleResProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSFProducer_v2 import *

from PhysicsTools.NanoAODTools.postprocessing.wmass.preSelection import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.additionalVariables import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.genLepSelection import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.CSVariables import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.genVproducer import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.recoZproducer import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.harmonicWeights import *

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
parser.add_argument('-genOnly',    '--genOnly',type=int, default=0,    help="")
parser.add_argument('-trigOnly',    '--trigOnly',type=int, default=0,    help="")
args = parser.parse_args()
isMC      = args.isMC
crab      = args.crab
passall   = args.passall
dataYear  = args.dataYear
maxEvents = args.maxEvents
runPeriod = args.runPeriod
redojec   = args.redojec
jesUncert = args.jesUncert
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

################################################ JEC
"""print "JECTag =", bcolors.OKGREEN, jecTag,  bcolors.ENDC, \
    "jesUncertainties =", bcolors.OKGREEN, jmeUncert,  bcolors.ENDC, \
    "redoJec =", bcolors.OKGREEN, redojec,  bcolors.ENDC
"""
#Function definition
#createJMECorrector(isMC=True, dataYear=2016, runPeriod="B", jesUncert="Total", redoJec=True, saveJets=False, crab=False)
jmeCorrections = createJMECorrector(isMC, str(dataYear), runPeriod, jesUncert, redojec, False, crab)
################################################ MET
# MET dictionary 
doJERVar     = True
doJESVar     = True
doUnclustVar = True
metdict = {
    "PF" : { "tag" : "MET",  "systs"  : [""] },
    #"TK"    : { "tag" : "TkMET",    "systs"  : [""] },
    #"puppi" : { "tag" : "PuppiMET", "systs"  : [""] },
    }

if jmeCorrections!=None:
    metdict["PF"]["systs"].extend( ["nom"] ) 

if isMC:
    metdict["GEN"] = {"tag" : "GenMET", "systs"  : [""]}
    if doJERVar:
        metdict["PF"]["systs"].extend( ["jerUp", "jerDown"] )
    if doJESVar:
        metdict["PF"]["systs"].extend( ["jesTotalUp", "jesTotalDown"] )
    if doUnclustVar:
        metdict["PF"]["systs"].extend( ["unclustEnUp", "unclustEnDown"] )

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
    
# muon dictionary
mudict = { "PF" : { "tag" : "Muon", "systs" : [""] } }
if dataYear in [2016, 2017, 2018]:
    mudict["roccor"] = { "tag" : "Muon",   "systs"  : ["corrected", "correctedUp",  "correctedDown"] }
if isMC:
    mudict["GEN"] = { "tag" : "GenMuon",  "systs" : ["bare"] }
    # these exist only for 2017
    #if dataYear==2017:
    #mudict["roccor"]["systs"] = ["corrected", "correctedUp",  "correctedDown"]    

##Muon SF
triggerHisto = {2016:['IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio', 'IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio'], 
                2017:['IsoMu27_PtEtaBins/pt_abseta_ratio', 'IsoMu27_PtEtaBins/pt_abseta_ratio'], 
                2018:['IsoMu24_PtEtaBins/pt_abseta_ratio', 'IsoMu24_PtEtaBins/pt_abseta_ratio']
                }
idHisto = {2016: ["NUM_MediumID_DEN_genTracks_eta_pt", "NUM_MediumID_DEN_genTracks_eta_pt_stat", "NUM_MediumID_DEN_genTracks_eta_pt_syst"], 
           2017: ["NUM_MediumID_DEN_genTracks_pt_abseta", "NUM_MediumID_DEN_genTracks_pt_abseta_stat", "NUM_MediumID_DEN_genTracks_pt_abseta_syst"],
           2018: ["NUM_MediumID_DEN_genTracks_pt_abseta", "NUM_MediumID_DEN_genTracks_pt_abseta"]
           }

isoHisto = {2016: ["NUM_TightRelIso_DEN_MediumID_eta_pt", "NUM_TightRelIso_DEN_MediumID_eta_pt_stat", "NUM_TightRelIso_DEN_MediumID_eta_pt_syst"],
            2017: ["NUM_TightRelIso_DEN_MediumID_pt_abseta", "NUM_TightRelIso_DEN_MediumID_pt_abseta_stat", "NUM_TightRelIso_DEN_MediumID_pt_abseta_syst"],
            2018: ["NUM_TightRelIso_DEN_MediumID_pt_abseta", "NUM_TightRelIso_DEN_MediumID_pt_abseta"]
            }
##This is required beacuse for 2016 ID SF, binning is done for eta;x-axis is eta
##But in any case, maybe useful if POG decides to switch from abs(eta) to eta
##Not used for Trigger
useAbsEta = { 2016 : False, 2017 : True, 2018 : True}
ptEtaAxis = { 2016 : False, 2017 : True, 2018 : True}

if dataYear == 2016:
    lepSFTrig = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "Trigger", histos=triggerHisto[dataYear], dataYear=str(dataYear), runPeriod="BCDEF")
    lepSFTrig_GH = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "Trigger", histos=triggerHisto[dataYear], dataYear=str(dataYear), runPeriod="GH")
    lepSFID   = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "ID", histos=idHisto[dataYear], dataYear=str(dataYear), runPeriod="BCDEF", useAbseta=useAbsEta[dataYear], ptEtaAxis=ptEtaAxis[dataYear])
    lepSFISO  = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "ISO", histos=isoHisto[dataYear], dataYear=str(dataYear), runPeriod="BCDEF", useAbseta=useAbsEta[dataYear], ptEtaAxis=ptEtaAxis[dataYear])
    lepSFID_GH   = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "ID", histos=idHisto[dataYear], dataYear=str(dataYear), runPeriod="GH", useAbseta=useAbsEta[dataYear], ptEtaAxis=ptEtaAxis[dataYear])
    lepSFISO_GH  = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "ISO", histos=isoHisto[dataYear], dataYear=str(dataYear), runPeriod="GH", useAbseta=useAbsEta[dataYear], ptEtaAxis=ptEtaAxis[dataYear])
elif dataYear == 2017:
    lepSFTrig = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "Trigger", histos=triggerHisto[dataYear], dataYear=str(dataYear), runPeriod="BCDEF")
    lepSFID   = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "ID", histos=idHisto[dataYear], dataYear=str(dataYear), runPeriod="BCDEF", useAbseta=useAbsEta[dataYear], ptEtaAxis=ptEtaAxis[dataYear])
    lepSFISO  = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "ISO", histos=isoHisto[dataYear], dataYear=str(dataYear), runPeriod="BCDEF", useAbseta=useAbsEta[dataYear], ptEtaAxis=ptEtaAxis[dataYear])
elif dataYear == 2018:
    lepSFTrig = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "Trigger", histos=triggerHisto[dataYear], dataYear=str(dataYear), runPeriod="ABCD")
    lepSFID   = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "ID", histos=idHisto[dataYear], dataYear=str(dataYear), runPeriod="ABCD", useAbseta=useAbsEta[dataYear], ptEtaAxis=ptEtaAxis[dataYear])
    lepSFISO  = lambda : lepSFProducerV2(lepFlavour="Muon", cut = "ISO", histos=isoHisto[dataYear], dataYear=str(dataYear), runPeriod="ABCD", useAbseta=useAbsEta[dataYear], ptEtaAxis=ptEtaAxis[dataYear])
################################################ GEN

Wtypes = ['bare', 'preFSR', 'dress']

################################################

##This is temporary for testing purpose
#input_dir = "/gpfs/ddn/srm/cms/store/"
input_dir = "/eos/cms/store/"

ifileMC = ""
if dataYear==2016:
    ifileMC = "mc/RunIISummer16NanoAODv5/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext2-v1/120000/FF69DF6E-2494-F543-95BF-F919B911CD23.root"
    #input_dir = "/gpfs/ddn/srm/cms/store/user/emanca/"
    #ifileMC = "NanoWMassV4/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/NanoWMass/190218_175825/0000/myNanoProdMc_NANO_41.root"
elif dataYear==2017:
    ifileMC = "mc/RunIIFall17NanoAODv4/DYJetsToLL_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/20000/41874784-9F25-7C49-B4E3-6EECD93B77CA.root"    
elif dataYear==2018:
    ifileMC = "mc/RunIIAutumn18NanoAODv4/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano14Dec2018_102X_upgrade2018_realistic_v16-v1/270000/320474A7-2A79-E042-BD91-BD48021177A2.root"

ifileDATA = ""
if dataYear==2016:
    ifileDATA = "data/Run2016D/DoubleEG/NANOAOD/Nano14Dec2018-v1/280000/481DA5C0-DF96-5640-B5D1-208F52CAC829.root"
elif dataYear==2017:
    ifileDATA = "data/Run2017E/DoubleMuon/NANOAOD/31Mar2018-v1/710000/A452D873-4B6E-E811-BE23-FA163E60E3B4.root"
elif dataYear==2018:
    ifileDATA = "data/Run2018D/SingleMuon/NANOAOD/14Sep2018_ver2-v1/110000/41819B10-A73F-BC4A-9CCC-FD93D80D5465.root"

input_files = []
modules = []

if isMC:
    input_files.append( input_dir+ifileMC )
    if (not genOnly and not trigOnly):
        modules = [puWeightProducer(), 
                   preSelection(isMC=isMC, passall=passall, dataYear=dataYear),  
	           lepSFTrig(),
                   lepSFID(),
                   lepSFISO(),
                   jmeCorrections(),
                   recoZproducer(mudict=mudict, isMC=isMC),
                   additionalVariables(isMC=isMC, mudict=mudict, metdict=metdict), 
                   genLeptonSelection(Wtypes=Wtypes), 
                   CSVariables(Wtypes=Wtypes), 
                   genVproducer(Wtypes=Wtypes),
                   #harmonicWeights(Wtypes=Wtypes),
                   ]
        # add before recoZproducer
        if muonScaleRes!=None: modules.insert(5, muonScaleRes())
        if dataYear == 2016: 
            modules.insert(2,lepSFTrig_GH())
            modules.insert(3,lepSFID_GH())
            modules.insert(4,lepSFISO_GH())
    elif genOnly: 
        modules = [genLeptonSelection(Wtypes=Wtypes, filterByDecay=True),CSVariables(Wtypes=Wtypes),genVproducer(Wtypes=Wtypes)]
    elif trigOnly: 
        modules = [puWeightProducer(),preSelection(isMC=True, passall=passall, dataYear=dataYear, trigOnly=True)]
    else:
        modules = []
else:
    input_files.append( input_dir+ifileDATA )
    modules = [preSelection(isMC=isMC, passall=passall, dataYear=dataYear), 
               recoZproducer(mudict=mudict, isMC=isMC),
               additionalVariables(isMC=isMC, mudict=mudict, metdict=metdict),
               ]
    # add before recoZproducer
    if jmeCorrections!=None: modules.insert(1,jmeCorrections())
    # add before recoZproducer
    if muonScaleRes!=None:   modules.insert(1, muonScaleRes())

treecut = ("Entry$<" + str(maxEvents) if maxEvents > 0 else None)
kd_file = "keep_and_drop"
if isMC:
    kd_file += "_MC"
    if genOnly: kd_file+= "GenOnly"
    elif trigOnly: kd_file+= "TrigOnly"
else:
    kd_file += "_Data"
kd_file += ".txt"

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
