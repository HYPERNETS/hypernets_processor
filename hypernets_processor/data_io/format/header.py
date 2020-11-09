"""
Header definitions for Hypernets '.spe' raw data
"""

HEADER_DEF = [(2, "Total Dataset Length", '<H'),
             (1, "Spectrum Type Information", '<B'),
             (8, "acquisition_time", '<Q'),
             (2, "integration_time", '<H'),
             (4, "temperature", '<f'),
             (2, "Pixel Count", '<H'),
             (2, "acceleration_x_mean", '<h'),
             (2, "acceleration_x_std", '<h'),
             (2, "acceleration_y_mean", '<h'),
             (2, "acceleration_y_std", '<h'),
             (2, "acceleration_z_mean", '<h'),
             (2, "acceleration_z_std", '<h')]
