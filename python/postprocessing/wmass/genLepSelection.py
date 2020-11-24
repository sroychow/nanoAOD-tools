import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class leptonSelection(Module):
    def __init__(self):
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("GenPart_preFSRLepIdx1", "I")
        self.out.branch("GenPart_preFSRLepIdx2", "I")
        self.out.branch("GenDressedLepton_dressMuonIdx", "I")
        self.out.branch("genVtype", "I")
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        genParticles = Collection(event, "GenPart")

        status746leptons = []
        otherleptons = []
        prefsrleptons =[]
        myIdx = -99
        myNuIdx = -99
        
        for i,g in enumerate(genParticles) :
            if not abs(g.pdgId) in [13, 14]: continue
            if (g.status == 746): status746leptons.append( (i,g) )
            elif (g.status == 1 and ( (g.statusFlags  >> 8) & 1) ): otherleptons.append( (i,g) )
            else: continue
            

        if   (len(status746leptons)) == 2:
            prefsrleptons=status746leptons
        elif (len(status746leptons) == 1 and len(otherleptons) == 1):
            prefsrleptons=status746leptons+otherleptons
        elif (len(status746leptons) == 0 and len(otherleptons) == 2):
            prefsrleptons=otherleptons

        prefsrleptons.sort(key = lambda x: x[1].pt, reverse=True ) #order by pt in decreasing order
        if not len(prefsrleptons) == 2:
            print 'found', len(prefsrleptons), 'leptons'
            print 'did not find exactly 2 proper leptons. check your code!'
            for (i,g) in prefsrleptons:
                print g.pdgId, g.pt, g.eta
        gVtype=prefsrleptons[0][1].pdgId

        self.out.fillBranch("genVtype", gVtype)

        self.out.fillBranch("GenPart_preFSRLepIdx1", prefsrleptons[0][0] if abs(prefsrleptons[0][1].pdgId) < 0 else prefsrleptons[1][0])
        self.out.fillBranch("GenPart_preFSRLepIdx2", prefsrleptons[1][0] if abs(prefsrleptons[0][1].pdgId) < 0 else prefsrleptons[0][0])
        

        ############################################## dressed muon selection from GenDressedLepton collection
        genDressedLeptons = Collection(event,"GenDressedLepton")

        myIdx = -99
        dressmuons = []
        for i,l in enumerate(genDressedLeptons) :
            if abs(l.pdgId)==13: dressmuons.append((i,l))
        
        if len(dressmuons)>0:
            dressmuons.sort(key = lambda x: x[1].pt, reverse=True ) #order by pt in decreasing order
            myIdx = dressmuons[0][0]

        self.out.fillBranch("GenDressedLepton_dressMuonIdx",myIdx)
        
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

genLeptonSelectModule = lambda : leptonSelection() 
 
