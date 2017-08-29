import os
import pathlib

# Path to Data Assistant tools
_daGPTools = str((pathlib.Path(__file__).parents[1] / "Shared\\GPTools\\pyt").absolute())
# location for local output
_localOutputPath = str(pathlib.Path(__file__).parents[0] / 'testOutput')
_outputDirectory = os.path.join(_daGPTools, 'scripts', 'dla.gdb')

########### Source and Target ##########
# DB Workspaces
_localWorkspace = list()
_localWorkspace.append(
    {"Source": str(pathlib.Path(".\localData\WaterDataMigration.gdb").absolute()),
     "Target": str(pathlib.Path(".\localData\WaterDataMigration.gdb").absolute()),
     "SourceName": "source",
     "TargetName": "Target",
     "xmlLocation": os.path.join(_localOutputPath, "GDB_to_GDB.xml"),
     "outXML": os.path.join(_localOutputPath, "test_GDB.xml"),
     "correctXML": str(pathlib.Path(r".\testOutput\correctXML\GDB\correct_GDB.xml").absolute()),
     "MatchLibrary": str(pathlib.Path(r".\testOutput\correctXML\GDB\MatchLocal.xml").absolute())
     })

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
