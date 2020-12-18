import struct

import time

from hypernets_processor.data_io.spectrum import Spectrum


def stringifyBinaryToHex(data):
	return " ".join("{:02x}".format(c) for c in data)


if __name__ == '__main__':
	# NOK: SWIR-IR, VIS-RAD garbles with len 4119
	with open('RADIOMETER/01_002_0090_2_0180_192_00_0000_03_0000.spe', 'rb') as f:
	# OK: 3x VIS-IR
	# with open('01_001_0090_2_0180_128_08_0000_03_0000.spe', 'rb') as f:
	# NOK: VIS-RAD garbles with len 4119
	# with open('01_004_0090_2_0140_128_16_0000_03_0000.spe', 'rb') as f:
	# NOK: SWIR-IR, then VIS-RAD garbles with len 4119
	# with open('01_005_0090_2_0180_192_00_0000_03_0000.spe', 'rb') as f:
	# NOK: VIS-RAD garbles with len 4119
	# with open('01_007_0090_2_0040_128_16_0000_06_0000.spe', 'rb') as f:
	# NOK: SWIR-IR, SWIR-IR, SWIR-IR, VIS-RAD garbles
	# with open('01_008_0090_2_0180_192_00_0000_03_0000.spe', 'rb') as f:
	# NOK: VIS-RAD garbles
	# with open('01_010_0090_2_0140_128_16_0000_03_0000.spe', 'rb') as f:
	# NOK: VIS-RAD garbles
	# with open('01_011_0090_2_0180_192_00_0000_03_0000.spe', 'rb') as f:
	# OK: vis-IR, VIS-IR, VIS-IR
	# with open('01_013_0090_2_0180_128_08_0000_03_0000.spe', 'rb') as f:
	# NOK: SWIR-IR, SWIR-IR, VIS-RAD (4119 bytes, crashes)
	# with open('01_014_0090_2_0180_192_00_0000_03_0000.spe', 'rb') as f:
		# get length of file
		f.seek(0, 2)
		file_size = f.tell()
		f.seek(0)
		print('file size: {}'.format(file_size))
		byte_pointer = 0
		chunk_size = 1
		chunk_counter = 1
		while file_size-byte_pointer:
			print('Parsing chunk No {}, size {} bytes, bytes left: {}'.format(chunk_counter, chunk_size, file_size-byte_pointer))
			chunk_size = struct.unpack('<H', f.read(2))[0]
			if chunk_size == 4119:
				chunk_size = 4131
			f.seek(byte_pointer)
			chunk_body = f.read(chunk_size)
			spectrum = Spectrum.parse_raw(chunk_body)
			# spectrum.print_header()
			print('body length:{}, position in file: {}'.format(len(spectrum.body), f.tell()))
			byte_pointer = f.tell()
			chunk_counter += 1
			time.sleep(3)
