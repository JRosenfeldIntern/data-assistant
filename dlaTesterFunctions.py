import arcpy, os, dla
from inc_datasources import _configMatrix, _XMLMethodNames, _localWorkspace

#takes the xml file and creates the fields that should be in the new feature class
def build_correct_fields(xmlLocation):
	fields = dla.getXmlElements(xmlLocation, "Field")
	correct_fields = []
	for field in fields:
		if str.lower(dla.getNodeValue(field, "TargetName")) != "globalid":
			correct_fields.append(dla.getNodeValue(field, "TargetName"))
	return correct_fields

#creates a searchCursor for a given feature class and returns an array of that table
def build_table(directory,table):
	arcpy.env.workspace = directory
	cursor = arcpy.da.SearchCursor(table,"*")
	return [row for row in cursor]

# the dla.gdb is the test workspace the feature classes are created in. To pull the one we want, we clear the workspace
# so that the newly created one is the only one that exists. This function clears the workspace.
def clearFeatureClasses(directory):
	arcpy.env.workspace = directory
	featureclasses = arcpy.ListFeatureClasses()
	for featureclass in featureclasses:
		arcpy.Delete_management(os.path.join(directory, featureclass))

# checks to see the fields are correctly labeled in the new file
def test_fields(tester,directory,localWorkspace,xmlLocation): #TODO: Currently omitting GlobalID checks
	correctFields = build_correct_fields(xmlLocation)
	arcpy.env.workspace = directory
	featureclass = arcpy.ListFeatureClasses()[0]
	fields = arcpy.ListFields(featureclass)

	fieldnames = []
	for field in fields:
		if field.name != "" and field.name != "OBJECTID" and field.name != "Shape" and str.lower(
				field.name) != "globalid":
			fieldnames.append(field.name)

	for cfield in correctFields:
		tester.assertTrue(fieldnames.__contains__(cfield))

# ensures there are a correct amount of rows. At the moment is O(n), there might be a more efficient way that doesn't
# require iterating through the rows
def test_length(tester,mode,localWorkspace,rowLimit=100):

	sourceFeatureClass = ""
	targetFeatureClass = ""
	arcpy.env.workspace = localWorkspace["Source"]
	for fc in arcpy.ListFeatureClasses():
		if fc == localWorkspace["TargetName"]:
			targetFeatureClass = fc
		if fc == localWorkspace["SourceName"]:
			sourceFeatureClass = fc

	sourceFCPath = localWorkspace["Source"]
	sourceCursor = build_table(sourceFCPath,sourceFeatureClass)

	targetFCPath = localWorkspace["Target"]
	targetCursor = build_table(targetFCPath,targetFeatureClass)

	directory = r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\dla.gdb" #TODO: correct directory
	arcpy.env.workspace = directory
	featureclass = arcpy.ListFeatureClasses()[0]
	cursor = build_table(directory,featureclass)

	if mode == "Preview":
		tester.assertEqual(len(cursor),rowLimit)
	if mode == "Stage":
		tester.assertEqual(len(cursor),len(sourceCursor))
	if mode == "Append":
		tester.assertEqual(len(targetCursor),len(cursor)+len(sourceCursor))



def test_data(tester,sourceDataPath,localDataPath,xmlLocation,cutoff = 0,AppendCheck = False):
	defaultValues = {}
	for field in arcpy.ListFields(localDataPath):
		defaultValues[field.name] = field.defaultValue
	#iterates through the fields from xml document and checks value, field by field, row by row
	for field in dla.getXmlElements(xmlLocation,"Field"): #TODO: rework to address mulitple tests
		method = dla.getNodeValue(field,"Method")
		methods = _XMLMethodNames
		sourcefield = dla.getNodeValue(field,"SourceName")
		targetfield = dla.getNodeValue(field,"TargetName")
		cursor = [row for row in arcpy.da.SearchCursor(localDataPath,targetfield)]
		cursor = cursor[cutoff:] #brings the target table up to the append point if appending

		if sourcefield == "(None)": #testing for None must be done outside the main for loop
			if AppendCheck:
				for row in cursor:
					tester.assertEqual(row[0],defaultValues[targetfield])
				continue
			for row in cursor:
				testNone(tester,row[0])
			continue

		sourceCursor = [row for row in arcpy.da.SearchCursor(sourceDataPath,sourcefield)]

		for row,sourceRow in zip(cursor,sourceCursor):
			row = row[0]
			sourceRow = sourceRow[0]
			if method == methods["Copy"]:
				if str.lower(dla.getNodeValue(field,"TargetName")) == "globalid": #really weird outcomes with globalID
				 	continue
				testCopy(tester,sourceRow,row)

			if method == methods["Set Value"]:
				testSetValue(tester,row)

			if method == methods["Value Map"]:
				testValueMap(tester,row)

			if method == methods["Change Case"]:
				testChangeCase(tester,sourceRow,row,field)

			if method == methods["Concatenate"]:
				testConcatenate(tester,row,field)

			if method == methods["Left"]:
				testLeft(tester,sourceRow,row,field)

			if method == methods["Right"]:
				testRight(tester,sourceRow,row,field)

			if method == methods["Substring"]:  # BUG Substring will take a null field and make substring from 'None' ???
				testSubstring(tester,sourceRow,row,field)

			if method == methods["Split"]:
				testSplit(tester,row,field)

			if method == methods["Conditional Value"]:  # for some reason to add strings as conditional they must be surrounded by " or '
				testConditionalVal(tester,sourceRow,row,field)

			if method == methods["Domain Map"]:
				testDomainMap(tester,sourceRow,row,field)

def testNone(tester,newTargetValue): #Very very messy implementation
	tester.assertIsNone(newTargetValue)

#checks to see if the Copy function worked properly. Target value should be the same as Source value
def testCopy(tester,sourceValue,targetValue):
	print("source:",sourceValue,"value:",targetValue)
	# try:
	# 	tester.assertEqual(sourceValue, targetValue)
	# except:
	# 	try:
	# 		svalue = float(sourceValue)
	# 		tester.assertEqual(sourceValue, targetValue)
	# 	except:
	# 		tester.assertEqual(str(sourceValue),str(targetValue))

#checks to see if the Set Value function worked properly. All Target values should be equal to the value
def testSetValue(tester,targetValue):
	setValue = dla.getNodeValue(field, "SetValue")
	try:
		setValue = float(setValue)
		tester.assertEqual(targetValue,
	                 setValue)
	except:
		tester.assertEqual(targetValue,str(setValue))

#checks to see that if the Source value is equal to sValue, the Target value is equal to tValue
def testValueMap(tester,targetValue):
	valueMaps = field.getElementsByTagName("ValueMap")
	for valueMap in valueMaps:
		sourceValues = valueMap.getElementsByTagName("sValue")
		targetValues = valueMap.getElementsByTagName("tValue")
		for source, target in zip(sourceValues, targetValues):
			sValue = dla.getTextValue(source)
			tValue = dla.getTextValue(target)
			if sourceRow.getValue(sourcefield) == sValue:
				tester.assertEqual(tValue, targetValue)

#checks to see if the case has been changed depending on which action was requested
def testChangeCase(tester,sourceValue,targetValue,field):
	case = dla.getNodeValue(field, "ChangeCase")
	if case == "UpperCase":
		tester.assertEqual(targetValue, str.capitalize(sourceValue))
	if case == "Lowercase":
		tester.assertEqual(targetValue, str.lower(sourceValue))
	if case == "Title":
		for t, s in zip(str.split(targetValue),
		                str.split(sourceValue)):
			tester.assertEqual(t, str.capitalize(s))
	if case == "Capitalize":
		tester.assertEqual(targetValue, str.capitalize(sourceValue))

#checks to see if the two fields were concatenated correctly in the Target value
def testConcatenate(tester,targetValue,field):
	seperator = dla.getNodeValue(field, "Seperator")
	if seperator == "(space)":
		seperator = " "
	confields = field.getElementsByTagName("cFields")
	for confield in confields:
		fieldreplacers = confield.getElementsByTagName("cField")
		finishedOutput = ""
		first = False
	for f in fieldreplacers:
		if first:
			finishedOutput += f
			first = True
		else:
			finishedOutput += (seperator + f)
	tester.assertEqual(targetValue, finishedOutput)

#checks to ensure the Target value is the source value's first "count" of characters
def testLeft(tester,sourceValue,targetValue,field):
	count = dla.getNodeValue(field, "Left")
	count = int(count)
	tester.assertEqual(targetValue, sourceValue[:count])

#checks to ensure the Target value is the source value's last "count" of characters
def testRight(tester,sourceValue,targetValue,field):
	count = dla.getNodeValue(field, "Right")
	count = int(count)
	tester.assertEqual(targetValue,
	                 sourceValue[len(sourceRow.getValue(sourcefield)) - count:])

#checks to see the Target value is the specified substring of the Source value as dictated by start and length
def testSubstring(tester,sourceValue,targetValue,field):
	start = int(dla.getNodeValue(field, "Start"))
	length = int(dla.getNodeValue(field, "Length"))
	tester.assertEqual(targetValue,
	                 sourceValue[start:start + length - 1])

#checks to see that testSplit follows the preview rules (as in the error handling) and also splits properly given
#valid parameters
def testSplit(tester,targetValue,field):
	splitAt = dla.getNodeValue(field, "SplitAt")
	part = dla.getNodeValue(field, "Part")
	try:
		finishedOutput = str.split(row.getValue(targetfield), splitAt)
		finishedOutput = finishedOutput[part]
		tester.assertEqual(row.getValue(targetfield), finishedOutput)
	except:
		tester.assertEqual(row.getValue(targetfield), None)

#chips off the string characters and ensures that the conditonal value is evaluated correctly
def testConditionalVal(tester,sourceValue,targetValue,field):
	oper = dla.getNodeValue(field, "Oper")
	if oper[0] == "\"" or oper[0] == "\'":
		oper = oper[1:-1]
	ifStatement = dla.getNodeValue(field, "If")
	if ifStatement[0] == "\"" or ifStatement[0] == "\'":
		ifStatement = ifStatement[1:-1]
	thenStatement = dla.getNodeValue(field, "Then")
	if thenStatement[0] == "\"" or thenStatement[0] == "\'":
		thenStatement = thenStatement[1:-1]
	elseStatement = dla.getNodeValue(field, "Else")
	if elseStatement[0] == "\"" or elseStatement[0] == "\'":
		elseStatement = elseStatement[1:-1]
	try:
		thenStatement = float(thenStatement)
	except:
		thenStatement = str(thenStatement)
	if oper == "==":
		if sourceValue == ifStatement:
			tester.assertEqual(targetValue, thenStatement)
		else:
			tester.assertEqual(targetValue, elseStatement)
	if oper == "!=":
		if sourceValue != ifStatement:
			tester.assertEqual(targetValue, thenStatement)
		else:
			tester.assertEqual(targetValue, elseStatement)
	if oper == "<":
		if sourceValue < ifStatement:
			tester.assertEqual(targetValue, thenStatement)
		else:
			tester.assertEqual(targetValue, elseStatement)
	if oper == ">":
		if sourceValue > ifStatement:
			tester.assertEqual(targetValue, thenStatement)
		else:
			tester.assertEqual(targetValue, elseStatement)

#works very similar to ValueMapping, just with domain XML terminology
def testDomainMap(tester,sourceValue,targetValue,field):
	domainMaps = field.getElementsByTagName("DomainMap")
	for domainMap in domainMaps:
		sourceValues = domainMap.getElementsByTagName("sValue")
		targetValues = domainMap.getElementsByTagName("tValue")
		for source, target in zip(sourceValues, targetValues):
			sValue = dla.getTextValue(source)
			tValue = dla.getTextValue(target)
			if sValue != "(None)":
				if sourceValue == sValue:
					try:
						targetValue = float(targetValue)
						tester.assertEqual(tValue,targetValue)
					except:
						tester.assertEqual(tValue, str(
						targetValue))
