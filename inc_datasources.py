import os, sys, pathlib

# Path to Data Assistant tools
_daGPTools = r"C:\Users\Win10\AppData\Local\ESRI\ArcGISPro\AssemblyCache\{28142961-b645-420f-ba2a-72bcf8212558}\GPTools\arcpy"
# location for local output
_localOutputPath = str(pathlib.Path(__file__).parents[0] / 'testOutput')
_outputDirectory = str(pathlib.Path(__file__).parents[0] / 'dla.gdb')

########### Source and Target ##########
# DB Workspaces
_localWorkspace = []
_localWorkspace.append(
	{"Source": str(pathlib.Path(".\localData\WaterDataMigration.gdb").absolute()),
	 "Target": str(pathlib.Path(".\localData\WaterDataMigration.gdb").absolute()),
	 "SourceName": "source",
	 "TargetName": "Target"})
# _localWorkspace.append({"Source":str(pathlib.Path(".\localData").absolute()),
#                       "Target":str(pathlib.Path(".\localData").absolute()),
#                        "SourceName":"source.lyrx",
#                        "TargetName":"Target.lyrx"})


# DB Connection
_dbConnStr = []
_dbConnStr.append({"title": "GDB Source",
                   "dataPath": str(pathlib.Path(".\localData\WaterDataMigration.gdb\source").absolute())})
_dbConnStr.append({"title": "GDB Target",
                   "dataPath": str(pathlib.Path(".\localData\WaterDataMigration.gdb\Target").absolute())})

_dbConnStr.append({"title": "Layer Source",
                   "dataPath": str(pathlib.Path(".\localData\source.lyrx").absolute())})
_dbConnStr.append({"title": "Layer Target",
                   "dataPath": str(pathlib.Path(".\localData\Target.lyrx").absolute())})

########### Source and Target Matrix ##########
_configMatrix = []
_configMatrix.append({"Source": _dbConnStr[0],
                      "Target": _dbConnStr[1],
                      "xmlLocation": os.path.join(_localOutputPath, "GDB_to_GDB.xml"),
                      "outXML": os.path.join(_localOutputPath, "test_GDB.xml"),
                      "correctXML": str(pathlib.Path(r".\testOutput\correctXML\GDB\correct_GDB.xml").absolute()),
                      "MatchLibrary":str(pathlib.Path(r".\testOutput\correctXML\GDB\MatchLocal.xml").absolute())})
# _configMatrix.append({"Source":_dbConnStr[2],
#                      "Target":_dbConnStr[3],
#                      "xmlLocation":os.path.join(_localOutputPath,"lyrx_to_lyrx.xml"),
#                      "outXML":os.path.join(_localOutputPath,"test_lyrx.xml")})

########### Additional Config Files ##########
# Valid Configuration Files
_validConfigFiles = []
_validConfigFiles.append({"title": "FGDB to FGDB", "case": "Copy", "field": "all", "pathToFile": r"<files>/.xml"})
_validConfigFiles.append({"title": "FGDB to EGDB", "case": "Copy", "field": "all", "pathToFile": r"<files>/.xml"})
_validConfigFiles.append({"title": "EGDB to EGDB", "case": "Copy", "field": "all", "pathToFile": r"<files>/.xml"})
_validConfigFiles.append({"title": "EGDB to FGDB", "case": "Copy", "field": "all", "pathToFile": r"<files>/.xml"})

# Invalid Configuration Files
_invalidConfigFiles = []
_invalidConfigFiles.append(
	{"title": "FGDB to FGDB", "case": "incomplete value map, no otherwise", "field": "Phases Built",
	 "pathToFile": r"<files>/.xml"})
_invalidConfigFiles.append(
	{"title": "FGDB to FGDB", "case": "incomplete domain map, no otherwise", "field": "Phases Built",
	 "pathToFile": r"<files>/.xml"})
_invalidConfigFiles.append(
	{"title": "FGDB to view only EGDB", "case": "Copy", "field": "all", "pathToFile": r"<files>/.xml"})

# XML Method Names. Change these if you ever change XML formatting
_XMLMethodNames = {"None": "None",
                   "Copy": "Copy",
                   "Set Value": "SetValue",
                   "Value Map": "ValueMap",
                   "Change Case": "ChangeCase",
                   "Concatenate": "Concatenate",
                   "Left": "Left",
                   "Right": "Right",
                   "Substring": "Substring",
                   "Split": "Split",
                   "Conditional Value": "ConditionalValue",
                   "Domain Map": "DomainMap"}
