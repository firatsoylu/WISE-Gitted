#!/usr/bin/python

import json, sys, getopt, csv, os
from operator import itemgetter
from datetime import datetime

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print '-i <inputfile> '
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            outputfile = inputfile.replace(".csv", "Out.csv")
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    testtype = 'NA'
    print inputfile
    if inputfile.lower().find('pre') != -1: #fileinfo keeps track of pre/post and the unit info
        testtype = 'pre'
    elif inputfile.lower().find('post') != -1:
        testtype = 'post'
    else:
        testtype.append('notfound')

    csv.field_size_limit(sys.maxsize)
    datafile = open(inputfile, "rU")   # open SQL csv file
    inData = csv.DictReader(datafile)
    full_data_set = [row for row in inData]        # read data by row into big list
    posDict, sortedList = setPosDict(findNodes(full_data_set)) # find out what nodes exist and how many questions are in each
    global outputTable
    outputTable = []
    outputTable = createHeader(outputTable, sortedList) #create headers for output table
    totalNodes = max(posDict.values()) + sortedList[-1][1][1] #find total number of questions
    for row in full_data_set:
        #Ignoring these question types!
        if row['nodetype'] != 'SVGDrawNode' and row['nodetype'] != 'MatchSequenceNode' and row['nodetype'] != 'TableNode':
            rowData = json.loads(row['data'])
            #check for existing row, if False, then no dups, if it is a dup, record the location in the table
            match, count = isDups(row['id'], row['workgroupid'], outputTable)
            if match == False:
                rowTable = []
                rowTable.append(row['id']) #tack on runid and user id to the row first
                rowTable.append(row['workgroupid'])
                rowTable.append(row['username'])
                rowTable.append(row['sgender'])
                rowTable.append(row['parentprojectid'])
                for i in range(totalNodes): #fill all of the question columns with zeros
                    rowTable.append(0)
                position, scoreTable = parseNode(row, rowData, posDict) #get the data and the position in the table the data should be placed
                n = 0
                for i in scoreTable: #replace the null values in the correct spot in the table with the data
                    rowTable[position + n] = i
                    n = n + 1
                outputTable.append(rowTable) # put the row into the output table
            else:
                position, scoreTable = parseNode(row, rowData, posDict) #get the data and the position in the table the data should be placed
                n = 0
                for i in scoreTable: #replace the null values in the correct spot in the table with the data
                    outputTable[count][position + n] = i
                    n = n + 1

    #print outputTable   
    #restructure_table (outputTable, outputfile, testtype)
    writefile(outputfile, outputTable)
    
def restructure_table (outputTable, outputfile, testtype):
    print outputTable
    table_length = len(outputTable)
    table_width = len(outputTable[1])
    nodes_list = outputTable[0][3:table_width]
    node_types_list = []
    
    for n in range(len(nodes_list)):
        if nodes_list[n].find('mc') != -1:
            node_types_list.append('mc')
        else:
            node_types_list.append('or')

    no_of_responses = len(nodes_list)
    new_o = []

    for i in range(1,table_length):
        runID = outputTable[i][0]       #runID
        userID = outputTable[i][1]      #userID
        username = outputTable[i][2]    #username
        sgender = outputTable[i][3]
        parentprojectid = outputTable[i][4]

        responses = outputTable[i][5:table_width]


        for k in range(no_of_responses):
            new_line = [runID, userID, username, nodes_list[k], node_types_list[k], responses[k], testtype]
            new_o.append(new_line)

    new_o.insert(0,['runID','userID','username','node', 'type', 'response','prepost','gender','parentprojectid'])          
    writefile(outputfile, new_o)

def writefile(outFile, outputTable):
    out = open(outFile, 'w')
    outfileWriter = csv.writer(out)
    for row in outputTable:
        outfileWriter.writerow([unicode(s).encode("utf-8") for s in row])
    print 'SUCCESS!! file written to ' + outFile

def createHeader(table, sortedList):
    table.extend(['runid','userID', 'username','gender','parentprojectid'])
    for i in sortedList:
        if i[1][1] == 1:
            if i[0][-1] == 'l':  #only one response but 'al' question type
                table.append(i[0] + '!')
            else:
                table.append(i[0])
        else:
            for n in range(i[1][1]):
                table.append(i[0] + '-' + str(n) + '!')
    return [table]

def isDups(runId, userID, output):
    count = 0
    match = False
    for entry in output:
        # look for entry that has the same run id and userid, if you find a match, return true
        if entry[0] == runId and entry[1] == userID:
            match = True
            break
        else:
            match = False
        count = count + 1
    if match == True:
        return True, count
    else:
        return False, count

def findDup(runId, userID, output):
    count = 0
    for entry in output:
        if entry[0] == runId and entry[1] == userID:
            return count
        count = count + 1

def findNodes(data):
    nodeDict = {}
    for row in data:
        # get rid of question types we won't be analyzing here
        if row['nodetype'] != 'SVGDrawNode' and row['nodetype'] != 'MatchSequenceNode' and row['nodetype'] != 'TableNode':
            match = False
            #since we just want to get an idea about number of questions, we need a dict of all the possible nodes
            for node in nodeDict.keys():
                # if these match, we already have this node in our dictionary, set the flag and break
                if node == row['nodeid']:
                    match = True
                    break
            # if we didn't find a match, add that unique node to the node Dict
            if match == False:
                nodeDict[row['nodeid']] = json.loads(row['data'])
    return nodeDict

def setPosDict(nodeDict):
    count = 0
    tempDict = {}
    for i in nodeDict:
        #get the node number (for sorting)
        nodeNum = int(i[5:-3])
        if i[-2:] == 'al':
            #if this is an assessment list item find out how many questions there are
            count = len(nodeDict[i]['nodeStates'][0]['assessments'])
        else:
            #otherwise just count the items in nodestate (should be 1)
            count = 1 #len(nodeDict[i]['nodeStates'])
        #create a dict of these values
        tempDict[i] = [nodeNum, count]
    #sort that dictionary into a list
    sortedList = sorted(tempDict.items(), key=lambda (k, (v1, v2)): v1)
    posDict = {}
    n = 0
    #create a dict that has the nodeID as the key and the position number as the value
    for i in sortedList:
        posDict[i[0]] = n
        n = n + i[1][1]
    return posDict, sortedList

def parseNode(row, rowData, posDict):
    for node in posDict:
        if row['nodeid'] == node:
            position = posDict[node] + 3
            if node[-2:] == 'al':
                scoreList = checkScoreALOR(rowData, position)
            elif node[-2:] == 'mc':
                scoreList = checkScoreMC(rowData, position)
            elif node[-2:] == 'or':
                scoreList = checkScoreOR(rowData, position)
            elif node[-2:] == 'hn':
                scoreList = checkScoreHN(rowData, position)
            elif node[-2:] == 'bs':
                scoreList = checkScoreBS(rowData, position)
    return position, scoreList

def checkScoreALOR(rowData, position):
    node = []
    n=0
    if 'assessments' in rowData['nodeStates'][0]:
        for item in rowData['nodeStates'][0]['assessments']:
            if item['response'] != None:
                if 'autoScoreResult' in item['response']:  #multiple choice
                    qStr='mc' #set question type string
                    if 'choiceScore' in item['response']['autoScoreResult']:
                        if item['response']['autoScoreResult']['choiceScore'] == 1:
                            node.append(1)
                        else:
                            node.append(0)
                    elif 'isCorrect' in item['response']['autoScoreResult']:
                        if item['response']['autoScoreResult']['isCorrect'] == True:
                            node.append(1)
                        else:
                            node.append(0)
                    else:
                        node.append(0)
                else: #open response
                    qStr='or' #set question type string
                    node.append(item['response']['text'])
                modifyHeader(qStr, position+n) #modify header to include question type string
            else:
                node.append(0)
            n = n + 1
    else:
        qStr='or'
        modifyHeader(qStr, position+n) #modify header to include question type string
        checkScoreOR(rowData, position)
    return node

def modifyHeader(qStr, pos):
    curStr = outputTable[0][pos]
    if curStr[-1] == '!':
        outputTable[0][pos] = curStr[:-1] + '-' + qStr

def checkScoreOR(rowData, position):
    node = []
    numList = []
    for i in rowData['nodeStates']:
        numList.append(i['timestamp'])
    for a in rowData['nodeStates']:
        if a['timestamp'] == max(numList):
            node.append(a['response'][0])
    return node

def checkScoreBS(rowData, position):
    node = []
    numList = []
    #could have more than one response, so take the latest response
    for item in rowData['nodeStates']:
        if item['response'] != None:
            numList.append(item['timestamp'])
    for a in rowData['nodeStates']:
        if a['timestamp'] == max(numList):
            node.append(item['response'])
    if len(node) == 0:
        node.append(0)
    return node

def checkScoreHN(rowData, position):
    node = []
    temp = []
    for item in rowData['nodeStates']:
        if item['response'] != None and item['response'] != '':
            temp.append(item['response'])
        else:
            temp.append(0)
    #could have more than one response, but since this is due to minor edits, just take the last one
    if len(temp) > 1:
        node.append(temp[-1])
    else:
        node = temp
    return node

def checkScoreMC(rowData, position):
    node = []
    numList = []
    for i in rowData['nodeStates']:
        numList.append(i['timestamp'])
    for a in rowData['nodeStates']:
        if a['timestamp'] == max(numList):
            node.append(' | '.join(a['response']))
    return node

def keyCheck(item, key):
    if key in item['response']['autoScoreResult']:
        return True

def assessCheck(item, key):
    if key in item['nodeStates'][0]:
        return True

if __name__ == "__main__":
    main(sys.argv[1:]) 