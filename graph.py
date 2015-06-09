import pymongo as pm
import snap
import csv


def build_graph(database, collection):
    client = pm.MongoClient()
    db = client[database]
    coll = db[collection]

    graph = snap.TNGraph.New()

    coll_length = coll.count()
    for i in range(coll_length):
       builder(int(coll.find()[i]["user_id"]), coll.find()[i]["friends"], coll.find()[i]["followers"], graph)

    print graph.Empty()
    print "Nodes:"
    print graph.GetNodes()
    print "Edges:"
    print graph.GetEdges()
    print "Custering Coefficients:"
    print snap.GetClustCf(graph,-1)
    print "Triads:"
    print snap.GetTriads(graph,-1)
    print snap.PrintInfo(graph, "Graph Info")
    '''
    eccentricity = []

    node_count = 1
    for node in graph.Nodes():
        print node_count
        ecc = snap.GetNodeEcc(graph, node.GetId(), False)
        eccentricity.append(ecc)
        node_count += 1

    #print "Eccentricities:"
    #print eccentricity
    
    ecc_file = open('tsa_undirected.csv', 'wb')
    wr = csv.writer(ecc_file)
    wr.writerow(eccentricity)

    #H = snap.TIntStrH()
    #snap.SaveGViz(graph, 'tsa_network_graph.gv', 'tsa Network', False, H)
    '''
def builder(user_id, friends, followers, graph):
    try:
        graph.AddNode(user_id)
    except:
        pass

    for f in friends:
        f = int(f)
        try:
            graph.AddNode(f)
        except:
            pass

        try:
            graph.AddEdge(f,user_id)
        except:
            pass

    for f in followers:
        f = int(f)
        try:
            graph.AddNode(f)
        except:
            pass

        try:
            graph.AddEdge(user_id,f)
        except:
            pass

def build_undirected_graph(database, collection):
    client = pm.MongoClient()
    db = client[database]
    coll = db[collection]

    graph = snap.TUNGraph.New()

    coll_length = coll.count()
    for i in range(coll_length):
       builder(int(coll.find()[i]["user_id"]), coll.find()[i]["friends"], coll.find()[i]["followers"], graph)

    snap.PrintInfo(graph, "Graph Info", False)

#-----------------------------------

if __name__ == '__main__':
    build_graph('tsa_network_2', 'ids')
    build_undirected_graph('tsa_network_2', 'ids')
