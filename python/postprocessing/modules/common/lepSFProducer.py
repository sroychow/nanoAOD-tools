import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module,

##By definition the first histo in the histos list is the SF, and the following are the errors.
class lepSFProducer(Module):
    def __init__(self, lepFlavour="Muon", leptonSelectionTag, sfFile="MuSF.root", histos=["IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio"], sfTags=['SF'], useAbseta=True, ptEtaAxis=True,dataYear="2016", runPeriod="B"):
        self.lepFlavour = lepFlavour
        self.histos = [h for h in histos]
        self.useAbseta = useAbseta
        self.ptEtaAxis = ptEtaAxis
        effFile = sfFile
        self.effFile = "%s/src/PhysicsTools/NanoAODTools/python/postprocessing/data/leptonSF/%s/year%s/" % (os.environ['CMSSW_BASE'],lepFlavour, dataYear, effFile)
        #Branch prefix to be written in outPut
        branchPrefix = self.lepFlavour + "_" + leptonSelectionTag + "_" + runPeriod
        self.histos    = ROOT.std.vector(str)(len(histos))
        self.histoTags = ROOT.std.vector(str)(len(histos))

        for i in range(len(histos)): self.histos[i] = histos[i]; self.branchName[i] = branchPrefix + sfTags[i];
        try:
            ROOT.gSystem.Load("libPhysicsToolsNanoAODTools")
            dummy = ROOT.WeightCalculatorFromHistogram
        except Exception as e:
            print "Could not load module via python, trying via ROOT", e
            if "/WeightCalculatorFromHistogram_cc.so" not in ROOT.gSystem.GetLibraries():
                print "Loading C++ helper from %s/src/PhysicsTools/NanoAODTools/src/WeightCalculatorFromHistogram.cc" % os.environ['CMSSW_BASE']
                ROOT.gROOT.ProcessLine(".L %s/src/PhysicsTools/NanoAODTools/src/WeightCalculatorFromHistogram.cc++" % os.environ['CMSSW_BASE'])
            dummy = ROOT.WeightCalculatorFromHistogram

    def beginJob(self):
        for i in range(len(self.histos)):
            self._worker_lep_SF[i] = ROOT.WeightCalculatorFromHistogram(self.loadHisto(self.effFile, self.histos[i]))

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for i in range(range(len(self.branchName))):
            self.out.branch(self.branchName[i], "F", lenVar="n" + self.lepFlavour)

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def loadHisto(self,filename,hname):
        tf = ROOT.TFile.Open(filename)
        hist = tf.Get(hname)
        hist.SetDirectory(0)
        tf.Close()
        return hist

    def getSF(self, lepPt, lepEta):
        if self.useAbseta:
            lepEta = abs(lepEta)
        return self._worker_lep_SF[0].getWeight(lepPt, lepEta ) if self.ptEtaAxis else self._worker_lep_SF.getWeight(lepEta, lepPt )

    def getSFError(self, i, lepPt, lepEta):
        if self.useAbseta:
            lepEta = abs(lepEta)
        return self._worker_lep_SF[i].getWeightErr(lepPt, lepEta ) if self.ptEtaAxis else self._worker_lep_SF[i].getWeightErr(lepEta, lepPt )

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        leptons = Collection(event, self.lepFlavour)
        for i in range(len(self.histos)):
            if i == 0:
                sf_lep = [ self.getSF(lep.pt,lep.eta) for lep in leptons ]
            else:
                sf_lep = [ self.getSFError(i, lep.pt,lep.eta) for lep in leptons ]
            self.out.fillBranch(self.branchName[i], sf_lep)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

