.. user_adhoc - description of how to use the processor for ad hoc sequence processing
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 23/3/20

.. _user_adhoc:

Ad-hoc Sequence Processing
==========================

This section provides a user guide for running the **hypernets_processor** module to process specified field acquisitions, or sequences, on an ad-hoc basis outside of any automated processing.

Prerequisites
-------------

**hypernets_processor** is distributed using Git, from the project's `GitHub <https://github.com/HYPERNETS/hypernets_processor>`_ repository. Git can be installed from the from the `Git website <https://git-scm.com>`_.

Python 3 is required to run the software, the `Anaconda <https://www.anaconda.com>`_ distribution provides a convenient way to install this.

Installation
------------

First clone the project repository from GitHub::

   $ git clone https://github.com/HYPERNETS/hypernets_processor.git

Then install the module with pip::

   $ pip install hypernets_processor/

This will also automatically install any dependencies.

If you are installing the module to contribute to its development, it is recommended you follow the install instructions on the :ref:`developers` page.

Sequence Processing
-------------------

Once installed the `hypernets_sequence_processor` command-line tool provides the means to process raw sequence data, it is run as follows::

   $ hypernets_sequence_processor -i <input_directory> -o <output_directory> -n <network>

where:

* `input_directory` - directory of raw sequence product, or directory containing a number of raw sequence products, to process.
* `output_directory` - directory to write output data to.
* `network` - network name, `land` or `water`. The default configuration for this network is applied for the processing.

To see more options, try::

   $ hypernets_sequence_processor --help

Alternatively, the processing can be specified with a job configuration file as follows::

   $ hypernets_sequence_processor -j <job_config_path>

where:

* `job_config_path` - path of a job configuration file. See :ref:`user_processor-job_setup` for information on initialising a job configuration file.

Specifying processing with a custom job configuration file allows non-network-default configuration values to be set, for example, chosen calibration function.
See also :ref:`processing-processing_config` for more details about the processing parameters that can be given.

Examples
-------------------

Ad-hoc processing of a single sequence for a site called M1BE can be done with the following command::

   $ hypernets_sequence_processor -i /home/waterhypernet/HYPSTAR/Raw/M1BE/DATA/SEQ20231031T182051 -o /home/waterhypernet/HYPSTAR/Processed/test/ -n water --max-level L2A

While, processing all sequences within a single directory can be done with::

   $ hypernets_sequence_processor -i /home/waterhypernet/HYPSTAR/Raw/M1BE/DATA/ -o /home/waterhypernet/HYPSTAR/Processed/test/ -n water  --max-level L2A


If the adhoc processing don't refer to a user defined job configuration path, input parameters for the processing configuration are taken by default from

* /hypernets_processor/hypernets_processor/etc/processor_land_defaults.config, or,
* /hypernets_processor/hypernets_processor/etc/processor_water_defaults.config,

for the land and water network respectively.