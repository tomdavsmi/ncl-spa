# Student allocation algorithm
# Richard D. Morey, 18 March 2013

# Implementation of algorithm of:
# Abraham, D.J., Irving, R.W. and Manlove, D.M. (2007)
# Two algorithms for the student-project allocation problem.
# Journal of Discrete Algorithms, 5  (1).   pp. 73-90.
# http://dx.doi.org/10.1016/j.jda.2006.03.006

# Ported from Perl to Python by Thomas D. Smith (Newcastle
# University).

##

#
############################################################
#                    CONFIGURATION                         #
############################################################
import sys
import random
import library
import csv
import allocation_class as allocation
from datetime import datetime
# print updates?
updates = True

# Randomly distribute unassigned at the end?
distributeUnassigned = True

# Define file names for input
studentsFN = "students.txt"
lecturersFN = "lecturers.txt"
projectsFN = "projects.txt"

# Define file name for output. These files will be overwritten!
outStudentsFN = "studentAssignments.txt"
outProjectsFN = "projectAssignments.txt"
outLecturersFN = "lecturerAssignments.txt"

# Change random seed for shuffling of students and projects
randomize = 1  # If 0, no randomization

# Limit the number of iterations performed? -1 for no limit
iterationLimit = -1

############################## END CONFIGURATION ##########################
# Do not edit anything below this line unless you know what you are doing #
###########################################################################

# Use the imported files to form the input dictionaries
# TODO: Change this entire section so it pulls from a single excel sheet, probably via a pandas dataframe or just raw xlrd
studPrefs = {}
CopyStudPrefs = {}
studentID = ""
unassignedStudents = []
with open (studentsFN) as file:
	for line in file:
		line = line.strip("\n")
		linearray = line.split(" ",)
		if linearray[0] in studentID:
			sys.exit("Error: duplicate student found! Check input files!")
		studentID = linearray[0]
		del linearray[0]
		prefs = list(dict.fromkeys(linearray))
		studPrefs.update({studentID: prefs})
		CopyStudPrefs.update({studentID: tuple(prefs)})
		unassignedStudents.append(studentID)

lecturerprefs = {}
lecturercaps = {}
lecturerID = ""
lecturers = []
with open (lecturersFN) as file:
	for line in file:
		line = line.strip("\n")
		linearray = line.split(" ",)
		if linearray[0] in lecturers:
			sys.exit("Error: duplicate lecturer found! Check input files!")
		lecturers.append(linearray[0])
		lecturerID = linearray[0]
		del linearray[0]
		lecturercapacity = linearray[0]
		del linearray[0]
		prefs = linearray
		if lecturerID not in lecturerprefs:
			lecturerprefs.update({lecturerID:[]})
			for x in prefs:
				lecturerprefs[lecturerID].append(x)
		else:
			lecturerprefs[lecturerID].append(prefs)
			for x in prefs:
				lecturerprefs[lecturerID].append(x)
		lecturercaps.update({lecturerID:lecturercapacity})

projects = []
lectProjs = {}
projLects = {}
projCaps = {}
with open (projectsFN) as file:
	for line in file:
		line = line.strip("\n")
		linearray = line.split(" ",)
		projID = linearray[0]
		projCap = linearray[1]
		projLecturer = linearray[2]
		if linearray[0] in projects:
			sys.exit("Error: duplicate project found! Check input files!")
		projects.append(projID)
		if projLecturer not in lecturers:
			sys.exit("Error! Project " + projID + " does not have a valid supervisor")
		if projLecturer not in lectProjs:
			lectProjs.update({projLecturer:[]})
			lectProjs[projLecturer].append(projID)
		else:
			lectProjs[projLecturer].append(projID)
		projLects.update({projID:projLecturer})
		projCaps.update({projID:projCap})

#Start input validation

#Make sure projects students have selected actually exist in the list of possible projects
for k, v in studPrefs.items():
	for x in v:
		if x not in projects:
			sys.exit("Error! Student " +k+ " has selected a project not in list")

#Make sure each project has a positive, non-zero capacity
for k, v in projCaps.items():
	if 0 >= int(v):
		sys.exit("Error! Project " +k+" has zero or negative capacity")

#Make sure each lecturer has a positive, non-zero capacity
for k, v in lecturercaps.items():
	if 0 >= int(v):
		sys.exit("Error! Project " +k+" has zero or negative capacity")


# Create projected preference list - first pass; add students not on lecturer's list

for k, v in studPrefs.items():
	for project in v:
		idx = library.firstidx(lecturerprefs[projLects[project]],k)
		if idx == -1:
			lecturerprefs[projLects[project]].append(k)


projectedPrefs = {}
# Create projected preference list - second pass; add students to projected list
for k, v in projLects.items():
	for student in lecturerprefs[v]:
		if library.firstidx(studPrefs[student], k) > -1:
			if k not in projectedPrefs:
				projectedPrefs.update({k: []})
				projectedPrefs[k].append(student)
			else:
				projectedPrefs[k].append(student)



maxidx = 0
done = 0
iters = 0
projAssignments = dict()
lectAssignments = dict()
studAssignments = dict()
nProj = 0
currentStudent = ""

while done != 1:
	iters += 1
	if randomize == 1:
		random.shuffle(unassignedStudents)

	if iters > iterationLimit & iterationLimit != -1:
		print("Maximum number of iterations "+str(iterationLimit)+" before convergence")
		done = 1

	if len(unassignedStudents) > 0:
		for value in unassignedStudents:
			currentStudent = value
			nProj = len(studPrefs[currentStudent])
			if nProj > 0:
				break
		if nProj > 0:  ### We have a student who still has projects in their list - heart of the alogrithm
			currentProject = studPrefs[currentStudent][0]
			currentLecturer = projLects[currentProject]
			if currentProject not in projAssignments:
				projAssignments.update({currentProject:[]})
				projAssignments[currentProject].append(currentStudent)
			else:
				projAssignments[currentProject].append(currentStudent)

			if currentLecturer not in lectAssignments:
				lectAssignments.update({currentLecturer:[]})
				lectAssignments[currentLecturer].append(currentStudent)
			else:
				lectAssignments[currentLecturer].append(currentStudent)

			studAssignments.update({currentStudent:currentProject})
			idx = library.firstidx(unassignedStudents,currentStudent)
			unassignedStudents.pop(idx)
			if updates == True:
				print(str(iters)+" : Assigned "+currentStudent+" to project "+currentProject+" with supervisor "+currentLecturer+"\n")

			#Is the project the student was just assigned to overloaded?
			if len(projAssignments[currentProject]) > int(projCaps[currentProject]):
				maxidx = -1
				for value in projAssignments[currentProject]:
					idx = library.firstidx(projectedPrefs[currentProject], value)
					if idx == -1:
						maxidx = idx
						worst = value
						break
					if idx > maxidx:
						maxidx = idx
						worst = value

				if updates == True:
					print("Project " + currentProject + " is overloaded. Removing " + worst + ".\n")
				idx = library.firstidx(lectAssignments[currentLecturer],worst)
				lectAssignments[currentLecturer].pop(idx)
				idx = library.firstidx(projAssignments[currentProject],worst)
				projAssignments[currentProject].pop(idx)
				if worst not in unassignedStudents:
					unassignedStudents.append(worst)

				if worst in studAssignments:
					studAssignments.pop(worst)

			#Is the lecturer of the project the student was just assigned to overloaded?
			if len(lectAssignments[currentLecturer]) > int(lecturercaps[currentLecturer]):
				maxidx = -1
				for value in lectAssignments[currentLecturer]:
					idx = library.firstidx(lecturerprefs[currentLecturer],value)
					if idx == -1:
						maxidx = idx
						worst = value
						break
					if idx > maxidx:
						maxidx = idx
						worst = value

				if updates == True:
					print("Lecturer " + currentLecturer + " is overloaded. Removing " + worst + ".\n")
				idx = library.firstidx(lectAssignments[currentLecturer], worst)
				lectAssignments[currentLecturer].pop(idx)
				if worst in studAssignments:
					idx = library.firstidx(projAssignments[studAssignments[worst]], worst)
					projAssignments[studAssignments[worst]].pop(idx)

				if worst not in unassignedStudents:
					unassignedStudents.append(worst)

				if worst in studAssignments:
					studAssignments.pop(worst)

			#Is the project full?
			if len(projAssignments[currentProject]) == int(projCaps[currentProject]):
				maxidx = -1
				for value in projAssignments[currentProject]:
					idx = library.firstidx(projectedPrefs[currentProject], value)
					if idx == -1:
						maxidx = idx
						worst = value
						break
					if idx > maxidx:
						maxidx = idx
						worst = value

				if updates == True:
					print("Project "+currentProject+" is full: removing successors to "+worst)
				idx = library.firstidx(projectedPrefs[currentProject],worst)
				a = []
				if idx == -1 or idx == len(projectedPrefs[currentProject])-1:
					pass
				else:
					for i in range(idx+1,len(projectedPrefs[currentProject])):
						a.append(projectedPrefs[currentProject][i])
				for i in a:
					while True:
						idx = library.firstidx(studPrefs[i],currentProject)
						if idx > -1:
							studPrefs[i].pop(idx)
						if idx == -1:
							break

			#Is the lecturer full?
			if len(lectAssignments[currentLecturer]) == int(lecturercaps[currentLecturer]):
				maxidx = -1
				for value in lectAssignments[currentLecturer]:
					idx = library.firstidx(lecturerprefs[currentLecturer], value)
					if idx == -1:
						maxidx = idx
						worst = value
						break
					if idx > maxidx:
						maxidx = idx
						worst = value

				if updates == True:
					print("Lecturer "+currentLecturer+" is full: removing successors to "+worst+"\n")
				idx = library.firstidx(lecturerprefs[currentLecturer],worst)
				a = []
				if idx == -1 or idx == len(lecturerprefs[currentLecturer])-1:
					pass
				else:
					for i in range(idx+1,len(lecturerprefs[currentLecturer])):
						a.append(lecturerprefs[currentLecturer][i])
				for i in a:
					for project in lectProjs[currentLecturer]:
						while True:
							idx = library.firstidx(projectedPrefs[project], i)
							if idx > -1:
								projectedPrefs[project].pop(idx)
							if idx == -1:
								break
						while True:
							idx = library.firstidx(studPrefs[i],project)
							if idx > -1:
								studPrefs[i].pop(idx)
							if idx == -1:
								break
			if updates == True:
				print(str(iters)+": Remaining students:" + str(unassignedStudents)+"\n-------------\n")
		else:
			done= 1
	else:
		done= 1

freeprojects = []
unassignedStudentsCopy = unassignedStudents
if distributeUnassigned == True:
	# if randomize == 1:
	# 	random.shuffle(unassignedStudentsCopy)
	freeprojects = library.findFreeProjects(projAssignments, projCaps, lectAssignments, lecturercaps, lectProjs)
	if updates == True:
		print("***Distributing remaining "+str(len(unassignedStudents))+" students***\n")
	if updates == True and len(unassignedStudents) <= len(freeprojects):
		print(str(
			len(freeprojects)) + " projects are available. All remaining students will be randomly allocated a project\n")
	elif updates == True and len(freeprojects) < len(unassignedStudents):
		diff = len(unassignedStudents) - len(freeprojects)
		print(
			str(len(freeprojects)) + " projects are available. " + diff + " students will not be assigned to projects\n")

	for student in unassignedStudentsCopy:
		if len(freeprojects) > 0:
			thisproject = random.choice(freeprojects)
			thislecturer = projLects[thisproject]
			if thisproject not in projAssignments:
				projAssignments.update({thisproject: []})
				projAssignments[thisproject].append(student)
			else:
				projAssignments[thisproject].append(student)

			if thislecturer not in lectAssignments:
				lectAssignments.update({thislecturer: []})
				lectAssignments[thislecturer].append(student)
			else:
				lectAssignments[thislecturer].append(student)

			studAssignments.update({student:thisproject})
			freeprojects.pop(0)
			print(student+"\t")
		#unassignedStudents.remove(student)
		else:
			break

	for student in studAssignments:
		if student in unassignedStudents:
			unassignedStudents.remove(student)

# FIXME: Code assigns every student, but why is the work-around required?
# TODO: Change this functionality slightly so students are assigned to a random project within a preference-ranked topic area

if len(freeprojects) > 0 and updates == True:
	print("There are "+str(len(freeprojects))+" projects remaining\n")
elif updates == True and len(freeprojects) == 0:
	print("All available topics have been assigned")
#calculate some stats on the quality of the assignment
ranks = []
for key, value in studAssignments.items():
	ranks.append(library.firstidx(CopyStudPrefs[key],value)+1)
averank = sum(ranks)/len(ranks)
percent_rank1 = (ranks.count(1)/len(ranks))*100
percent_rank2 = (ranks.count(2)/len(ranks))*100
percent_rank3 = (ranks.count(3)/len(ranks))*100
percent_rank4 = (ranks.count(4)/len(ranks))*100
percent_rank5 = (ranks.count(5)/len(ranks))*100
percent_rank0 = (ranks.count(0)/len(ranks))*100
#Print student assignments to file
with open (outStudentsFN, "w") as file:
	file.write("UNASSIGNED STUDENTS: \t"+str(unassignedStudents)+"\n")
	for key, value in studAssignments.items():
		ranking = library.firstidx(CopyStudPrefs[key],value)
		file.write(key+"\t"+value+"\t"+str(ranking+1)+"\n")
	file.write("\nAverage ranking: "+str(averank)+"\n")
	file.write("Percent with highest ranked choice: "+str(percent_rank1)+"%\n")
	file.write("Percent with 2nd ranked choice: " + str(percent_rank2) + "%\n")
	file.write("Percent with 3rd ranked choice: " + str(percent_rank3) + "%\n")
	file.write("Percent with 4th ranked choice: " + str(percent_rank4) + "%\n")
	file.write("Percent with 5th ranked choice: " + str(percent_rank5) + "%\n")
	file.write("Percent with an unranked project: " + str(percent_rank0) + "%\n")
	file.write("Percent unable to be allocated: "+str((len(unassignedStudents)/len(ranks))*100)+"%\n")

#Print project assignments to file
with open (outProjectsFN, "w") as file:
	file.write("UNASSIGNED PROJECTS:\t"+str(freeprojects)+"\n")
	for key, value in projAssignments.items():
		file.write(key+"\t"+str(value)+"\n")

#Generate list of under-capacity lecturers
undercapacitylects = {}
for key,value in lectAssignments.items():
	if len(value) < int(lecturercaps[key]):
		diff = int(lecturercaps[key]) - len(value)
		undercapacitylects.update({key:diff})

#Print lecturer assignments to file
with open (outLecturersFN, "w") as file:
	file.write("UNDER-CAPACITY:\n")
	for key,value in undercapacitylects.items():
		file.write(key+"\t"+str(value)+"\n")
	file.write("LECTURER ASSIGNMENTS:\n")
	for key, value in lectAssignments.items():
		file.write(key+"\t"+str(value)+"\n")


print("Program finished. "+str(len(unassignedStudents))+" students remain unassigned")

