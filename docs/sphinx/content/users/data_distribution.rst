.. description of data distribution
   Author: Pieter De Vis
   Email: pieter.de.vis@npl.co.uk
   Created: 20/03/24
.. _data_distribution:

Data Distribution
======================

The distribution of Near Real-Time (NRT, 24 hours between data acquisition and data availability)
LANDHYPERNET and WATERHYPERNET data will happen through the data portals for the
LANDHYPERNET (www.landhypernet.org.uk) and WATERHYPERNET (www.waterhypernet.org).
However, during the current prototype phase, where improvement of the quality checks is still ongoing,
and further site-specific quality checks are still being added by the site-owners, these data portals are
restricted to consortium members. In addition, for the WATERHYPERNET network the distribution may
be delayed to ensure that the NCEP/GDAS forecast data for wind speed are made available for the latest
sequence (should be less than 24hours). Data transfer from the system to the server may also delay the
NRT processing (e.g., due to poor 4G connections on the field). In the near future, these data portals will
be opened to the public and will become the reference source of data for HYPERNETS.

In the meantime, a subset of the HYPERNETS data until 2023-04-31 is publicly available and can be
found on Zenodo (`Brando et al., 2023 <https://doi.org/10.5281/zenodo.8057823>`_; `Brando and Vilas, 2023 <https://doi.org/10.5281/zenodo.8057531>`_; `De Vis et al., 2023 <https://doi.org/10.5281/zenodo.8039303>`_; `Dogliotti et al., 2023 <https://doi.org/10.5281/zenodo.8057728>`_;
`Doxaran and Corizzi, 2023a <https://doi.org/10.5281/zenodo.8057777>`_;`Doxaran and Corizzi, 2023b <https://doi.org/10.5281/zenodo.8057789>`_; `Piegari et al., 2023 <https://doi.org/10.5281/zenodo.8048425>`_; `Goyens and Gammaru, 2023 <https://doi.org/10.5281/zenodo.8059881>`_; `Morris et al., 2023 <https://doi.org/10.5281/zenodo.7962557>`_;
`Saberioon et al., 2023a <https://doi.org/10.5281/zenodo.8048348>`_; `Saberioon et al., 2023b <https://doi.org/10.5281/zenodo.8044522>`_; `Sinclair et al., 2023 <https://doi.org/10.5281/zenodo.8060798>`_). The initial datasets provided here in June 2023 were
produced using the v1.0 of the HYPERNETS PROCESSOR (see Section 2.5). A new version of the datasets
on Zenodo will be released upon publication of this paper, using the v2.0 of the HYPERNETS PROCESSOR.

To follow the Findable-Accessible-Interoperable and Reusable principles (FAIR), particular attention
is given to the data format and metadata, and, data accessibility. Files are in the NetCDF CF-convention
version 1.8 format. Common metadata (e.g., metadata section added with each data product) follow the
INSPIRE directives15 in accordance with the EN ISO 19115 for the metadata elements and the Dublin
Core Metadata Initiative16. Instrument, component and system metadata are bound by a unique metadata
key (i.e., system id) allowing to trace the history of the system (e.g., replacement, maintenance, system
updates or instrument setup improvements).
