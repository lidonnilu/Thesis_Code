import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})

import pymulskips
print(pymulskips.__path__)
from pymulskips import setuprun, process


# Dataset di riferimento
data_samples = {
    '153': {
        'Power': 6.10,
        'T_seed_middle': 2072.24,
        'T_seed_edge': 0,
        'T_source_middle': 2080.20,
        'T_source_edge': 2080.20,
        'Exp-Growth-Rate': 287
    }
}

# Compilazione MulSKIPS
execpath = '/Users/filipporuberto/miniforge3/envs/mulskips_env/MulSKIPS/mulskips-source'
lenx, leny, lenz = 120, 120, 2400
setuprun.setup_mulskips_src(execpath, lenx, leny, lenz)

# Setup parametri
randseed = 9117116
newdT = 0 #10
Tseed = data_samples['153']['T_seed_middle'] + 273.15 + newdT
Tsource_0 = data_samples['153']['T_source_middle'] + 273.15 + newdT
dT = 100
Tsource = Tsource_0 + dT
gr = data_samples['153']['Exp-Growth-Rate']
KMC_lattice_constant = 0.436 / 12
target_thickness = 0.75 * lenz * KMC_lattice_constant * 1e-3  # micron

if dT != 0:
    gr *= dT / 25

tottime = 3600 * target_thickness / gr
Nout = 30

# Simulazione
simtype = 'F'
ptranszig = 0.93
runpath = os.getcwd() + '/data-{}-{}-{}'.format(dT, newdT, randseed)

# Setup processo PVD
pvdclass = process.PVD(substrate='SiC-3C', precursors=['Si', 'Si2C', 'SiC2'],
                       calibration_type='avrov', Tsource=Tsource, Tseed_center=Tseed)

# Esegui simulazione
setuprun.run_mulskips(
    execpath, runpath,
    Simulation=simtype,
    mp=pvdclass,
    PtransZig=ptranszig,
    Seed_box=[120, 0, 0],
    RunType='R',
    IDUM=randseed,
    setup_only=False,
    ExitStrategy='Time',
    TotTime=tottime,
    OutTime=tottime / Nout
)
