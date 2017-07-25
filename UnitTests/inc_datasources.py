import os
import pathlib

# Path to Data Assistant tools
_daGPTools = r"C:\Users\Win10\AppData\Local\ESRI\ArcGISPro\AssemblyCache\{28142961-b645-420f-ba2a-72bcf8212558}\GPTools\arcpy"
# location for local output
_localOutputPath = str(pathlib.Path(__file__).parents[0] / 'testOutput')
_outputDirectory = str(pathlib.Path(__file__).parents[0] / 'dla.gdb')

########### Source and Target ##########
# DB Workspaces
_localWorkspace = list()
_localWorkspace.append(
    {"Source": str(pathlib.Path(".\localData\WaterDataMigration.gdb").absolute()),
     "Target": str(pathlib.Path(".\localData\WaterDataMigration.gdb").absolute()),
     "SourceName": "source",
     "TargetName": "Target",
     "OriginalPath": str(pathlib.Path(".\localData\Originals\WaterDataMigration.gdb\Target").absolute())})  # might not need
# _localWorkspace.append({"Source":str(pathlib.Path(".\localData").absolute()),
#                       "Target":str(pathlib.Path(".\localData").absolute()),
#                        "SourceName":"source.lyrx",
#                        "TargetName":"Target.lyrx"})


# DB Connection
_dbConnStr = list()
_dbConnStr.append({"title": "GDB Source",
                   "dataPath": str(pathlib.Path(".\localData\WaterDataMigration.gdb\source").absolute())})
_dbConnStr.append({"title": "GDB Target",
                   "dataPath": str(pathlib.Path(".\localData\WaterDataMigration.gdb\Target").absolute())})

_dbConnStr.append({"title": "Layer Source",
                   "dataPath": str(pathlib.Path(".\localData\source.lyrx").absolute())})
_dbConnStr.append({"title": "Layer Target",
                   "dataPath": str(pathlib.Path(".\localData\Target.lyrx").absolute())})

########### Source and Target Matrix ##########
_configMatrix = list()
_configMatrix.append({"Source": _dbConnStr[0],
                      "Target": _dbConnStr[1],
                      "xmlLocation": os.path.join(_localOutputPath, "GDB_to_GDB.xml"),
                      "outXML": os.path.join(_localOutputPath, "test_GDB.xml"),
                      "correctXML": str(pathlib.Path(r".\testOutput\correctXML\GDB\correct_GDB.xml").absolute()),
                      "MatchLibrary": str(pathlib.Path(r".\testOutput\correctXML\GDB\MatchLocal.xml").absolute())})
# _configMatrix.append({"Source":_dbConnStr[2],
#                      "Target":_dbConnStr[3],
#                      "xmlLocation":os.path.join(_localOutputPath,"lyrx_to_lyrx.xml"),
#                      "outXML":os.path.join(_localOutputPath,"test_lyrx.xml")})


########## XML Syntax ############
# XML Method Names. Change these if XML formatting ever changes
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
