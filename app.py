import eel
import os
from py2neo import Graph
import src.Main

from src.Neo4jHelper import Neo4JHelper


def buildNodes(nodeRecord):
    data = {"id": str(nodeRecord.n._id), "label": next(iter(nodeRecord.n.labels))}
    data.update(nodeRecord.n.properties)

    return {"data": data}

def buildEdges(relationRecord):
    data = {"source": str(relationRecord.r.start_node._id), 
            "target": str(relationRecord.r.end_node._id),
            "relationship": relationRecord.r.rel.type}

    return {"data": data}

def get_graph():
    neoHelper = Neo4JHelper()
    res= neoHelper.getAllByLabel("Python")
    print (res);
    #nodes = map(buildNodes, graph.cypher.execute('MATCH (n) RETURN n'))
    #edges = map(buildEdges, graph.cypher.execute('MATCH ()-[r]->() RETURN r'))  

    #return jsonify(elements = {"nodes": nodes, "edges": edges})    

if __name__ =="__main__":
    #get_graph()           
    #nodes= src.Main.main()        
    # 開啟網頁
    eel.init(f'{os.path.dirname(os.path.realpath(__file__))}/web')
    eel.start('main.html', mode='chrome-app')  # 網頁 (app模式)
    
    
    
@eel.expose
def updateNodes():    
    eel.addNodes("" , 0)()