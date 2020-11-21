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
    return (abs(mu.eta)<2.4 and mu.pt>10 and abs(mu.dxy)<0.05 and abs(mu.dz)<0.2)
##NOTE: LooseId + iso
def loose_muon_id(mu):
    return (fiducial_muon(mu) and mu.isPFcand and mu.pfRelIso04_all< 0.25 and mu.pt>10)
##NOTE: LooseId only
def loose_muon_idonly(mu):
    return (fiducial_muon(mu) and mu.isPFcand and mu.pt>10)

##NOTE: MediumId + iso
def medium_muon_id(mu):
    return (fiducial_muon(mu) and mu.mediumId and mu.pfRelIso04_all<=0.15 and mu.pt>20)
##NOTE: MediumIdonly
def medium_muon_idonly(mu):
    return (fiducial_muon(mu) and mu.mediumId and mu.pt>20)
##NOTE: MediumId + antiIsolated
def medium_aiso_muon_id(mu):
    return (fiducial_muon(mu) and mu.mediumId and mu.pfRelIso04_all> 0.15 and mu.pt>20)

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
        self.out.branch("Idx_mu1", "I", title="index of W-like muon / index of Z-like 1st muon")
        self.out.branch("Idx_mu2", "I", title="index of Z-like 2nd muon")
        self.out.branch("Vtype", "I", title="0:W-like; 1:Fake-like; 2:Z-like; 3:SS-dimuon; 4:OS Loose Idonly dimuon")
        self.out.branch("Vtype_subcat", "I", title="0:For all Vtypes except 4; 1 = leading mu isolated & sub-leading anti-isolated; 2 = both anti-isolated")
        self.out.branch("MET_filters", "I", title="AND of all MET filters")
        self.out.branch("nVetoElectrons", "I", title="Number of veto electrons")
        self.out.branch("IsTObjmatched_mu1", "B", title="Is muon1 mathced to trigger obj")
        self.out.branch("IsTObjmatched_mu2", "B", title="Is muon2 matched to trigger obj")


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
        self.out.fillBranch("HLT_SingleMu24", int(HLT_pass24))
        for hlt in triggers27_OR:
            if not hasattr(event, "HLT_"+hlt): continue
            HLT_pass27 |= getattr(event, "HLT_"+hlt)
        self.out.fillBranch("HLT_SingleMu27", int(HLT_pass27))

        # MET filters
        met_filters_AND = True
        for key,val in self.met_filters[self.dataYear].items():
            met_filters_AND &=  (not (val & (1 << (1-int(self.isMC)) )) or getattr(event, "Flag_"+key))
        self.out.fillBranch("MET_filters", int(met_filters_AND))

        # Muon selection
        all_muons = Collection(event, "Muon")
        ##This enumerate part should always be on all_muons
        loose_muons       = [ [mu,imu] for imu,mu in enumerate(all_muons) if loose_muon_id(mu) ]
        medium_muons      = [ [mu,imu] for imu,mu in enumerate(all_muons) if medium_muon_id(mu)]
        medium_aiso_muons = [ [mu,imu] for imu,mu in enumerate(all_muons) if medium_aiso_muon_id(mu)]
        looseIdonly_muons = [ [mu,imu] for imu,mu in enumerate(all_muons) if loose_muon_idonly(mu) ]

        loose_muons.sort( key = lambda x: x[0].pt, reverse=True )
        medium_muons.sort(key = lambda x: x[0].pt, reverse=True )
        medium_aiso_muons.sort(key = lambda x: x[0].pt, reverse=True )
        looseIdonly_muons.sort(key = lambda x: x[0].pt, reverse=True )

        # Electron selection
        all_electrons  = Collection(event, "Electron")    
        veto_electrons = [ [ele,iele] for iele,ele in enumerate(all_electrons) if veto_electron_id(ele) ]
        self.out.fillBranch("nVetoElectrons", len(veto_electrons))

        event_flag = -1        
        event_subcat = 0
        (idx1, idx2) = (-1, -1)
        # Z-like event
        if len(loose_muons)>=2:
            if len(loose_muons)==2:
                (idx1, idx2) = (loose_muons[0][1], loose_muons[1][1])
                event_flag = 2 if (loose_muons[0][0].charge+loose_muons[1][0].charge)==0 else 3
            else: event_flag = -1
        # W-like event: 1 loose, 1 medium
        elif len(medium_muons)==1:
            event_flag = 0
            (idx1, idx2) = (medium_muons[0][1], -1)
        # Fake-like event
        elif len(medium_muons)==0 and len(medium_aiso_muons)==1:
            event_flag = 1
            (idx1, idx2) = (medium_aiso_muons[0][1], -1)
        #Two OS muons passing Loose Id only
        elif len(looseIdonly_muons)>=2:
            if len(looseIdonly_muons)==2 and (looseIdonly_muons[0][0].charge + looseIdonly_muons[1][0].charge)== 0:
                (idx1, idx2) = (looseIdonly_muons[0][1], looseIdonly_muons[1][1])
                event_flag = 4
                if (looseIdonly_muons[0][0].pfRelIso04_all < 0.15 and looseIdonly_muons[1][0].pfRelIso04_all >= 0.25) or \
                   (looseIdonly_muons[1][0].pfRelIso04_all < 0.15 and looseIdonly_muons[0][0].pfRelIso04_all >= 0.25) :
                    event_subcat = 1
                elif looseIdonly_muons[0][0].pfRelIso04_all >= 0.15 and looseIdonly_muons[1][0].pfRelIso04_all >= 0.15:
                    event_subcat = 2
            else: event_flag = -1
        # anything else        
        else:   
            event_flag = -1

        ##Selected muon trigger object matching
        all_trigs = Collection(event, "TrigObj")
        #v6 filter bits info: 1 = TrkIsoVVL, 2 = Iso, 4 = OverlapFilter PFTau, 8 = IsoTkMu for Muon
        muon_trigs = [ trig for trig in all_trigs if trig.id==13 and ((trig.filterBits>>0 & 1 ) or (trig.filterBits>>1 & 1 ))]
        mtobj1=isTriggerObjMatched(all_muons[idx1], muon_trigs, R=0.3) if idx1 != -1 else False
        mtobj2=isTriggerObjMatched(all_muons[idx2], muon_trigs, R=0.3) if idx2 != -1 else False
    
        self.out.fillBranch("Idx_mu1", idx1)
        self.out.fillBranch("Idx_mu2", idx2)
        self.out.fillBranch("Vtype", event_flag)
        self.out.fillBranch("Vtype_subcat", event_subcat)
        self.out.fillBranch("IsTObjmatched_mu1", mtobj1)
        self.out.fillBranch("IsTObjmatched_mu2", mtobj2)
        
        if self.trigOnly:
            if event_flag not in [0,1] :
                return (False or self.passall)
            else:
                return True
        
        if (event_flag not in [0,1,2,3,4]) or not (HLT_pass24 or HLT_pass27): 
            return (False or self.passall)

        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

preSelectionModule = lambda : preSelection() 
