#
import sys
import numpy as np
import os
import time
import shutil
import shlex, subprocess

GLOBAL_PATH='/home/casp13/deepsf_3d/Github/test/DeepSF/';

if __name__ == '__main__':

    #print len(sys.argv)
    if len(sys.argv) != 8:
            print 'please input the right parameters: list, model, weight, kmax'
            sys.exit(1)
    
    
    test_list=sys.argv[1] 
    relationfile=sys.argv[2] #fold_label_relation2.txt 
    templateFile=sys.argv[3] #d2dc3a_ 172     a.1.1.2 a.1
    prediction_dir_train=sys.argv[4] #
    prediction_dir_test=sys.argv[5] #
    TopL=sys.argv[6]
    workingdir=sys.argv[7] #

    listdir = workingdir +'/search_list_dir'
    score_resultsdir = workingdir +'/score_ranking_dir'
    if not os.path.isdir(listdir):
        os.makedirs(listdir)
    else:
        shutil.rmtree(listdir)
        os.makedirs(listdir)
    #os.makedirs(listdir)
    if not os.path.isdir(score_resultsdir):
        os.makedirs(score_resultsdir)
    else:
        shutil.rmtree(score_resultsdir)
        os.makedirs(score_resultsdir)
    ### read relationfile
    #os.makedirs(score_resultsdir)
    sequence_file=open(relationfile,'r').readlines() 
    fold2label = dict()
    for i in xrange(len(sequence_file)):
        if sequence_file[i].find('Label') >0 :
            #print "Skip line ",sequence_file[i]
            continue
        fold = sequence_file[i].rstrip().split('\t')[0]
        label = sequence_file[i].rstrip().split('\t')[1]
        if fold not in fold2label:
            fold2label[fold]=int(label)
   
    ### read templateFile
    sequence_file=open(templateFile,'r').readlines() 
    fold2proteins = dict()
    for i in xrange(len(sequence_file)):
        line=sequence_file[i]
        fold = sequence_file[i].rstrip().split('\t')[3]
        proteins = sequence_file[i].rstrip().split('\t')[0]
        #check if protein pdb exists
        tpdb="";
        tpdb1 = GLOBAL_PATH+"/database/SCOP/SCOP_template_PDB/pdb/"+proteins+".atom";
        tpdb2 = GLOBAL_PATH+"/database/ECOD/ECOD_template_PDB//pdb/"+proteins+".atom";
        tpdb3 = GLOBAL_PATH+"/database/ECOD/ECOD_template_PDB/pdb/"+proteins+".atom";
        if os.path.isfile(tpdb1):
            tpdb = tpdb1;
        elif os.path.isfile(tpdb2):
            tpdb = tpdb2;
        elif os.path.isfile(tpdb3):
            tpdb = tpdb3;
        else:
            continue
        if fold not in fold2label:
             print fold, "not in ",relationfile
        foldid = fold2label[fold]
        if foldid not in fold2proteins:
            fold2proteins[foldid]=[]
            fold2proteins[foldid].append(line)
        else:
            fold2proteins[foldid].append(line)
    
    ### read test list     
    
    sequence_file=open(test_list,'r').readlines() 
    for i in xrange(len(sequence_file)):
        if sequence_file[i].find('Length') >0 : 
            print "Skip line ",sequence_file[i]
            continue
        pdb_name = sequence_file[i].rstrip().split('\t')[0]
        prediction_file = prediction_dir_test+'/'+pdb_name+'.prediction'
        if not os.path.isfile(prediction_file):
            raise Exception("prediciton file not exists: ",prediction_file, " pass!")
        #print "Loading ",prediction_file
        prediciton_results = np.loadtxt(prediction_file)     
        top1_prediction=prediciton_results.argsort()[-1:][::-1]
        if top1_prediction[0] not in fold2proteins:
            print "\n#################" ,pdb_name," pdb's fold ",top1_prediction[0], " couldn't find the template in ",templateFile, " do not refine\n\n\n"
            #continue
        topL_prediction=prediciton_results.argsort()[-int(TopL):][::-1]
        
        
        selected_templist_file = listdir+'/'+pdb_name+'.templist'
        
        num_pro = 0
          ### get proteins in these folds 
        potential_proteins = []
        with open(selected_templist_file, "w") as myfile:
          for fd in topL_prediction:
            if fd not in fold2proteins:
               #print fd, " s couldn't find the template in ",templateFile
               continue
            
            proteins_array = fold2proteins[fd]
            
            #print "Found ",fd, " for ",pdb_name, "with ", len(proteins_array)
            for pro in proteins_array:
               potential_proteins.append(pro)
               num_pro +=1
               myfile.write(pro)
          
        #if num_pro == 0:
            #print pdb_name, " couldn't find the template in ",templateFile
        selected_query_file = listdir+'/'+pdb_name+'.querylist'
        with open(selected_query_file, "a") as myfile:
           myfile.write(sequence_file[i]) 
            

