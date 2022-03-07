#coding=utf-8
import re

from parse import FenZi

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
    lines = open('equations.txt').readlines()
    for l in lines:
        mm = l.strip().split(' ',2)
        if len(mm)>1:
            m = splitter.split(mm[1])
            out = [equation(x) if not x in ('+', '=') else x 
                        for x in m]
            print( mm[0], '$$'+(''.join( [str(r) for r in out]))+'$$')
        else:
            print( l )

loop()