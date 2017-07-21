import arcpy, os, dla
from inc_datasources import _configMatrix, _XMLMethodNames, _localWorkspace, _outputDirectory


# takes the xml file and creates the fields that should be in the new feature class
def build_correct_fields(xmlLocation):
	fields = dla.getXmlElements(xmlLocation, "Field")
	correct_fields = []
	for field in fields:
		if str.lower(dla.getNodeValue(field, "TargetName")) != "globalid":
			correct_fields.append(dla.getNodeValue(field, "TargetName"))
	return correct_fields


# creates a searchCursor for a given feature class and returns an array of that table
def build_table(directory, table):
	arcpy.env.workspace = directory
	cursor = arcpy.da.SearchCursor(table, "*")
	return [row for row in cursor]


# the dla.gdb is the test workspace the feature classes are created in. To pull the one we want, we clear the workspace
# so that the newly created one is the only one that exists. This function clears the workspace.
def clearFeatureClasses(directory):
	arcpy.env.workspace = directory
	featureclasses = arcpy.ListFeatureClasses()
	for featureclass in featureclasses:
		arcpy.Delete_management(os.path.join(directory, featureclass))

#after the data is replaced or appended, this function will restore the target to the original state
def restoreData(copyPath, targetpath):
	try:
		copyCursor = arcpy.da.UpdateCursor(copyPath,"*")
		targetCursor = arcpy.da.UpdateCursor(targetpath, "*")

		for copyRow, targetRow in zip(copyCursor, targetCursor):
			targetCursor.updateRow(copyRow)
		for row in targetCursor:
			targetCursor.deleteRow()
	except:
		pass

# checks to see the fields are correctly labeled in the new file
def test_fields(tester, directory, localWorkspace, xmlLocation):  # TODO: Currently omitting GlobalID checks
	correctFields = build_correct_fields(xmlLocation)
	arcpy.env.workspace = directory
	featureclass = arcpy.ListFeatureClasses()[0]
	fields = arcpy.ListFields(featureclass)

	fieldnames = []
	for field in fields:
		if field.name.lower() not in ["","objectid", "shape","globalid"]:
			fieldnames.append(field.name)

	for cfield in correctFields:
		tester.assertIn(fieldnames,cfield)


# ensures there are a correct amount of rows.
def test_length(tester, mode, localWorkspace, rowLimit=100):
	sourceFeatureClass = ""
	targetFeatureClass = ""
	arcpy.env.workspace = localWorkspace["Source"]
	for fc in arcpy.ListFeatureClasses(): #TODO: update this. shouldn't have to iterate through all Feature Classes
		if fc == localWorkspace["TargetName"]:
			targetFeatureClass = fc
		if fc == localWorkspace["SourceName"]:
			sourceFeatureClass = fc

	sourceFCPath = localWorkspace["Source"]
	sourceCursor = build_table(sourceFCPath, sourceFeatureClass)

	targetFCPath = localWorkspace["Target"]
	targetCursor = build_table(targetFCPath, targetFeatureClass)

	directory = _outputDirectory
	arcpy.env.workspace = directory
	featureclass = arcpy.ListFeatureClasses()[0]
	cursor = build_table(directory, featureclass)

	if mode == "Preview":
		tester.assertEqual(len(cursor), rowLimit)
	if mode == "Stage":
		tester.assertEqual(len(cursor), len(sourceCursor))
	if mode == "Append":
		tester.assertEqual(len(targetCursor), len(cursor) + len(sourceCursor))
	if mode == "Replace":
		tester.assertEqual(len(targetCursor),len(cursor))

# due to the nature of the ReplaceByField mutation of the attribute table, a seperate function is needed to test it
def test_replace_data(tester, targetDataPath, sourceDataPath, xmlLocation):
	ReplaceBy = dla.getXmlElements(xmlLocation, "ReplaceBy")[0]
	FieldName = dla.getNodeValue(ReplaceBy, "FieldName")
	Operator = dla.getNodeValue(ReplaceBy, "Operator")
	Value = dla.getNodeValue(ReplaceBy, "Value")

	for field in dla.getXmlElements(xmlLocation, "Field"): #pulling relevant fields for the cursor from the xml file
		if str.lower(sourcefield) == "globalid" or str.lower(dla.getNodeValue(field, "TargetName")) == "globalid":
			continue
		targetfields.append(dla.getNodeValue(field, "TargetName"))

	indexFieldName = targetfields.index(FieldName)
	copy = arcpy.da.SearchCursor(copyDataPath, targetfields) # takes a copy of the target before the Replace was done
	target = arcpy.da.SearchCursor(targetDataPath, targetfields)# identical fields to the copy generator

	replacedRowsList = []
	for copyRow, targetRow in zip(copy, target): #will iterate through until all of the copy cursor is exhausted
		while targetRow != copyRow:
			if Operator == "=":
				tester.assertEqual(targetRow[indexFieldName], Value)
			if Operator == "!=":
				tester.assertNotEqual(targetRow[indexFieldName], Value)
			if Operator == "Like":
				tester.assertIn(Value, targetRow[indexFieldName])

			replacedRowList.append(copyRow)
			copyRow = copy.next()

	for targetRow, copyRow in zip(target, replacedRowsList): #now iterates through the rows that should have been
		tester.assertEqual(targetRow, copyRow) # appended to ensure order and accuracy. Here the target cursor starts
											   # at where the beginning of the re-appended rows should be

# ensures the data fits what it should be according to the specified method
def test_data(tester, sourceDataPath, localDataPath, xmlLocation, cutoff=0, AppendCheck=False):
	defaultValues = {}
	fields = []
	for field in arcpy.ListFields(localDataPath):
		defaultValues[field.name] = field.defaultValue
	# iterates through the fields from xml document and checks value, field by field, row by row
	for field in dla.getXmlElements(xmlLocation, "Field"):  # TODO: rework to address mulitple tests
		method = dla.getNodeValue(field, "Method")
		methods = _XMLMethodNames
		sourcefield = dla.getNodeValue(field, "SourceName")
		targetfield = dla.getNodeValue(field, "TargetName")
		cursor = [row for row in arcpy.da.SearchCursor(localDataPath, targetfield)] #TODO: look into time complexity/PANDA
		cursor = cursor[cutoff:]  # brings the target table up to the append point if appending
		if sourcefield == "(None)":  # testing for None must be done outside the main for loop
			for row in cursor:
				testNone(tester,row[0],defaultValues[targetfield],AppendCheck)
			continue

		sourceCursor = [row for row in arcpy.da.SearchCursor(sourceDataPath, sourcefield)]



		for row, sourceRow in zip(cursor, sourceCursor):
			row = row[0]
			sourceRow = sourceRow[0]
			if method == methods["Copy"]:
				if str.lower(
						dla.getNodeValue(field, "TargetName")) == "globalid":  # really weird outcomes with globalID
					continue
				testCopy(tester, sourceRow, row)
			elif method == methods["Set Value"]:
				testSetValue(tester, row,field)

			elif method == methods["Value Map"]:
				testValueMap(tester, row,field)

			elif method == methods["Change Case"]:
				testChangeCase(tester, sourceRow, row, field)

			elif method == methods["Concatenate"]:
				testConcatenate(tester, row, field)

			elif method == methods["Left"]:
				testLeft(tester, sourceRow, row, field)

			elif method == methods["Right"]:
				testRight(tester, sourceRow, row, field)

			elif method == methods["Substring"]:  # BUG Substring will take a null field and make substring from 'None' ???
				testSubstring(tester, sourceRow, row, field)

			elif method == methods["Split"]:
				testSplit(tester, row, field)

			elif method == methods["Conditional Value"]:  # for some reason to add strings as conditional they must be surrounded by " or '
				testConditionalVal(tester, sourceRow, row, field)

			elif method == methods["Domain Map"]:
				testDomainMap(tester, sourceRow, row, field)
			else:
				tester.assertIn(method,methods)


def testNone(tester, newTargetValue, defaultValue, AppendCheck):  # Very very messy implementation
	if AppendCheck:
		tester.assertEqual(newTargetValue,defaultValue)
	else:
		tester.assertIsNone(newTargetValue)


# checks to see if the Copy function worked properly. Target value should be the same as Source value
def testCopy(tester, sourceValue, targetValue): #TODO: Come up with a better way of assesing this
	try:
		tester.assertEqual(sourceValue, targetValue)
	except: #TODO: get type of source field and targetfield to avoid nested try
		try:
			svalue = float(sourceValue)
			tester.assertEqual(sourceValue, targetValue)
		except:
			tester.assertEqual(str(sourceValue), str(
				targetValue))

def testSetValue(tester, targetValue,field):# checks to see if the Set Value function worked properly. All Target values should be equal to the value
	setValue = dla.getNodeValue(field, "SetValue")
	try:
		setValue = float(setValue)
		tester.assertEqual(targetValue,
		                   setValue)
	except:
		tester.assertEqual(targetValue, str(setValue))


# checks to see that if the Source value is equal to sValue, the Target value is equal to tValue
def testValueMap(tester, targetValue,field):
	valueMaps = field.getElementsByTagName("ValueMap")
	for valueMap in valueMaps:
		sourceValues = valueMap.getElementsByTagName("sValue")
		targetValues = valueMap.getElementsByTagName("tValue")
		for source, target in zip(sourceValues, targetValues):
			sValue = dla.getTextValue(source)
			tValue = dla.getTextValue(target)
			if sourceRow.getValue(sourcefield) == sValue: #TODO: change this to the updated cursor
				tester.assertEqual(tValue, targetValue)


# checks to see if the case has been changed depending on which action was requested
def testChangeCase(tester, sourceValue, targetValue, field):

	case = dla.getNodeValue(field, "ChangeCase")
	if case == "UpperCase":
		tester.assertEqual(targetValue, sourceValue.upper())
	if case == "Lowercase":
		tester.assertEqual(targetValue, str.lower(sourceValue))
	if case == "Title":
		for t, s in zip(str.split(targetValue),
		                str.split(sourceValue)):
			tester.assertEqual(t, str.capitalize(s))
	if case == "Capitalize":
		tester.assertEqual(targetValue, str.capitalize(sourceValue))


# checks to see if the two fields were concatenated correctly in the Target value
def testConcatenate(tester, targetValue, field):
	seperator = dla.getNodeValue(field, "Separator")
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

# checks to ensure the Target value is the source value's first "count" of characters
def testLeft(tester, sourceValue, targetValue, field):
	count = dla.getNodeValue(field, "Left")
	count = int(count)
	tester.assertEqual(targetValue, sourceValue[:count])


# checks to ensure the Target value is the source value's last "count" of characters
def testRight(tester, sourceValue, targetValue, field):
	count = dla.getNodeValue(field, "Right")
	count = int(count)
	tester.assertEqual(targetValue,
	                   sourceValue[len(sourceRow.getValue(sourcefield)) - count:]) #TODO: update to new cursor syntax


# checks to see the Target value is the specified substring of the Source value as dictated by start and length
def testSubstring(tester, sourceValue, targetValue, field):
	start = int(dla.getNodeValue(field, "Start"))
	length = int(dla.getNodeValue(field, "Length"))
	tester.assertEqual(targetValue,
	                   sourceValue[start:start + length])


# checks to see that testSplit follows the preview rules (as in the error handling) and also splits properly given
# valid parameters
def testSplit(tester, targetValue, field):
	splitAt = dla.getNodeValue(field, "SplitAt")
	part = dla.getNodeValue(field, "Part")
	try:
		finishedOutput = str.split(row.getValue(targetfield), splitAt)
		finishedOutput = finishedOutput[part]
		tester.assertEqual(row.getValue(targetfield), finishedOutput)
	except:
		tester.assertEqual(row.getValue(targetfield), None)


# chips off the string characters and ensures that the conditonal value is evaluated correctly
def testConditionalVal(tester, sourceValue, targetValue, field):
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


# works very similar to ValueMapping, just with domain XML terminology
def testDomainMap(tester, sourceValue, targetValue, field):
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
						tester.assertEqual(tValue, targetValue)
					except:
						tester.assertEqual(tValue, str(
							targetValue))


#taken from https://bitbucket.org/ianb/formencode/src/tip/formencode/doctest_xml_compare.py?fileviewer=file-view-default#cl-70
def xml_compare(x1, x2, reporter=None):
    if x1.tag != x2.tag:
        if reporter:
            reporter('Tags do not match: %s and %s' % (x1.tag, x2.tag))
        return False
    for name, value in x1.attrib.items():
        if x2.attrib.get(name) != value:
            if reporter:
                reporter('Attributes do not match: %s=%r, %s=%r'
                         % (name, value, name, x2.attrib.get(name)))
            return False
    for name in x2.attrib.keys():
        if name not in x1.attrib:
            if reporter:
                reporter('x2 has an attribute x1 is missing: %s'
                         % name)
            return False
    if not text_compare(x1.text, x2.text):
        if reporter:
            reporter('text: %r != %r' % (x1.text, x2.text))
        return False
    if not text_compare(x1.tail, x2.tail):
        if reporter:
            reporter('tail: %r != %r' % (x1.tail, x2.tail))
        return False
    cl1 = x1.getchildren()
    cl2 = x2.getchildren()
    if len(cl1) != len(cl2):
        if reporter:
            reporter('children length differs, %i != %i'
                     % (len(cl1), len(cl2)))
        return False
    i = 0
    for c1, c2 in zip(cl1, cl2):
        i += 1
        if not xml_compare(c1, c2, reporter=reporter):
            if reporter:
                reporter('children %i do not match: %s'
                         % (i, c1.tag))
            return False
    return True


def text_compare(t1, t2):
    if not t1 and not t2:
        return True
    if t1 == '*' or t2 == '*':
        return True
    return (t1 or '').strip() == (t2 or '').strip()