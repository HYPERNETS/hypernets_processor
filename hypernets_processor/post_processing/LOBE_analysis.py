import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt


data = pd.read_csv('T:/ECO/EOServer/data/insitu/hypernets/post_processing_qc/JSIT_2025-01-01_2025-07-01_None_None_None_None.csv')
print(data.head)

refl_keys = [x for x in data.columns if 'refl' in x]
spectra = np.ones((len(data), len(refl_keys)))
wavs = [''.join(filter(str.isdigit, key)) for key in refl_keys]

ndvi = (data[' refl_842nm'] - data[' refl_665nm'])/(data[' refl_842nm'] + data[' refl_665nm'])
timestamps = [dt.fromtimestamp(ts) for ts in data[' acquisition_time'].values]
vza = data[' vza'].values

fig = plt.figure(figsize=(12,4), dpi = 200)
ax = fig.add_subplot(1,1,1)
ax.scatter(timestamps, ndvi, c = vza, cmap = 'rainbow', s= 0.1)
cbar = plt.colorbar(ax.collections[0], ax=ax)
cbar.set_label('VZA (degrees)')
ax.set_xlabel('Date')
ax.set_ylabel('NDVI')
fig.suptitle('JSIT 2025-01-01 to 2025-07-01')
plt.tight_layout()
fig.savefig('T:/ECO/EOServer/joe/hypernets_plots/JSIT_TOPCAT/JSIT_2025-01-01_2025-07-01_NDVI_VZA.png', bbox_inches='tight')