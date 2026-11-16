import os
import sys
import struct
import numbers
import re
import math
from datetime import datetime

from row64tools.bytestream import bytestream as bStream
from row64tools import ramdb

BasicNames = ["null","int","bigint","float","bigfloat","text"]
BasicTypes = [0,0,1,2,3,4,5,5,4,4,5,5,5,4,4,4,4,4,5,5,2]
Steps = [0,4,8,4,8,10] # byte steps for each type
ColumnTypes = ["drop","null","int","bigint","float","bigfloat","text","image","longitude","latitude","3dobj","pdf","url","xcord","ycord","zcord","xperc","yperc","note3d","note2d","datetime","timedelta"]

class stream64(object):
	
	def __init__(self, in_url):

		self.url = in_url
		self.debug_to_file = False
		self.RPath = ""
		self.nb_cols = 0
		self.col_set = False
		self.rcol_names = [] # column names from ramdb file
		self.rcol_types = [] # column types from ramdb file
		self.rcol_sizes = [] # column sizes from ramdb file
		self.col_names = [] # send names (different than rcol_names - UPSERT can be a subset)
		self.col_types = [] # send types (different than rcol_types - UPSERT can be a subset)
		self.col_sizes = [] # send sizes (different than rcol_sizes - UPSERT can be a subset)
		self.basic_types = []
		self.col_map = []
		self.Log = True
		self.Cmd = ""
		self.DBName = ""
		self.TableName = ""
		self.KeyIndex = 0
		self.verbose = False
		if "v=2" in self.url:self.verbose = True

	def get_date64(self, inDateStr, inFormat):
		# dt = datetime.strptime(dStr, "%m/%d/%Y %H:%M")
		dt = datetime.strptime(inDateStr, inFormat)
		tStamp = int(dt.timestamp() * 1000) * 1000000 # 1 ms -> 1000000 ns
		return tStamp

	def get_12h_timestr(self, inH):
		hour = int(inH)
		mdec = inH - hour
		minutes = int(mdec * 60)
		ap = "AM"
		if hour < 1: hour = 12
		elif hour > 12:ap="PM";hour -= 12
		return str(hour)+":"+str(minutes).zfill(2) + " " + ap + " PDT"

	def get_24h_timestr(self, inH):
		hour = int(inH)
		mdec = inH - hour
		minutes = int(mdec * 60)
		if hour < 1: hour = 12
		elif hour > 24:hour -= 24
		return str(hour)+":"+str(minutes).zfill(2)

	def set_types(self, inTList):

		# NOTE: set_types will only work with all column names
		# If you want to send a sub-set that has column alignment, use set_types_from_ramdb

		if self.col_set == False:
			raise Exception("ERROR: Cannot set_types until set_columns has been called")
		if len(self.col_names) != len(inTList):
			raise Exception("ERROR: set_types length doesn't match set_columns length")
		self.basic_types = []
		self.col_types = []
		self.col_sizes = []
		for i,key in enumerate(inTList):
			if isinstance(key, numbers.Number): # it's a number, use it directly
				cType = key
				if cType >= len(ColumnTypes):
					raise Exception("SYNTAX ERROR: set_types, type: "+cType+"is invalid")
				bTypeI = BasicTypes[cType]
				self.col_types.append(cType)
				self.basic_types.append(bTypeI)
				self.col_sizes.append(Steps[bTypeI])
			else: # assume it's a text version of the type, look for a match
				for j in range(len(ColumnTypes)):
					if ColumnTypes[j] == key:
						self.col_map.append(i)
						cType = ColumnTypes[j]
						bTypeI = BasicTypes[j]
						self.col_types.append(j)
						self.basic_types.append(bTypeI)
						self.col_sizes.append(Steps[bTypeI])
						break
				else:
					raise Exception("SYNTAX ERROR: set_types, type: "+key+" not found")

	def get_folder(self): # get parent folder where the process was started             
		pathname = os.path.dirname(sys.argv[0])
		return os.path.abspath(pathname) 

	def set_types_from_ramdb(self, inPath):
		if self.col_set == False:
			raise Exception("ERROR: Cannot set_types until set_columns has been called")
		self.RPath = inPath
		if not os.path.exists(inPath):
			raise Exception("INVALID ramdb path, file not found")
		self.basic_types = []
		self.col_types = []
		self.col_sizes = []
		self.get_ramdb_info()
		for key in self.col_names:
			gotMatch = False
			for i,cName in enumerate(self.rcol_names):
				if cName == key:
					self.col_map.append(i)
					# print(key+":",ColumnTypes[self.rcol_types[i]])
					cType = ColumnTypes[self.rcol_types[i]]
					self.basic_types.append(BasicTypes[self.rcol_types[i]])
					self.col_types.append(self.rcol_types[i])
					self.col_sizes.append(self.rcol_sizes[i])
					gotMatch = True
					break
			if not gotMatch:
				raise Exception("ERROR, set_in could not find column name"+key)

	def set_columns(self, inColNames): 
		self.col_names = inColNames
		self.col_set = True

	def msg_from_pandas(self,inDf, db="", table=""):
		
		# msg_from_pandas is only CREATE to make new .ramdb
		# automatic type detection would cause type changing errors in UPSERT
		nbRows = len(inDf.index)
		nbCols = len(inDf.columns)

		bs = bStream() # message bytestream
		bs.add_string("Func","API")
		bs.add_string("DBAlias","Row64")
		bs.add_string("DBName",db)
		bs.add_string("TableName",table)
		bs.add_string("Event","CREATE") 
		bs.add_int32("KeyIndex",0)

		rb = ramdb.bytestream_from_df(inDf)
		bs.add_stream( "Data", rb.save_to_buffer() )

		if self.debug_to_file:
			rb.save("/home/row64/debug_stream_df.ramdb") # debug dataframe as .ramdb file
			bs.save("/home/row64/debug_stream_msg.ramdb") # debug entire message as .ramdb file
		return b"BS="+bs.save_to_buffer()

	def set_output(self, command="UPSERT", db="", table="", key=0):
		
		if not re.fullmatch(r"[0-9a-zA-Z_-]+", table):
			raise Exception("INVALID table, valid characters are: 0-9a-zA-z-_")
		if command!="UPSERT" and command!="CREATE" and command!="UPSERT VERBOSE" and command!="CREATE VERBOSE" and command!="CLEAR":
			raise Exception("set_output INVALID command: " + command)
		if command=="UPSERT" and key == None:
			raise Exception("set_output INVALID UPSERT: key index not set")
		if command=="UPSERT" and key < 0:
			raise Exception("set_output INVALID UPSERT: key index less than 0")
		if command=="UPSERT" and key > len(self.col_types):
			raise Exception("set_output INVALID UPSERT: key index greater than number of columns")
		if db=="":raise Exception("db not set")
		if table=="":raise Exception("table not set")
		if self.RPath != "":
			if command=="CREATE" and len(self.col_names) != len(self.rcol_names):
				raise Exception("set_output INVALID CREATE: ramdb number of columns is a different length")
			path1 = os.path.join("/var/www/ramdb/live/RAMDB.Row64", db)
			if not os.path.exists(path1):
				raise Exception("set_output INVALID DbName: " + db + " not found")
			path2 = os.path.join(path1, table+".ramdb")
			if not os.path.exists(path2):
				raise Exception("set_output INVALID TableName: " + table +" not found")
		if command == "UPSERT VERBOSE" or command == "CREATE VERBOSE":
			self.verbose = True
		self.Cmd = command
		self.DBName = db
		self.TableName = table
		if key == None: self.KeyIndex=0
		else: self.KeyIndex = key
		return True

	def get_ramdb_info(self):
		bs = bStream()
		bs.read( self.RPath )
		self.nb_cols = bs.get_int64("NbCols")
		self.rcol_names = bs.get_string_vector("ColNames")
		self.rcol_types = bs.get_int32_vector("ColTypes")
		self.rcol_sizes = bs.get_int32_vector("ColSizes")

	def add_text_list(self, inTList, inCMint, inCTile, inCMintPos):
		lenBuf = bytearray()
		for i in range(len(inTList)):
			if isinstance(inTList[i], str):
				inCMint.extend(inTList[i].encode())
				iLen = len(inTList[i])
				inCTile += bytearray(struct.pack('Q', inCMintPos)) # uint 64
				lenBuf += bytearray(struct.pack('H', iLen)) # uint 16
				inCMintPos+=iLen
			else: # Ingest NaN or Null string value into "" blank zero length string 
				inCTile += bytearray(struct.pack('Q', inCMintPos)) #uint 64
				lenBuf += bytearray(struct.pack('H', 0)) #uint 16
		inCTile += lenBuf
		return inCMintPos

	def add_text_list_debug(self, inTList, inCMint, inCTile, inCMintPos):
		lenBuf = bytearray()
		for i in range(len(inTList)):
			if isinstance(inTList[i], str):
				inCMint.extend(inTList[i].encode())
				iLen = len(inTList[i])
				inCTile += bytearray(struct.pack('Q', inCMintPos)) # uint 64
				lenBuf += bytearray(struct.pack('H', iLen)) # uint 16
				inCMintPos+=iLen
			else: # Ingest NaN or Null string value into "" blank zero length string 
				inCTile += bytearray(struct.pack('Q', inCMintPos)) #uint 64
				lenBuf += bytearray(struct.pack('H', 0)) #uint 16
				print("WARNING: value:",inTList[i],"is not text.  Converted to zero length string");
		inCTile += lenBuf
		return inCMintPos

	def geo_img_msg(self, inBuf, inGroup, inDashname, inSheet, inImgName):
		bs = bStream()
		bs.add_string("Func", "API")
		bs.add_string("Event","GEO IMAGE")
		bs.add_string("Group",inGroup)
		bs.add_string("Name",inDashname)
		bs.add_string("Sheet", inSheet)
		bs.add_string("FileName", inImgName)
		bs.add_buffer( "Data", inBuf )
		return b"BS="+bs.save_to_buffer()

	def img_msg(self, inBuf, inGroup, inDashname, inImgName): # sends images to panes from buffer
		bs = bStream()
		bs.add_string("Func", "API")
		bs.add_string("Event","DASH IMAGE")
		bs.add_string("Group",inGroup)
		bs.add_string("Name",inDashname)
		bs.add_string("FileName", inImgName)
		bs.add_buffer( "Data", inBuf )
		return b"BS="+bs.save_to_buffer()
	
	def img_msg_from_path(self, inPath, inGroup, inDashname): # sends images to panes
		if ( os.path.exists( inPath ) ) :
			fName = os.path.basename(inPath)
			with open(inPath, 'rb') as f:
				bs = bStream()
				bs.add_string("Func", "API")
				bs.add_string("Event","DASH IMAGE")
				bs.add_string("Group",inGroup)
				bs.add_string("Name",inDashname)
				bs.add_string("FileName", fName)
				bs.add_buffer( "Data", f.read() )
				# bs.save("/home/row64/Downloads/gen_img_2.msg") # uncomment to debug by saving to file
				return b"BS="+bs.save_to_buffer()
		return None
	
	def gen_msg(self, inList):

		# Single Row Example: ["car1", 234.1, 52.2]
		# Multi-Row Example: [["car1","car2"], [234.1,234.2], [52.2,52.3]]
		
		if self.TableName == "":raise Exception("gen_msg: Table name has not been set")

		multiList = False
		nbRows = 1
		if type(inList[0]) is list: 
			multiList = True
			nbRows = len(inList[0])
			
		if(multiList):
			sizeError=False
			for i,ct in enumerate(self.basic_types):
				size = len(inList[i])
				if i != 0 and lastSize != size:sizeError=True;break
				lastSize = size
			if sizeError:
				cSizes = []
				for i,ct in enumerate(self.basic_types):cSizes.append(len(inList[i]))
				print("column sizes:",cSizes)
				raise Exception("gen_msg: Column lengths do not match, producing an invalid dataframe")

		bs = bStream() # message bytestream
		bs.add_string("Func","API")
		bs.add_string("DBAlias","Row64")
		bs.add_string("DBName",self.DBName)
		bs.add_string("TableName",self.TableName)
		bs.add_string("Event",self.Cmd)
		bs.add_int32("KeyIndex",self.KeyIndex)
		
		rb = bStream() # ramdb bytestream
		rb.add_string("Name","")
		rb.add_int64("NbCols",len(self.col_types))
		rb.add_int64("NbRows",nbRows)
		rb.add_string_vector("ColNames",self.col_names)
		rb.add_int32_vector("ColTypes",self.col_types)
		rb.add_int32_vector("ColSizes",self.col_sizes)
		if self.Cmd == "UPSERT" or self.Cmd == "UPSERT VERBOSE":
			rb.add_int32_vector("ColMap",self.col_map)

		cTile = bytearray()
		cMint = bytearray()
		cMintPos = 0
		
		if self.verbose: ################################# VERBOSE DEBUG FEEDBACK #################################
			if len(self.col_types)==0:
				print("ERROR: Column Types have not been set.  Call set_types or set_types_from_ramdb.")
			if multiList:
				for i,ct in enumerate(self.basic_types):
					if ct == 1: # int
						for j in range(len(inList[i])):
							if isinstance(inList[i][j], numbers.Number):
								cTile += bytearray(struct.pack('i', int(inList[i][j])))
							else:
								print("WARNING:", inList[i][j], "is not a valid int, converting to NULL value")
								cTile += bytes.fromhex("00000080") # 0x80000000 sentinal NULL value
					elif ct == 2: # bigint
						for j in range(len(inList[i])):
							if isinstance(inList[i][j], numbers.Number):
								cTile += bytearray(struct.pack('q', int(inList[i][j])))
							else:
								print("WARNING:", inList[i][j], "is not a valid bigint, converting to NULL value")
								cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
					elif ct == 3: # float
						for j in range(len(inList[i])):
							if isinstance(inList[i][j], numbers.Number):
								cTile += bytearray(struct.pack('f', float(inList[i][j])))
							else:
								print("WARNING:", inList[i][j], "is not a valid float, converting to NULL value")
								cTile += bytes.fromhex("FFFFFFFF")  # 0xFFFFFFFF sentinal NULL value
					elif ct == 4: # bigfloat
						for j in range(len(inList[i])):
							if isinstance(inList[i][j], numbers.Number):
								cTile += bytearray(struct.pack('d', float(inList[i][j]))) # Python float = double
							else:
								print("WARNING:", inList[i][j], "is not a valid bigfloat, converting to NULL value")
								cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
					elif ct == 5: # text
						cMintPos = self.add_text_list_debug(inList[i], cMint, cTile, cMintPos)

			else:
				for i,ct in enumerate(self.basic_types):
					if ct == 1: # int
						if i>=len(inList):
							print("WARNING: type length:",len(self.basic_types),"is greater than gen_msg inList:",len(inList))
							cTile += bytes.fromhex("00000080") # 0x80000000 sentinal NULL value
						elif isinstance(inList[i], numbers.Number):
							cTile += bytearray(struct.pack('i', int(inList[i])))
						else:
							print("WARNING:", inList[i], "is not a valid int, converting to NULL value")
							cTile += bytes.fromhex("00000080") # 0x80000000 sentinal NULL value
					elif ct == 2: # bigint
						if i>=len(inList):
							print("WARNING: type length:",len(self.basic_types),"is greater than gen_msg inList:",len(inList))
							cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
						elif isinstance(inList[i], numbers.Number):
							cTile += bytearray(struct.pack('q', int(inList[i])))
						else:
							print("WARNING:", inList[i], "is not a valid bigint, converting to NULL value")
							cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
					elif ct == 3: # float
						if i>=len(inList):
							print("WARNING: type length:",len(self.basic_types),"is greater than gen_msg inList:",len(inList))
							cTile += bytes.fromhex("FFFFFFFF")  # 0xFFFFFFFF sentinal NULL value
						elif isinstance(inList[i], numbers.Number):
							cTile += bytearray(struct.pack('f', float(inList[i])))
						else:
							print("WARNING:", inList[i], "is not a valid float, converting to NULL value")
							cTile += bytes.fromhex("FFFFFFFF")  # 0xFFFFFFFF sentinal NULL value
					elif ct == 4: # bigfloat
						if i>=len(inList):
							print("WARNING: type length:",len(self.basic_types),"is greater than gen_msg inList:",len(inList))
							cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
						elif isinstance(inList[i], numbers.Number):
							cTile += bytearray(struct.pack('d', float(inList[i]))) # Python float = double
						else:
							print("WARNING:", inList[i], "is not a valid bigfloat, converting to NULL value")
							cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
					elif ct == 5: # text
						cMintPos = self.add_text_list_debug([inList[i]], cMint, cTile, cMintPos)

		else: ################################# SILENT NO FEEDBACK #################################
			if multiList:
				for i,ct in enumerate(self.basic_types):
					if ct == 1: # int
						for j in range(len(inList[i])):
							if isinstance(inList[i][j], numbers.Number):
								cTile += bytearray(struct.pack('i', int(inList[i][j])))
							else:
								cTile += bytes.fromhex("00000080") # 0x80000000 sentinal NULL value
					elif ct == 2: # bigint
						for j in range(len(inList[i])):
							if isinstance(inList[i][j], numbers.Number):
								cTile += bytearray(struct.pack('q', int(inList[i][j])))
							else:
								cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
					elif ct == 3: # float
						for j in range(len(inList[i])):
							if isinstance(inList[i][j], numbers.Number):
								cTile += bytearray(struct.pack('f', float(inList[i][j])))
							else:
								cTile += bytes.fromhex("FFFFFFFF")  # 0xFFFFFFFF sentinal NULL value
					elif ct == 4: # bigfloat
						for j in range(len(inList[i])):
							if isinstance(inList[i][j], numbers.Number):
								cTile += bytearray(struct.pack('d', float(inList[i][j]))) # Python float = double
							else:
								cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
					elif ct == 5: # text
						cMintPos = self.add_text_list_debug(inList[i], cMint, cTile, cMintPos)
						
			else:
				for i,ct in enumerate(self.basic_types):
					if ct == 1: # int
						if i>=len(inList):
							cTile += bytes.fromhex("00000080") # 0x80000000 sentinal NULL value
						elif isinstance(inList[i], numbers.Number):
							cTile += bytearray(struct.pack('i', int(inList[i])))
						else:
							cTile += bytes.fromhex("00000080") # 0x80000000 sentinal NULL value
					elif ct == 2: # bigint
						if i>=len(inList):
							cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
						elif isinstance(inList[i], numbers.Number):
							cTile += bytearray(struct.pack('q', int(inList[i])))
						else:
							cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
					elif ct == 3: # float
						if i>=len(inList):
							cTile += bytes.fromhex("FFFFFFFF")  # 0xFFFFFFFF sentinal NULL value
						elif isinstance(inList[i], numbers.Number):
							cTile += bytearray(struct.pack('f', float(inList[i])))
						else:
							cTile += bytes.fromhex("FFFFFFFF")  # 0xFFFFFFFF sentinal NULL value
					elif ct == 4: # bigfloat
						if i>=len(inList):
							cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
						elif isinstance(inList[i], numbers.Number):
							cTile += bytearray(struct.pack('d', float(inList[i]))) # Python float = double
						else:
							cTile += bytes.fromhex("0000000000000080")  # 0x8000000000000000 sentinal NULL value
					elif ct == 5: # text
						cMintPos = self.add_text_list_debug([inList[i]], cMint, cTile, cMintPos)
		
		rb.add_buffer("cTile",cTile)
		rb.add_buffer("cMint",cMint)
		bs.add_stream("Data",rb.save_to_buffer() )
		
		if self.debug_to_file:
			rb.save("/home/row64/debug_stream_df.ramdb") # debug dataframe as .ramdb file
			bs.save("/home/row64/debug_stream_msg.ramdb") # debug entire message as .ramdb file
		return b"BS="+bs.save_to_buffer()

