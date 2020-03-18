import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class triggerSelection(Module):
    def __init__(self, isMC=True, passall=False, dataYear=2016, trigOnly=False):
        self.isMC = isMC
        self.passall = passall
        self.dataYear = str(dataYear)
        self.trigOnly = trigOnly
        self.trigDict = {
            "SingleMu"  : ["HLT_IsoMu20", "HLT_IsoTkMu20", "HLT_IsoMu22", "HLT_IsoTkMu22", "HLT_IsoMu24", "HLT_IsoTkMu24"],
            "SingleEle" : ["HLT_Ele25_eta2p1_WPTight_Gsf", "HLT_Ele27_WPTight_Gsf", "HLT_Ele27_eta2p1_WPLoose_Gsf", "HLT_Ele32_eta2p1_WPTight_Gsf"],
            "DoubleEle" : ["HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",  "HLT_DoubleEle33_CaloIdL_GsfTrkIdVL"],
            "DoubleMu"  : ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL", "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL"],
        }
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("user_HLT_SingleMu", "B", title="Event passes OR of all Single Muon HLT triggers")
        self.out.branch("user_HLT_SingleEle", "B", title="Event passes OR of Single Electron HLT triggers")
        self.out.branch("user_HLT_DoubleMu", "B", title="Event passes OR of all Double Muon HLT triggers")
        self.out.branch("user_HLT_DoubleEle", "B", title="Event passes OR of Double Electron HLT triggers")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        # Trigger bit
        passSingleMu, passSingleEle, passDoubleMu, passDoubleEle = False, False, False, False

        #Check trigger decisions##SingleMu
        for hlt in self.trigDict["SingleMu"]:
            if not hasattr(event, hlt): continue
            passSingleMu |= getattr(event, hlt)
        self.out.fillBranch("user_HLT_SingleMu", int(passSingleMu))

        #Check trigger decisions##SingleEle
        for hlt in self.trigDict["SingleEle"]:
            if not hasattr(event, hlt): continue
            passSingleEle |= getattr(event, hlt)
        self.out.fillBranch("user_HLT_SingleEle", int(passSingleEle))

        #Check trigger decisions##DoubleMu
        for hlt in self.trigDict["DoubleMu"]:
            if not hasattr(event, hlt): continue
            passDoubleMu |= getattr(event, hlt)
        self.out.fillBranch("user_HLT_DoubleMu", int(passDoubleMu))

        #Check trigger decisions##DoubleEle
        for hlt in self.trigDict["DoubleEle"]:
            if not hasattr(event, hlt): continue
            passDoubleEle |= getattr(event, hlt)
        self.out.fillBranch("user_HLT_DoubleEle", int(passDoubleEle))

        if not passSingleMu and not passSingleEle and not passDoubleMu and not passDoubleEle:
            return (False or self.passall)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
triggerModule = lambda : triggerSelection() 
