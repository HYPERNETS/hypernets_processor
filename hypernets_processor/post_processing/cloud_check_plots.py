import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = np.loadtxt(r'C:/Users/jr20/code/hypernets_cloud_checks/first_cc_0875.csv', delimiter = ',')

tols = data[0,:]

aod_0_outs = data[1,:]
aod_0_good = data[2,:]

aod_1_outs = data[3,:]
aod_1_good = data[4,:]

aod_2_outs = data[5,:]
aod_2_good = data[6,:]

aod_3_outs = data[7,:]
aod_3_good = data[8,:]

fig, ax = plt.subplots(1, 1, figsize = (6,4), dpi = 150)


ax.plot(tols, aod_0_outs, label = 'AOD = 0.0: Outliers', color = 'r', linestyle = 'solid')
ax.plot(tols, aod_0_good, label = 'AOD = 0.0: Good Data', color = 'r', linestyle = 'dotted')
ax.plot(tols, aod_1_outs, label = 'AOD = 0.1: Outliers', color = 'orange', linestyle = 'solid')
ax.plot(tols, aod_1_good, label = 'AOD = 0.1: Good Data', color = 'orange', linestyle = 'dotted')
ax.plot(tols, aod_2_outs, label = 'AOD = 0.2: Outliers', color = 'blue', linestyle = 'solid')
ax.plot(tols, aod_2_good, label = 'AOD = 0.2: Good Data', color = 'blue', linestyle = 'dotted')
ax.plot(tols, aod_3_outs, label = 'AOD = 0.3: Outliers', color ='green', linestyle = 'solid')
ax.plot(tols, aod_3_good, label = 'AOD = 0.3: Good Data', color = 'green', linestyle = 'dotted')

ax.set_xlabel('Tolerance')
ax.set_ylabel('Percentage of Data Removed')
ax.set_title('Cloud Check Tolerance Analysis for 550nm')
'''

ax.plot(tols, aod_0_outs - aod_0_good, label = 'AOD = 0.0', color = 'r', linestyle = 'solid')
ax.plot(tols, aod_1_outs - aod_1_good, label = 'AOD = 0.1', color = 'orange', linestyle = 'solid')
ax.plot(tols, aod_2_outs - aod_2_good, label = 'AOD = 0.2', color = 'blue', linestyle = 'solid')
ax.plot(tols, aod_3_outs - aod_3_good, label = 'AOD = 0.3', color ='green', linestyle = 'solid')


ax.set_xlabel('Tolerance')
ax.set_ylabel('Difference in Percentage of Data Removed')
ax.set_title('Cloud Check Tolerance Analysis for 550nm')
'''

plt.legend()
plt.show()

