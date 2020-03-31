import ROOT
import math
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
##Trigger object matching
def matches_any(mu,trigs,R):
    for t in trigs:        
        dR = math.sqrt((mu.eta-t.eta)**2 + math.acos(math.cos(mu.phi-t.phi))**2) 
        if dR<=R: return True
    return False

def isTriggerObjMatched(mu, trigs, R):
    for t in trigs:        
        dR = math.sqrt((mu.eta - t.eta)**2 + math.acos(math.cos(mu.phi - t.phi))**2) 
        if dR<=R: return True
    return False

def fiducial_muon(mu):
    return (abs(mu.eta)<2.4 and mu.pt>4. and abs(mu.dxy)<0.05 and abs(mu.dz)<0.1)

##NOTE: looseId
def loose_muon(mu):
    return (fiducial_muon(mu) and abs(mu.sip3d) < 4. and (mu.isGlobal or mu.isTracker))

##NOTE: TightId
def tight_muon(mu):
    if not loose_muon(mu): return False
    if mu.pt < 200. and mu.isPFcand:
        return True
    elif mu.pt > 200. and mu.highPtId >= 1: 
	return True
    return False

##Veto against electron
def veto_electron_id(ele):
    etaSC = ele.eta + ele.deltaEtaSC
    if (abs(etaSC) <= 1.479):
        return (ele.pt>10 and abs(ele.dxy)<0.05 and abs(ele.dz)<0.1 and ele.cutBased>=1 and ele.pfRelIso03_all< 0.30)
    else:
        return (ele.pt>10 and abs(ele.dxy)<0.10 and abs(ele.dz)<0.2 and ele.cutBased>=1 and ele.pfRelIso03_all< 0.30)

class preSelection(Module):
    def __init__(self, isMC=True, passall=False, dataYear=2016, trigOnly=False):
        self.isMC = isMC
        self.passall = passall
        self.dataYear = str(dataYear)
        self.trigOnly = trigOnly
        self.tobjlenVar = "nSelTrigObj"
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
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree

        self.out.branch("HLT_SingleMu24", "B", title="Event passes OR of HLT triggers at 24 GeV")

        self.out.branch("HLT_SingleMu27", "B", title="Event passes OR of HLT triggers at 27 GeV")

        self.out.branch("HLT_Dimuon25_Jpsi", "B", title="Event passes HLT_Dimuon25_Jpsi")

        self.out.branch("HLT_Mu17_Photon30_IsoCaloId", "B", title="Event passes HLT_Mu17_Photon30_IsoCaloId")

        self.out.branch("HLT_DoubleMu20_7_Mass0to30_Photon23", "B", title="Event passes HLT_DoubleMu20_7_Mass0to30_Photon23")

        self.out.branch("HLT_DoubleMu4_3_Jpsi", "B", title="Event passes HLT_DoubleMu4_3_Jpsi")

        self.out.branch("MET_filters", "I", title="AND of all MET filters")
        self.out.branch("nVetoElectrons", "I", title="Number of veto electrons")
        self.out.branch("MET_filters", "I", title="AND of all MET filters")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        # Trigger bit
        if self.isMC==False:
            triggers24_OR = ["IsoMu24", "IsoTkMu24"]
            triggers27_OR = ["IsoMu27"]
        else:
            triggers24_OR = ["IsoMu24", "IsoTkMu24"]
            triggers27_OR = ["IsoMu27"]
        HLT_pass24, HLT_pass27 = False, False
        for hlt in triggers24_OR:
            if not hasattr(event, "HLT_"+hlt): continue
            HLT_pass24 |= getattr(event, "HLT_"+hlt)
        for hlt in triggers27_OR:
            if not hasattr(event, "HLT_"+hlt): continue
            HLT_pass27 |= getattr(event, "HLT_"+hlt)

        HLT_passMu17_Photon30 = False
        if hasattr(event, "HLT_Mu17_Photon30_IsoCaloId"):
            HLT_passMu17_Photon30 = getattr(event, "HLT_Mu17_Photon30_IsoCaloId")

	HLT_passDimu25_jpsi = False
	if hasattr(event, "HLT_Dimuon25_Jpsi"):
	    HLT_passDimu25_jpsi = getattr(event, "HLT_Dimuon25_Jpsi")

	HLT_DoubleMu20_7_Mass0to30_Photon23 = False
	if hasattr(event, "HLT_DoubleMu20_7_Mass0to30_Photon23"):
	    HLT_DoubleMu20_7_Mass0to30_Photon23 = getattr(event, "HLT_DoubleMu20_7_Mass0to30_Photon23")

	HLT_DoubleMu4_3_Jpsi = False
	if hasattr(event, "HLT_DoubleMu4_3_Jpsi"):
	    HLT_DoubleMu4_3_Jpsi = getattr(event, "HLT_DoubleMu4_3_Jpsi")



        self.out.fillBranch("HLT_SingleMu24", int(HLT_pass24))
        self.out.fillBranch("HLT_SingleMu27", int(HLT_pass27))
        self.out.fillBranch("HLT_Dimuon25_Jpsi", int(HLT_passDimu25_jpsi))
        self.out.fillBranch("HLT_Mu17_Photon30_IsoCaloId", int(HLT_passMu17_Photon30))
        self.out.fillBranch("HLT_DoubleMu20_7_Mass0to30_Photon23", int(HLT_DoubleMu20_7_Mass0to30_Photon23))
        self.out.fillBranch("HLT_DoubleMu4_3_Jpsi", int(HLT_DoubleMu4_3_Jpsi))

       ##note-Ideally when running on data, should make sure atleast one of the trigges is fired
        
        # MET filters
        met_filters_AND = True
        for key,val in self.met_filters[self.dataYear].items():
            met_filters_AND &=  (not (val & (1 << (1-int(self.isMC)) )) or getattr(event, "Flag_"+key))

        self.out.fillBranch("MET_filters", int(met_filters_AND))

        # Muon selection
        #all_muons = Collection(event, "Muon")
        ##This enumerate part should always be on all_muons
        #loose_muons       = [ [mu,imu] for imu,mu in enumerate(all_muons) if loose_muon(mu) ]
        #tight_muons       = [ [mu,imu] for imu,mu in enumerate(all_muons) if tight_muon(mu) ]
 
        # Electron selection
        all_electrons  = Collection(event, "Electron")    
        veto_electrons = [ [ele,iele] for iele,ele in enumerate(all_electrons) if veto_electron_id(ele) ]
        self.out.fillBranch("nVetoElectrons", len(veto_electrons))
   
        
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

preSelectionModule = lambda : preSelection() 
