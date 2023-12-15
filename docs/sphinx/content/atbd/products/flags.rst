.. flags - algorithm theoretical basis
   Author: Pieter De Vis
   Email: pieter.de.vis@npl.co.uk
   Created: 12/04/2023
.. _flags:


Flags description 
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The quality flag field consists of 32 bits. Every bit is related to the absence or presence of a a flag as described in the table below. The quality flag value given in each data level is the compound value of the specific bits of each raised flag. Some flags are left as placeholders for future updates. Note, additional flags can be added, the table below presents the flags used in the current version.
The tables below also have a column for the :ref:`anomalies` raised by a particular quality checks.

**Table 1: Common Flags description**

.. csv-table::
   :file: table_flags_common.csv
   :class: longtable
   :widths: 1 2 1 1 4 1
   :header-rows: 1

**Table 2: Land-specific Flags description**

.. csv-table::
   :file: table_flags_land.csv
   :class: longtable
   :widths: 1 2 1 1 4 1
   :header-rows: 1

**Table 3: Water-specific Flags description**

.. csv-table::
   :file: table_flags_water.csv
   :class: longtable
   :widths: 1 2 1 1 4 1
   :header-rows: 1




