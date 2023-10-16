""" This Script is meant as a starting point for Anna to start looking at the uncertainty on aerosol retrievals"""

'''___Built-In Modules___'''
from GraspFunctionsNPL import make_sdatfile

'''___Third-Party Modules___'''
import numpy as np
import datetime
import corner_edited
import matplotlib.pyplot as plt
import scipy

'''___NPL Modules___'''
#from eopy import Product
import kumara


filename='atmos_retrieval'
# First, read in the surface reflectance as a function of wavelength, as well as set the aerosol and water vapour
reflpath='/home/pdv/project_Anna/Gobabeb_reflectance_nonan.txt'
#this will scale aerosol profile
aerosol=0.06
H2O=7.6  
#CH4=30

samples=np.load(filename+".npy")
samples=samples[200::]

aerosolticks=np.array([0.04,0.06,0.08])
H2Oticks=np.array([5,10])

print(np.percentile(samples[:,0],50),np.percentile(samples[:,0],50)-np.percentile(samples[:,0],16),np.percentile(samples[:,0],84)-np.percentile(samples[:,0],50))
print(np.percentile(samples[:,1],50),np.percentile(samples[:,1],50)-np.percentile(samples[:,1],16),np.percentile(samples[:,1],84)-np.percentile(samples[:,1],50))

fig = corner_edited.corner(samples, labels=[r"aerosol $\tau$", r"H2O"], ticks=[aerosolticks,H2Oticks], ticklabels=[aerosolticks,H2Oticks], plot_contours=False)
fig.savefig(f'{filename}_summed.png')


# results_mcmc = map(lambda v: (v[1], v[2]-v[1], v[1]-v[0]), zip(*np.percentile(samples, [16, 50, 84], axis=0)))
# print(results_mcmc[:])
