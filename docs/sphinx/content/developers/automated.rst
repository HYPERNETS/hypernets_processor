.. use_processing - description of running the processor in an automated manner
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 22/10/20

.. _user_automated:

Automated Processing
====================

This section provides a user guide for running the **hypernets_processor** module as an automated processor of incoming field data. In this scenario, a set of field hypstar systems are regularly syncing raw data to a server.  Running on this server, the **hypernets_processor** processes the data and adds it to an archive that can be accessed through a user portal.

Covered in this section is installing and setting up the processor, setting up specific job (e.g. field site) and running the automated job scheduler.

Prerequisites
-------------

**hypernets_processor** is distributed using Git, from the project's `GitHub <https://github.com/HYPERNETS/hypernets_processor>`_ repository. This can be installed on your Linux server using your package manager of choice, following the instruction on the `Git website <https://git-scm.com/download/linux>`_.

Python 3 is required to run the software, the `Anaconda <https://www.anaconda.com>`_ distribution provides a convenient way to install this.

Server Installation
-------------------

First clone the project repository from GitHub::

   $ git clone https://github.com/HYPERNETS/hypernets_processor.git

To facilitate proper version control of processor configuration, create a new branch for your installed code::

   $ git checkout -b <installation_name>_operational

Then install the module with setup tools, including the option to setup the processor::

   $ python setup.py develop --setup-processor

This automatically installs the processor and its dependencies, followed by the running a processor setup routine (see :ref:`user_processor-processor_setup` more details).

Finally, commit any changes to the module made during set up and push::

   $ git add -A
   $ git commit -m "initial setup on server"
   $ git push

Any future changes to the processor configuration should be committed, to ensure appropriate version control. Updates to the processor are then made by merging release branches onto the operational branch (see :ref:`user_processor-updates`).

.. _user_processor-processor_setup:

Processor Configuration
-----------------------

To set the processor configuration, a setup routine is run upon installation. This can be rerun at any time as::

   $ hypernets_processor_setup

This sets up the processor configuration such that it correctly points to the appropriate log file, directories and databases, creating any as necessary. By default any created log file or databases are added to the defined processor working directory.

For further configuration one can directly edit the processor configuration file, e.g.::

   $ vim <installation_directory>/hypernets_processor/etc/processor.config


.. _user_processor-job_setup:

Job Setup
---------

In the context of the `hypernets_processor`, processing a particular data stream from a given field site is defined as a job.

To initialise a new job to run in the processor, run the following::

   $ hypernets_processor_job_init -n <job_name> -s <site_id> -w <job_working directory> -i <raw_data_directory> --add-to-scheduler

where:

* `job_name` - is the name of the job within the context of the hypernets processor (could, for example, be set as the site name).
* `site_id` - four letter abbreviation of site name, as defined in format definition document.
* `job_working_directory` - the working directory of the job. A job configuration file is created in this directory, called `<job_name>.config`.
* `raw_data_directory` - the directory the field data is synced to.
* `add_to_scheduler` - option to add the job to the list of scheduled jobs, should be set.

As well as defining required job configuration information, the job configuration file can also be used to override any processor configuration defaults (e.g. chosen calibration function, which file levels to write, see :ref:`config`), except the set of protected processor configuration defaults (e.g. processor version number).
To see what configuration values may be set review the processor configuration file (:ref:`config`).

For all jobs, it is important relevant metadata be added to the metadata database, so it can be added to the data products.

.. _user_processor-scheduler:

Running Job Scheduler
---------------------

Once setup the automated processing scheduler can be started with::

   $ hypernets_scheduler

To see options, try::

   $ hypernets_scheduler --help

All jobs are run regularly, processing any new data synced to the server from the field since the last run. The run schedule is defined in the scheduler config, which may be edited as::

   $ vim <installation_directory>/hypernets_processor/etc/scheduler.config

Processed products are added to the data archive and listed in the archive database. Any anomalies are add to the anomaly database. More detailed job related log information is added to the job log file. Summary log information for all jobs is added to the processor log file.

To amend the list of scheduled jobs, edit the list of job configuration files listed in the processor jobs file as::

   $ vim <installation_directory>/hypernets_processor/etc/jobs.txt

.. _user_processor-updates:

Updates
-------

Updates to the processor are then made by merging release branches onto the operational branch.

Processing databases
-------

During the data processing three sqlite databases are populated :ref:`SQL_databases`.
These databases can be viewed in a terminal using, for instance, sqlite3.
To open the anomaly database::

$ sqlite3 anomaly.db

In sqlite select anomalies based on site id and/or anomaly id (:ref:`SQL_databases`)::

$ sqlite> SELECT * FROM anomalies WHERE site_id=="VEIT" AND anomaly_id=="x";

Get more information about the anomalies table::

$.schema anomalies

To open the archive database and check the products, you can use the following commands::

$ sqlite3 anomaly.db
$ sqlite> PRAGMA table_info(products);

To investigate specific products, e.g. based on date, processing level and or processing version::

$ sqlite> SELECT * FROM products WHERE sequence_name LIKE "%SEQ2023%";
$ sqlite> SELECT * FROM products WHERE product_level =="L2A";
$ SELECT * FROM products WHERE product_name LIKE '%v1.0.nc%';

To quit, use CTRL+D.

Examples
-------------------

As an example, the following steps are required to automatically process data transferred from the field (e.g. from a site called M1BE) to a server.

After running the `hypernets_processor_setup` as follow::

$ hypernets_processor_setup

the following fields are required (examples in bold):

* Update network, currently 'w' (y/n) [n]: **y**
* Set network default config values (overwrites existing) (y/n) [y]: **y**
* Update archive_directory, currently '/home/hypstar/Processed' (y/n) [n]: **y**
* Set archive_directory: **/waterhypernet/hypstar/processed**
* Update processor_working_directory, currently '/home/rhymer/.hypernets' (y/n) [n]:**y**
* Set processor_working_directory: **/home/processor/working_directory**
* Update metadata_db_url, currently 'sqlite:////waterhypernet/hypstar/Processed/metadata.db' (y/n) [n]:**y**
* Set metadata_db_url [sqlite:////waterhypernet/HYPSTAR/Processed/metadata.db]: **sqlite:////waterhypernet/hypstar/processed/metadata.db**
* Update anomaly_db_url, currently 'sqlite:////waterhypernet/hypstar/Processed/anomaly.db' (y/n) [n]:**y**
* Set anomaly_db_url [sqlite:////waterhypernet/HYPSTAR/Processed/metadata.db]: **sqlite:////waterhypernet/hypstar/processed/anomaly.db**
* Update archive_db_url, currently 'sqlite:////waterhypernet/hypstar/Processed/archive.db' (y/n) [n]:**y**
* Set archive_db_url [sqlite:////waterhypernet/HYPSTAR/Processed/metadata.db]: **sqlite:////waterhypernet/hypstar/processed/archive.db**

Once the processor configuration has been setup, jobs need to be initiated using the following command ::

$ hypernets_processor_job_init -n M1BE -s M1BE -w /home/processor/working_directory/ -i /waterhypernet/HYPSTAR/Raw/M1BE/DATA/ --add-to-scheduler

Note, several jobs can be initiated in the single `jobs.txt` file using the same line as above with the site specific raw data directory and processing name for each site.
Before launching the scheduler, ensure that the following configuration files are present in your working directory:

* [site_id].config : For instance, for the above example, M1BE.config, contains all the input parameters for the processing of this particular job.
* processor.config : Contains the common input parameters for all the jobs initiated in `jobs.txt`.
* scheduler.config : Includes input parameters for the scheduler.

See also :ref:`config` for more details about the processing parameters that can be given.


Next, launch the hypernets scheduler as follow::

$ hypernets_scheduler

Or use nohup, screen or any other tool allowing to run commands in background. Using nohup, the hypernets_scheduler can be launched::

$ nohup hypernets_scheduler &

Once launched, the following log files will be populated with all the required notifications about the ongoing processing.

* [site_id].log (e.g. M1BE.log)
* scheduler.log

A handy command that lists the ongoing nohup tasks is::

$ lsof | grep nohup.out

If an ongoing nohup task needs to be aborted, kill the task with::

$ kill -9 [ID of the ongoing processing]



