# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 15:18:45 2015

@author: Brendan
"""

import grass.script as gscript

driver="cairo"

gscript.run_command('d.mon', stop=driver)
