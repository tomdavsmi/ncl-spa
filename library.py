def findWorst(justAdded, ref_prefList, ref_studentList):
    idx = 0
    maxIdx = -1
    worst = ""
    studentList = ref_studentList
    prefList    = ref_prefList

    prefLength = len(prefList)

    # return($justAdded) if(
    #   (firstidx { $_ eq $justAdded } @prefList) == -1
    # );
    # Find worst student in project
    for value in studentList:
        try:
            idx = prefList.index(value)
            if idx > maxIdx:
                maxIdx = idx
                worst = value
        except:
            maxIdx = idx
            worst = value

    return worst

def firstidx(list,element):
    try:
        idx = list.index(element)
    except:
        idx = -1
    return idx

def findFreeProjects(projAssignments, projCaps, lectAssignments, lectCaps, lectProjs):
    """

    :rtype: list
    """
    freeProjs = []
    for lecturer in lectCaps.keys():
        if lecturer not in lectAssignments:
            lectAssignments.update({lecturer: []})
        if len(lectAssignments[lecturer]) < int(lectCaps[lecturer]):
            for project in lectProjs[lecturer]:
                if project not in projAssignments:
                    projAssignments.update({project: []})
                if len(projAssignments[project]) < int(projCaps[project]):
                    freeProjs.append(project)

    return freeProjs