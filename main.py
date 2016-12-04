#!/usr/bin/python
"""
	main.py

	This software is licensed under the MIT license. See LICENSE for more information.
"""

import re
import os
import struct

import exportmission

class Application(object):
	signatures = {
		"// Mission file created by ConvertMission from": exportmission.process_mission,
	}

	def main(self):
		with open("Tribes - Aerial Assault.bin", "r") as handle:
			buffer = handle.read()
			buffer_length = len(buffer)

			print("Opened file. Length: %u" % buffer_length)
			for signature in self.signatures:
				signature_pattern = re.compile(signature)
				print("Searching for signature - %s" % repr(signature))

				signature_length = len(signature)

				for match in signature_pattern.finditer(buffer):
					match_text = match.group(0)
					match_start = match.start()

					tested_buffer = buffer[match_start:match_start + signature_length]
					self.signatures[signature](self, signature, buffer, match_start)

if __name__ == "__main__":
	Application().main()
