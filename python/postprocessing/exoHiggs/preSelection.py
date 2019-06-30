import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module


def fiducial_muon(mu, ptCut, etaCut, dxyCut, dzCut):
    return (abs(mu.eta) < etaCut and mu.pt > ptCut  and abs(mu.dxy) < dxyCut and abs(mu.dz) < dzCut)
def loose_muon_id(mu, ptCut, etaCut, dxyCut, dzCut):
    return (fiducial_muon(mu, ptCut, etaCut, dxyCut, dzCut) and mu.isPFcand and mu.pt>5.)
def medium_muon_id(mu):
    return (fiducial_muon(mu,ptCut, etaCut, dxyCut, dzCut) and mu.mediumId and mu.pt>20.)

#anti-isolated muon selection
def medium_aiso_muon_id(mu):
    return (fiducial_muon(mu) and mu.mediumId and mu.pfRelIso04_all> 0.30 and mu.pt>20)

def fiducial_electron(ele, ptCut, etaCut, dxyCut, dzCut):
    return (abs(ele.eta) < ptCut and ele.pt > etaCut and abs(ele.dxy) < dxyCut and abs(ele.dz) < dzCut)
def loose_electron_id(ele, ptCut, etaCut, dxyCut, dzCut):
    return (fiducial_electron(ele, ptCut, etaCut, dxyCut, dzCut) and ele.isPFcand and ele.pt>5.)
def medium_electron_id(ele, ptCut, etaCut, dxyCut, dzCut):
    return (fiducial_electron(ele, ptCut, etaCut, dxyCut, dzCut) and ele.mediumId and ele.pt>20.)

#anti-isolated muon selection
def medium_aiso_electron_id(ele, ptCut, etaCut, dxyCut, dzCut):
    return (fiducial_ele(ele, ptCut, etaCut, dxyCut, dzCut) and ele.mediumId and ele.pfRelIso04_all> 0.30 and ele.pt>20)

def veto_electron_id(ele, ptCut, etaCut, dxyCut, dzCut):
    etaSC = ele.eta + ele.deltaEtaSC
    if (abs(etaSC) <= 1.479):
        return (ele.pt>10 and abs(ele.dxy)<0.05 and abs(ele.dz)<0.1 and ele.cutBased>=1 and ele.pfRelIso03_all< 0.30)
    else:
        return (ele.pt>10 and abs(ele.dxy)<0.10 and abs(ele.dz)<0.2 and ele.cutBased>=1 and ele.pfRelIso03_all< 0.30)


class preSelection(Module):
    def __init__(self, isMC=True, passall=False, dataYear=2016):
        self.isMC = isMC
        self.passall = passall
        self.dataYear = str(dataYear)

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
        self.out.branch("EVtype", "I", title="0:two muons same charge; 1: two electrons same charge; 2:e + mu same charge")
        self.out.branch("MET_filters", "I", title="AND of all MET filters")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        # MET filters
        met_filters_AND = True
        for key,val in self.met_filters[self.dataYear].items():
            met_filters_AND &=  (not (val & (1 << (1-int(self.isMC)) )) or getattr(event, "Flag_"+key))
        self.out.fillBranch("MET_filters", int(met_filters_AND))

        # Muon selection
        all_muons = Collection(event, "Muon")
        loose_muons = [ mu for mu in all_muons if loose_muon_id(mu, 5., 2.4, 0.5, 1.) ]

        loose_muons.sort( key = lambda x: x.pt, reverse=True )

        # Electron selection
        all_electrons  = Collection(event, "Electron")    
        loose_electrons = [ ele for ele in all_electrons if loose_electron_id(ele, 5., 2.4, 0.5, 1.) ]
        loose_electrons.sort( key = lambda x: x.pt, reverse=True )

        event_flag = 9999        
       
        if len(loose_muons) >= 2:
	    mcharge = loose_muons[0].charge
            for i in range(1,len(loose_muons)):
                if loose_muons[i].charge ==  mcharge:
                    event_flag = 0
		    break
        elif len(loose_electrons) >= 2:
            echarge = loose_electrons[0].charge
            for i in range(1,len(loose_electrons)):
                if loose_electrons[i].charge ==  echarge:
                    event_flag = 1
		    break
	elif len(loose_muons) >= 1 and len(loose_electrons) >= 1:
	    for mu in loose_muons:
                mcharge = mu.charge
	        for ele in loose_electrons:
		    if mcharge == ele.charge:
		        event_flag = 2
			break
	else:
	    event_flag = 100		     

        if (event_flag not in [0,1,2,3]): 
            return (False or self.passall)

        self.out.fillBranch("EVtype", event_flag)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

preSelectionModule = lambda : preSelection() 
