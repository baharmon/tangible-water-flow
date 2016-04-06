# -*- coding: utf-8 -*-

"""
@brief: spatial analysis for the tangible water flow experiment

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.

@author: Brendan Harmon (brendanharmon@gmail.com)
"""

import os
import sys
import atexit
import grass.script as gscript
from grass.exceptions import CalledModuleError
import matplotlib.pyplot as plt

# set graphics driver
driver = "cairo"

# temporary region
gscript.use_temp_region()

# set grass data directory
grassdata = os.path.normpath("C:/Users/Brendan/Documents/grassdata/")  # specify the full filepath filename of your grassdata directory

# set rendering directories
render_dir = os.path.normpath("results/analysis/")
render = os.path.join(grassdata, render_dir)
series_dir = os.path.normpath("results/summary/")
series = os.path.join(grassdata, series_dir)

# set paramters
overwrite = True

# set variables
experiments = 2
iterator = experiments+1

# set color rules
depressions_colors = '0% aqua\n100% blue'
depth_colors = '0 255:255:255\n0.001 255:255:0\n0.05 0:255:255\n0.1 0:127:255\n0.5 0:0:255\n100% 0:0:0'

# set region
region = "dem@PERMANENT"
gscript.run_command('g.region', rast=region, res=3)

# driver settings
info = gscript.parse_command('r.info', map=region, flags='g')
width = int(info.cols)+int(info.cols)/2
height = int(info.rows)

def main():
    #analyze_models()
    cells, distance = analyze_series()
    plot_series(cells, distance)
    atexit.register(cleanup)
    sys.exit(0)


def cleanup():
    try:
        # remove temporary maps
        gscript.run_command('g.remove', type='raster', name=['depressionless_dem', 'flow_dir', 'dx', 'dy'], flags='f')

    except CalledModuleError:
        pass


def analyze_models():
    """Compute the relief, contours, water flow, difference in water flow, depressions, and concentrated flow for each model in each experiment"""

    # list scanned DEMs
    dems = gscript.list_grouped('rast', pattern='*dem*')['analysis']

    # iterate through scanned DEMs
    for dem in dems:

        # variables
        relief = dem.replace("dem", "relief")
        contour = dem.replace("dem", "contour")
        depth = dem.replace("dem", "depth")
        before = "depth@PERMANENT"
        after = depth
        difference = dem.replace("dem", "diff")
        depressions = dem.replace("dem", "depressions")

        # compute relief
        gscript.run_command('r.relief', input=dem, output=relief, altitude=90, azimuth=45, zscale=1, units="intl", overwrite=overwrite)

        # compute contours
        gscript.run_command('r.contour', input=dem, output=contour, step=5, overwrite=overwrite)

        # simulate water flow
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(render, depth+".png"), overwrite=overwrite)
        gscript.run_command('r.slope.aspect', elevation=dem, dx='dx', dy='dy', overwrite=overwrite)
        gscript.run_command('r.sim.water', elevation=dem, dx='dx', dy='dy', rain_value=300, depth=depth, nwalkers=5000, niterations=4, overwrite=overwrite)
        gscript.run_command('g.remove', flags='f', type='raster', name=['dx', 'dy'])
        gscript.run_command('d.shade', shade=relief, color=depth, brighten=75)
        gscript.run_command('d.vect', map=contour, display='shape')
        gscript.run_command('d.legend', raster=depth, fontsize=9, at=(10, 90, 1, 4))
        gscript.run_command('d.mon', stop=driver)

        # identify depressions
        gscript.run_command('r.fill.dir', input=dem, output='depressionless_dem', direction='flow_dir',overwrite=overwrite)
        gscript.run_command('r.mapcalc', expression='{depressions} = if({depressionless_dem} - {dem} > {depth}, {depressionless_dem} - {dem}, null())'.format(depressions=depressions, depressionless_dem='depressionless_dem', dem=dem, depth=0), overwrite=overwrite)
        gscript.write_command('r.colors', map=depressions, rules='-', stdin=depressions_colors)
        gscript.run_command('g.remove', flags='f', type='raster', name=['depressionless_dem','flow_dir'])
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(render, depressions+".png"), overwrite=overwrite)
        gscript.run_command('d.shade', shade=relief, color=depressions, brighten=75)
        gscript.run_command('d.vect', map=contour, display='shape')
        gscript.run_command('d.legend', raster=depressions, fontsize=9, at=(10, 90, 1, 4))
        gscript.run_command('d.mon', stop=driver)

        # compute the difference between the modeled and reference flow depth
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(render, difference+".png"), overwrite=overwrite)
        gscript.run_command('r.mapcalc', expression='{difference} = {before} - {after}'.format(before=before, after=after, difference=difference), overwrite=overwrite)
        gscript.run_command('r.colors', map=difference, color='differences')
        gscript.run_command('d.shade', shade=relief, color=difference, brighten=75)
        gscript.run_command('d.vect', map=contour, display='shape')
        gscript.run_command('d.legend', raster=difference, fontsize=9, at=(10, 90, 1, 4))
        gscript.run_command('d.mon', stop=driver)


def analyze_series():
    """compute the difference, water flow, depressions, and concentrated flow for each series of models"""

    cells = []
    distance = []

    # compute percentage of cells with depressions in the reference
    univar_ref_cells = gscript.parse_command('r.univar', map="depressions@PERMANENT", separator='newline', flags='g')
    total_count = float(univar_ref_cells['cells'])
    null_count = float(univar_ref_cells['null_cells'])
    depression_count = total_count - null_count
    reference_percent = depression_count/total_count*100
    cells.append(reference_percent)
    print 'percentage cells with depressions in reference: ' + str(reference_percent)

    for i in range(1, iterator):

        # variables
        diff_pattern = "*diff_"+str(i)
        depth_pattern = "*depth_"+str(i)
        depressions_pattern = "*depressions_"+str(i)
        reference_contour = "contour@PERMANENT"
        reference_relief = "relief@PERMANENT"
        mean_diff = "mean_diff_"+str(i)
        mean_depth = "mean_depth_"+str(i)
        max_depth = "max_depth_"+str(i)
        sum_depth = "sum_depth_"+str(i)
        mean_depressions = "mean_depressions_"+str(i)
        max_depressions = "max_depressions_"+str(i)
        sum_depressions = "sum_depressions_"+str(i)
        concentrated_flow = "concentrated_flow_"+str(i)
        concentrated_points = "concentrated_points_"+str(i)
        reference_points = "concentrated_points"
        flow_distance = "flow_distance_"+str(i)
        copied_points = 'copied_points_'+str(i)

        # list depths
        depth_list = gscript.list_grouped('rast', pattern=depth_pattern)['analysis']

        # list of differences of depths
        diff_list = gscript.list_grouped('rast', pattern=diff_pattern)['analysis']

        # list depths
        depressions_list = gscript.list_grouped('rast', pattern=depressions_pattern)['analysis']

        # compute the mean of depths
        gscript.run_command('r.series', input=depth_list, output=mean_depth, method="average", overwrite=overwrite)
        gscript.write_command('r.colors', map=mean_depth, rules='-', stdin=depth_colors)
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(series, mean_depth+".png"), overwrite=overwrite)
        gscript.run_command('d.shade', shade=reference_relief, color=mean_depth, brighten=75)
        gscript.run_command('d.vect', map=reference_contour, display='shape')
        gscript.run_command('d.legend', raster=mean_depth, fontsize=9, at=(10, 90, 1, 4))
        gscript.run_command('d.mon', stop=driver)

        # compute mean of differences of depths
        gscript.run_command('r.series', input=diff_list, output=mean_diff, method="average", overwrite=overwrite)
        gscript.run_command('r.colors', map=mean_diff, color='differences')
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(series, mean_diff+".png"), overwrite=overwrite)
        gscript.run_command('d.shade', shade=reference_relief, color=mean_diff, brighten=75)
        gscript.run_command('d.vect', map=reference_contour, display='shape')
        gscript.run_command('d.legend', raster=mean_diff, fontsize=9, at=(10, 90 ,1 ,4))
        gscript.run_command('d.mon', stop=driver)

        # compute maximum flow depth
        gscript.run_command('r.series', input=depth_list, output=max_depth, method="maximum", overwrite=overwrite)
        gscript.write_command('r.colors', map=max_depth, rules='-', stdin=depth_colors)
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(series, max_depth+".png"), overwrite=overwrite)
        gscript.run_command('d.shade', shade=reference_relief, color=max_depth, brighten=75)
        gscript.run_command('d.vect', map=reference_contour, display='shape')
        gscript.run_command('d.legend', raster=max_depth, fontsize=9, at=(10, 90, 1, 4))
        gscript.run_command('d.mon', stop=driver)

        # compute sum of flow depth
        gscript.run_command('r.series', input=depth_list, output=sum_depth, method="sum", overwrite=overwrite)
        gscript.write_command('r.colors', map=sum_depth, rules='-', stdin=depth_colors)
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(series, sum_depth+".png"), overwrite=overwrite)
        gscript.run_command('d.shade', shade=reference_relief, color=sum_depth, brighten=75)
        gscript.run_command('d.vect', map=reference_contour, display='shape')
        gscript.run_command('d.legend', raster=sum_depth, fontsize=9, at=(10, 90, 1, 4))
        gscript.run_command('d.mon', stop=driver)

        # compute mean depressions
        gscript.run_command('r.series', input=depressions_list, output=mean_depressions, method="average", overwrite=overwrite)
        gscript.write_command('r.colors', map=mean_depressions, rules='-', stdin=depressions_colors)
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(series, mean_depressions+".png"), overwrite=overwrite)
        gscript.run_command('d.shade', shade=reference_relief, color=mean_depressions, brighten=75)
        gscript.run_command('d.vect', map=reference_contour, display='shape')
        gscript.run_command('d.legend', raster=mean_depressions, fontsize=9, at=(10, 90, 1, 4))
        gscript.run_command('d.mon', stop=driver)

        # compute maximum depressions
        gscript.run_command('r.series', input=depressions_list, output=max_depressions, method="maximum", overwrite=overwrite)
        gscript.write_command('r.colors', map=max_depressions, rules='-', stdin=depressions_colors)
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(series,max_depressions+".png"), overwrite=overwrite)
        gscript.run_command('d.shade', shade=reference_relief, color=max_depressions, brighten=75)
        gscript.run_command('d.vect', map=reference_contour, display='shape')
        gscript.run_command('d.legend', raster=max_depressions, fontsize=9, at=(10, 90, 1, 4))
        gscript.run_command('d.mon', stop=driver)

        # compute sum of depressions
        gscript.run_command('r.series', input=depressions_list, output=sum_depressions, method="sum", overwrite=overwrite)
        gscript.write_command('r.colors', map=sum_depressions, rules='-', stdin=depressions_colors)
        gscript.run_command('d.mon', start=driver, width=width, height=height, output=os.path.join(series, sum_depressions+".png"), overwrite=overwrite)
        gscript.run_command('d.shade', shade=reference_relief, color=sum_depressions, brighten=75)
        gscript.run_command('d.vect', map=reference_contour, display='shape')
        gscript.run_command('d.legend', raster=sum_depressions, fontsize=9, at=(10, 90, 1, 4))
        gscript.run_command('d.mon', stop=driver)

        # extract concentrated flow
        gscript.run_command('r.mapcalc', expression='{concentrated_flow} = if({mean_depth}>=0.05,{mean_depth},null())'.format(mean_depth=mean_depth, concentrated_flow=concentrated_flow), overwrite=overwrite)
        gscript.write_command('r.colors', map=concentrated_flow, rules='-', stdin=depth_colors)
        gscript.run_command('r.random', input=concentrated_flow, npoints='100%', vector=concentrated_points, overwrite=overwrite)

        # compute distance from reference
        gscript.run_command('g.copy', vector=[reference_points+'@PERMANENT', copied_points], overwrite=overwrite)
        gscript.run_command('v.db.addcolumn', map=copied_points, columns='distance INTEGER', overwrite=overwrite)
        gscript.run_command('v.distance', from_=copied_points, to=concentrated_points, upload='dist', column='distance', output=flow_distance, separator='newline', overwrite=overwrite)
        univar_distance = gscript.parse_command('v.db.univar', map=copied_points, column='distance', flags='g', overwrite=overwrite)
        dist = float(univar_distance['sum'])
        distance.append(dist)
        print 'sum of min distance in experiment '+str(i)+': ' + str(dist)
        mean_dist = float(univar_distance['mean'])
        print 'mean of min distance in experiment '+str(i)+': ' + str(mean_dist)

        # render
        gscript.run_command('d.mon', start=driver, width=width*2, height=height*2, output=os.path.join(series,concentrated_flow+".png"), overwrite=overwrite)
        gscript.run_command('d.shade', shade=reference_relief, color=mean_diff, brighten=75)
        gscript.run_command('d.vect', map=reference_contour, display='shape')
        gscript.run_command('d.vect', map=reference_points, display='shape', color='blue')
        gscript.run_command('d.vect', map=concentrated_points, display='shape', color='red')
        gscript.run_command('d.vect', map=flow_distance, display='shape')
        gscript.run_command('d.mon', stop=driver)

        # compute number of cells with depressions
        univar = gscript.parse_command('r.univar', map=sum_depressions, separator='newline', flags='g')
        nulls = float(univar['null_cells'])
        depression_cells = total_count - nulls
        depression_percent = depression_cells/total_count*100
        cells.append(depression_percent)
        print 'percent of cells with depressions in experiment '+str(i)+': ' + str(depression_percent)

    return cells, distance


def plot_series(cells, distance):
    """plot the percent of cells with depressions and the minumum distance of mean concentrated flow points from the reference for each experiment"""

    depression_plot = os.path.join(series, "depression_cells.png")
    distance_plot = os.path.join(series, "distance.png")

    # plot depressions
    plt.figure(frameon=False, figsize=(6, 6), tight_layout=True)
    labels = ('Reference', 'Digital', 'Tangible')
    x = range(len(labels))
    y = cells
    plt.bar(x, y, color="gray", width=0.5, align='center', alpha=0.5, antialiased=True)
    plt.xticks(x, labels)
    plt.xlabel('Experiment')
    plt.ylabel('Percent cells')
    # plt.title('Percent of cells with depressions for each experiment')
    plt.savefig(depression_plot, dpi=300, transparent=True)
    plt.close()

    # plot distance
    plt.figure(frameon=False, figsize=(4, 6), tight_layout=True)
    labels = ('Digital', 'Tangible')
    x = range(len(labels))
    y = distance
    plt.bar(x, y, color="gray", width=0.5, align='center', alpha=0.5, antialiased=True)
    plt.xticks(x, labels)
    plt.xlabel('Experiment')
    plt.ylabel('Cumulative distance (ft)')
    # plt.title('Sum of minimum distance of concentrated flow from reference for each experiment')
    plt.savefig(distance_plot, dpi=300, transparent=True)
    plt.close()


if __name__ == "__main__":
    atexit.register(cleanup)
    sys.exit(main())
