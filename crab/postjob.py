#!/usr/bin/env python
import commands
import time
import re
import os
import string
from os import listdir
from os.path import isfile, join
import sys
import argparse

from CRABClient.UserUtilities import config, getUsernameFromSiteDB
from CRABAPI.RawCommand import crabCommand

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

parser = argparse.ArgumentParser("")
parser.add_argument('-tag', '--tag', type=str, default="TEST",      help="")
parser.add_argument('-isMC', '--isMC', type=int, default=1,      help="")
parser.add_argument('-dataYear', '--dataYear',type=int, default=2016, help="")
parser.add_argument('-run', '--run',type=str, default='batch', help="")
parser.add_argument('-pushback', '--pushback',type=int, default=0, help="")
parser.add_argument('-xrootd', '--xrootd',type=int, default=0, help="")
parser.add_argument('-srm', '--srm',type=str, default='gpfs', help="")
parser.add_argument('-proxy', '--proxy',type=int, default=1, help="")
parser.add_argument('-nmax', '--nmax',type=int, default=999, help="")
args = parser.parse_args()
tag = args.tag
isMC = args.isMC
dataYear = args.dataYear
run = args.run
xrootd = args.xrootd
pushback = args.pushback
srm = args.srm
proxy = args.proxy
n_max_files = args.nmax
samples = ('mc' if isMC else 'data')+'samples_'+str(dataYear)+'.txt'

################################################################################

import subprocess

select_first_trial = True
#n_max_files = 999
use_crab_dir = True

# needed for CRAB utilities and lcg tools
if proxy:
    os.system('voms-proxy-init --voms cms')

username = getUsernameFromSiteDB()
path = '/eos/user/s/sroychow/jpsi/CMSSW_10_2_20_UL/src/PhysicsTools/NanoAODTools/crab/'

outdir_master, outdir_proxy = "",""

if srm=='eos':
    outdir_master = "/eos/user/s/sroychow/jpsi/dataTree/NanoAOD%s-%s/" % (str(dataYear), tag)
else:
    print "No valid scratch space specified"
    exit(1)

if proxy and not os.path.isdir(outdir_proxy):
    os.system('mkdir -p '+outdir_proxy)

if proxy:
    proxy_name = os.environ['X509_USER_PROXY'].split('/')[2]
    cpproxycmd = 'cp %s %s' %  (os.environ['X509_USER_PROXY'], outdir_proxy+proxy_name)
    os.system(cpproxycmd)
    print '>', bcolors.OKBLUE, cpproxycmd, bcolors.ENDC

print "Reading inputs from:",  bcolors.OKGREEN, 'postcrab_'+samples.rstrip('.txt')+'_'+tag+'.txt', bcolors.ENDC
if pushback:
    print "Pushing back to SRM area:", bcolors.OKGREEN, "/gpfs/ddn/srm/cms/store/user/"+username,  bcolors.ENDC
else:
    print "Hadding to scratch area:", bcolors.OKGREEN, outdir_master,  bcolors.ENDC

fres = open('postcrab_'+samples.rstrip('.txt')+'_'+tag+'_result.txt', 'a')
fin = open('postcrab_'+samples.rstrip('.txt')+'_'+tag+'.txt', 'r')
content = fin.readlines()
sample_dirs = [x.strip() for x in content]
for sample_dir in sample_dirs:    
    if sample_dir[0]=='#':
        continue
    task_name = sample_dir.split('/')[-2]
    sample_name = sample_dir.split('/')[-4]
    ext = ''
    if isMC:
        prod_tag = sample_dir.split('/')[-3]
        idx_ext = prod_tag.find('ext')    
        if idx_ext!=-1:
            ext = '_'+prod_tag[idx_ext:idx_ext+4]
        else:
            print " => no extensions found in sample %s" % sample_dir.split('/')[-3]
        if 'NanoWMass' in prod_tag:
            ext = '_'+task_name
            print " => sample will be added label '%s'" % task_name
    else:
        idx_ext = sample_dir.split('/')[-3].find('Nano')
        ext = '_'+(sample_dir.split('/')[-3][0:idx_ext-1])
    job_name = task_name.replace('_', '')
    script_name = 'hn_'+task_name
    fout = open(script_name+'_cfg.txt','w')
    fout.write('#!/bin/bash\n\n')
    fout.write('cd '+path+'\n')
    fout.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    fout.write('eval `scramv1 runtime -sh`\n')
    if proxy:
        fout.write('echo "Creating a proxy..."\n')
        fout.write('export X509_USER_PROXY=%s' % outdir_proxy+proxy_name+'\n')
    fout.write('\n')
    pos = sample_dir.find("cms")
    sample_dir_from_cms = sample_dir[pos-1:] 
    if not os.path.isdir(outdir_master):
        mkoutdirmastercmd = "mkdir -p "+outdir_master
        print '>', bcolors.OKBLUE, mkoutdirmastercmd, bcolors.ENDC
        fout.write('echo "Creating a tmp directory..."\n')
        fout.write(mkoutdirmastercmd+'\n')
        if run=='shell': os.system(mkoutdirmastercmd)
    outdir = ""
    if pushback:
        outdir = outdir_master+"/"+task_name+"/"
    else:
        outdir = outdir_master+"/"+sample_name+ext+"/"
    if not os.path.isdir(outdir):
        mkoutdircmd = "mkdir -p "+outdir
        print '>', bcolors.OKBLUE, mkoutdircmd, bcolors.ENDC
        fout.write('echo "Creating a tmp directory..."\n')
        fout.write(mkoutdircmd+'\n')
        if run=='shell': os.system(mkoutdircmd)                

    if xrootd:
        sample_dir_srmls = sample_dir.replace('/gpfs/ddn/srm/cms/', 'xrootd-cms.infn.it:1194 ls ')
        crab_trial = "0000"
        sample_dir_srmls += ("/"+crab_trial+"/")
        print '>', bcolors.OKBLUE, 'xrdfs '+sample_dir_srmls, bcolors.ENDC
        res = commands.getoutput('xrdfs '+sample_dir_srmls).split('\n')
        files = []
        for lres in res:
            if 'tree_' not in lres: continue
            files.append('root://xrootd-cms.infn.it/'+lres)
    else:
        if not os.path.isdir(sample_dir):
            files = []
            print 'Directory NOT found!'
        else:
            crab_trials = os.listdir(sample_dir)
            for crab_trial in crab_trials:
                if select_first_trial and crab_trial!="0000":
                    continue
            files = [sample_dir+"/"+crab_trial+"/"+x for x in os.listdir(sample_dir+'/'+crab_trial) if "tree_" in x]

    nfiles, nfinish, nall = len(files), 0, 0
    if use_crab_dir:
        for d in os.listdir('./'):
            if 'crab_' in d and '_task_' in d:
                crablog = open(d+'/crab.log')
                crabloglines = [x.strip() for x in crablog]
                for crablogline in crabloglines:
                    if task_name in crablogline:
                        print 'Task name matches CRAB directory', bcolors.OKBLUE, d, bcolors.ENDC
                        res = crabCommand('status', dir=d)
                        nall = len(res['jobList']) 
                        for r in res['jobList']:
                            if r[0]=='finished': nfinish += 1
                        break
    print "All tasks:     ", bcolors.OKGREEN,  "%s" % nall, bcolors.ENDC 
    print "Finished tasks:", bcolors.OKGREEN,  "%s" % nfinish, bcolors.ENDC 
    print "Found in dir:  ", bcolors.OKGREEN,  "%s" % nfiles, bcolors.ENDC
    print ' => fraction of hadded files:', "(%s)/(%s) = " % (nfiles,nall), bcolors.OKBLUE, "%s" % (float(nfiles)/nall if nall>0 else -1), bcolors.ENDC
    fres.write("%s, %s, %s/%s\n" % (task_name, sample_name+ext, nfiles, nall) )

    if nfiles==0:
        continue

    fout.close()
    for ib in range(int(nfiles)/int(n_max_files)+1):

        postfix = ''
        if nfiles>n_max_files: postfix = '_'+str(ib)

        fout_b = open(script_name+postfix+'.sh','w')
        fout =  open(script_name+'_cfg.txt', 'r')
        for line in fout:
            fout_b.write(line)
        fout.close()

        haddargs = outdir+"tree"+postfix+".root "
        for nf,f in enumerate(files):
            if nf/n_max_files==ib:
                haddargs += f+" "
        haddcmd = "python ../scripts/haddnano.py "+haddargs

        print '>', bcolors.OKBLUE, haddcmd, bcolors.ENDC
        fout_b.write('echo "Running hadd..."\n')
        fout_b.write(haddcmd+'\n')
        if run=='shell': 
            os.system(haddcmd)
            if os.path.isfile(outdir+"tree"+postfix+".root"): print "File", bcolors.OKBLUE, outdir+"tree"+postfix+".root", bcolors.ENDC, "saved."
            else: print bcolors.FAIL, "File "+outdir+"tree"+postfix+".root NOT found.", bcolors.ENDC         
        if pushback:
            pushbackcmd = 'lcg-cp -b -U srmv2 -v file://'+outdir+'tree'+postfix+'.root'+' \"srm://stormfe1.pi.infn.it:8444/srm/managerv2?SFN='+sample_dir_from_cms+'/tree'+postfix+'.root'+'\"'
            print bcolors.OKBLUE, pushbackcmd, bcolors.ENDC
            if run=='shell':
                if os.path.isfile(outdir+"tree"+postfix+".root"):
                    print "File:", bcolors.OKGREEN, outdir+"tree"+postfix+".root", bcolors.ENDC, "found. Move back to SRM"
                    os.system(pushbackcmd)
                    if os.path.isfile(sample_dir+"/tree"+postfix+".root"):
                        print "File:", bcolors.OKGREEN, sample_dir+"/tree"+postfix+".root", bcolors.ENDC, "is in SRM. Remove tmp files" 
                        rmcmd = "rm -r "+outdir
                        print bcolors.OKBLUE, rmcmd, bcolors.ENDC
                        os.system(rmcmd) 
                        fout_b.write(rmcmd+'\n')
                    else:
                        print "File:", bcolors.FAIL, sample_dir+"/tree"+postfix+".root", "NOT found.", bcolors.ENDC
                else:
                    print "File:", bcolors.FAIL, outdir+"tree"+postfix+".root", bcolors.ENDC, "NOT found."                
            elif run=='batch':
                fout_b.write(pushbackcmd+'\n')
                rmcmd = "rm -r "+outdir
                print bcolors.OKBLUE, rmcmd, bcolors.ENDC
                fout_b.write('echo "Removing tmp directory..."\n')
                fout_b.write(rmcmd+'\n')
                fout_b.write('echo "Done!"\n')
        fout_b.close()
        if run=='batch': 
            os.system('chmod +x '+script_name+postfix+'.sh')
            submit_to_queue = 'bsub -q cms -J '+job_name+postfix+' -o '+path+'/'+script_name+postfix+'.stdout'+' -e '+path+'/'+script_name+postfix+'.stderr'+' -cwd `pwd` '+path+'/'+script_name+postfix+'.sh'
            print '>', bcolors.OKBLUE, submit_to_queue, bcolors.ENDC
            os.system(submit_to_queue)
            time.sleep( 1.0 )
            print "@@@@@ END JOB @@@@@"        

fin.close()
fres.close()
