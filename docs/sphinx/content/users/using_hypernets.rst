.. use_processing - description of running the processor in an automated manner
   Author: seh2
   Email: sam.hunt@npl.co.uk
   Created: 22/10/20

.. _user_using_hypernets:

Using HYPERNETS data
======================

This section provides on how to use the HYPERNETS data produced by the **hypernets_processor** module.
The HYPERNETS products include products from L0 (raw data) to L2A (refelctance data), which each have different variables, uncertainties, quality flags and metadata.
In this section we will briefly describe what data is available in each of the files and how to access it.
We will also briefly discuss the plots made by the processor and how to access these.
The **hypernets_processor** also produces some SQL databases. These are desribed in .
We do not provide further details on how to access these databases, since they are only meant for internal use.


downloading data
------------------
**water network**
The data for the water HYPERNETS data can also be accessed through an online data portal (www.waterhypernet.org).
Via waterhypernet.org, monthly and yearly zip files with all the available products per site and per level (i.e., L1C and LA) can be downloaded.

**land network**
The data for the land HYPERNETS data can also be accessed through an online data portal (www.landhypernets.org).
In addition to downloading monthly zip files with all the available products per site, it is also possible to do a query.


accessing data
------------------


Using obsarray
-------------------

