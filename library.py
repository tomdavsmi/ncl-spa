import pandas as pd
import numpy as np
import re
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


def check_prefs(studPrefs):
    for key, value in studPrefs.items():
        if len(value) != len(list(dict.fromkeys(value))):
            value = list(dict.fromkeys(value))


def statgen(studPrefs,studAssignments, studTopicPrefs):
    rankings = []
    for key, value in studAssignments.items():
        ranking = firstidx(studPrefs[key], value) + 1
        if ranking == 0:
            ranking = firstidx(studTopicPrefs[key],value[0])+8
            if ranking == -1:
                ranking = 11
        rankings.append(ranking)
    col1 = []
    col2 = []
    for x in range(1, 12):
        col1.append(rankings.count(x))
        col2.append(round((rankings.count(x)/len(studAssignments.keys()))*100,2))
    df = pd.DataFrame({"Ranks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], "Count": col1, "%": col2})
    df['Cum %'] = df['%'].cumsum()
    array = df.to_numpy()
    np.delete(array, 0, 1)

    return(array)

def atof(text):
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    float regex comes from https://stackoverflow.com/a/12643073/190597
    '''
    return [ atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)', text) ]