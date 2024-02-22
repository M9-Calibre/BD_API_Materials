"""
    description
   Plots the yield locus for the Hill48 yield criterion in the material coordinate system
    INPUT: .csv file of the test with the 3 components of stress on the material coordinate system
    OUTPUT: Plots the principal yield surface on material coordinate system and the material points on the stress space
    Run by writting on the command line: "YieldLocus.py"
"""
import base64
# IMPORT PACKAGES -------------------------------------------------------------
from cmath import pi
from io import BytesIO

from .PythonScript_main import *
import numpy as np
import os
import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from collections import Counter
import math

#  --------------------------------------------------------------- method - MAIN
def main(arguments):

    #Yield Locus processing data
    #Retrieving material parameters

    F = arguments["F"]
    H = arguments["H"]
    G = arguments["G"]
    N = arguments["N"]
    K = arguments["K"]
    eps0 = arguments["eps0"]
    n_swift = arguments["n_swift"]

    cwd = os.getcwd()
    EqPlastStrain = np.range(0, 1, 0.01)

    #StressXX = np.array([float(x) for x in StressXX])
    #StressYY = np.array([float(x) for x in StressYY])
    #StressXY = np.array([float(x) for x in StressXY])
    #MinPrincStress = np.array([float(x) for x in MinPrincStress])
    #MaxPrincStress = np.array([float(x) for x in MaxPrincStress])



    # Calculating Hardening law
    # TODO: Add ifs to function
    SigmaY = K*((eps0+EqPlastStrain)**n_swift) #func(EqPlastStrain, *args) --> SigmaY

    # Normaliation of the components of stress
    #StressXX_norm = StressXX/SigmaY
    #StressYY_norm = StressYY/SigmaY

    #Creating mesh points for populating the equations
    x_min = -10
    x_max = 10
    y_min = -10
    y_max = 10
    x1, x2 = np.meshgrid(np.arange(x_min,x_max, 0.1), np.arange(y_min,y_max, 0.1))

    #Hill48 yield criterion for plane stress conditions (2D) #TODO: convert to function shear
    Hill_0 = H*(x1-x2)**2+G*(x1**2)+F*(x2**2)+2*N*(0**2)
    Hill_02 = H*(x1-x2)**2+G*(x1**2)+F*(x2**2)+2*N*(0.2**2)
    Hill_04 = H*(x1-x2)**2+G*(x1**2)+F*(x2**2)+2*N*(0.4**2)
    Hill_06 = H*(x1-x2)**2+G*(x1**2)+F*(x2**2)+2*N*(0.6**2)

# ------------- graph properties ----------------
    FS = 24
    plt.rcParams['axes.facecolor'] = (1, 1, 1)  
    plt.rcParams['figure.facecolor'] = (1, 1, 1)
    plt.rcParams["font.family"] = "sans"
    plt.rcParams["font.serif"] = "Times New Roman"
    plt.rcParams['font.size'] = FS
    params = {"ytick.color" : (0, 0, 0),
          "xtick.color" : (0, 0, 0),
          "grid.color" : (0, 0 , 0),
          "text.color" : (0, 0, 0),
          "axes.labelcolor" : (0, 0, 0),
          "axes.edgecolor" : (.15, .15, .15),
          "text.usetex": False}
    plt.rcParams.update(params)

    box = dict(boxstyle='Square,pad=0.05',fc='w',ec='w')
    al = 'center'
    al2 = 'left'
    fnt = 12
# ------------- Yield Locus - Material direction -------------

    fig1 = plt.figure(figsize=(16,9))
    ax = plt.axes([0.22, 0.24, .86, .83])

    colors = EqPlastStrain


    YF0 = plt.contour(x1,x2,Hill_0,[1], colors='k',linestyles='dashdot', linewidths=1.2)
    YF02 = plt.contour(x1,x2,Hill_02,[1], colors='k',linestyles='dashdot', linewidths=1.2)
    YF04 = plt.contour(x1,x2,Hill_04,[1], colors='k',linestyles='dashdot', linewidths=1.2)
    YF06 = plt.contour(x1,x2,Hill_06,[1], colors='k',linestyles='dashdot', linewidths=1.2)

    plt.plot([0,0],[-1.5,1.5],'k--',lw=0.7)
    plt.plot([-1.5,1.5],[0,0],'k--',lw=0.7)

    #plt.title(test_config + " | " + Param[i] + " sensitivity | Step:" + str(Step))
    plt.xlabel('$\sigma_{11}/\sigma_y$')
    plt.ylabel('$\sigma_{22}/\sigma_y$')
    plt.xlim(-1.5,1.5)
    plt.ylim(-1.5,1.5)
    ax.tick_params(axis='x', colors=(0,0,0))
    ax.tick_params(axis='y', colors=(0,0,0))

    name = '$\sigma_{12}/\sigma_y=0$, \nincrements of 0.2'
    plt.text(1.25,1.16,name,ha=al,va=al,ma=al2,bbox=box,fontsize=fnt)

    leg = ax.legend(loc='lower right',frameon=False, ncol=1, fontsize=fnt, markerscale=3.0,handletextpad=0.1,bbox_to_anchor=(0.1,0.01),
                handleheight=1.5, labelspacing=0.5)
    for l in leg.get_lines():
        l.set_alpha(1)

    # cjet = plt.cm.get_cmap('jet', 12)
    sm1 = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=0,vmax=max(EqPlastStrain)))
    sm1._A = []
    tks = np.linspace(0,max(abs(EqPlastStrain)),5)
    clb1 = plt.colorbar(sm1,ticks=tks, ax=ax)
    clb1.solids.set_rasterized(True)
    clb1.set_ticklabels(['%.2f'%round(i,2) for i in tks])
    clb1.set_label(r'$\bar{\epsilon}^\mathrm{p}$',labelpad=-40,y=1.1, rotation=0)
    clb1.solids.set(alpha=1)

    plt.clim(0,max(abs(EqPlastStrain)))



    buf = BytesIO()
    fig1.savefig(buf, dpi=600, bbox_inches='tight', pad_inches=.15, format='png')
    buf.seek(0)
    img = "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')

    plt.close(fig1)

    return img

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()