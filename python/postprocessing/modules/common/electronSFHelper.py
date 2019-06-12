import os, sys
import subprocess

from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSFProducer import *

#lepSFhelper template
#(lepFlavour="Muon", leptonSelectionTag, sfFile="MuSF.root", histos=["IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio"], sfTags=['SF'], useAbseta=True, ptEtaAxis=True,dataYear="2016", runPeriod="B"):
#Egamma SF files - (x axis supercluter eta, y axis pt) for all years
#Files for 2016 in from the twiki are named 2016LegacyReReco_ElectronMVA80_Fall17V2.root, name changed to 2016_ElectronMVA80noiso.root
#
###Possible values of leptonSelectionTags are:-
#   MVA80noiso, MVA80, MVA90noiso, MVA90
###

def electronSFcreator(leptonSelectionTag, dataYear):
    sfactorFile = dataYear + "2017_Electron" + leptonSelectionTag + ".root"
    histoList  = ['EGamma_SF2D', 'EGamma_SF2D']
    branchTags = ['SF', 'Total']
    eleSF = lambda : lepSFProducerV2( lepFlavour="Electron", leptonSelectionTag=leptonSelectionTag, sfFile=sfactorFile, histos=histoList, sfTags=branchTags, dataYear=dataYear, ptEtaAxis=False, useAbseta=False)
    return eleSF
