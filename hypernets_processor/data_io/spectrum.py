"""
Spectrum class, written by Kaspars Laizans at Tartu University
"""


import struct
from enum import Enum

import os

import time


class EntranceType(Enum):
	RADIANCE = 0x02
	IRRADIANCE = 0x01
	DARK = 0x00


class Radiometer(Enum):
	VIS = 0x02
	SWIR = 0x01
	BOTH = 0x03


class Spectrum:
	class SpectrumHeader:
		class AccelStats:
			mean_x = None
			mean_y = None
			mean_z = None
			std_x = None
			std_y = None
			std_z = None

			@classmethod
			def parse_raw(cls, data):
				a = Spectrum.SpectrumHeader.AccelStats()
				a.mean_x, a.std_x, a.mean_y, a.std_y, a.mean_z, a.std_z = struct.unpack('<hhhhhh', data)
				return a

		class SpectrumType:
			optics = None
			radiometer = None

			def __init__(self):
				self.optics = 0
				self.radiometer = 0

			@classmethod
			def parse_raw(cls, data):
				otype = Spectrum.SpectrumHeader.SpectrumType()
				o = (data >> 3) & 0x03
				r = (data >> 6) & 0x03
				otype.optics = EntranceType(o)
				otype.radiometer = Radiometer(r)
				return otype

		total_length = 0
		spectrum_type = 0
		timestamp = 0
		exposure_time = 0
		pixel_count = 0
		temperature = 0
		accel_stats = None

		def __init__(self):
			self.total_length = 0
			self.spectrum_type = 0
			self.timestamp = 0
			self.exposure_time = 0
			self.temperature = 0
			self.pixel_count = 0

		@classmethod
		def parse_header(cls, data):
			h = Spectrum.SpectrumHeader()
			h.total_length, h.spectrum_type, h.timestamp, h.exposure_time, h.temperature, h.pixel_count \
				= struct.unpack('<HBQHfH', data[:19])
			h.spectrum_type = Spectrum.SpectrumHeader.SpectrumType.parse_raw(h.spectrum_type)
			h.accel_stats = Spectrum.SpectrumHeader.AccelStats.parse_raw(data[19:31])
			return h

	header = None
	body = []
	crc32 = 0

	def __init__(self):
		self.header = None
		self.body = []
		self.crc32 = 0

	def save(self, path):
		with open(path, 'w') as f:
			f.write('Dataset length: {} bytes\n'
					'Timestamp: {} ms\n'
					'CRC32: {} \n'
					'Entrance: {}\n'
					'Radiometer: {}\n'
					'Exposure time: {} ms\n'
					'Sensor temperature: {} \'C\n'
					'Pixel count: {}\n'
					'Tilt:\n'
					'\tx:{}\u00B1{}\n'
					'\t y:{}\u00B1{}\n'
					'\t z:{}\u00B1{}\n'.format(self.header.total_length, self.header.timestamp, hex(self.crc32[0]), self.header.spectrum_type.optics.name, self.header.spectrum_type.radiometer.name,
															self.header.exposure_time, self.header.temperature, self.header.pixel_count,
															self.header.accel_stats.mean_x,
															self.header.accel_stats.std_x,
															self.header.accel_stats.mean_y,
															self.header.accel_stats.std_y,
															self.header.accel_stats.mean_z,
															self.header.accel_stats.std_z))

			for i in range(self.header.pixel_count-1):
				f.write('{}\t{}\n'.format(i, self.body[i]))

	def return_header(self):
		return (
		 #'Dataset length: {} bytes\n'
		 #'Timestamp: {} ms\n'
		 #'CRC32: {} \n'
		 'Entrance: {}\t'
		 'Radiometer: {}\n'
		 'Exposure time: {} ms\t'
		 'Sensor temperature: {} \'C \t'
		 'Pixel count: {}\n'
		 'Tilt:\n'
		 '\tx:{}\u00B1{}\n'
		 '\t y:{}\u00B1{}\n'
		 '\t z:{}\u00B1{}\n'.format(self.header.spectrum_type.optics.name,
		 						self.header.spectrum_type.radiometer.name,
		 						self.header.exposure_time, self.header.temperature, self.header.pixel_count,
									self.header.accel_stats.mean_x,
									self.header.accel_stats.std_x,
									self.header.accel_stats.mean_y,
									self.header.accel_stats.std_y,
									self.header.accel_stats.mean_z,
									self.header.accel_stats.std_z))

	@classmethod
	def parse_raw(cls, data, save_raw=False, slot=0):
		s = Spectrum()
		s.header = Spectrum.SpectrumHeader.parse_header(data)
		for i in range(s.header.pixel_count):
			pixel, = struct.unpack('<H', data[31+i*2:33+i*2])
			s.body.append(pixel)
		s.crc32 = struct.unpack('<I', data[len(data)-4:])
		if save_raw:
			save_path = os.path.join('..', 'specs', 'run1', time.strftime("%Y_%m_%d_T%H%M%S_") + s.header.spectrum_type.optics.name +'_' + str(slot) + '.bin')
			with open(save_path, 'wb') as f:
				f.write(data)
		return s


def pack_optics(radiometer: Radiometer, optics: EntranceType):
	return (radiometer.value << 6) | (optics.value << 3)
