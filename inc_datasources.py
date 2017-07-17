import os,sys,pathlib

# Path to Data Assistant tools
_daGPTools = r"C:\Users\Win10\AppData\Local\ESRI\ArcGISPro\AssemblyCache\{28142961-b645-420f-ba2a-72bcf8212558}\GPTools\arcpy"
# location for local output
_localOutputPath = os.path.join(str(pathlib.Path(__file__).parents[0]),'testOutput')

########### Source and Target ##########
# DB Workspaces
_localWorkspace = []
_localWorkspace.append({"Source":r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\localData\WaterDataMigration.gdb",
                        "Target": r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\localData\WaterDataMigration.gdb",
                        "SourceName":"source",
                        "TargetName":"Target"})
_localWorkspace.append({"Source":r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\localData",
                       "Target":r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\localData",
                        "SourceName":"source.lyrx",
                        "TargetName":"Target.lyrx"})


# DB Connection
_dbConnStr = []
_dbConnStr.append({"title":"GDB Source",
                   "dataPath":r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\localData\WaterDataMigration.gdb\source"})
_dbConnStr.append({"title":"GDB Target",
                   "dataPath":r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\localData\WaterDataMigration.gdb\Target"})

_dbConnStr.append({"title":"Layer Source",
                   "dataPath":r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\localData\source.lyrx"})
_dbConnStr.append({"title":"Layer Target",
                   "dataPath":r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\localData\Target.lyrx"})


########### Source and Target Matrix ##########
_configMatrix=[]
_configMatrix.append({"Source":_dbConnStr[0],
                      "Target":_dbConnStr[1],
                      "xmlLocation":os.path.join(_localOutputPath,"GDB_to_GDB.xml"),
                      "case":"EGDB to EDGB"})
#_configMatrix.append({"Source":_dbConnStr[2],
#                      "Target":_dbConnStr[3],
#                      "xmlLocation":os.path.join(_localOutputPath,"lyrx_to_lyrx.xml")})

########### Additional Config Files ##########
# Valid Configuration Files
_validConfigFiles=[]
_validConfigFiles.append({"title":"FGDB to FGDB", "case":"Copy", "field":"all", "pathToFile":r"<files>/.xml"})
_validConfigFiles.append({"title":"FGDB to EGDB", "case":"Copy", "field":"all", "pathToFile":r"<files>/.xml"})                         
_validConfigFiles.append({"title":"EGDB to EGDB", "case":"Copy", "field":"all", "pathToFile":r"<files>/.xml"})
_validConfigFiles.append({"title":"EGDB to FGDB", "case":"Copy", "field":"all", "pathToFile":r"<files>/.xml"})

# Invalid Configuration Files
_invalidConfigFiles=[]
_invalidConfigFiles.append({"title":"FGDB to FGDB", "case":"incomplete value map, no otherwise", "field":"Phases Built", "pathToFile":r"<files>/.xml"})
_invalidConfigFiles.append({"title":"FGDB to FGDB", "case":"incomplete domain map, no otherwise", "field":"Phases Built", "pathToFile":r"<files>/.xml"})
_invalidConfigFiles.append({"title":"FGDB to view only EGDB", "case":"Copy", "field":"all", "pathToFile":r"<files>/.xml"})

#XML Method Names. Change these if you ever change XML formatting
_XMLMethodNames = {"None":"None",
            "Copy":"Copy",
            "Set Value":"SetValue",
            "Value Map": "ValueMap",
            "Change Case":"ChangeCase",
            "Concatenate":"Concatenate",
            "Left": "Left",
            "Right" : "Right",
            "Substring": "Substring",
            "Split":"Split",
            "Conditional Value":"ConditionalValue",
            "Domain Map":"DomainMap"}


