# -*- coding: utf-8 -*-

"""
@brief: reference maps for the tangible water flow experiment

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.

@author: Brendan Harmon (brendanharmon@gmail.com)
"""

import os
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

    # switch between png and cairo driver

    # temporary region
    gscript.use_temp_region()

    # set grass data directory
    grassdata = os.path.normpath("C:/Users/Brendan/Documents/grassdata/") # specify the full filepath filename of your grassdata directory

    # set rendering directory
    render_dir = os.path.normpath("results/reference/")
    render = os.path.join(grassdata,render_dir)

    # set paramters
    overwrite = True

    # set DEM
    dem = "dem@PERMANENT"

    # variables
    region=dem
    relief=dem.replace("dem","relief")
    contour=dem.replace("dem","contour")
    slope=dem.replace("dem","slope")
    forms=dem.replace("dem","form")
    depth=dem.replace("dem","depth")
    before=region
    after=dem
    regression=dem.replace("dem","regress")
    difference=dem.replace("dem","diff")

    # set region
    gscript.run_command('g.region', rast=region, res=3)

    # render DEM
    info = gscript.parse_command('r.info', map=dem, flags='g')
    width=int(info.cols)+int(info.cols)/2
    height=int(info.rows)
    gscript.run_command('d.mon', start=driver, width=width, height=height,  output=os.path.join(render,dem+".png"), overwrite=overwrite)
    gscript.run_command('r.colors', map=dem, color="elevation")
    gscript.run_command('g.region', rast="dem")
    gscript.run_command('r.relief', input=dem, output=relief, altitude=60, azimuth=45, zscale=1, units="intl", overwrite=overwrite)
    gscript.run_command('g.region', rast=region)
    gscript.run_command('r.contour', input=dem, output=contour, step=5, overwrite=overwrite)
    gscript.run_command('d.shade', shade=relief, color=dem, brighten=75)
    gscript.run_command('d.vect', map=contour, display="shape")
    gscript.run_command('d.legend', raster=dem, fontsize=10, at=(10,70,1,4))
    gscript.run_command('d.mon', stop=driver)

    # compute slope
    gscript.run_command('d.mon', start=driver, width=width, height=height,  output=os.path.join(render,slope+".png"), overwrite=overwrite)
    gscript.run_command('r.param.scale', input=dem, output=slope, size=9, method="slope", overwrite=overwrite)
    gscript.run_command('r.colors', map=slope, color="slope")
    gscript.run_command('d.shade', shade=relief, color=slope, brighten=75)
    gscript.run_command('d.vect', map=contour, display='shape')
    gscript.run_command('d.legend', raster=slope, fontsize=10, at=(10,90,1,4))
    gscript.run_command('d.mon', stop=driver)

    # #compute landforms # requires r.geomorphon addon
    # gscript.run_command('d.mon', start=driver, width=width, height=height,  output=os.path.join(render,forms+".png"), overwrite=overwrite)
    # gscript.run_command('r.geomorphon', dem=dem, forms=forms, search=9, skip=6, overwrite=overwrite)
    # gscript.run_command('d.shade', shade=relief, color=forms, brighten=75)
    # gscript.run_command('d.vect', map=contour, display='shape')
    # #gscript.run_command('d.legend', raster=forms)
    # gscript.run_command('d.mon', stop=driver)

    # simulate water flow
    gscript.run_command('d.mon', start=driver, width=width, height=height,  output=os.path.join(render,depth+".png"), overwrite=overwrite)
    gscript.run_command('r.slope.aspect', elevation=dem, dx='dx', dy='dy', overwrite=overwrite)
    gscript.run_command('r.sim.water', elevation=dem, dx='dx', dy='dy', rain_value=300, depth=depth, nwalkers=5000, niterations=4, overwrite=overwrite)
    gscript.run_command('g.remove', flags='f', type='raster', name=['dx', 'dy'])
    gscript.run_command('d.shade', shade=relief, color=depth, brighten=75)
    gscript.run_command('d.vect', map=contour, display='shape')
    gscript.run_command('d.legend', raster=depth, fontsize=10, at=(10,90,1,4))
    gscript.run_command('d.mon', stop=driver)

    # compute difference
    gscript.run_command('d.mon', start=driver, width=width, height=height,  output=os.path.join(render,difference+".png"), overwrite=overwrite)
    regression_params = gscript.parse_command('r.regression.line', flags='g', mapx=before, mapy=after, overwrite=overwrite)
    gscript.run_command('r.mapcalc', expression='{regression} = {a} + {b} * {before}'.format(a=regression_params['a'], b=regression_params['b'],before=before,regression=regression), overwrite=overwrite)
    gscript.run_command('r.mapcalc', expression='{difference} = {regression} - {after}'.format(regression=regression,after=after,difference=difference), overwrite=overwrite)
    gscript.run_command('r.colors', map=difference, color="differences")
    gscript.run_command('d.shade', shade=relief, color=difference, brighten=75)
    gscript.run_command('d.vect', map=contour, display='shape')
    gscript.run_command('d.legend', raster=difference, fontsize=10, at=(10,90,1,4))
    gscript.run_command('d.mon', stop=driver)
    gscript.run_command('g.remove', flags='f', type='raster', name=regression)

if __name__ == "__main__":
    atexit.register(cleanup)
    sys.exit(main())
