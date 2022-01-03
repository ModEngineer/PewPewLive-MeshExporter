#Copyright 2020 ModEngineer
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
import warnings
from copy import deepcopy


class GraphError(Exception):
    """Error class for this module"""
    pass


class Auto:
    """NoneType-like object that represents the automatic value"""
    def __repr__(self):
        return "Auto"

    def __str__(self):
        return "Auto"


class ExitContainer():
    """Error container class that can be used to raise the error or to get an exit code. 0 is a generic, non-error code, negative codes should represent errors, and positive codes should represent non-error program states."""
    class ExitContainerWarning(Warning):
        pass

    def __init__(self, exception=None, code=Auto()):
        #Exit code processing with exception checking
        self.exception = exception
        #Auto handling
        if type(code) is Auto or code is Auto:
            if exception == None:
                self.code = 0
            else:
                self.code = -0x1
        else:
            self.code = code
        #Positive code handling and exception warning
        if type(code) is int:
            if code >= 0:
                if exception != None:
                    warnings.warn(
                        "ExitContainer with an exception should not have a positive code.",
                        category=ExitContainer.ExitContainerWarning)
            #Negative code handling and exception warning
            elif code < 0:
                if exception == None:
                    warnings.warn(
                        "ExitContainer without an exception should not have a negative code.",
                        category=ExitContainer.ExitContainerWarning)

    def raise_exception(self):
        """A function that raises the ExitContainer's exception if it has an exception stored"""
        if self.exception != None:
            raise self.exception


#Graph validation function. Checks graph connections, endpoint count, and nonexistent nodes listed as connections.
def validate_graph(graphData):

    try:
        endpointCount = 0
        for node in graphData:
            if type(graphData[node]) not in [list, tuple]:
                return ExitContainer(
                    TypeError(
                        "Type " + repr(type(graphData[node])) +
                        " is not a list or a tuple. The graphData argument requires that connections are stored in lists or tuples."
                    ), -0x2)
            try:
                for connectedNode in graphData[node]:
                    if not node in graphData[connectedNode]:
                        return ExitContainer(
                            GraphError(
                                "Nodes " + repr(node) + " and " +
                                repr(connectedNode) +
                                " do not list each other in their connections."
                            ), -0x3)
            except KeyError as exc:
                try:
                    raise GraphError("Node " + repr(exc.args[0]) +
                                     " does not exist.") from exc
                except GraphError as exc2:
                    return ExitContainer(exc2, -0x4)
            if len(graphData[node]) % 2 == 1:
                endpointCount += 1
                if endpointCount > 2:
                    return ExitContainer(
                        GraphError(
                            "Graph cannot contain more than 2 nodes of odd degree."
                        ), -0x5)
        if not is_connected(graphData):
            return ExitContainer(GraphError("Graph is not connected."), -0x6)
        return ExitContainer()
    except Exception as e:
        return ExitContainer(e)


#Node remover
def remove_node(node, graphData):
    for connection in graphData[node]:
        graphData[connection].remove(node)
    del graphData[node]


#Edge remover
def remove_edge(node1, node2, graphData):
    graphData[node1].remove(node2)
    graphData[node2].remove(node1)


#Node creator
def add_node(node, graphData):
    if node in graphData.keys():
        raise GraphError("Node already in graph")
    graphData[node] = []


#Edge creator
def add_edge(node1, node2, graphData):
    if not node1 in graphData.keys():
        add_node(node1, graphData)
    if not node2 in graphData.keys():
        add_node(node2, graphData)
    if not node1 in graphData[node2]:
        graphData[node2].append(node1)
    if not node2 in graphData[node1]:
        graphData[node1].append(node2)


def dfs(graphData, vertex=Auto()):
    s = []
    discovered = []
    if type(vertex) is Auto or vertex is Auto:
        vertex = list(graphData.keys())[0]
    s.append(vertex)
    while s:
        vertex = s.pop()
        if not vertex in discovered:
            discovered.append(vertex)
            for w in graphData[vertex]:
                s.append(w)
    return discovered


def is_connected(graphData):
    discovered = dfs(graphData)
    #DFS, returns a list of discovered nodes after picking an arbitrary node
    #Loop that checks if any node isn't discovered
    for key in graphData.keys():
        if not key in discovered:
            return False
    return True


#Bridge-finding.
def find_bridges(graphData):
    if not is_connected(graphData):
        raise GraphError("Unconnected graph cannot be tested for bridges")
    #Init
    processed = []
    bridges = []
    #Loop that removes an edge temporarily, runs DFS, and checks if the graph is still connected
    for start in graphData.keys():
        for end in graphData[start]:
            if (start, end) in processed or (end, start) in processed:
                continue
            processed.append((start, end))
            tempGData = deepcopy(graphData)
            remove_edge(start, end, tempGData)
            if not is_connected(tempGData):
                bridges.append((start, end))
    return bridges


#Function that collapses a list of lists into a single list
def __collapse_list_list(listList, recursive=False):
    outList = []
    for item in listList:
        if type(item) == list:
            if recursive:
                item = __collapse_list_list(deepcopy(item), True)
            outList += item
        else:
            outList.append(item)
    return outList


#Function that checks if all items in subList are in containerList
def __list_contains_list(subList, containerList):
    for item in subList:
        if item not in containerList:
            return False
    return True


#Graph splitter
def split_unconnected(graphData):

    if is_connected(graphData):
        return [graphData]
    dfsresults = []
    while not __list_contains_list(graphData.keys(),
                                   __collapse_list_list(dfsresults)):
        dfsresults.append(
            dfs(graphData,
                vertex=[
                    vert for vert in graphData.keys()
                    if not vert in __collapse_list_list(dfsresults)
                ][0]))
    outputGraphs = []
    for result in dfsresults:
        currentGraph = {}
        for node in result:
            currentGraph[node] = graphData[node]
        outputGraphs.append(currentGraph)
    return outputGraphs


def split_at_bridge(splitNode, node2, graphData):
    bridgeList = find_bridges(graphData)
    if not ((splitNode, node2) in bridgeList or
            (node2, splitNode) in bridgeList):
        raise GraphError("Cannot split graph on non-bridge")
    outGraphs = []
    outGraphs.append(deepcopy(graphData))
    outGraphs.append(deepcopy(graphData))
    for connection in outGraphs[0][splitNode]:
        if connection != node2:
            remove_edge(splitNode, connection, outGraphs[0])
    bridgeGraphDFS = dfs(outGraphs[0], splitNode)
    loopDict = deepcopy(outGraphs[0])
    for node in loopDict:
        if not node in bridgeGraphDFS:
            remove_node(node, outGraphs[0])
    loopDict = deepcopy(outGraphs[1])
    for node in loopDict:
        if node in bridgeGraphDFS and node != splitNode:
            remove_node(node, outGraphs[1])
    return outGraphs


#Fleury implementation based on Wikipedia's pseudocode
def fleury(graphData, checkPath=True):
    """Fleury's algorithm for finding a Eulerian path in an undirected graph"""
    #Init
    tempGData = deepcopy(graphData)
    endpoints = []
    #Endpoint finding
    for node in tempGData:
        if len(tempGData[node]) % 2 == 1:
            endpoints.append(node)
    if len(endpoints) == 0:
        currentNode = list(tempGData.keys())[0]
    else:
        currentNode = endpoints[0]
    path = [currentNode]
    #Mainloop
    while tempGData[currentNode]:
        #Next-edge-finder. Prefers non-bridges
        bridges = find_bridges(tempGData)
        nonBridgeConnections = [
            connection for connection in tempGData[currentNode]
            if not connection in bridges
        ]
        if nonBridgeConnections:
            nextNode = nonBridgeConnections[0]
        else:
            nextNode = tempGData[currentNode][0]
        #Next-node-queuing and path building
        remove_edge(currentNode, nextNode, tempGData)
        if not tempGData[currentNode]:
            remove_node(currentNode, tempGData)
        path.append(nextNode)
        currentNode = nextNode
    #Path validation
    if checkPath:
        for node in graphData:
            for connection in graphData[node]:
                listContainedList = False
                for index in range(len(path) - 1):
                    if __list_contains_list([node, connection],
                                            [path[index], path[index + 1]]):
                        listContainedList = True
                        break
                if not listContainedList:
                    return None
    return path


# Automatic splitting of graph into multiple graphs with Eulerian paths (NOT FUNCTIONAL)
# def auto_split(graphData, returnGraphs=True, returnPaths=False):
#     assert returnGraphs or returnPaths, "auto_split must have a selected return value."
#     output = {}
#     if returnGraphs:
#         output["graphs"] = []
#     if returnPaths:
#         output["paths"] = []
#     fleuryTest = fleury(graphData)
#     if fleuryTest:
#         if returnGraphs:
#             output["graphs"] = [graphData]
#         if returnPaths:
#             output["paths"] = [fleuryTest]
#         return output
#     eulerianParts = []
#     tempGData = deepcopy(graphData)
#     while tempGData:
#         currentFleury = fleury(tempGData, False)
#         eulerianParts.append(currentFleury)
#         if returnGraphs:
#             output["graphs"].append({})
#         for index, node1 in enumerate(currentFleury[:-1]):
#             node2 = currentFleury[index + 1]
#             remove_edge(node1, node2, tempGData)
#             if returnGraphs:
#                 add_edge(node1, node2, output["graphs"][-1])
#         tempTempGData = deepcopy(tempGData)
#         for node in tempTempGData:
#             if not tempGData[node]:
#                 if returnGraphs and not node in __collapse_list_list(
#                         eulerianParts):
#                     output["graphs"].append([node])
#                 remove_node(node, tempGData)
#         del tempTempGData
#     if returnPaths:
#         output["paths"] = eulerianParts
#     return output
