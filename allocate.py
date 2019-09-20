import library
import random
import re

def allocate(studPrefs,unassignedStudents,lecturerprefs,projLects,lectProjs,lecturercaps,projCaps,randomise,updates,iterationLimit):
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
		if randomise == 1:
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
	return {"Student Assignments":studAssignments, "Lecturer Assignments": lectAssignments, "Project Assignments": projAssignments, "Unassigned Students": unassignedStudents}



def random_distribute(unassignedStudents,studAssignments,projAssignments,projCaps,lectAssignments,lecturercaps, lectProjs, projLects, updates):
	freeprojects = []
	unassignedStudentsCopy = unassignedStudents
	freeprojects = library.findFreeProjects(projAssignments, projCaps, lectAssignments, lecturercaps, lectProjs)
	if updates == True:
		print("***Distributing remaining "+str(len(unassignedStudents))+" students***\n")
	if updates == True and len(unassignedStudents) <= len(freeprojects):
		print(str(
			len(freeprojects)) + " projects are available. All remaining students will be randomly allocated a project\n")
	elif updates == True and len(freeprojects) < len(unassignedStudents):
		diff = len(unassignedStudents) - len(freeprojects)
		print(
			str(len(freeprojects)) + " projects are available. " + str(diff) + " students will not be assigned to projects\n")

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
			if updates:
				print("Student "+student+" has been allocated to project "+thisproject+" with lecturer "+thislecturer)
			studAssignments.update({student:thisproject})
			freeprojects.pop(0)

	for student in studAssignments:
		if student in unassignedStudents:
			unassignedStudents.remove(student)

	return{"Student Assignments": studAssignments, "Lecturer Assignments":lectAssignments, "Project Assignments":projAssignments, "Unassigned Students": unassignedStudents}

def topic_distribute(unassignedStudents,studTopicPrefs,studAssignments,projAssignments,projCaps,lectAssignments,lecturercaps, projLects, lectProjs, updates):
	freeprojects = []
	unassignedStudentsCopy = unassignedStudents
	freeprojects = library.findFreeProjects(projAssignments, projCaps, lectAssignments, lecturercaps, lectProjs)
	if updates == True:
		print("***Distributing remaining " + str(len(unassignedStudents)) + " students***\n")
	elif updates == True and len(freeprojects) < len(unassignedStudents):
		diff = len(unassignedStudents) - len(freeprojects)
		print(
			str(len(
				freeprojects)) + " projects are available. " + diff + " students will not be assigned to projects\n")
	inorgfree = []
	orgfree = []
	medfree = []
	physfree = []
	for project in freeprojects:
		if re.match("I[A-Z][0-9][0-9]", project) is not None:
			inorgfree.append(project)
		if re.match("O[A-Z][0-9][0-9]", project) is not None:
			orgfree.append(project)
		if re.match("P[A-Z][0-9][0-9]", project) is not None:
			physfree.append(project)
		if re.match("M[A-Z][0-9][0-9]", project) is not None:
			medfree.append(project)
	for student in unassignedStudentsCopy:
		print("Assigning student "+student)
		if len(freeprojects) > 0:
			print("There are "+str(len(freeprojects))+" projects remaining")
			for topic in studTopicPrefs[student]:
				print("Currently looking for an "+topic+" project")
				if topic == "I" and len(inorgfree) > 0:
					print("Found I")
					thisproject = random.choice(inorgfree)
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
					studAssignments.update({student: thisproject})
					freeprojects.remove(thisproject)
					inorgfree.remove(thisproject)
					#unassignedStudents.remove(student)
					if updates:
						print("Allocated "+student+" to project "+thisproject+" with lecturer "+ thislecturer+"\n")
					break
				if topic == "O" and len(orgfree) > 0:
					print("Found O")
					thisproject = random.choice(orgfree)
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

					studAssignments.update({student: thisproject})
					freeprojects.remove(thisproject)
					orgfree.remove(thisproject)
					#unassignedStudents.remove(student)
					if updates:
						print(
							"Allocated " + student + " to project " + thisproject + " with lecturer " + thislecturer + "\n")
					break
				if topic == "P" and len(physfree) > 0:
					print("Found P")
					thisproject = random.choice(physfree)
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

					studAssignments.update({student: thisproject})
					freeprojects.remove(thisproject)
					physfree.remove(thisproject)
					#unassignedStudents.remove(student)
					if updates:
						print(
							"Allocated " + student + " to project " + thisproject + " with lecturer " + thislecturer + "\n")
					break
				if topic == "M" and len(medfree) > 0:
					print("Found M")
					thisproject = random.choice(medfree)
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

					studAssignments.update({student: thisproject})
					freeprojects.remove(thisproject)
					medfree.remove(thisproject)
					#unassignedStudents.remove(student)
					if updates:
						print(
							"Allocated " + student + " to project " + thisproject + " with lecturer " + thislecturer + "\n")
					break
	for student in studAssignments:
		if student in unassignedStudents:
			unassignedStudents.remove(student)
	#random.shuffle(unassignedStudentsCopy)

	return{"Student Assignments": studAssignments, "Lecturer Assignments":lectAssignments, "Project Assignments":projAssignments, "Unassigned Students": unassignedStudents}