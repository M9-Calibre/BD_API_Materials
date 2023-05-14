"""
    description
   Identification process and experiment design for the Arcan experimental test using Abaqus

    INPUT: .odb file of the test
    OUTPUT: Parameters identified

    This files assumes the result files .odb have been already generated
    Run by writting on the command line: "python AbaqusPythonScript_main.py"
"""

# IMPORT PACKAGES -------------------------------------------------------------
import numpy as np
import sys
import os
import csv
import subprocess

# User settings ----------------------------------------------------------------
test_name = 'ArcanSpecimen'  # USE NAME OF TEST
available_test_configs = '0', '45', '90' # Available FEA results in terms of load and material direction
test_config = 'Load_90_MatDir_90' #Load_90_MatDir_0 , Load_45_MatDir_0, Load_0_MatDir_0,...
show_plots = 'no' #yes, no | if the plots are to be shown when running the script

#Hill48 yield function + Swift hardening law ----------------------------------------------------------------
Param = ['F','H','N','K','eps_0','n_swift']
Ref_param = [0.3748, 0.4709, 1.1125, 979.46, 0.00535, 0.194] #F, H, N, K, eps_0, n
Param_variation = 0.1 # Parameter variation

#Define scripts to execute ----------------------------------------------------------------
run_AbaqustoMatchID = 'yes'              #yes, no | runs the Abaqus to MatchID script to prepare results for 
                                        #virtual experiment
run_FEA_ExtractResults = 'no'           #yes, no | extracts the FEA results
run_FEA_princStrainStress_plots = 'no'  #yes, no | plots the FEA principal strains and stresses graphs
run_FEA_HeterCriterion = 'no'           #yes, no | Calculates the heterogeinity criterion for all test 
                                        #configurations
run_Synthetic_DIC = 'no'                #yes, no | Runs MatchID to create synthetic images based on the FEA
                                        #results and performs the 2D DIC analysis
Run_DIC_princStrain_plots = 'no'        #yes, no | plots the DIC principal strains and stresses graphs
run_SensAnal_UpdateParam = 'no'         #yes, no | Updates the inpute files for the sensitivity analysis
                                        #WARNING: This function still requires to run .inp files manually 
                                        #afterwards.
run_SensAnal_ExtractResults = 'no'      #yes, no | extracts the sensitivity analysis FEA results  
run_SenSAnal_plots = 'no'               #yes, no | plots the sensitivity analysis difference plots   
run_FEA_plots = 'no'                    #yes, no | plots the FEA EqPlastic strain map, rotation angle, 
                                        #principal strain ratios map and lode angle vs stress triaxility      
run_YieldLocus_plot = 'no'              #yes, no | plots the Yield Locus on the material directions for
                                        #the chosen test configuration     
run_YieldLocus_All_plot = 'no'          #yes, no | plots the Yield Locus on the material directions for
                                        #all material directions                                 
#  --------------------------------------------------------------- method - MAIN
def main():
    print('Using',test_name, 'with test configuration:', test_config)
    if run_AbaqustoMatchID == 'yes':
        cmd= "abaqus cae noGUI=AbaqusPythonScriptToMatchID.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Generated new MatchID input files.')  
    
    if run_FEA_ExtractResults == 'yes':
        cmd= "abaqus cae noGUI=AbaqusPythonScript_Results.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Generated new principal FEA principal stress and strains results files.')  

    if run_FEA_princStrainStress_plots == 'yes':
        cmd= "python AbaqusPrincipalStressStrain_plots.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Generated new principal FEA principal stress and strains plots.')  

    if run_FEA_HeterCriterion == 'yes':
        cmd= "python Abaqus_HeterogeneityCriterion.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Performed new calculation of the FEA heterogeneity criterion for the test configurations available.')  
 
    if run_Synthetic_DIC == 'yes':
        cwd = os.getcwd()
        try:
            path_to_save_FEDEF = os.path.join(cwd,test_config,'MatchID','FE_DEF')
            os.chdir(path_to_save_FEDEF)
            os.system("matchid.exe " + test_name + "_FEDEF.mtind")
            print('Generated new synthetic images.')  
        except:
            print('FE_DEF error')
            pass
        try:
            path_to_save_DIC = os.path.join(cwd,test_config,'MatchID','DIC')
            os.chdir(path_to_save_DIC)
            os.system("matchid.exe " + test_name + "_DIC.m2inp")
            print('Performed new DIC analysis.')  
            os.chdir(cwd)
        except:
            print('DIC error')
            pass

    if Run_DIC_princStrain_plots == 'yes':
        cmd= "python DIC_PrincipalStrain_plots.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Generated new principal DIC principal strains plots.')  

    if run_SensAnal_UpdateParam == 'yes':
        cmd= "python ParameterSensitivity_updParam.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Updating input files for sensitivity analysis. WARNING: This requires to execute the ABAQUS analysis manually in order to obtain the updated .odb file.')  

    if run_SensAnal_ExtractResults == 'yes':
        cmd= "abaqus cae noGUI=AbaqusSensAnalysis_Results.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Extracted the sensitivity analysis FEA results.')  

    if run_SenSAnal_plots == 'yes':
        cmd= "python SensivityAnalysis_plots.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Plotted the sensitivity analysis strain and stress differences.')  

    if run_FEA_plots == 'yes':
        cmd= "python Abaqus_plots.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Plotted the FEA Eq. plastic strain map, rotation angle, principal strain ratios map and lode angle vs stress triaxility.')  
    
    if run_YieldLocus_plot == 'yes':
        cmd= "python YieldLocus.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Plotted the Yield Locus on the material directions for the chosen test configuration.')  

    if run_YieldLocus_All_plot == 'yes':
        cmd= "python YieldLocus_all.py"
        p= subprocess.Popen(cmd, shell=True)
        out, err = p.communicate()
        print('Plotted the Yield Locus on the material directions for all material directions.')          
        
    print('Done.')        

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
run_FEA_plots