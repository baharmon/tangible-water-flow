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

def main():
    analyze_reference()
    atexit.register(cleanup)
    sys.exit(0)

def cleanup():
    try:
        # remove temporary maps
        gscript.run_command('g.remove', type='raster', name=['depressionless_dem','flow_dir','dx', 'dy'], flags='f')

    except CalledModuleError:
        pass

def analyze_reference():
    """compute the relief, contours, slope, water flow, difference, depressions, and concentrated flow of the reference landscape"""

    # temporary region
    gscript.use_temp_region()

    # set grass data directory
    grassdata = os.path.normpath("C:/Users/Brendan/Documents/grassdata/") # specify the full filepath filename of your grassdata directory

    # set rendering directory
    render_dir = os.path.normpath("results/reference/")
    render = os.path.join(grassdata,render_dir)

    # set color rules
    depressions_colors = '0% aqua\n100% blue'
    depth_colors = '0 255:255:255\n0.001 255:255:0\n0.05 0:255:255\n0.1 0:127:255\n0.5 0:0:255\n100% 0:0:0'
    difference_colors = '-0.5 blue\n0 white\n0.5 red'

    # set paramters
    overwrite = True

    # set DEM
    dem = "dem"

    # variables
    region=dem
    relief=dem.replace("dem","relief")
    contour=dem.replace("dem","contour")
    slope=dem.replace("dem","slope")
    depth=dem.replace("dem","depth")
    before="depth"
    after=depth
    difference=dem.replace("dem","diff")
    depressions=dem.replace("dem","depressions")
    concentrated_flow='concentrated_flow'
    concentrated_points='concentrated_points'

    # set region
    gscript.run_command('g.region', rast=region, res=3)

    # render DEM
    info = gscript.parse_command('r.info', map=dem, flags='g')
    width=int(info.cols)+int(info.cols)/2
    height=int(info.rows)
    gscript.run_command('d.mon', start=driver, width=width, height=height,  output=os.path.join(render,dem+".png"), overwrite=overwrite)
    gscript.run_command('r.colors', map=dem, color="elevation")
    gscript.run_command('g.region', rast="dem")
    gscript.run_command('r.relief', input=dem, output=relief, altitude=90, azimuth=45, zscale=1, units="intl", overwrite=overwrite)
    gscript.run_command('g.region', rast=region)
    gscript.run_command('r.contour', input=dem, output=contour, step=5, overwrite=overwrite)
    gscript.run_command('d.shade', shade=relief, color=dem, brighten=75)
    gscript.run_command('d.vect', map=contour, display="shape")
    gscript.run_command('d.legend', raster=dem, fontsize=9, at=(10,70,1,4))
    gscript.run_command('d.mon', stop=driver)

    # compute slope
    gscript.run_command('d.mon', start=driver, width=width, height=height,  output=os.path.join(render,slope+".png"), overwrite=overwrite)
    gscript.run_command('r.param.scale', input=dem, output=slope, size=9, method="slope", overwrite=overwrite)
    gscript.run_command('r.colors', map=slope, color="slope")
    gscript.run_command('d.shade', shade=relief, color=slope, brighten=75)
    gscript.run_command('d.vect', map=contour, display='shape')
    gscript.run_command('d.legend', raster=slope, fontsize=9, at=(10,90,1,4))
    gscript.run_command('d.mon', stop=driver)

    # simulate water flow
    gscript.run_command('d.mon', start=driver, width=width, height=height,  output=os.path.join(render,depth+".png"), overwrite=overwrite)
    gscript.run_command('r.slope.aspect', elevation=dem, dx='dx', dy='dy', overwrite=overwrite)
    gscript.run_command('r.sim.water', elevation=dem, dx='dx', dy='dy', rain_value=300, depth=depth, nwalkers=5000, niterations=4, overwrite=overwrite)
    gscript.run_command('g.remove', flags='f', type='raster', name=['dx', 'dy'])
    gscript.run_command('d.shade', shade=relief, color=depth, brighten=75)
    gscript.run_command('d.vect', map=contour, display='shape')
    gscript.run_command('d.legend', raster=depth, fontsize=9, at=(10,90,1,4))
    gscript.run_command('d.mon', stop=driver)

    # identify depressions
    gscript.run_command('r.fill.dir', input=dem, output='depressionless_dem', direction='flow_dir',overwrite=overwrite)
    gscript.run_command('r.mapcalc', expression='{depressions} = if({depressionless_dem} - {dem} > {depth}, {depressionless_dem} - {dem}, null())'.format(depressions=depressions, depressionless_dem='depressionless_dem', dem=dem, depth=0), overwrite=overwrite)
    gscript.write_command('r.colors', map=depressions, rules='-', stdin=depressions_colors)
    gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(render,depressions+".png"), overwrite=overwrite)
    gscript.run_command('d.shade', shade=relief, color=depressions, brighten=75)
    gscript.run_command('d.vect', map=contour, display='shape')
    gscript.run_command('d.legend', raster=depressions, fontsize=9, at=(10,90,1,4))
    gscript.run_command('d.mon', stop=driver)

    # compute the difference between the modeled and reference flow depth
    gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(render,difference+".png"), overwrite=overwrite)
    gscript.run_command('r.mapcalc', expression='{difference} = {before} - {after}'.format(before=before,after=after,difference=difference), overwrite=overwrite)
    gscript.write_command('r.colors', map=difference, rules='-', stdin=difference_colors)
    gscript.run_command('d.shade', shade=relief, color=difference, brighten=75)
    gscript.run_command('d.vect', map=contour, display='shape')
    gscript.run_command('d.legend', raster=difference, fontsize=9, at=(10,90,1,4))
    gscript.run_command('d.mon', stop=driver)

    # extract concentrated flow
    gscript.run_command('r.mapcalc', expression='{concentrated_flow} = if({depth}>=0.05,{depth},null())'.format(depth=depth,concentrated_flow=concentrated_flow), overwrite=overwrite)
    gscript.write_command('r.colors', map=concentrated_flow, rules='-', stdin=depth_colors)
    gscript.run_command('r.random', input=concentrated_flow, npoints='100%', vector=concentrated_points, overwrite=overwrite)
    gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(render,concentrated_flow+".png"), overwrite=overwrite)
    gscript.run_command('d.shade', shade=relief, color=concentrated_flow, brighten=75)
    gscript.run_command('d.vect', map=concentrated_points, display='shape')
    gscript.run_command('d.legend', raster=concentrated_flow, fontsize=9, at=(10,90,1,4))
    gscript.run_command('d.mon', stop=driver)

    # compute number of cells with depressions
    univar = gscript.parse_command('r.univar', map=depressions, separator='newline', flags='g')
    depression_cells =  float(univar['sum'])
    print 'cells with depressions: ' + str(depression_cells)

if __name__ == "__main__":
    main()
