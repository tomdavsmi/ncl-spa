# Implementation of Student Allocation Algorithm into a wider Python-based solution
# Thomas David Smith, 17th Sept. 2019

# Implementation of algorithm of:
# Abraham, D.J., Irving, R.W. and Manlove, D.M. (2007)
# Two algorithms for the student-project allocation problem.
# Journal of Discrete Algorithms, 5  (1).   pp. 73-90.
# http://dx.doi.org/10.1016/j.jda.2006.03.006


# Please see documentation for more information about input & output
# formats, as well as constraints and possible usage scenarios

# Ported from a Perl algorithm by Richard D. Morey to Python
import input_output as inout
import sys
import allocate
import copy
import random
import library
############################################################
#                    CONFIGURATION                         #
############################################################
# Here you can fine-tune the run with different settings

# File names for the file containing student preference data, and for the master list of projects
students_filename = "Data/SPA_Testv2.xlsx"
project_filename = "Data/CHY3011 lists of projects 19-20.xlsx"

# File names for the output excel sheet
out_filename = "out.xlsx"

# Logging setting: to file or to terminal?
updates = True
logging = "terminal"

# Shuffle order of unassigned student list?
randomise = True
topicallocate = True
randomallocate = True

# Iteration limit (usually not important but can be useful for debugging) set as -1 for no limit
iterationLimit = -1

############################################################
#                 END OF CONFIGURATION                     #
############################################################

students = inout.importStudents(students_filename)
proj_lects = inout.importProjs_Lects(project_filename)

# Student Oriented Data
med_studPrefs = students["Med Prefs"]
medinit_unassignedStudents = students["Med-Unassigned"]
nonmed_studPrefs = students["Non-Med Prefs"]
nonmedinit_unassignedStudents = students["Unassigned"]

library.check_prefs(med_studPrefs)
library.check_prefs(nonmed_studPrefs)

copy_med_studPrefs = copy.deepcopy(med_studPrefs)
copy_nonmed_studPrefs = copy.deepcopy(nonmed_studPrefs)
copy_studPrefs ={**copy_med_studPrefs, **copy_nonmed_studPrefs}

# Project Oriented Data
projCaps = proj_lects["Project Capacities"]
projLects = proj_lects["Project Lecturers"]
projects = proj_lects["Projects"]

# Lecturer Oriented Data
lecturers = proj_lects["Lecturers"]
lectPrefs = proj_lects["Lecturer Preferences"]
lectPrefs_copy = copy.deepcopy(lectPrefs)
lecturercaps = proj_lects["Lecturer Capacities"]
lectProjs = proj_lects["Lecturer's Projects"]

#Now we have all the data extracted from the input files it is time to validate it
for k, v in med_studPrefs.items():
	for project in v:
		if project not in projects:
			sys.exit("Error! Student " +project+ " has selected a project "+project+" which does not exist")

for k, v in nonmed_studPrefs.items():
	for project in v:
		if project not in projects:
			sys.exit("Error! Student " +project+ " has selected a project "+project+" which does not exist")

#Make sure each project has a positive, non-zero capacity
for k, v in projCaps.items():
	if 0 >= int(v):
		sys.exit("Error! Project " +k+" has zero or negative capacity")

#Make sure each lecturer has a positive, non-zero capacity
for k, v in lecturercaps.items():
	if 0 >= int(v):
		sys.exit("Error! Project " +k+" has zero or negative capacity")

#Make sure there is enough capacity between all the lecturers to accomodate all the students
print(lecturercaps)
exit(69)
sumcaps = 0
for key, value in lecturercaps.items():
	sumcaps += value

if int(sumcaps) < (len(medinit_unassignedStudents) + len(nonmedinit_unassignedStudents)):
	sys.exit("Not enough capacity between all lecturers: only "+str(sumcaps)+" lecturer slots available for "+str((len(medinit_unassignedStudents) + len(nonmedinit_unassignedStudents)))+" students. Check input files.")
# Run the main allocation function
# MedChem
if randomise:
	random.shuffle(medinit_unassignedStudents)
medallocation = allocate.allocate(med_studPrefs, medinit_unassignedStudents, lectPrefs, projLects, lectProjs, lecturercaps, projCaps, randomise, updates, iterationLimit)
med_studAssignments = medallocation["Student Assignments"]
med_lectAssignments = medallocation["Lecturer Assignments"]
med_projAssignments = medallocation["Project Assignments"]
med_unassignedStudents = medallocation["Unassigned Students"]

# Remove any assigned medicinal topics from the preference lists of any non-med chem student
for key, value in nonmed_studPrefs.items():
	for project in value:
		if project in med_studAssignments:
			value.remove(project)

if randomise:
	random.shuffle(nonmedinit_unassignedStudents)
# Non Med-Chem
nonmedallocation = allocate.allocate(nonmed_studPrefs, nonmedinit_unassignedStudents, lectPrefs_copy, projLects, lectProjs, lecturercaps, projCaps, randomise, updates, iterationLimit)
# Unpack output dictionaries
nonmed_studAssignments = nonmedallocation["Student Assignments"]
nonmed_lectAssignments = nonmedallocation["Lecturer Assignments"]
nonmed_projAssignments = nonmedallocation["Project Assignments"]
nonmed_unassignedStudents = nonmedallocation["Unassigned Students"]

# Combine the two outpt dicts since we're now going to treat everything the same
unassignedStudents = nonmed_unassignedStudents + med_unassignedStudents
studAssignments = {**med_studAssignments, **nonmed_studAssignments}
lectAssignments = {**med_lectAssignments, **nonmed_lectAssignments}
projAssignments = {**med_projAssignments, **nonmed_projAssignments}


# Build Topic Preference dictionaries for unassigned Students
med_TopicPrefs = students["Med Topic Prefs"]
nonmed_TopicPrefs = students["Non-Med Topic Prefs"]
comb_TopicPrefs = {**med_TopicPrefs, **nonmed_TopicPrefs}
studTopicPrefs = {}
for student in unassignedStudents:
	studTopicPrefs.update({student:comb_TopicPrefs[student]})

# Run the random allocation function
finaldist_topic = {}
if len(unassignedStudents) > 0 and topicallocate:
	if randomise:
		random.shuffle(unassignedStudents)
	finaldist_topic = allocate.topic_distribute(unassignedStudents,studTopicPrefs,studAssignments,projAssignments,projCaps,lectAssignments,lecturercaps,projLects,lectProjs,updates)
	unassignedStudents = finaldist_topic["Unassigned Students"]
	studAssignments = finaldist_topic["Student Assignments"]
	lectAssignments = finaldist_topic["Lecturer Assignments"]
	projAssignments = finaldist_topic["Project Assignments"]

randomlyAllocatedStudents = []
if len(unassignedStudents) > 0 and randomallocate:
	if randomise:
		random.shuffle(unassignedStudents)
	randomlyAllocatedStudents = copy.deepcopy(unassignedStudents)
	rand_dist = allocate.random_distribute(unassignedStudents,studAssignments,projAssignments,projCaps,lectAssignments,lecturercaps,lectProjs, projLects, updates)
	unassignedStudents = rand_dist["Unassigned Students"]
	studAssignments = rand_dist["Student Assignments"]
	lectAssignments = rand_dist["Lecturer Assignments"]
	projAssignments = rand_dist["Project Assignments"]


unassignedProjects = library.findFreeProjects(projAssignments,projCaps,lectAssignments,lecturercaps,lectProjs)
unassignedProjects_Caps = {}
for project in unassignedProjects:
	unassignedProjects_Caps.update({project:projCaps[project]})

undercapacityLects = {}
for key, value in lecturercaps.items():
	if key in lectAssignments.keys():
		if len(lectAssignments[key]) < int(value):
			diff = int(value) - len(lectAssignments[key])
			undercapacityLects.update({key:diff})
	else:
		undercapacityLects.update({key: value})

for key in list(lectAssignments.keys()):
	if lectAssignments[key] == []:
		del lectAssignments[key]

stats = library.statgen(copy_studPrefs, studAssignments, comb_TopicPrefs)
# Finally export all the values into a single output spreadsheet
inout.export_all(out_filename,studAssignments,copy_studPrefs,projLects,lectAssignments,unassignedStudents,undercapacityLects,unassignedProjects_Caps,stats, randomlyAllocatedStudents)

if len(unassignedStudents) == 0:
	print("All students have been allocated a project, the program will now terminate.\n May the force be with you.")
else:
	print("Program has finished but has been unable to allocate "+str(len(unassignedStudents))+" students to projects")
