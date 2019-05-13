import os
import copy
import math


#MUON VARIATIONS
muon_pf = ''
muon_corrected = "_corrected" # corrected = Rochester
muon_correctedUp = "_correctedUp"
muon_correctedDown = "_correctedDown"

#MET VARIATIONS
met_pf = ''
met_nom = '_nom'# nom = MET w/ jet smearing
met_jerUp = '_jerUp'
met_jerDown = '_jerDown'
met_jesUp = '_jesTotalUp'
met_jesDown = '_jesTotalDown'
met_unclustUp = '_unclustEnUp'
met_unclustDown = '_unclustEnDown'

selections = {

    'W' : {
        'mc' : {
            'cut': 'Vtype==0 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && ' % muon) \
                #('Muon%s_MET%s_mt[Idx_mu1]>40.' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : 'TMath::Abs(LHEWeight_originalXWGTUP)/LHEWeight_originalXWGTUP*' \
                'puWeight*' \
                'Muon_effSF[Idx_mu1]',
            },
        'data' : {
            'cut': 'Vtype==0 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && ' % muon_pt) \
                #('Muon%s_MET%s_mt[Idx_mu1]>40. ' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : '',
            },
        },

    'Fake' : {
        'mc' : {
            'cut': 'Vtype==1 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && ' % muon_pt) \
                #('Muon%s_MET%s_mt[Idx_mu1]<40. ' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : 'TMath::Abs(LHEWeight_originalXWGTUP)/LHEWeight_originalXWGTUP*' \
                'puWeight*' \
                'Muon_effSF[Idx_mu1]',
            },
        'data' : {
            'cut': 'Vtype==0 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && ' % muon_pt) \
                #('Muon%s_MET%s_mt[Idx_mu1]<40.' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : '',
            },
        },

    'Z' : {
        'mc' : {
            'cut': 'Vtype==2 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && Muon_pt%s[Idx_mu2]>20.' % (muon_pt, muon_pt)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : 'TMath::Abs(LHEWeight_originalXWGTUP)/LHEWeight_originalXWGTUP*' \
                'puWeight*' \
                'Muon_effSF[Idx_mu1]*Muon_effSF[Idx_mu2]',
            },
        'data' : {
            'cut': 'Vtype==2 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Idx_mu1]>25. && Muon_pt%s[Idx_mu2]>20.' % (muon_pt, muon_pt)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : '',
            },
        },
    }

selections['Wplus'] = copy.deepcopy(selections['W'])
selections['Wminus'] = copy.deepcopy(selections['W'])
selections['Wplus']['mc']['cut']  += ' && Muon_charge[Idx_mu1]>0'
selections['Wminus']['mc']['cut'] += ' && Muon_charge[Idx_mu1]<0'

selections['Fakeplus'] = copy.deepcopy(selections['Fake'])
selections['Fakeminus'] = copy.deepcopy(selections['Fake'])
selections['Fakeplus']['mc']['cut']  += ' && Muon_charge[Idx_mu1]>0'
selections['Fakeminus']['mc']['cut'] += ' && Muon_charge[Idx_mu1]<0'


def HistoDict(name_,title_,Nbin_,min_,max_,cut_):
    dictOut = {
    'name' : name_,
    'title' : title_,
    'Nbin' : Nbin_,
    'min' : min_,
    'max' : max_,
    'cut' : cut_
    }
    return dictOut

variables =  {



    'W' : {
        'Muon_pt' : HistoDict(('Muon%s_pt[Idx_mu1]' % muon_pf),"$P_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'Muon_eta' : HistoDict(('Muon%s_eta[Idx_mu1]' % muon_pf),"$\eta$",100,-4,4,"Idx_mu1>=0"),
        'Muon_phi' : HistoDict(('Muon%s_phi[Idx_mu1]' % muon_pf),"$\phi$",30,-math.pi,math.pi,"Idx_mu1>=0"),
        'Muon_pfRelIso04' : HistoDict(('Muon%s_pfRelIso04_all[Idx_mu1]' % muon_pf),"relIso ",100,0,0.4,"Idx_mu1>=0"),
        'Muon_dxy' : HistoDict(('Muon%s_dxy[Idx_mu1]' % muon_pf),"d_{xy} [cm]",100,-0.01,0.01,"Idx_mu1>=0"),
        'Muon_dz' : HistoDict(('Muon%s_dz[Idx_mu1]' % muon_pf),"$d_z$ [cm]",100,-0.1,0.1,"Idx_mu1>=0"),
        'Muon_MET_mt' : HistoDict(('Muon%s_MET%s_mt[Idx_mu1]' % (muon_pf, met_pf)),"$M_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'Muon_MET_h_pt' : HistoDict(('Muon%s_MET%s_hpt[Idx_mu1]' % (muon_pf, met_pf)),"$P_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'Muon_MET_uPar' : HistoDict(('Muon_MET%s_uPar' % met_pf),"P_{T} [GeV]",100,-200,200,"1"),
        'Muon_MET_uPer' : HistoDict(('Muon_MET%s_uPer' % met_pf),"P_{T} [GeV]",100,-200,200,"1"),
        'GenMuon_bare_GenMET_mt' : HistoDict(('GenMuon_bare_GenMET_mt[Idx_mu1]'),"P_{T} [GeV]",100,0,200,"Idx_mu1>=0"),
        'GenMuon_bare_GenMET_hpt' : HistoDict(('GenMuon_bare_GenMET_hpt[Idx_mu1]'),"P_{T} [GeV]",100,0,200,"Idx_mu1>=0"),
        'MET_pt' : HistoDict(('MET%s_pt' % met_pf),"P_{T} [GeV]",100,0,200,"1"),
        'MET_phi' : HistoDict(('MET%s_phi' % met_pf),"$\phi$",30,-math.pi,math.pi,"1"),
        'GenV_bare_mass' : HistoDict(('GenV_bare%s_mass' % muon_pf),"M [GeV]",100,0,200,"(genVtype==14 || genVtype==13)"),
        'GenV_bare_y': HistoDict(('GenV_bare%s_y' % muon_pf),"y",100,-10,10,"(genVtype==14 || genVtype==13)"),
        'GenV_bare_qt' : HistoDict(('GenV_bare%s_qt' % muon_pf),"P_{T} [GeV]",100,0,200,"(genVtype==14 || genVtype==13)"),
        'GenV_bare_CStheta' : HistoDict(('GenV_bare%s_CStheta' % muon_pf),"$\Theta$",100,-1,1,"(genVtype==14 || genVtype==13)"),
        'GenV_bare_CSphi'  : HistoDict(('GenV_bare%s_CSphi' % muon_pf),"$\phi$",30,-math.pi,math.pi,"(genVtype==14 || genVtype==13)"),
        'PV_npvsGood' : HistoDict('PV_npvsGood',"N",100,0,100,"1"),

    },

    'Z' : {
        'Muon_pt_1' : HistoDict(('Muon%s_pt[Idx_mu1]' % muon_pf),"$P_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'Muon_eta_1' : HistoDict(('Muon%s_eta[Idx_mu1]' % muon_pf),"$\eta$",100,-4,4,"Idx_mu1>=0"),
        'Muon_phi_1' : HistoDict(('Muon%s_phi[Idx_mu1]' % muon_pf),"$\phi$",30,-math.pi,math.pi,"Idx_mu1>=0"),
        'Muon_pfRelIso04_1' : HistoDict(('Muon%s_pfRelIso04_all[Idx_mu1]' % muon_pf),"relIso ",100,0,0.4,"Idx_mu1>=0"),
        'Muon_dxy_1' : HistoDict(('Muon%s_dxy[Idx_mu1]' % muon_pf),"d_{xy} [cm]",100,-0.01,0.01,"Idx_mu1>=0"),
        'Muon_dz_1' : HistoDict(('Muon%s_dz[Idx_mu1]' % muon_pf),"$d_z$ [cm]",100,-0.1,0.1,"Idx_mu1>=0"),
        'Muon_pt_2' : HistoDict(('Muon%s_pt[Idx_mu2]' % muon_pf),"$P_{T}$ [GeV]",100,0,200, "Idx_mu2>=0"),
        'Muon_eta_2' : HistoDict(('Muon%s_eta[Idx_mu2]' % muon_pf),"$\eta$",100,-4,4, "Idx_mu2>=0"),
        'Muon_phi_2' : HistoDict(('Muon%s_phi[Idx_mu2]' % muon_pf),"$\phi$",100,-math.pi,math.pi, "Idx_mu2>=0"),
        'Muon_pfRelIso04_2' : HistoDict(('Muon%s_pfRelIso04_all[Idx_mu2]' % muon_pf),"relIso ",100,0,0.4, "Idx_mu2>=0"),
        'Muon_dxy_2' : HistoDict(('Muon%s_dxy[Idx_mu2]' % muon_pf),"d_{xy} [cm]",100,-0.01,0.01, "Idx_mu2>=0"),
        'Muon_dz_2' : HistoDict(('Muon%s_dz[Idx_mu2]' % muon_pf),"$d_z$ [cm]",100,-0.1,0.1, "Idx_mu2>=0"),
        'RecoZ_Muon_mass': HistoDict(('RecoZ_Muon%s_mass' % muon_pf),"M [GeV]",100,0,200,"1"),
        'RecoZ_Muon_y': HistoDict(('RecoZ_Muon%s_y' % muon_pf),"y",100,-10,10,"1"),
        'RecoZ_Muon_pt': HistoDict(('RecoZ_Muon%s_pt' % muon_pf),"P_{T} [GeV]",100,0,200,"1"),
        'RecoZ_Muon_CStheta': HistoDict(('RecoZ_Muon%s_CStheta' % muon_pf),"$\Theta$",100,-1,1,"1"),
        'RecoZ_Muon_CSphi': HistoDict(('RecoZ_Muon%s_CSphi' % muon_pf),"$\phi$",30,-math.pi,math.pi,"1"),
        'RecoZ_Muon_MET_uPar' : HistoDict(('RecoZ_Muon_MET%s_uPar' % met_pf),"P_{T} [GeV]",100,-200,200,"1"),
        'RecoZ_Muon_MET_uPer' : HistoDict(('RecoZ_Muon_MET%s_uPer' % met_pf),"P_{T} [GeV]",100,-200,200,"1"),
        'GenFromRecoZ_GenMuon_bare_mass' : HistoDict(('GenFromRecoZ_GenMuon_bare%s_mass' % muon_pf),"M [GeV]",100,0,200,"1"),
        'GenFromRecoZ_GenMuon_bare_y': HistoDict(('GenFromRecoZ_GenMuon_bare%s_y' % muon_pf),"y",100,-10,10,"1"),
        'GenFromRecoZ_GenMuon_bare_pt' : HistoDict(('GenFromRecoZ_GenMuon_bare%s_pt' % muon_pf),"P_{T} [GeV]",100,0,200,"1"),
        'GenFromRecoZ_GenMuon_bare_CStheta' : HistoDict(('GenFromRecoZ_GenMuon_bare%s_CStheta' % muon_pf),"$\Theta$",100,-1,1,"1"),
        'GenFromRecoZ_GenMuon_bare_CSphi'  : HistoDict(('GenFromRecoZ_GenMuon_bare%s_CSphi' % muon_pf),"$\phi$",30,-math.pi,math.pi,"1"),
        'PV_npvsGood' : HistoDict('PV_npvsGood',"N",100,0,100,"1"),

    },

    'Cut_and_Weight' : {
        'HLT_SingleMu24' : HistoDict(('HLT_SingleMu24'),"",5,0,5,"1"), #temporary
        'HLT_SingleMu27' : HistoDict(('HLT_SingleMu27'),"",5,0,5,"1"), #temporary
        'MET_filters' : HistoDict(('MET_filters'),"",5,0,5,"1"), #temporary
        'nVetoElectrons' : HistoDict(('nVetoElectrons'),"N",5,0,5,"1"), #temporary
        'Muon_pt_1' : HistoDict(('Muon%s_pt[Idx_mu1]' % muon_pf),"$P_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'Muon_pt_2' : HistoDict(('Muon%s_pt[Idx_mu2]' % muon_pf),"$P_{T}$ [GeV]",100,0,200, "Idx_mu2>=0"),
        'Muon_MET_mt' : HistoDict(('Muon%s_MET%s_mt[Idx_mu1]' % (muon_pf, met_pf)),"$M_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'Muon_effSF_1' : HistoDict(('Muon%s_ID_SF[Idx_mu1]*Muon%s_ISO_SF[Idx_mu1]*Muon%s_Trigger_SF[Idx_mu1]' % (muon_pf,muon_pf,muon_pf)),"",100,0.5,1.5,"Idx_mu1>=0"),
        'Muon_effSF_2' : HistoDict(('Muon%s_ID_SF[Idx_mu2]*Muon%s_ISO_SF[Idx_mu2]*Muon%s_Trigger_SF[Idx_mu2]' % (muon_pf,muon_pf,muon_pf)),"",100,0.5,1.5,"Idx_mu2>=0"),
        'puWeight' : HistoDict(('puWeight'),"",100,-10,10,"1"),
        'puWeight_Up' : HistoDict(('puWeightUp'),"",100,-10,10,"1"),
        'puWeight_Down' : HistoDict(('puWeightDown'),"",100,-10,10,"1"),
        'genWeight' : HistoDict(("genWeight"),"",10,-1.5,1.5,"1"), # /abs() doesent' work
    },

    'Variations' : {
        'Muon_pt_pf' : HistoDict(('Muon%s_pt[Idx_mu1]' % muon_pf),"$P_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'Muon_pt_corrected' : HistoDict(('Muon%s_pt[Idx_mu1]' % muon_corrected),"$P_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'Muon_pt_correctedUp' : HistoDict(('Muon%s_pt[Idx_mu1]' % muon_correctedUp),"$P_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'Muon_pt_correctedDown' : HistoDict(('Muon%s_pt[Idx_mu1]' % muon_correctedDown),"$P_{T}$ [GeV]",100,0,200,"Idx_mu1>=0"),
        'MET_pt_pf' : HistoDict(('MET%s_pt' % met_pf),"P_{T} [GeV]",100,0,200,"1"),
        'MET_pt_nom' : HistoDict(('MET%s_pt' % met_nom),"P_{T} [GeV]",100,0,200,"1"),
        'MET_pt_jerUp' : HistoDict(('MET%s_pt' % met_jerUp),"P_{T} [GeV]",100,0,200,"1"),
        'MET_pt_jerDown' : HistoDict(('MET%s_pt' % met_jerDown),"P_{T} [GeV]",100,0,200,"1"),
        'MET_pt_jesTotalUp' : HistoDict(('MET%s_pt' % met_jesUp),"P_{T} [GeV]",100,0,200,"1"),
        'MET_pt_jesTotalDown' : HistoDict(('MET%s_pt' % met_jesDown),"P_{T} [GeV]",100,0,200,"1"),
        'MET_pt_unclustEnUp' : HistoDict(('MET%s_pt' % met_unclustUp),"P_{T} [GeV]",100,0,200,"1"),
        'MET_pt_unclustEnDown' : HistoDict(('MET%s_pt' % met_unclustDown),"P_{T} [GeV]",100,0,200,"1"),
        'GenV_bare_mass' : HistoDict(('GenV_bare%s_mass' % muon_pf),"M [GeV]",100,0,200,"(genVtype==14 || genVtype==13)"),
        'GenV_bare_y': HistoDict(('GenV_bare%s_y' % muon_pf),"y",100,-10,10,"(genVtype==14 || genVtype==13)"),
        'GenV_bare_qt' : HistoDict(('GenV_bare%s_qt' % muon_pf),"P_{T} [GeV]",100,0,200,"(genVtype==14 || genVtype==13)"),
        'GenV_bare_CStheta' : HistoDict(('GenV_bare%s_CStheta' % muon_pf),"$\Theta$",100,-1,1,"(genVtype==14 || genVtype==13)"),
        'GenV_bare_CSphi'  : HistoDict(('GenV_bare%s_CSphi' % muon_pf),"$\phi$",30,-math.pi,math.pi,"(genVtype==14 || genVtype==13)"),
        'GenV_preFSR_mass' : HistoDict(('GenV_preFSR%s_mass' % muon_pf),"M [GeV]",100,0,200,"(genVtype==14 || genVtype==13)"),
        'GenV_preFSR_y': HistoDict(('GenV_preFSR%s_y' % muon_pf),"y",100,-10,10,"(genVtype==14 || genVtype==13)"),
        'GenV_preFSR_qt' : HistoDict(('GenV_preFSR%s_qt' % muon_pf),"P_{T} [GeV]",100,0,200,"(genVtype==14 || genVtype==13)"),
        'GenV_preFSR_CStheta' : HistoDict(('GenV_preFSR%s_CStheta' % muon_pf),"$\Theta$",100,-1,1,"(genVtype==14 || genVtype==13)"),
        'GenV_preFSR_CSphi'  : HistoDict(('GenV_preFSR%s_CSphi' % muon_pf),"$\phi$",30,-math.pi,math.pi,"(genVtype==14 || genVtype==13)"),
        'GenV_dress_mass' : HistoDict(('GenV_dress%s_mass' % muon_pf),"M [GeV]",100,0,200,"(genVtype==14 || genVtype==13)"),
        'GenV_dress_y': HistoDict(('GenV_dress%s_y' % muon_pf),"y",100,-10,10,"(genVtype==14 || genVtype==13)"),
        'GenV_dress_qt' : HistoDict(('GenV_dress%s_qt' % muon_pf),"P_{T} [GeV]",100,0,200,"(genVtype==14 || genVtype==13)"),
        'GenV_dress_CStheta' : HistoDict(('GenV_dress%s_CStheta' % muon_pf),"$\Theta$",100,-1,1,"(genVtype==14 || genVtype==13)"),
        'GenV_dress_CSphi'  : HistoDict(('GenV_dress%s_CSphi' % muon_pf),"$\phi$",30,-math.pi,math.pi,"(genVtype==14 || genVtype==13)"),
    }

}
variables['Fake'] = copy.deepcopy(variables['W'])
