import ROOT
import math
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

def isTriggerObjMatched(mu, trigs, DR):
    for i,t in trigs:
        if deltaR(mu.eta, mu.phi, t.eta, t.phi) <= DR:
            return (i,True)
    return (-1,False)

class muonTriggerMatchProducer(Module):
    def __init__(self, saveIdTriggerObject=True, deltaRforMatch=0.3, minNumberMatchedMuons=0):
        self.saveIdTriggerObject = saveIdTriggerObject # if True save also id of object in TrigObj collection that is matched to the muon, as a new Muon_trigObjIdx collection
        self.deltaRforMatch      = deltaRforMatch
        self.minNumberMatchedMuons = minNumberMatchedMuons
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Muon_hasTriggerMatch", "I", lenVar="nMuon")
        if self.saveIdTriggerObject:
            self.out.branch("Muon_trigObjIdx",      "I", lenVar="nMuon")
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        trgObjs = Collection(event, "TrigObj")
        muons   = Collection(event, "Muon")
        muon_trigs = [ (i,trig) for i,trig in enumerate(trgObjs) if trig.id == 13 and ((trig.filterBits>>0 & 1 ) or (trig.filterBits>>1 & 1 ))]
        trigMatch = []
        trigIdx   = []  # -1 if no match, else index of trigger object in TrigObj collection
        for m in muons:
            (i,isTrigMatch) = isTriggerObjMatched(m,muon_trigs,DR=self.deltaRforMatch)
            trigIdx.append(i)
            trigMatch.append(isTrigMatch)
        self.out.fillBranch("Muon_hasTriggerMatch", trigMatch)
        if self.saveIdTriggerObject:
            self.out.fillBranch("Muon_trigObjIdx", trigIdx)
        
        nMatchedMuons = 0
        for t in trigMatch:
            if t:
                nMatchedMuons += 1
        if nMatchedMuons < self.minNumberMatchedMuons:
            return False
        else:
            return True


#########################################################


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

muTrigMatch = lambda : muonTriggerMatchProducer(saveIdTriggerObject=True, deltaRforMatch=0.3, minNumberMatchedMuons=0)
# if minNumberMatchedMuon > 0, discard events if there are less than minNumberMatchedMuons muons that are matched to trigger objects
