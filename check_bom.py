#!/usr/bin/env python

#===============================================================================
#
#  Copyright 2017 VIDAS SIMKUS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#===============================================================================


#===============================================================================
# 
# This script uses dkapia.py to check a project's BOM against specified DigiKey part number
#
#===============================================================================

import subprocess
import json
import sys
import os
import package_types

#
# The "CSV" files I use are generated by KiBOM:
# https://github.com/SchrodingersGat/KiBoM
#

INFILE = "/opt/dev/git_work/VIOBOARD_V1_Schematics/BBB_SHIELD_V2/BBB_SHIELD_V2_bom.csv"
SEP_CHAR = '|'

#
# The various column indexes in the CSV file.  Indexing is zero-based
#

# Row/group ID 
COL_IDX_ROW = 0

# Description of component
COL_IDX_DESC = 1

# KiCAD part name
COL_IDX_COMP = 2

# Component IDs that are instances of this type of component.  The IDs are expected to be space separated.
COL_IDX_IDS = 3

# Component value 
COL_IDX_VALUE = 4

# KiCAD pad name
COL_IDX_PAD = 5

# Number of such components in the schematic.
COL_IDX_COUNT = 6

# Manufacturer
COL_IDX_MFG = 8

# Manufacturer part number
COL_IDX_MFGPN = 10

# DigiKey part number
COL_IDX_DKPN = 12


DEBUG = False

#===============================================================================
#
# End "configuration" section
#
#===============================================================================


MY_DIR =  os.path.normpath(os.path.dirname(sys.argv[0]))

def is_smt_part(_json):
	if "ParametricData" not in _json.keys():
		raise RuntimeError("ParametricData is not a key the supplied JSON object.")
	pd = _json["ParametricData"]

	for i in pd:
		if "Id" not in i.keys():
			continue

		if i["Id"] == 69 and i["Text"] == "Mounting Type":
			if i["Value"]["Id"] in package_types.DIGIKEY_SMT_MOUNTING_TYPES:
				return True

		if i["Id"] == 1291 and i["Text"] == "Supplier Device Package":
			if i["Value"]["Id"] in package_types.DIGIKEY_SMT_SUPPLIER_PACKAGES:
				return True;

		if ["Id"] == 16 and i["Text"] == "Package / Case":
				if i["Value"]["Id"] in package_types.DIGIKEY_SMT_PACKAGE_TYPES:
					return True;

	return False

def is_smt_pad(_pad):
	for kw in package_types.SMT_KEYWORDS:
		if kw in _pad:
			return True
	return False

def get_part_info(dkpn):
	parms = [os.path.join(MY_DIR,"dkapia.py"), "PART_SEARCH", "-P", dkpn, "-rmMl", "-rmPp", "-rmPd"]

	proc = subprocess.Popen(parms, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	(stdoutdata, stderrdata) = proc.communicate(None)

	if proc.returncode != 0:
		print stderrdata
		return None

	return json.loads(stdoutdata)

def guess_schematic_package(l):
	"""
	Guesses the package type based on pad type in the BOM file.
	@return: Type of (mount_type,package_type).  mount_type is a broad mount type contstant PKG_MOUNT_TYPE from package_types.py  
	"""
	package_type_str = l[COL_IDX_PAD]

	mount_type = package_types.PKG_MOUNT_TYPE_UNKNOWN
	package_type = package_types.PKG_DK_SMT_INVALID


	if "0805" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_0805
	elif "1206" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_1206
	elif "2512" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_2512
	elif "TQFP-44" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_TQFP_44
	elif "SOD-323" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_SC_76
	elif "SOIC-14" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_SOIC_14
	elif "SOIC-16" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_SOIC_16
	elif "SOIC-8" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_SOIC_8
	elif "SOIC-28" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_SOIC_28
	elif "SOT-23-6" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_SOT_23_6
	elif "SOT-23-5" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_SOT_23_5
	elif "SOT-23" in package_type_str:
		print >>sys.stderr,"Possible bug: pad: %s\n%s" % (package_type_str,str(l))
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_SOT_23
	elif "DO-214" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_DO_214
	elif "SOD-123F" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_SOD_123F
	elif "TO_277" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_TO_277
	elif "MSOP-10" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_SMT
		package_type = package_types.PKG_DK_SMT_MSOP_10
	elif "TO-92" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_TH
		package_type = package_types.PKG_TH_TO_92
	elif "TO-220-3" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_TH
		package_type = package_types.PKG_TH_TO_220_3
	elif "TO-220" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_TH
		package_type = package_types.PKG_TH_TO_220
	elif "TO-251" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_TH
		package_type = package_types.PKG_TH_TO_251
	elif "HC49" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_TH
		package_type = package_types.PKG_TH_HC_49
	elif "DIP-8" in package_type_str:
		mount_type = package_types.PKG_MOUNT_TYPE_TH
		package_type = package_types.PKG_TH_DIP_8
	elif "Vx78-1000" in package_type_str:
		# This is what we call a cludge
		mount_type = package_types.PKG_MOUNT_TYPE_TH
		package_type = package_types.PKG_TH_SIP_3



	return (mount_type,package_type)

def guess_digikey_package(jo):
	"""
	Attempts to extract the mount type package ID from DigiKey data.
	@param jo: JSON output from part search.
	"""

	package = None
	package_id = None

	mount_type = None
	mount_type_id = None

	for p in jo["Parameters"]:
		if "ParameterId" in p.keys():
			if p["ParameterId"] == 16:	# Package/Case
				package = p["Value"]
				package_id = int(p["ValueId"])

			if p["ParameterId"] == 69:	# Mounting type
				mount_type = p["Value"]
				mount_type_id = int(p["ValueId"])


	if (package is None or package_id is None) and (mount_type is None or mount_type_id is None):
		raise RuntimeError("Failed to find package information in provided JSON input.")

	if DEBUG:
		print "DEBUG<guess_digikey_package>: Identified package: %s, package_id: %s" % (str(package),str(package_id))

	pkg_mount_type = package_types.PKG_MOUNT_TYPE_UNKNOWN

	#
	# If the mount type is specified use that.
	#
	if mount_type_id in package_types.DIGIKEY_SMT_MOUNTING_TYPES and mount_type_id in package_types.DIGIKEY_TH_MOUNTING_TYPES:
		pkg_mount_type = package_types.PKG_MOUNT_TYPE_AMBIG
	elif mount_type_id in package_types.DIGIKEY_SMT_MOUNTING_TYPES:
		pkg_mount_type = package_types.PKG_MOUNT_TYPE_SMT
	elif mount_type_id in package_types.DIGIKEY_TH_MOUNTING_TYPES:
		pkg_mount_type = package_types.PKG_MOUNT_TYPE_TH

	#
	# If mount type is not specified, try to deduce
	#
	if pkg_mount_type == package_types.PKG_MOUNT_TYPE_UNKNOWN:
		if package_id in package_types.DIGIKEY_SMT_PACKAGE_TYPES:
			pkg_mount_type = package_types.PKG_MOUNT_TYPE_SMT
		elif package_id in package_types.DIGIKEY_TH_PACKAGE_TYPES:
			pkg_mount_type = package_types.PKG_MOUNT_TYPE_TH

	return (pkg_mount_type,package_id)

i = 0

comp_id = None
dkpn = None
jo = None

with open(INFILE, "rt") as in_file:
	i = i + 1
	in_file.readline()

	for l in in_file:
		l = l.strip()
		if len(l) < 1:
			break

		l = l.split(SEP_CHAR)

		try:
			comp_id = l[COL_IDX_IDS]
			dkpn = l[COL_IDX_DKPN]
		except IndexError as e:
			print >>sys.stderr, "Failed to get line contents.  Check configuration.  Make sure that field separator is set correctly.\nException: %s" % (str(e))
			break

		if len(dkpn) < 1:
			continue

		pad = l[COL_IDX_PAD]

		if DEBUG:
			print "DEBUG<main>: Looking at DKPN: %s for components: %s" % (dkpn,comp_id)

		try:
			jo = get_part_info(dkpn)
		except Exception as e:
			raise RuntimeError("Uncaught exception:",e)

		if jo is None:
			continue

		dk_mount,dk_package = guess_digikey_package(jo)
		sc_mount,sc_package = guess_schematic_package(l)

		if DEBUG:
			print ""


		#print dkpn + " --> " + str(guess_digikey_package(jo))

		if dk_mount != sc_mount or dk_package != sc_package:

			#
			# Pointers to footprint conversion functions
			#
			dk_fc = None
			sc_fc = None

			if dk_mount == package_types.PKG_MOUNT_TYPE_SMT:
				dk_fc = package_types.digikey_smt_type_to_string
			elif dk_mount == package_types.PKG_MOUNT_TYPE_TH: 
				dk_fc = package_types.digikey_th_type_to_string
			else:
				dk_fc = package_types.digikey_invalid_type_to_string

			if sc_mount == package_types.PKG_MOUNT_TYPE_SMT:
				sc_fc = package_types.schematic_smt_type_to_string
			elif sc_mount == package_types.PKG_MOUNT_TYPE_TH: 
				sc_fc = package_types.schematic_th_type_to_string
			else:
				sc_fc = package_types.schematic_invalid_type_to_string				

			print >>sys.stderr,":( -- Possible mismatch for component: [%s]" % str(comp_id)
			print >>sys.stderr, "	Mount type:	Schematic:	[%s]	Digikey	[%s]" % (package_types.pkg_mount_type_to_string(sc_mount),package_types.pkg_mount_type_to_string(dk_mount));
			print >>sys.stderr, "	Package:	Schematic:	[%s]	Digikey	[%s]" % (sc_fc(sc_package),dk_fc(dk_package));

			print >> sys.stderr,""



