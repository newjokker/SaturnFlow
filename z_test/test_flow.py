# -*- coding: utf-8  -*-
# -*- author: jokker -*-


from SaturnFlow.run import SaturnFlow_V2
from SaturnFlow.product import ProductBase

a = SaturnFlow_V2("127.0.0.1", "111")

p = ProductBase()

a.register(p)

a.run()








