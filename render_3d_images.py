#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@brief: 3D rendering for the tangible water flow experiment

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.

@author: Brendan Harmon (brendanharmon@gmail.com)
"""

import os
import grass.script as gscript

# temporary region
gscript.use_temp_region()

# set environment
env = gscript.gisenv()

overwrite = True
env['GRASS_OVERWRITE'] = overwrite
env['GRASS_VERBOSE'] = False
env['GRASS_MESSAGE_FORMAT'] = 'standard'
gisdbase = env['GISDBASE']
location = env['LOCATION_NAME']
mapset = env['MAPSET']

# set path
render_3d = os.path.join(gisdbase, location, 'render_3d')

# set variables
res = 3 # resolution of the region

# 3d variables
color_3d = "192:192:192"
res_3d = 1
height_3d = 2000
perspective = 25
light_position = (0.68, -0.68, 0.95)
fringe = "ne"
fringe_elevation = 250
format_3d = "tif"
size_3d = (1000, 1000)
vpoint_size = 4
vpoint_marker = "x"
vpoint_color = "red"
vline_width = 2
vline_color = "black"
# arrow_position = (100, 100)
# arrow_size = 100

# 3d color rules with null values and default set to light gray
dem_colors_3d = """\
0% 0:191:191
20% 0:255:0
40% 255:255:0
60% 255:127:0
80% 191:127:63
100% 200:200:200
nv 192:192:192
default 192:192:192
"""
slope_colors_3d = '0 192:192:192\n2 255:255:0\n5 0:255:0\n10 0:255:255\n15 0:0:255\n30 255:0:255\n50 255:0:0\n90 0:0:0\nnv 192:192:192\ndefault 192:192:192'
depressions_colors_3d = '0% aqua\n100% blue\nnv 192:192:192\ndefault 192:192:192'
depth_colors_3d = '0 192:192:192\n0.001 255:255:0\n0.05 0:255:255\n0.1 0:127:255\n0.5 0:0:255\n100% 0:0:0\nnv 192:192:192\ndefault 192:192:192'
forms_colors_3d = '0 192:192:192\n1 220:220:220\n2 56:0:0\n3 200:0:0\n4 255:80:20\n5 250:210:60\n6 255:255:60\n7 180:230:20\n8 60:250:150\n9 0:0:255\n10 0:0:56\n11 255:0:255\nnv 192:192:192\ndefault 192:192:192'
dem_difference_colors_3d = '-40 blue\n0 192:192:192\n40 red\nnv 192:192:192\ndefault 192:192:192'
flow_difference_colors_3d = '0% blue\n0 192:192:192\n100% red\nnv 192:192:192\ndefault 192:192:192'
slope_difference_colors_3d = '-30 blue\n0 192:192:192\n30 red\nnv 192:192:192\ndefault 192:192:192'
forms_difference_colors_3d = '-10 blue\n0 192:192:192\n10 red\nnv 192:192:192\ndefault 192:192:192'
grey = '0% 192:192:192\n100% 192:192:192\nnv 192:192:192\ndefault 192:192:192'
# stdev_dem_difference_colors_3d = '250 blue\n0 white\n350 red\nnv 192:192:192\ndefault 192:192:192'
# stdev_dem_regression_difference_colors_3d = '-11 blue\n0 white\n11 red\nnv 192:192:192\ndefault 192:192:192'
# stdev_slope_difference_colors_3d = '-40 blue\n0 white\n40 red\nnv 192:192:192\ndefault 192:192:192'
url="http://soliton.vm.bytemark.co.uk/pub/cpt-city/mpl/viridis.cpt" # http://soliton.vm.bytemark.co.uk/pub/cpt-city/mpl/inferno.cpt


# variables
region_1 = "mean_dem_1"
region_2 = "mean_dem_2"
mean_dem_1 = "mean_dem_1"
mean_dem_2 = "mean_dem_2"
mean_depth_1 = "mean_depth_1"
mean_depth_2 = "mean_depth_2"
mean_diff_1 = "mean_diff_1"
mean_diff_2 = "mean_diff_2"
mean_diff_bright_1 = "mean_diff_bright_1"
mean_diff_bright_2 = "mean_diff_bright_2"
mean_depressions_1 = "mean_depressions_1"
mean_depressions_2 = "mean_depressions_2"
concentrated_points_1 = "concentrated_points_1"
concentrated_points_2 = "concentrated_points_2"
flow_distance_1 = "flow_distance_1"
flow_distance_2 = "flow_distance_2"

# set region
gscript.run_command('g.region',
                    rast="dem",
                    res=res)

# 3D render elevation
gscript.write_command('r.colors',
    map="dem",
    rules='-',
    stdin=dem_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map="dem",
    color_map="dem",
    #color=color_3d,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, "dem"),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render depth
gscript.write_command('r.colors',
    map="depth",
    rules='-',
    stdin=depth_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map="dem",
    color_map="depth",
    #color=color_3d,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, "depth"),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render depressions
gscript.write_command('r.colors',
    map="depressions",
    rules='-',
    stdin=depressions_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map="dem",
    color_map="depressions",
    #color=color_3d,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, "depressions"),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render mean flow difference
gscript.write_command('r.colors',
    map="diff",
    rules='-',
    stdin=grey)
gscript.run_command('m.nviz.image',
    elevation_map="dem",
    color_map="diff",
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, "diff"),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# set region
gscript.run_command('g.region',
                    rast=region_1,
                    res=res)

# 3D render elevation
gscript.write_command('r.colors',
    map=mean_dem_1,
    rules='-',
    stdin=dem_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_1,
    color_map=mean_dem_1,
    #color=color_3d,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, mean_dem_1),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render depth
gscript.write_command('r.colors',
    map=mean_depth_1,
    rules='-',
    stdin=depth_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_1,
    color_map=mean_depth_1,
    #color=color_3d,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, mean_depth_1),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render depressions
gscript.write_command('r.colors',
    map=mean_depressions_1,
    rules='-',
    stdin=depressions_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_1,
    color_map=mean_depressions_1,
    #color=color_3d,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, mean_depressions_1),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render mean flow difference
gscript.write_command('r.colors',
    map=mean_diff_1,
    rules='-',
    stdin=flow_difference_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_1,
    color_map=mean_diff_1,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, mean_diff_1),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render mean flow distance
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_1,
    color_map=mean_diff_1,
    vpoint=concentrated_points_1,
    vpoint_size=vpoint_size,
    vpoint_marker=vpoint_marker,
    vpoint_color=vpoint_color,
    vline=flow_distance_1,
    vline_width=vline_width,
    vline_color=vline_color,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, flow_distance_1),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# set region
gscript.run_command('g.region',
                    rast=region_2,
                    res=res)

# 3D render elevation
gscript.write_command('r.colors',
    map=mean_dem_2,
    rules='-',
    stdin=dem_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_2,
    color_map=mean_dem_2,
    #color=color_3d,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, mean_dem_2),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render depth
gscript.write_command('r.colors',
    map=mean_depth_2,
    rules='-',
    stdin=depth_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_2,
    color_map=mean_depth_2,
    #color=color_3d,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, mean_depth_2),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render depressions
gscript.write_command('r.colors',
    map=mean_depressions_2,
    rules='-',
    stdin=depressions_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_2,
    color_map=mean_depressions_2,
    #color=color_3d,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, mean_depressions_2),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render mean flow difference
gscript.write_command('r.colors',
    map=mean_diff_2,
    rules='-',
    stdin=flow_difference_colors_3d)
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_2,
    color_map=mean_diff_2,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, mean_diff_2),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )

# 3D render mean flow distance
gscript.run_command('m.nviz.image',
    elevation_map=mean_dem_2,
    color_map=mean_diff_2,
    vpoint=concentrated_points_2,
    vpoint_size=vpoint_size,
    vpoint_marker=vpoint_marker,
    vpoint_color=vpoint_color,
    vline=flow_distance_2,
    vline_width=vline_width,
    vline_color=vline_color,
    resolution_fine=res_3d,
    height=height_3d,
    perspective=perspective,
    light_position=light_position,
    fringe=fringe,
    fringe_color=color_3d,
    fringe_elevation=fringe_elevation,
    #arrow_position=arrow_position,
    #arrow_size=arrow_size,
    output=os.path.join(render_3d, flow_distance_2),
    format=format_3d,
    size=size_3d,
    errors='ignore'
    )
