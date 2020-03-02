import ROOT
import math
import copy

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

#global definition of CS angles
#def azimuth(phi):
#    if phi<0.0:
#        phi += 2*math.pi
#    return phi

def getCSangles(muon,neutrino):

    Lp4  = ROOT.TLorentzVector(0.,0.,0.,0.)
    Np4 = ROOT.TLorentzVector(0.,0.,0.,0.)
    if hasattr(muon, "pt"):
        Lp4.SetPtEtaPhiM(muon.pt, muon.eta, muon.phi, muon.mass)
        Np4.SetPtEtaPhiM(neutrino.pt, neutrino.eta, neutrino.phi, 0.)
    else:
        Lp4.SetPtEtaPhiM(muon.Pt(), muon.Eta(), muon.Phi(), muon.M())
        Np4.SetPtEtaPhiM(neutrino.Pt(), neutrino.Eta(), neutrino.Phi(), 0.)
    Wp4 = Lp4 + Np4
    
    Wp4_rot = copy.deepcopy(Wp4)
    Lp4_rot = copy.deepcopy(Lp4)

    # align W/L along x axis
    Wp4_rot.RotateZ( -Wp4.Phi() )
    Lp4_rot.RotateZ( -Wp4.Phi() )

    # first boost
    boostL = Wp4_rot.BoostVector()
    boostL.SetX(0.0)
    boostL.SetY(0.0)
    Lp4_rot.Boost( -boostL )
    Wp4_rot.Boost( -boostL )

    # second boost
    boostT = Wp4_rot.BoostVector()
    Lp4_rot.Boost( -boostT )

    # the CS frame defines the z-axis according to the W pz in the lab 
    flip_z = -1 if Wp4.Rapidity()<0.0 else +1

    # compute PS point
    #print 'flip', flip_z, ': ', azimuth(Lp4_rot.Phi()*flip_z), ' --- ', math.atan2(Lp4_rot.Py()*flip_z,Lp4_rot.Px()*flip_z)
    return [Lp4_rot.CosTheta()*flip_z, math.atan2(Lp4_rot.Py()*flip_z, Lp4_rot.Px())]

class CSVariables(Module):
    def __init__(self,  Wtypes=['bare', 'preFSR', 'dress']):
        self.Wtypes = Wtypes
        self.vars = ['CStheta','CSphi']
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for t in self.Wtypes:
            for v in self.vars:
                self.out.branch("GenV_%s_%s" % (t,v), "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        results = {}
        for t in self.Wtypes:
            for v in self.vars:
                results[t+'_'+v] = 0.0
            
        if abs(event.genVtype) in [13,14]:
            genParticles = Collection(event, "GenPart")
            genDressedLeptons = Collection(event,"GenDressedLepton")
            idx_nu = event.Idx_nu
            for t in self.Wtypes:
                genCollection = genParticles if t in ["bare", "preFSR"] else genDressedLeptons
                idx_mu1 = getattr(event, "Idx_"+t+"_mu1")
                idx_mu2 = getattr(event, "Idx_"+t+"_mu2")
                if idx_mu1>=0:
                    ps = getCSangles(genCollection[idx_mu1], (genParticles[idx_nu] if idx_nu>=0 else genCollection[idx_mu2]) )
                    for iv,v in enumerate(self.vars):
                        results["%s_%s" % (t,v)] = ps[iv]

        for t in self.Wtypes:
            for v in self.vars:
                self.out.fillBranch("GenV_%s_%s" % (t,v), results["%s_%s" % (t,v)])

        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

CSAngleModule = lambda : CSVariables()
