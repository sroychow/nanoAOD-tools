from ROOT import *
from ROOT import gStyle
import os
import argparse
gROOT.Reset()
gROOT.SetBatch(True)
gStyle.SetOptStat("eMRi")  #(012211100)
from definitions import variables


parser = argparse.ArgumentParser("Fast Plotter for postprocessing")
parser.add_argument('-Nevents',     '--Nevents',        type=int,  default=100,               action='store', help='number of events to plot')
parser.add_argument('-inputFile',   '--inputFile',      type=str,                             action='store', help='input file. No default provided')
parser.add_argument('-outputFile',  '--outputFile',     type=str, default='DQM_output.root',  action='store', help='output file name')
parser.add_argument('-dataset',     '--dataset',        type=str, default='dataset',          action='store', help='dataset name')
parser.add_argument('-refFile',     '--refFile',        type=str, default='',                 action='store', help='reference File. If empty not evaluated')
parser.add_argument('-refDataset',  '--refDataset',     type=str, default='refDataset',       action='store', help='refDataset name. Used only if refFile is given')

args = parser.parse_args()
Nevents     = args.Nevents
inputFile   = args.inputFile
outputFile  = args.outputFile
dataset     = args.dataset
refFile     = args.refFile
refDataset  = args.refDataset

myfile = TFile(inputFile)
mytree = myfile.Events

print("tree entries",mytree.GetEntries())

variables
canvaslist = {}
histolist = {}
output = TFile(outputFile,"recreate")

os.mkdir('./systematics')

#dimuon????? check!
for key_part, part in variables.items() :

    if(key_part!="Variations") :

        if(key_part=="W") :
            goodV = "0"
        elif(key_part=="Z") :
            goodV = "2"
        elif(key_part=="Fake"):
            goodV = "1"
        else :
            goodV="-999"
        for key_var, var in part.items() :

            hName = key_part+'_'+var["name"]
            histolist[hName] = TH1F(hName,hName,var["Nbin"],var["min"],var["max"])
            if(key_part!='Cut_and_Weight') :
                mytree.Project(hName,var["name"],"Vtype=="+goodV+" &&"+var['cut'],"",Nevents)
            else :
                mytree.Project(hName,var["name"],"Vtype>=0 &&"+var["cut"],"",Nevents)
            histolist[hName].GetXaxis().SetTitle(var["title"])
            histolist[hName].SetBinContent(var["Nbin"],histolist[hName].GetBinContent(var["Nbin"])+histolist[hName].GetBinContent(var["Nbin"]+1)) #overflow in last bin
            histolist[hName].SetBinContent(1,histolist[hName].GetBinContent(1)+histolist[hName].GetBinContent(0)) #underflow in first bin
            histolist[hName].SetLineWidth(2)

            canvaslist['c_'+key_part+'_'+key_var] = TCanvas('c_'+key_part+'_'+key_var,'c_'+key_part+'_'+key_var, 800,600)
            canvaslist['c_'+key_part+'_'+key_var].cd()
            histolist[hName].Draw()
            canvaslist['c_'+key_part+'_'+key_var].SetGrid()

            legSample = TLegend(0.1,0.95,0.7,0.9)
            legSample.SetHeader(dataset)
            legSample.SetBorderSize(0)
            legSample.Draw("SAME")
            legSample.SetFillStyle(0)

            canvaslist['c_'+key_part+'_'+key_var].SaveAs(dataset+'_'+key_part+'_'+key_var+'.png')

            output.cd()
            canvaslist['c_'+key_part+'_'+key_var].Write()
            histolist[hName].Write()


    #Variations
    else :
        for key_var, var in part.items() :
            hName = key_part+'_'+var["name"]
            histolist[hName] = TH1F(hName,hName,var["Nbin"],var["min"],var["max"])
            mytree.Project(hName,var["name"],"Vtype>=0 &&"+var["cut"],"",Nevents)
            histolist[hName].GetXaxis().SetTitle(var["title"])
            histolist[hName].SetBinContent(var["Nbin"],histolist[hName].GetBinContent(var["Nbin"])+histolist[hName].GetBinContent(var["Nbin"]+1)) #overflow in last bin
            histolist[hName].SetBinContent(1,histolist[hName].GetBinContent(1)+histolist[hName].GetBinContent(0)) #underflow in first bin
            histolist[hName].Sumw2()

        def RatioPlot(name_num, name_den,range_min,range_max,logFlag) :

                    #ratio between histograms

                    hName = 'histoDiv_'+part[name_num]['name']+"_over_"+part[name_den]['name']
                    canvaslist['c_'+key_part+'_'+ hName] = TCanvas('c_'+key_part+'_'+hName,'c_'+key_part+'_'+hName, 800,600)
                    histolist[hName] = TH1F(hName,hName,part[name_den]["Nbin"],part[name_den]["min"],part[name_den]["max"])
                    histolist[hName].Divide(histolist[key_part+'_'+part[name_num]['name']],histolist[key_part+'_'+part[name_den]['name']])
                    histolist[hName].SetLineWidth(2)

                    canvaslist['c_'+key_part+'_'+ hName].cd()
                    canvaslist['c_'+key_part+'_'+ hName].SetGrid()
                    if(logFlag) :
                        canvaslist['c_'+key_part+'_'+ hName].SetLogy()
                    histolist[hName].Draw()

                    legSample = TLegend(0.1,0.95,0.7,0.9)
                    legSample.SetHeader(dataset)
                    legSample.SetBorderSize(0)
                    legSample.Draw("SAME")
                    legSample.SetFillStyle(0)

                    canvaslist['c_'+key_part+'_'+hName].SaveAs('./systematics/'+dataset+'_'+key_part+'_'+hName+'.png')
                    output.cd()
                    canvaslist['c_'+key_part+'_'+ hName].Write()
                    histolist[hName].Write()



                    #ratio events-by-events

                    hName = 'EvByEv_'+part[name_num]['name']+"_over_"+part[name_den]['name']
                    histolist[hName] = TH1F(hName,hName,part[name_den]["Nbin"],range_min,range_max)
                    mytree.Project(hName,part[name_num]['name']+'/'+part[name_den]['name'],"Vtype>=0 &&"+part[name_den]['cut'],"",Nevents)
                    histolist[hName].GetXaxis().SetTitle(name_num+'/'+name_den)
                    histolist[hName].SetBinContent(part[name_den]["Nbin"],histolist[hName].GetBinContent(part[name_den]["Nbin"])+histolist[hName].GetBinContent(part[name_den]["Nbin"]+1)) #overflow in last bin
                    histolist[hName].SetBinContent(1,histolist[hName].GetBinContent(1)+histolist[hName].GetBinContent(0))
                    histolist[hName].SetLineWidth(2)

                    canvaslist['c_'+key_part+'_'+ hName] = TCanvas('c_'+key_part+'_'+hName,'c_'+key_part+'_'+hName, 800,600)
                    canvaslist['c_'+key_part+'_'+ hName].cd()
                    histolist[hName].Draw()
                    canvaslist['c_'+key_part+'_'+ hName].SetGrid()

                    legSample = TLegend(0.1,0.95,0.7,0.9)
                    legSample.SetHeader(dataset)
                    legSample.SetBorderSize(0)
                    legSample.Draw("SAME")
                    legSample.SetFillStyle(0)

                    canvaslist['c_'+key_part+'_'+hName].SaveAs('./systematics/'+dataset+'_'+key_part+'_'+hName+'.png')
                    output.cd()
                    canvaslist['c_'+key_part+'_'+ hName].Write()
                    histolist[hName].Write()






        RatioPlot('Muon_pt_corrected','Muon_pt_pf',0.98,1.02,False)
        RatioPlot('Muon_pt_correctedUp','Muon_pt_corrected',0.98,1.02,False)
        RatioPlot('Muon_pt_correctedDown','Muon_pt_corrected',0.98,1.02,False)
        RatioPlot('MET_pt_nom','MET_pt_pf',0.5,1.5,False)
        RatioPlot('MET_pt_jerUp','MET_pt_nom',0.5,1.5,False)
        RatioPlot('MET_pt_jerDown','MET_pt_nom',0.5,1.5,False)
        RatioPlot('MET_pt_jesTotalUp','MET_pt_nom',0.5,1.5,False)
        RatioPlot('MET_pt_jesTotalDown','MET_pt_nom',0.5,1.5,False)
        RatioPlot('MET_pt_unclustEnUp','MET_pt_nom',0.5,1.5,False)
        RatioPlot('MET_pt_unclustEnDown','MET_pt_nom',0.5,1.5,False)

        RatioPlot('GenV_preFSR_mass','GenV_bare_mass',0.99,1.01, True)
        RatioPlot('GenV_preFSR_y','GenV_bare_y',0.99,1.01, True)
        RatioPlot('GenV_preFSR_qt','GenV_bare_qt',0.99,1.01, True)
        RatioPlot('GenV_preFSR_CStheta','GenV_bare_CStheta',0.99,1.01, True)
        RatioPlot('GenV_preFSR_CSphi','GenV_bare_CSphi',0.99,1.01, True)
        RatioPlot('GenV_dress_mass','GenV_bare_mass',0.99,1.01, True)
        RatioPlot('GenV_dress_y','GenV_bare_y',0.99,1.01, True)
        RatioPlot('GenV_dress_qt','GenV_bare_qt',0.99,1.01, True)
        RatioPlot('GenV_dress_CStheta','GenV_bare_CStheta',0.99,1.01, True)
        RatioPlot('GenV_dress_CSphi','GenV_bare_CSphi',0.99,1.01, True)


if(refFile!='') :
    myFile_ref = TFile(refFile)
    # print("before",mytree.GetEntries())
    mytree = myFile_ref.Events
    # print("after", mytree.GetEntries())


    for key_part, part in variables.items() :

        if(key_part!="Variations") :

            if(key_part=="W") :
                goodV = "0"
            elif(key_part=="Z") :
                goodV = "2"
            elif(key_part=="Fake"):
                goodV = "1"
            else :
                goodV="-999"
            for key_var, var in part.items() :

                hName = key_part+'_'+var["name"]+'_ref'
                histolist[hName] = TH1F(hName,hName,var["Nbin"],var["min"],var["max"])
                if(key_part!='Cut_and_Weight') :
                    mytree.Project(hName,var["name"],"Vtype=="+goodV+" &&"+var['cut'],"",Nevents)
                else :
                    mytree.Project(hName,var["name"],"Vtype>=0&&"+var['cut'],"",Nevents)
                histolist[hName].GetXaxis().SetTitle(var["title"])
                histolist[hName].SetBinContent(var["Nbin"],histolist[hName].GetBinContent(var["Nbin"])+histolist[hName].GetBinContent(var["Nbin"]+1)) #overflow in last bin
                histolist[hName].SetBinContent(1,histolist[hName].GetBinContent(1)+histolist[hName].GetBinContent(0)) #underflow in first bin
                histolist[hName].SetLineWidth(2)
                histolist[hName].SetLineColor(2)

                hName_main = key_part+'_'+var["name"]
                histolist[hName].Scale(histolist[hName_main].GetEntries()/histolist[hName].GetEntries())

                canvaslist['c_'+key_part+'_'+key_var].cd()
                histolist[hName].Draw("hist SAME")


                legComp = TLegend(0.7,0.65,0.98,0.45)
                legComp.AddEntry(histolist[hName_main],dataset)
                legComp.AddEntry(histolist[hName],"reference: "+ refDataset)
                legComp.Draw("SAME")

                canvaslist['c_'+key_part+'_'+key_var].SaveAs(dataset+'_'+key_part+'_'+key_var+'.png')

                output.cd()
                canvaslist['c_'+key_part+'_'+key_var].Write()
                histolist[hName].Write()


        #Variations
        else :
            for key_var, var in part.items() :
                hName = key_part+'_'+var["name"]+'_ref'
                hName_main = key_part+'_'+var["name"]

                histolist[hName] = TH1F(hName,hName,var["Nbin"],var["min"],var["max"])
                mytree.Project(hName,var["name"],"Vtype>=0 &&"+var['cut'],"",Nevents)
                histolist[hName].GetXaxis().SetTitle(var["title"])
                histolist[hName].SetBinContent(var["Nbin"],histolist[hName].GetBinContent(var["Nbin"])+histolist[hName].GetBinContent(var["Nbin"]+1)) #overflow in last bin
                histolist[hName].SetBinContent(1,histolist[hName].GetBinContent(1)+histolist[hName].GetBinContent(0)) #underflow in first bin
                histolist[hName].Sumw2()
                histolist[hName].Scale(histolist[hName_main].GetEntries()/histolist[hName].GetEntries())

            def RatioPlot_ref(name_num, name_den,range_min,range_max, logFlag) :


                        #ratio between histograms

                        hName = 'histoDiv_'+part[name_num]['name']+"_over_"+part[name_den]['name']+'_ref'
                        hName_main = 'histoDiv_'+part[name_num]['name']+"_over_"+part[name_den]['name']
                        histolist[hName] = TH1F(hName,hName,part[name_den]["Nbin"],part[name_den]["min"],part[name_den]["max"])
                        histolist[hName].Divide(histolist[key_part+'_'+part[name_num]['name']+'_ref'],histolist[key_part+'_'+part[name_den]['name']+'_ref'])
                        histolist[hName].SetLineWidth(2)
                        histolist[hName].SetLineColor(2)

                        canvaslist['c_'+key_part+'_'+ hName_main].cd()
                        if(logFlag) :
                            canvaslist['c_'+key_part+'_'+ hName_main].SetLogy()
                        histolist[hName].Draw("SAME")

                        legComp = TLegend(0.7,0.65,0.98,0.45)
                        legComp.AddEntry(histolist[hName_main],dataset)
                        legComp.AddEntry(histolist[hName],"reference: "+ refDataset)
                        legComp.Draw("SAME")

                        canvaslist['c_'+key_part+'_'+hName_main].SaveAs('./systematics/'+dataset+'_'+key_part+'_'+hName_main+'.png')

                        output.cd()
                        canvaslist['c_'+key_part+'_'+ hName_main].Write()
                        histolist[hName].Write()

                        #ratio events-by-events

                        hName = 'EvByEv_'+part[name_num]['name']+"_over_"+part[name_den]['name']+'_ref'
                        hName_main = 'EvByEv_'+part[name_num]['name']+"_over_"+part[name_den]['name']

                        histolist[hName] = TH1F(hName,hName,part[name_den]["Nbin"],range_min,range_max)
                        mytree.Project(hName,part[name_num]['name']+'/'+part[name_den]['name'],"Vtype>=0 &&"+part[name_den]['cut'],"",Nevents)
                        histolist[hName].GetXaxis().SetTitle(name_num+'/'+name_den)
                        histolist[hName].SetBinContent(part[name_den]["Nbin"],histolist[hName].GetBinContent(part[name_den]["Nbin"])+histolist[hName].GetBinContent(part[name_den]["Nbin"]+1)) #overflow in last bin
                        histolist[hName].SetBinContent(1,histolist[hName].GetBinContent(1)+histolist[hName].GetBinContent(0))
                        histolist[hName].SetLineWidth(2)
                        histolist[hName].SetLineColor(2)
                        histolist[hName].Scale(histolist[hName_main].GetEntries()/histolist[hName].GetEntries())


                        canvaslist['c_'+key_part+'_'+ hName_main].cd()
                        histolist[hName].Draw("hist SAME")

                        legComp = TLegend(0.7,0.65,0.98,0.45)
                        legComp.AddEntry(histolist[hName_main],dataset)
                        legComp.AddEntry(histolist[hName],"reference: "+ refDataset)
                        legComp.Draw("SAME")


                        canvaslist['c_'+key_part+'_'+hName_main].SaveAs('./systematics/'+dataset+'_'+key_part+'_'+hName_main+'.png')
                        output.cd()
                        canvaslist['c_'+key_part+'_'+ hName_main].Write()
                        histolist[hName].Write()


            RatioPlot_ref('Muon_pt_corrected','Muon_pt_pf',0.98,1.02,False)
            RatioPlot_ref('Muon_pt_correctedUp','Muon_pt_corrected',0.98,1.02,False)
            RatioPlot_ref('Muon_pt_correctedDown','Muon_pt_corrected',0.98,1.02,False)
            RatioPlot_ref('MET_pt_nom','MET_pt_pf',0.5,1.5,False)
            RatioPlot_ref('MET_pt_jerUp','MET_pt_nom',0.5,1.5,False)
            RatioPlot_ref('MET_pt_jerDown','MET_pt_nom',0.5,1.5,False)
            RatioPlot_ref('MET_pt_jesTotalUp','MET_pt_nom',0.5,1.5,False)
            RatioPlot_ref('MET_pt_jesTotalDown','MET_pt_nom',0.5,1.5,False)
            RatioPlot_ref('MET_pt_unclustEnUp','MET_pt_nom',0.5,1.5,False)
            RatioPlot_ref('MET_pt_unclustEnDown','MET_pt_nom',0.5,1.5,False)

            RatioPlot_ref('GenV_preFSR_mass','GenV_bare_mass',0.99,1.01,True)
            RatioPlot_ref('GenV_preFSR_y','GenV_bare_y',0.99,1.01,True)
            RatioPlot_ref('GenV_preFSR_qt','GenV_bare_qt',0.99,1.01,True)
            RatioPlot_ref('GenV_preFSR_CStheta','GenV_bare_CStheta',0.99,1.01,True)
            RatioPlot_ref('GenV_preFSR_CSphi','GenV_bare_CSphi',0.99,1.01,True)
            RatioPlot_ref('GenV_dress_mass','GenV_bare_mass',0.99,1.01,True)
            RatioPlot_ref('GenV_dress_y','GenV_bare_y',0.99,1.01,True)
            RatioPlot_ref('GenV_dress_qt','GenV_bare_qt',0.99,1.01,True)
            RatioPlot_ref('GenV_dress_CStheta','GenV_bare_CStheta',0.99,1.01,True)
            RatioPlot_ref('GenV_dress_CSphi','GenV_bare_CSphi',0.99,1.01,True)
