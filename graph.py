#coding=utf-8
import symbol
from py2neo import *
from chempy import Species,Reaction, Substance
from graphdb import GraphDB
from chempy.util import periodic 

def init_graphdb_data( reactions ):
    db = GraphDB('/tmp/test_graph.db')
    elements_tbl = [ dict(type='Element', id=i+1, name=symbol, fullname=periodic.names[i]) 
                        for i,symbol in enumerate(periodic.symbols) ]
    for ele in elements_tbl: 
        db.store_relation(ele['id'],'is_element_of',ele)

    for _idx, reac in enumerate( reactions ):
        def create_subst(k,num, role):
            subst = Substance.from_formula( k )
            db.store_relation( subst.name, role, reac)

            for k,v in subst.composition.items():
                if k>0:
                    # print(k,v)
                    # ele_node = elements_tbl[k-1]
                    db.store_relation( k, 'is_part_of', subst)
                    db.store_relation( subst.name, 'object_of', subst)

        for k,num in reac.reac.items(): create_subst(k,num,'left_of')
        for k,num in reac.prod.items(): create_subst(k,num,'right_of')

    for x in db(elements_tbl[1])(list):
        print(x )
        

def init_neo4j_data( reactions):
    graph = Graph('http://127.0.0.1:7474', user="neo4j", password="123456")
    tx = graph.begin()

    # init Element
    elements_tbl = []
    for i in range(len(periodic.symbols)):
        ele_node = Node('Element', name=periodic.symbols[i], fullname=periodic.names[i])
        elements_tbl.append( ele_node )
        tx.merge(ele_node, 'Element', 'name' )

    # composition
    for _idx, (reac,formula) in enumerate( reactions ):
        reac_node = Node('Reaction', name="React-%d"%_idx, formula=formula)
        tx.merge( reac_node,'Reaction', 'formula'  )  # formula重复

        def create_subst(k,num, role):
            subst = Substance.from_formula( k )
            subst_node = Node('Substance', name=subst.unicode_name, formula=k)
            rel = Relationship(subst_node, role, reac_node, num=num)
            tx.merge( subst_node, 'Substance', 'name' )
            tx.create( rel  )

            for k,v in subst.composition.items():
                if k>0:
                    # print(k,v)
                    ele_node = elements_tbl[k-1]
                    rel = Relationship(ele_node, 'form', subst_node, num=v)
                    tx.create(rel)

        for k,num in reac.reac.items(): create_subst(k,num,'left')
        for k,num in reac.prod.items(): create_subst(k,num,'right')

        # break
    tx.commit()
    return graph

class ChemQuery:
    def __init__(self):
        self.db = GraphDB('/tmp/test_graph.db')

    def element_detail(self, symbol_id):
        # print( symbol_id )
        return dict(
            element = self.db(symbol_id).is_element_of(list)[0],
            substances = self.db(symbol_id).is_part_of(list),
        )
    
    def reactions_of_subst(self, subst_name):
        return {'left': self.db(subst_name).left_of(list), 
                'right':self.db(subst_name).right_of(list) }

if __name__=="__main__":
    q = ChemQuery()
    print( q.element_detail(1) )