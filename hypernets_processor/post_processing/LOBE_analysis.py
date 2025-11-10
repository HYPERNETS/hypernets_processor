import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



data = pd.read_csv('T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/LOBE_2025Apr_2025May_QC_good.csv')
print(data.head)

refl_keys = [x for x in data.columns if 'refl' in x]
spectra = np.ones((len(data), len(refl_keys)))
wavs = [''.join(filter(str.isdigit, key)) for key in refl_keys]

blue_swir_index = (data[' refl_1020nm'] - data[' refl_415nm'])/(data[' refl_1020nm'] + data[' refl_415nm'])

for i in range(len(data)):
    for j, key in enumerate(refl_keys):
        spectra[i, j] = data[key][i]
        
print(data[' vaa'][1746])
plt.plot(wavs, spectra[1746,:], label = 'Mast')
plt.plot(wavs, spectra[1747,:], label = 'Soil')

plt.legend()    
plt.show()