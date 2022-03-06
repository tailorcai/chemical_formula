#coding=utf-8
import re

#按照+=,+,++,=,===进行分割
splitter = re.compile(r'(\+=|\+{1,2}|={1,3})')
p_equation = re.compile(r'(.+)(0-9\+|0-9\-|\+|\-)')
p_subscript = re.compile(r'(\d)')

p_fenzi = re.compile(r'^([0-9])?((?:[a-zA-Z()↑·↓]+[0-9]?)*)([0-9]?[\+|\-])?$')
p_fenzi_parts= re.compile(r'([a-zA-Z()↑·↓]+)([0-9]?)')
class FenZi:
    def __init__(self, p):
        self.valid = False
        self.ends = ''
        if p.endswith(')'):
            n = p.rfind('(')
            # print ('found )', n)
            self.ends = p[n:]
            p = p[:n-len(p)]
        elif p.endswith('）'):
            n = p.rfind('（')
            # print ('found )', n)
            self.ends = p[n:]
            p = p[:n-len(p)]
            
        m = p_fenzi.match(p)
        if not m: 
            return
        self.valid = True
        self.num = m.group(1)
        parts = m.group(2)
        self.suffix = m.group(3)
        self.parts = list( map( lambda x: [x[0],x[1]] , p_fenzi_parts.findall( parts )))
        
        if self.suffix and len(self.suffix)==1 and self.parts[-1][1]: # 如果离子没有数字，而最后
            self.suffix = self.parts[-1][1] + self.suffix
            self.parts[-1][1] = ''

    def __str__(self):
        if self.valid:
            return self.format()
        else:
            return 'invalid'

    def format(self):
        def r(x):
            return x[0] + ( '_'+x[1] if x[1] else '')
        
        suffix = '^{' + self.suffix + '}' if self.suffix else ''
        return ( self.num or '' ) + ''.join( [ r(x) for x in self.parts]) + suffix + self.ends


# print( FenZi("H2O") )
# print( FenZi("5Fe2+") )
# print( FenZi("5Nh4Co23+")    )
# print( FenZi("5Nh4Co3-")    )
# print( FenZi("5Nh4Co-")  )

# print( p_equation.match('2OH23+').groups() )
def equation(p,p1):
    if p in ('+$',): return ''
    if p in ('+=','=','==='):
        return "="
    if p in ('+', '++'): 
        return "+"

    if p1 in ('++','+=', '+$'):
        p = p + '+'

    # print( "input=",p,p1 )
    # 找离子
    fz = FenZi(p)
    if fz.valid:
    # print('m1',m1)
        return fz
    print('error', p)
    return '*'

def loop():
    lines = open('equations.txt').readlines()
    lines1 = (
    #     '1、氮气和氢气 N2+3H2=2NH3(高温高压催化剂)',
    # "11、澄清石灰水通入少量CO2: Ca2++2OH-+CO3=CaCO3↓+H2O",
    # '47、金属铁溶于盐酸中 Fe+2H+=Fe2++H2↑',
    # '48、铁粉与氯化铁溶液反应 Fe+2Fe3+=3Fe2+',
    '5、氨气和水 NH3+H2O=NH3·H2O（可逆）',
    '6、氯化铁和氨水 FeCl3+3NH3·H2O=Fe(OH)3(↓)+3NH4Cl(不太肯定是不是会发生氧化还原)',
    )
    pattern = re.compile(r'^(.*)\s(.*)$')
    for l in lines:
        mm = pattern.match(l.strip())
        if mm:
            #print('debug',m.groups())
            # print(m.group(1))
            m = splitter.split(mm.group(2))
            #print('debug', m)
            out = []
            if len(m[-1])==0 and m[-2] == '+':
                m[-2] = '+$'
            for i in range(len(m)-1):                
                out.append( equation(m[i],m[i+1] ))
            out.append( equation(m[-1],'') )
            # print( out )
            print( mm.group(1), '$$'+(''.join( [str(r) for r in out]))+'$$')
        else:
            print( l )


            # output text
            # convert equation


# for l in ('Ca2++2OH-+CO3=CaCO3↓+H2','',''):
#     equation(l )
loop()