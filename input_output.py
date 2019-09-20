#This file contains all the code for getting data into and out of the main allocation program
import pandas as pd
import re
import sys
import library
import xlsxwriter
from natsort import natsorted
import xlrd

def parseproject(projstr):
	code = re.search("[A-Z]+[0-9][0-9]", projstr).group()
	title = re.split("[A-Z]+[0-9][0-9][.]\s", projstr)[-1]
	return {"code": code, "title": title}


def importStudents(filename):
	# Check what the file name ends with to determine what to do with it
	studPrefs = {}
	studTopicPrefs = {}
	medChemStudPrefs = {}
	medChemStudTopicPrefs = {}
	unassigned = []
	med_unassigned = []
	preferenceregex = [re.compile("pref\s*\d",flags=re.IGNORECASE), re.compile("preference\s*\d",flags=re.IGNORECASE), re.compile("priority\s*\d",flags=re.IGNORECASE), re.compile("choice\s*\d",flags=re.IGNORECASE)]
	if filename.endswith(('.csv', '.txt')):
		df = pd.read_csv(filename, sep='	', header=0, engine='c')
	elif filename.endswith(('.xls', '.xlsx')):
		df = pd.read_excel(filename)
	else:
		sys.exit("File type not recognised")

	delcols = ["Entry #", 'Date Created', 'Date Updated', 'IP Address', 'Name - Last', 'Name - First']
	for col in delcols:
		if col in df.columns:
			del df[col]

	for index, row in df.iterrows():
		prefs = []
		topicprefs = []
		studentID = row["Student Number"]
		#extract preference columns (whatever they be named)
		prefcols = []
		for col in df.columns:
			for regex in preferenceregex:
				if re.match(regex,col):
					prefcols.append(re.match(regex,col).group())
		priority_cols = natsorted(prefcols)
		projstrings = []
		for col in priority_cols:
			if pd.isna(row[col]):
				pass
			else:
				projstrings.append(row[col])
		if studentID in studPrefs:
			sys.exit("Duplicate student found - "+studentID+" - check input files")
		for projstr in projstrings:
			code = parseproject(projstr)["code"]
			prefs.append(code)
		topicstrings = [row["First -- Priority list"], row["Second -- Priority list"], row["Third -- Priority list"]]
		for topicstr in topicstrings:
			if "Inorganic" in topicstr:
				topicprefs.append("I")
			elif "Organic" in topicstr:
				topicprefs.append("O")
			elif "Physical" in topicstr:
				topicprefs.append("P")
			elif "Medicinal" in topicstr:
				topicprefs.append("M")
		if "Medicinal" in row["Degree Programme"]:
			medChemStudPrefs.update({studentID:prefs})
			medChemStudTopicPrefs.update({studentID:topicprefs})
			med_unassigned.append(studentID)
		else:
			studPrefs.update({studentID: prefs})
			studTopicPrefs.update({studentID: topicprefs})
			unassigned.append(studentID)

	return {"Non-Med Prefs": studPrefs, "Non-Med Topic Prefs": studTopicPrefs, "Med Prefs": medChemStudPrefs, "Med Topic Prefs": medChemStudTopicPrefs, "Unassigned": unassigned, "Med-Unassigned": med_unassigned}


def importProjs_Lects(filename):
	projCaps = {}
	projLects = {}
	lectProjs = {}
	lectPrefs = {}
	lecturercaps = {}
	projects = []
	lecturers = []
	preferenceregex = [re.compile("pref\s*\d",flags=re.IGNORECASE), re.compile("preference\s*\d",flags=re.IGNORECASE), re.compile("priority\s*\d",flags=re.IGNORECASE), re.compile("choice\s*\d",flags=re.IGNORECASE)]
	if filename.endswith(".csv"):
		sys.exit("File type .csv not supported. Please refer to documentation")
	elif filename.endswith(".txt"):
		sys.exit("File type .txt not supported. Please refer to documentation")
	elif filename.endswith((".xls", ".xlsx")):
		xls = xlrd.open_workbook(filename, on_demand=True)
		sheetnames = xls.sheet_names()
		projregex = re.compile("[pP]rojects\s*\(\d*\)")
		lectregex = re.compile("lecturers", flags=re.IGNORECASE)
		supregex = re.compile("supervisors", flags=re.IGNORECASE)
		if any(re.match("[pP]roject(s*)",sheet) for sheet in sheetnames) == False:
			sys.exit("A \"projects\" sheet was not found in Projects/Lecturers .xlsx file. Check input files.")
		else:
			for sheet in sheetnames:
				if re.match("[pP]roject(s*)",sheet) is not None:
					projsheet = re.match("[pP]roject(s*)", sheet).group()
			df = pd.read_excel(filename,sheet_name=projsheet)
	else:
		sys.exit("File type not recognised")
	for index, row in df.iterrows():
		# Firstly extract lecturer from project codes
		proj_id = row["Project Code"]
		proj_lecturer = re.match("[A-Z][A-Z]", row["Project Code"], 1).group()
		# Create list of lecturers based on project codes
		if proj_lecturer not in lecturers:
			lecturers.append(proj_lecturer)
		# Finally construct project dicts
		if 'Capacity' in df.columns:
			projCap = row["Capacity"]
		else:
			projCap = 1
		if proj_id in projects:
			sys.exit("Duplicate project code found - "+proj_id+" - check input files")

		projects.append(proj_id)

		if proj_lecturer not in lecturers:
			sys.exit("Error! Project " + proj_id + " does not have a valid supervisor")
		if proj_lecturer not in lectProjs:
			lectProjs.update({proj_lecturer: []})
			lectProjs[proj_lecturer].append(proj_id)
		else:
			lectProjs[proj_lecturer].append(proj_id)

		projLects.update({proj_id: proj_lecturer})
		projCaps.update({proj_id: projCap})

	lectsheet = ""
	if any(re.match("[lL]ecturer(s*)",sheet) for sheet in sheetnames) == False:
		if any(re.match("[sS]upervisor(s*)",sheet) for sheet in sheetnames) == False:
			sys.exit("A \"lecturers\" sheet was not found in Projects/Lecturers .xlsx file. Check input files.")
		else:
			for sheet in sheetnames:
				if re.match("[sS]upervisor(s*)",sheet) is not None:
					lectsheet = re.match("[sS]upervisor(s*)",sheet).group()
	else:
		for sheet in sheetnames:
			if re.match("[lL]ecturer(s*)",sheet) is not None:
				lectsheet = re.match("[lL]ecturer(s*)",sheet).group()

	df_lects = pd.read_excel(filename, sheet_name=lectsheet)

	lecturercaps = {}
	lectPrefs={}
	sumcaps = 0
	for index, row in df_lects.iterrows():
		if "Capacity" in df_lects.columns:
			if row["Capacity"] < len(lectProjs[row["Code"]]):
				lecturercaps.update({row["Code"]: row["Capacity"]})
			else:
				lecturercaps.update({row["Code"]: len(lectProjs[row["Code"]])})
		else:
			lecturercaps.update({row["Code"]: len(lectProjs[row["Code"]])})

		#Create lecturerprefs dictionary
		lectPrefs.update({row["Code"]: []})
		prefcols = []
		#Get columns relating to preferences
		for col in df_lects.columns:
			for regex in preferenceregex:
				if re.match(regex, col):
					prefcols.append(re.match(regex, col).group())
		# Sort columns into ascending order
		priority_cols = natsorted(prefcols)
		#Filter out NaN columns
		for col in priority_cols:
			if pd.isna(row[col]):
				pass
			else:
				#Append non-NaN colunns to lecturer's preference list
				lectPrefs[row["Code"]].append(row[col])
	if len(lecturers) != len(list(lecturercaps.keys())):
		sys.exit(
			"Mismatch between lecturers derived from codes and lecturers present in lecturer list. Check input files.")

	return {"Projects": projects, "Lecturers": lecturers, "Lecturer Capacities": lecturercaps, "Lecturer Preferences": lectPrefs, "Project Capacities": projCaps, "Lecturer's Projects": lectProjs, "Project Lecturers": projLects}


def export_all(filename,studAssignments,copyStudPrefs,projLects,lectAssignments,unassignedStudents,undercapacityLects, unassignedProjects,stats, randomlyAllocatedStudents):
	workbook = xlsxwriter.Workbook(filename)
	worksheet1 = workbook.add_worksheet('Student Assignments')
	worksheet2 = workbook.add_worksheet('Lecturer Assignments')
	worksheet3 = workbook.add_worksheet('Undercapacity & Unassigned')
	worksheet4 = workbook.add_worksheet('Statistics')
	# Write Student Assignments
	row = 0
	col = 0
	for x in ["Student", "Project", "Rank", "Lecturer"]:
		worksheet1.write(row, col, x)
		col +=1
	for key, value in studAssignments.items():
		row += 1
		col = 0
		ranking = library.firstidx(copyStudPrefs[key], value)+1
		worksheet1.write(row,col,key)
		worksheet1.write(row, col+1,value)
		worksheet1.write(row, col+2,ranking)
		worksheet1.write(row, col+3,projLects[value])
	# Write Lecturer Assignments
	row = 0
	col = 0
	worksheet2.write(row, col,"Lecturer")
	for key, value in lectAssignments.items():
		row += 1
		col = 0
		worksheet2.write(row, col, key)
		for project in value:
			col += 1
			worksheet2.write(row, col, project)
	# Write Under-Capacity Lecturers, Unassigned Students, and Unassigned Projects
	row = 0
	col = 0
	worksheet3.write(row,col,"Undercapacity Lecturers")
	row += 1
	worksheet3.write(row, col, "Lecturer")
	worksheet3.write(row, col+1, "Free Slots")
	for key, value in undercapacityLects.items():
		row += 1
		worksheet3.write(row, col, key)
		worksheet3.write(row, col+1, value)
	row += 2
	row += 1
	worksheet3.write(row, col, "Unassigned Students")
	for student in unassignedStudents:
		col += 1
		worksheet3.write(row, col+1, student)
	row += 2
	col =0
	worksheet3.write(row, col, "Randomly Assigned Students")
	for student in randomlyAllocatedStudents:
		col +=1
		worksheet3.write(row, col+1, student)
	row += 2
	col = 0
	worksheet3.write(row, col, "Unassigned Projects")
	row += 1
	worksheet3.write(row, col, "Project")
	worksheet3.write(row, col+1, "Free Spaces")
	for key, value in unassignedProjects.items():
		row += 1
		worksheet3.write(row, col, key)
		worksheet3.write(row, col+1, value)
	# Write simple stat information about allocation
	row = 0
	col = 0
	worksheet4.write(row, 0, "Rank")
	worksheet4.write(row, 1, "Count")
	worksheet4.write(row, 2, "%")
	worksheet4.write(row, 3, "Cum. %")
	row = 1
	for y in range(stats.shape[1]):
		for x in range(stats.shape[0]):
			worksheet4.write(row+x, col+y, stats[x][y])
	workbook.close()
