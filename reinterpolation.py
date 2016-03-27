# -*- coding: utf-8 -*-

"""
@brief: digital elevation model re-interpolation for the tangible water flow experiment

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.

@author: Brendan Harmon (brendanharmon@gmail.com)
"""

import sys
import atexit
import grass.script as gscript
from grass.exceptions import CalledModuleError

# set graphics driver
driver = "cairo"

def cleanup():
    try:
        gscript.run_command('d.mon', stop=driver)
    except CalledModuleError:
        pass

def main():
    # temporary region
    gscript.use_temp_region()

    # set parameters
    overwrite = True
    tension = 25
    smooth = 5
    npmin = 300
    dmin = 0.5
    resolution = 10000

    # set region
    region = "dem@PERMANENT"

    # list scanned DEMs for experiment 1
    dems = gscript.list_grouped('rast', pattern='*dem_1')['reinterpolation']

    # iterate through scanned DEMs
    for dem in dems:

        # check alignment
        gscript.run_command('r.region', map=dem, raster=region)

        # reinterpolate DEM from random points using regularized spline with tension
        gscript.run_command('g.region', raster=region, res=3)
        gscript.run_command('r.random', input=dem, npoints=resolution, vector=dem.replace("dem","points"), flags='bd', overwrite=overwrite)
        gscript.run_command('v.surf.rst', input=dem.replace("dem","points"), elevation=dem,  tension=tension, smooth=smooth, npmin=npmin, dmin=dmin, overwrite=overwrite)
        gscript.run_command('r.colors', map=dem, color="elevation")
        gscript.run_command('g.remove', type='vector', pattern='*points*', flags='f')

    # list scanned DEMs for experiment 2
    dems = gscript.list_grouped('rast', pattern='*dem_2')['reinterpolation']

    # iterate through scanned DEMs
    for dem in dems:

        # check alignment
        gscript.run_command('r.region', map=dem, raster=region)

        # reinterpolate DEM from random points using regularized spline with tension
        gscript.run_command('g.region', raster=region, res=3)
        gscript.run_command('r.random', input=dem, npoints=resolution, vector=dem.replace("dem","points"), flags='bd', overwrite=overwrite)
        gscript.run_command('v.surf.rst', input=dem.replace("dem","points"), elevation=dem,  tension=tension, smooth=smooth, npmin=npmin, dmin=dmin, overwrite=overwrite)
        gscript.run_command('r.colors', map=dem, color="elevation")
        gscript.run_command('g.remove', type='vector', pattern='*points*', flags='f')

if __name__ == "__main__":
    atexit.register(cleanup)
    sys.exit(main())
