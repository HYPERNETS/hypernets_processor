.. config - algorithm theoretical basis
   Author: pdv
   Email: pieter.de.vis@npl.co.uk
   Created: 07/02/2022

.. _config:


Processing Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a lot of options that can alter the details of how the data is processed.
These options can be controlled by changing the values in three .config files, which are each stored in the
HYPERNETS working directory (details on how to set up the initial values for each of these from the default templates
can be found on the :ref:`user_automated` page):

1. **processor.config**: This file has all the main options for the processing of the data, which are in common between all the different sites.
These options range from the paths to the different database and relevant folders, to controlling which files and plots are created (and their format),
options for which measurement functions to use for each of the processing steps (as well as optional parameters for these steps) as well as
options for the uncertainty processing and quality checks.

2. **job.config**: This file has site_specific options. There will be individual jobs for each of the sites, and each can be given their own options (which overwrite the options in processor.config if present).

3. **scheduler.config**: This file has the options for the scheduling of jobs (e.g. how often to check for new data,
logging path, whether or not to use parallel_processing, etc). We also note here that the different jobs that should
be included in the current run can be edited in the jobs.txt file in the HYPERNETS working directory.

Together these files allow for the detailed control of the processing of the HYPERNETS data.