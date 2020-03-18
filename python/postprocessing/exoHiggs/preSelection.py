#!/usr/bin/env python        
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module


def fiducial_muon(mu, ptCut, etaCut, dxyCut, dzCut):
    return (abs(mu.eta) < etaCut and mu.pt > ptCut  and abs(mu.dxy) < dxyCut and abs(mu.dz) < dzCut)
def loose_muon_id(mu, ptCut, etaCut, dxyCut, dzCut):
    return (fiducial_muon(mu, ptCut, etaCut, dxyCut, dzCut) and mu.isPFcand and mu.pt>5.)

def fiducial_electron(ele, ptCut, etaCut, dxyCut, dzCut):
    return (abs(ele.eta) < ptCut and ele.pt > etaCut and abs(ele.dxy) < dxyCut and abs(ele.dz) < dzCut)
def loose_electron_id(ele, ptCut, etaCut, dxyCut, dzCut):
    return (fiducial_electron(ele, ptCut, etaCut, dxyCut, dzCut) and ele.isPFcand and ele.pt>5.)


class preSelection(Module):
    def __init__(self, isMC=True, passall=False, dataYear=2016):
        self.isMC = isMC
        self.passall = passall
        self.dataYear = str(dataYear)
        self.writeHistFile = True

        # baded on https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
        # val = 2*(IS FOR DATA) + 1*(IS FOR MC)
        self.met_filters = {
            "2016": { "goodVertices" : 3,
                      "globalTightHalo2016Filter": 3,
                      "HBHENoiseFilter": 3,
                      "HBHENoiseIsoFilter" : 3,
                      "EcalDeadCellTriggerPrimitiveFilter": 3
                      },
            "2017": { "goodVertices": 3,
                      "globalTightHalo2016Filter": 3,
                      "HBHENoiseFilter": 3,
                      "HBHENoiseIsoFilter": 3,
                      "EcalDeadCellTriggerPrimitiveFilter": 3,
                      "BadPFMuonFilter": 3,
                      "BadChargedCandidateFilter": 3,
                      "eeBadScFilter" : 2,
                      #"ecalBadCalibFilter": 3, # needs to be rerun
                      },
            "2018": { "goodVertices": 3,
                      "globalTightHalo2016Filter": 3,
                      "HBHENoiseFilter": 3,
                      "HBHENoiseIsoFilter": 3,
                      "EcalDeadCellTriggerPrimitiveFilter": 3,
                      "BadPFMuonFilter" : 3,
                      "BadChargedCandidateFilter" : 3,
                      "eeBadScFilter" : 2,
                      #"ecalBadCalibFilter": 3,  # needs to be rerun 
                      },
            }
        pass

    def beginJob(self, histFile=None,histDirName=None):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("user_evtype", "I", title="0:two muons same charge; 1: two electrons same charge; 2:e + mu same charge")
        self.out.branch("user_MetFilters", "I", title="AND of all MET filters")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        # MET filters
        met_filters_AND = True
        for key,val in self.met_filters[self.dataYear].items():
            met_filters_AND &=  (not (val & (1 << (1-int(self.isMC)) )) or getattr(event, "Flag_"+key))
        self.out.fillBranch("user_MetFilters", int(met_filters_AND))

        # Muon selection
        all_muons = Collection(event, "Muon")
        loose_muons = [ mu for mu in all_muons if loose_muon_id(mu, 7., 2.4, 0.5, 1.) ]

        loose_muons.sort( key = lambda x: x.pt, reverse=True )

        # Electron selection
        all_electrons  = Collection(event, "Electron")    
        loose_electrons = [ ele for ele in all_electrons if loose_electron_id(ele, 7., 2.5, 0.5, 1.) ]
        loose_electrons.sort( key = lambda x: x.pt, reverse=True )
 

        event_flag = -1        
        #EVFlags- 
        #Dimuon : OSign = 1, SSign = 2
        #Dielectron : OSign = 3, SSign = 4
        #EleMuon : OSign = 5, SSign = 6
        #WLike : Single Lepton medium Id + tight iso: muon = 7, electron = 8 
        if len(loose_muons) >= 2:
            event_flag = 1
        elif len(loose_electrons) >= 2:
            event_flag = 2
	elif len(loose_muons) >= 1 and len(loose_electrons) >= 1:
            event_flag = 3

        if (event_flag not in [1,2,3]): 
            return (False or self.passall)

        self.out.fillBranch("user_evtype", event_flag)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

preSelectionModule = lambda : preSelection() 
