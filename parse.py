#coding=utf-8
import re
import unittest

p_fenzi = re.compile(r'^([0-9])?((?:[a-zA-Z()↑·↓]+[0-9]?)*)([0-9]?[\+|\-])?([\(（].*[）\)])?$')
p_fenzi_parts= re.compile(r'([a-zA-Z()↑·↓]+)([0-9]?)')

class FenZi:
    def __init__(self, p):
        self.valid = False
        self.ends = ''
        # if p.endswith(')'):
        #     n = p.rfind('(')
        #     # print ('found )', n)
        #     self.ends = p[n:]
        #     p = p[:n-len(p)]
        # elif p.endswith('）'):
        #     n = p.rfind('（')
        #     # print ('found )', n)
        #     self.ends = p[n:]
        #     p = p[:n-len(p)]
            
        m = p_fenzi.match(p)
        if not m: 
            return
        self.valid = True
        self.num = m.group(1) or ''
        parts = m.group(2) or ''
        self.suffix = m.group(3) or ''
        self.ends= m.group(4) or ''
        # print( m.groups() )
        self.parts = list( map( lambda x: [x[0],x[1]] , p_fenzi_parts.findall( parts )))
        
        # if self.suffix and len(self.suffix)==1 and self.parts[-1][1]: # 如果离子没有数字，而最后
        #     self.suffix = self.parts[-1][1] + self.suffix
        #     self.parts[-1][1] = ''

    def __str__(self):
        if self.valid:
            return self.format()
        else:
            return 'invalid'

    def format(self):
        def r(x):
            return x[0] + ( '_'+x[1] if x[1] else '')
        
        suffix = self.suffix and '^' + ( '{' + self.suffix + '}' if len(self.suffix)>1 else self.suffix ) 
        return ( self.num or '' ) + ''.join( [ r(x) for x in self.parts]) + (suffix or '' ) + self.ends


class ReTestCase(unittest.TestCase):  
    def setUp(self):  
        self.splitter = re.compile(r'=|\+(?!(?:\+|=|$))')

    def testSplit(self):  
        i = "1++2+3+=4+5++6+"
        self.assertEqual(self.splitter.split(i), ['1+','2','3+','4','5+','6+'] )  
        i = "1-+2+3-=4+5-+6-"
        self.assertEqual(self.splitter.split(i), ['1-','2','3-','4','5-','6-'] )  

    def testFenZi(self):
        i = ["H2O", "5Fe2+", "5Nh4Co23+","5Nh4Co3-", "5Nh4Co-", "H2O(hello)", "H2O（hello）", "Nh4(CO2)3(hello)"]
        o = ["H_2O", "5Fe_2^+", "5Nh_4Co_2^{3+}", "5Nh_4Co_3^-", "5Nh_4Co^-", "H_2O(hello)", "H_2O（hello）","Nh_4(CO_2)_3(hello)" ]
        for x,y in zip(i,o):
            self.assertEqual( str(FenZi(x)),y )

    # lines = (
    # #     '1、氮气和氢气 N2+3H2=2NH3(高温高压催化剂)',
    # # "11、澄清石灰水通入少量CO2: Ca2++2OH-+CO3=CaCO3↓+H2O",
    # # '47、金属铁溶于盐酸中 Fe+2H+=Fe2++H2↑',
    # # '48、铁粉与氯化铁溶液反应 Fe+2Fe3+=3Fe2+',
    # '5、氨气和水 NH3+H2O=NH3·H2O（可逆）',
    # '6、氯化铁和氨水 FeCl3+3NH3·H2O=Fe(OH)3(↓)+3NH4Cl(不太肯定是不是会发生氧化还原)',
    # )
if __name__ == "__main__":  
    unittest.main()  