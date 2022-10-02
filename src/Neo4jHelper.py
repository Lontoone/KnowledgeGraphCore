from neo4j import GraphDatabase
from py2neo import Node,Relationship,Graph,NodeMatcher


class Neo4JHelper:
    def __init__(self):
        #連線
        self.uri ="neo4j://localhost:11003"
        self.driver= GraphDatabase.driver(self.uri, auth=("neo4j", "l0933209916"))
        self.graph=Graph(self.uri,auth=('neo4j','l0933209916'))
        #self.nodePairs=nodePairs
  
    def writeNode(self,nodePairs):    
        matcher=NodeMatcher(self.graph)
        #for pairs in nodePairs:
            #for pair in pairs:
        for pair in nodePairs:
                self.tx=self.graph.begin()    
                #session.write_transaction(self.createNode,pair)
                a=Node("Python", name=pair.entity1.name)
                a.__primarylabel__ = "Python"
                a.__primarykey__ =pair.entity1.name
                b=Node("Python", name=pair.entity2.name)
                b.__primarykey__ =pair.entity2.name
                b.__primarylabel__ = "Python"                
                
                existing_a = matcher.match('Python', name=pair.entity1.name).first()
                existing_b = matcher.match('Python', name=pair.entity2.name).first()
                if not existing_a:
                    self.tx.create(a)
                    existing_a=a                
                if not existing_b:
                    self.tx.create(b)
                    existing_b=b
                    
                rel=Relationship(existing_a,pair.relation,existing_b)
                self.tx.merge(rel)
                self.tx.commit()
        
    def getAllByLabel(self , labelName):
        nodes = NodeMatcher(self.graph)
        res = nodes.match(labelName).all()
        return res;
        