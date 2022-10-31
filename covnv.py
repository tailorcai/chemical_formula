#coding=utf-8
import re
from readline import set_auto_history

from parse import FenZi
from chempy import Species,Reaction, Substance

from collections import defaultdict
from pprint import pprint
from graph import init_neo4j_data, init_graphdb_data


#按照+=,+,++,=,===进行分割
splitter = re.compile(r'(=|\+(?!(?:\+|=|$)))')
p_equation = re.compile(r'(.+)(0-9\+|0-9\-|\+|\-)')
# p_subscript = re.compile(r'(\d)')

# print( FenZi("H2O") )
# print( FenZi("5Fe2+") )
# print( FenZi("5Nh4Co23+")    )
# print( FenZi("5Nh4Co3-")    )
# print( FenZi("5Nh4Co-")  )

# print( p_equation.match('2OH23+').groups() )
def equation(p):
    # print( p )
    fz = FenZi(p)
    if fz.valid:
        return fz
    print('error', p)
    return '*'

def loop():

    reactions = []
    lines = open('equations.txt').readlines()
    for l in lines:
        mm = [x for x in l.strip().split(' ',2) if x]       # 去掉连续空格
        if len(mm)>1:
            m = splitter.split(mm[1])

            equation = defaultdict(dict)
            idx = 'l'
            for x in m:
                try:
                    if x in ('+'): continue
                    if x in ('='): 
                        idx = 'r'
                        continue

                    fz = FenZi(x)
                    if not fz.valid:
                        # save to error 
                        continue
                    species = fz.to_species()
                    print( mm[0], x, species )
                    num = fz.num or '1'
                    # sp = Species.from_formula( species )
                    equation[idx][ species ] = int( num )

                except Exception as e:
                    print( e )
                    print( "error parsing, ", mm  )
                    raise e
            #print( mm[0], '$$'+(''.join( [str(r) for r in out]))+'$$')

            if equation:
                try: 
                    reac = Reaction( equation['l'], equation['r'], name=mm[0])
                    
                    # pprint( equation )
                    keys = []
                    keys.extend( equation['l'].keys() )
                    keys.extend( equation['r'].keys() )
                    subst = { _k: Substance.from_formula(_k) for _k in keys}

                    # print( reac.unicode(subst) )
                    # print( reac.active_prod_stoich() )
                    reac.data={'unicode':reac.unicode(subst)}
                    reactions.append( reac  )
                except Exception as e:
                    pprint( equation )
                    print( "===========", e )
                    raise e
                    # print( reac, prod)
        else:
            pass
            #print( l )
    return reactions


reactions = loop()

# init_neo4j_data(reactions)
init_graphdb_data(reactions)
# print( substances )