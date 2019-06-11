#!/usr/bin/env python
import os, sys
import subprocess

from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSFProducer import *

triggerHistoDict  = {
"2016" : {
    'IsoMu24' : ['IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio', 'IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio'],
    'Mu50'    : ['IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio', 'IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio']
    },
"2017" : {
    'IsoMu27' : ['IsoMu27_PtEtaBins/pt_abseta_ratio', 'IsoMu27_PtEtaBins/pt_abseta_ratio'],
    'Mu50'    : ['Mu50_PtEtaBins/pt_abseta_ratio', 'Mu50_PtEtaBins/pt_abseta_ratio'],
    },
"2018" : {
    'IsoMu24'    : ['IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio', 'IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio'],
    'Mu50_Mu100' : ['Mu50_OR_OldMu100_OR_TkMu100_PtEtaBins/pt_abseta_ratio', 'Mu50_OR_OldMu100_OR_TkMu100_PtEtaBins/pt_abseta_ratio']
    }
}

triggerBranchTags = {
"2016" :  { 'IsoMu24' : ['SF', 'STAT'], 'Mu50' : ['SF', 'ST'] },
"2017" :  { 'IsoMu27' : ['SF', 'STAT'], 'Mu50' : ['SF', 'ST'] },
"2018" :  { 'IsoMu24' : ['SF', 'STAT'], 'Mu50_Mu100' : ['SF', 'ST'] },
}


idHistoDict  = {
"2016" : {
    'HighPtID' : ['NUM_HighPtID_DEN_genTracks_eta_pair_newTuneP_probe_pt', 'NUM_HighPtID_DEN_genTracks_eta_pair_newTuneP_probe_pt_stat', 'NUM_HighPtID_DEN_genTracks_eta_pair_newTuneP_probe_pt_syst'],
    'LooseID'  : ['NUM_LooseID_DEN_genTracks_eta_pt', 'NUM_LooseID_DEN_genTracks_eta_pt_stat', 'NUM_LooseID_DEN_genTracks_eta_pt_syst'],
    'MediumID' : ['NUM_MediumID_DEN_genTracks_eta_pt', 'NUM_MediumID_DEN_genTracks_eta_pt_stat', 'NUM_MediumID_DEN_genTracks_eta_pt_syst'],
    'TightID'  : ['NUM_TightID_DEN_genTracks_eta_pt', 'NUM_TightID_DEN_genTracks_eta_pt_stat', 'NUM_TightID_DEN_genTracks_eta_pt_syst']
    },

"2017" : {
    'LooseID'        : ['NUM_LooseID_DEN_genTracks_pt_abseta', 'NUM_LooseID_DEN_genTracks_pt_abseta_stat', 'NUM_LooseID_DEN_genTracks_pt_abseta_syst'],
    'MediumID'       : ["NUM_MediumID_DEN_genTracks_pt_abseta", "NUM_MediumID_DEN_genTracks_pt_abseta_stat", "NUM_MediumID_DEN_genTracks_pt_abseta_syst"],
    'TightID'        : ['NUM_TightID_DEN_genTracks_pt_abseta', 'NUM_TightID_DEN_genTracks_pt_abseta_stat', 'NUM_TightID_DEN_genTracks_pt_abseta_syst'],
    'TrkHighPtID'    : ['NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta', 'NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_stat', 'NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_syst'],
    'SoftID'         : ['NUM_SoftID_DEN_genTracks_pt_abseta', 'NUM_SoftID_DEN_genTracks_pt_abseta_stat', 'NUM_SoftID_DEN_genTracks_pt_abseta_syst'],
    'MediumPromptID' : ['NUM_MediumPromptID_DEN_genTracks_pt_abseta', 'NUM_MediumPromptID_DEN_genTracks_pt_abseta_stat', 'NUM_MediumPromptID_DEN_genTracks_pt_abseta_syst']
    },

"2018" : {
    'LooseID'        : ['NUM_LooseID_DEN_genTracks_pt_abseta', 'NUM_LooseID_DEN_genTracks_pt_abseta_stat', 'NUM_LooseID_DEN_genTracks_pt_abseta_syst'],
    'MediumID'       : ["NUM_MediumID_DEN_genTracks_pt_abseta", "NUM_MediumID_DEN_genTracks_pt_abseta_stat", "NUM_MediumID_DEN_genTracks_pt_abseta_syst"],
    'TightID'        : ['NUM_TightID_DEN_genTracks_pt_abseta', 'NUM_TightID_DEN_genTracks_pt_abseta_stat', 'NUM_TightID_DEN_genTracks_pt_abseta_syst'],
    'TrkHighPtID'    : ['NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta', 'NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_stat', 'NUM_TrkHighPtID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_syst'],
    'SoftID'         : ['NUM_SoftID_DEN_genTracks_pt_abseta', 'NUM_SoftID_DEN_genTracks_pt_abseta_stat', 'NUM_SoftID_DEN_genTracks_pt_abseta_syst'],
    'MediumPromptID' : ['NUM_MediumPromptID_DEN_genTracks_pt_abseta', 'NUM_MediumPromptID_DEN_genTracks_pt_abseta_stat', 'NUM_MediumPromptID_DEN_genTracks_pt_abseta_syst']
    }
}

idBranchTags = {
"2016" : {
    'HighPtID' : ['SF', 'STAT', 'SYST'],
    'LooseID'  : ['SF', 'STAT', 'SYST'],
    'MediumID' : ['SF', 'STAT', 'SYST'],
    'TightID'  : ['SF', 'STAT', 'SYST']
    },

"2017" : {
    'LooseID'        : ['SF', 'STAT', 'SYST'],
    'MediumID'       : ['SF', 'STAT', 'SYST'],
    'TightID'        : ['SF', 'STAT', 'SYST'],
    'TrkHighPtID'    : ['SF', 'STAT', 'SYST'],
    'SoftID'         : ['SF', 'STAT', 'SYST'],
    'MediumPromptID' : ['SF', 'STAT', 'SYST']
    },

"2018" : {
    'LooseID'        : ['SF', 'STAT', 'SYST'],
    'MediumID'       : ['SF', 'STAT', 'SYST'],
    'TightID'        : ['SF', 'STAT', 'SYST'],
    'TrkHighPtID'    : ['SF', 'STAT', 'SYST'],
    'SoftID'         : ['SF', 'STAT', 'SYST'],
    'MediumPromptID' : ['SF', 'STAT', 'SYST']
    },
}

isoHistoDict = {
"2016" : {
    'LooseRelIso_LooseID'            : ['NUM_LooseRelIso_DEN_LooseID_eta_pt', 'NUM_LooseRelIso_DEN_LooseID_eta_pt_stat', 'NUM_LooseRelIso_DEN_LooseID_eta_pt_syst'],
    'LooseRelIso_MediumID'           : ['NUM_LooseRelIso_DEN_MediumID_eta_pt', 'NUM_LooseRelIso_DEN_MediumID_eta_pt_stat', 'NUM_LooseRelIso_DEN_MediumID_eta_pt_syst'],
    'LooseRelIso_TightIDandIPCut'    : ['NUM_LooseRelIso_DEN_TightIDandIPCut_eta_pt', 'NUM_LooseRelIso_DEN_TightIDandIPCut_eta_pt_stat', 'NUM_LooseRelIso_DEN_TightIDandIPCut_eta_pt_syst'],
    'LooseRelTkIso_HighPtIDandIPCut' : ['NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_eta_pair_newTuneP_probe_pt', 'NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_eta_pair_newTuneP_probe_pt_stat', 'NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_eta_pair_newTuneP_probe_pt_syst'],
    'TightRelIso_MediumID'           : [' NUM_TightRelIso_DEN_MediumID_eta_pt', ' NUM_TightRelIso_DEN_MediumID_eta_pt_stat', ' NUM_TightRelIso_DEN_MediumID_eta_pt_syst'],
    'TightRelIso_TightIDandIPCut'    : ['NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt', 'NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt_stat', 'NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt_syst']
    },

"2017" : {
    'TightRelIso_MediumID'        : [' NUM_TightRelIso_DEN_MediumID_pt_abseta ', ' NUM_TightRelIso_DEN_MediumID_pt_abseta_stat ', ' NUM_TightRelIso_DEN_MediumID_pt_abseta_syst '],
    'LooseRelIso_MediumID'        : [' NUM_LooseRelIso_DEN_MediumID_pt_abseta ', ' NUM_LooseRelIso_DEN_MediumID_pt_abseta_stat ', ' NUM_LooseRelIso_DEN_MediumID_pt_abseta_syst '],
    'TightRelIso_TightIDandIPCut' : [' NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta ', ' NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_stat ', ' NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_syst '],
    'LooseRelIso_LooseID'         : [' NUM_LooseRelIso_DEN_LooseID_pt_abseta ', ' NUM_LooseRelIso_DEN_LooseID_pt_abseta_stat ', ' NUM_LooseRelIso_DEN_LooseID_pt_abseta_syst '],
    'TightRelTkIso_TrkHighPtID'   : [' NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta ', ' NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat ',  'NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst '],
    'TightRelTkIso_TrkHighPtID'   : [' NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta ', ' NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat ', ' NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst '],
    'LooseRelTkIso_TrkHighPtID'   : [' NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta ', ' NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat ', ' NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst '],
    'LooseRelTkIso_HighPtIDandIPCut' : ['NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta ', ' NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat ', ' NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst '],
    'LooseRelIso_TightIDandIPCut' :    [' NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta ', ' NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_stat ', ' NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_syst '],
    'TightRelTkIso_DEN_HighPtIDandIPCut' : [' NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta ', ' NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat ', ' NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst '],
    },

"2018" : {
'TightRelIso_MediumID'           : [' NUM_TightRelIso_DEN_MediumID_pt_abseta ', ' NUM_TightRelIso_DEN_MediumID_pt_abseta_stat ', ' NUM_TightRelIso_DEN_MediumID_pt_abseta_syst '],
'LooseRelIso_MediumID'           : [' NUM_LooseRelIso_DEN_MediumID_pt_abseta ', ' NUM_LooseRelIso_DEN_MediumID_pt_abseta_stat ', ' NUM_LooseRelIso_DEN_MediumID_pt_abseta_syst '],
'TightRelIso_TightIDandIPCut'    : [' NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta ', ' NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_stat ', ' NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta_syst '],
'LooseRelIso_LooseID'            : [' NUM_LooseRelIso_DEN_LooseID_pt_abseta ', ' NUM_LooseRelIso_DEN_LooseID_pt_abseta_stat ', ' NUM_LooseRelIso_DEN_LooseID_pt_abseta_syst '],
'TightRelTkIso_TrkHighPtID'      : [' NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta ', ' NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat ', ' NUM_TightRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst '],
'LooseRelTkIso_TrkHighPtID'      : [' NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta ', ' NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_stat ', ' NUM_LooseRelTkIso_DEN_TrkHighPtID_pair_newTuneP_probe_pt_abseta_syst '],
'LooseRelTkIso_HighPtIDandIPCut' : [' NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta ', ' NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat ', ' NUM_LooseRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst '],
'LooseRelIso_TightIDandIPCut'    : [' NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta ', ' NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_stat ', ' NUM_LooseRelIso_DEN_TightIDandIPCut_pt_abseta_syst '],
'TightRelTkIso_HighPtID'         : [' NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta ', ' NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_stat ', ' NUM_TightRelTkIso_DEN_HighPtIDandIPCut_pair_newTuneP_probe_pt_abseta_syst '],
}
}

isoBranchTags = {
"2016" : {
    'LooseRelIso_LooseID'            : ['SF', 'STAT', 'SYST'],
    'LooseRelIso_MediumID'           : ['SF', 'STAT', 'SYST'],
    'LooseRelIso_TightIDandIPCut'    : ['SF', 'STAT', 'SYST'],
    'LooseRelTkIso_HighPtIDandIPCut' : ['SF', 'STAT', 'SYST'],
    'TightRelIso_MediumID'           : ['SF', 'STAT', 'SYST'],
    'TightRelIso_TightIDandIPCut'    : ['SF', 'STAT', 'SYST']
    },
"2017" : {
    'TightRelIso_MediumID'               : ['SF', 'STAT', 'SYST'],
    'LooseRelIso_MediumID'               : ['SF', 'STAT', 'SYST'],
    'TightRelIso_TightIDandIPCut'        : ['SF', 'STAT', 'SYST'],
    'LooseRelIso_LooseID'                : ['SF', 'STAT', 'SYST'],
    'TightRelTkIso_TrkHighPtID'          : ['SF', 'STAT', 'SYST'],
    'TightRelTkIso_TrkHighPtID'          : ['SF', 'STAT', 'SYST'],
    'LooseRelTkIso_TrkHighPtID'          : ['SF', 'STAT', 'SYST'],
    'LooseRelTkIso_HighPtIDandIPCut'     : ['SF', 'STAT', 'SYST'],
    'LooseRelIso_TightIDandIPCut'        : ['SF', 'STAT', 'SYST'],
    'TightRelTkIso_DEN_HighPtIDandIPCut' : ['SF', 'STAT', 'SYST'],
    },
"2018" : {
    'TightRelIso_MediumID'           : ['SF', 'STAT', 'SYST'],
    'LooseRelIso_MediumID'           : ['SF', 'STAT', 'SYST'],
    'TightRelIso_TightIDandIPCut'    : ['SF', 'STAT', 'SYST'],
    'LooseRelIso_LooseID'            : ['SF', 'STAT', 'SYST'],
    'TightRelTkIso_TrkHighPtID'      : ['SF', 'STAT', 'SYST'],
    'LooseRelTkIso_TrkHighPtID'      : ['SF', 'STAT', 'SYST'],
    'LooseRelTkIso_HighPtIDandIPCut' : ['SF', 'STAT', 'SYST'],
    'LooseRelIso_TightIDandIPCut'    : ['SF', 'STAT', 'SYST'],
    'TightRelTkIso_HighPtID'         : ['SF', 'STAT', 'SYST'],
    }
}


#lepSFhelper template
#(lepFlavour="Muon", leptonSelectionTag, sfFile="MuSF.root", histos=["IsoMu24_OR_IsoTkMu24_PtEtaBins/pt_abseta_ratio"], sfTags=['SF'], useAbseta=True, ptEtaAxis=True,dataYear="2016", runPeriod="B"):
class muonSFHelper():
    def __init__(self, leptonSelectionTag, dataYear="2016", runPeriod="B"):

        self.dataYear = dataYear
        self.runPeriod = runPeriod
        self.leptonSelectionTag = leptonSelectionTag
        ##This is required beacuse for 2016 ID SF, binning is done for eta;x-axis is eta
        ##But in any case, maybe useful if POG decides to switch from abs(eta) to eta
        ##Not used for Trigger
        self.useAbsEta = { "2016" : False, "2017" : True, "2018" : True}
        self.ptEtaAxis = { "2016" : False, "2017" : True, "2018" : True}
    def getTriggerSFCreator(triggerName):
        runPeriod = "BCDEF" if self.runPeriod in "BCDEF" else "GF"
        effFile = "Run" + runPeriod + "_SF_Trigger.root"
        mu_Trigger = lambda : lepSFProducerV2( lepFlavour="Muon", self.leptonSelectionTag, sfFile=effFile, histos=triggerHistoDict[self.runPeriod][triggerName], sfTags = triggerBranchTags[self.runPeriod][triggerName], dataYear=self.dataYear, runPeriod= self.runPeriod)
        return mu_Trigger

    def getIDSFCreator(idName):useAbseta=useAbsEta[dataYear], ptEtaAxis = self.ptEtaAxis[self.dataYear],
        runPeriod = "BCDEF" if self.runPeriod in "BCDEF" else "GF"
        effFile = "Run" + runPeriod + "_SF_ID.root"
        mu_ID = lambda : lepSFProducerV2( lepFlavour="Muon", self.leptonSelectionTag, sfFile=effFile, histos=idHistoDict[self.runPeriod][idName], sfTags = idBranchTags[self.runPeriod][idName], useAbseta=self.useAbsEta[self.dataYear], ptEtaAxis = self.ptEtaAxis[self.dataYear], dataYear=self.dataYear, runPeriod= self.runPeriod)
        return mu_ID

    def getISOSFCreator(isoName):useAbseta=useAbsEta[dataYear], ptEtaAxis = self.ptEtaAxis[self.dataYear],
        runPeriod = "BCDEF" if self.runPeriod in "BCDEF" else "GF"
        effFile = "Run" + runPeriod + "_SF_ISO.root"
        mu_ISO = lambda : lepSFProducerV2( lepFlavour="Muon", self.leptonSelectionTag, sfFile=effFile, histos=idHistoDict[self.runPeriod][isoName], sfTags = idBranchTags[self.runPeriod][isoName], useAbseta=self.useAbsEta[self.dataYear], ptEtaAxis = self.ptEtaAxis[self.dataYear], dataYear=self.dataYear, runPeriod= self.runPeriod)
        return mu_ISO
