import argparse
import pdb
import iris
import matplotlib.pyplot as plt
import iris.plot as iplt
import iris.coord_categorisation
import cmocean
import numpy
import calendar

import warnings
warnings.filterwarnings(action='ignore')


def read_data(fname, month):
    """Read an input data file"""
    
    cube = iris.load_cube(fname, 'precipitation_flux')
    
    iris.coord_categorisation.add_month(cube, 'time')
    cube = cube.extract(iris.Constraint(month=month))
    
    cube.attributes['title'] = '%s precipitation climatology (%s)' %(cube.attributes['model_id'], month)
    return cube


def convert_pr_units(cube):
    """Convert kg m-2 s-1 to mm day-1"""
    
    cube.data = cube.data * 86400
    cube.units = 'mm/day'
    
    return cube


def plot_data(cube, gridlines=False, ticks=None):
    """Plot the data."""
        
    fig = plt.figure(figsize=[12,5])    
    iplt.contourf(cube, cmap=cmocean.cm.haline_r, 
                  levels=numpy.arange(0, 10),
                  extend='max')

    plt.gca().coastlines()
    if gridlines:
        plt.gca().gridlines()
    cbar = plt.colorbar()
    cbar.set_label(str(cube.units))
    #cbar.set_tick(ticks)
    #if (len(ticks)>2):
    #    print('Got some ticks {0}'.format(ticks))
    
    plt.title(cube.attributes['title'])



def apply_mask(clim, mask):
    print("Got Mask")
    print(mask)
    #pdb.set_trace()
    sftlf_cube = iris.load_cube(mask[0], 'land_area_fraction')
    if (mask[1] == 'land'):
        chosen_mask = numpy.where(sftlf_cube.data < 50, True, False)
    else :
        chosen_mask = numpy.where(sftlf_cube.data > 50, True, False)
    clim.data = numpy.ma.asarray(clim.data)
    clim.data.mask = chosen_mask



def main(inargs):
    """Run the program."""
    #print("ticks is {0}".format(inargs.ticks))

    cube = read_data(inargs.infile, inargs.month)


    cube = convert_pr_units(cube)

    assert (cube.data.min() >= 0) , "nonphysical negative rainfall"

    assert (cube.data.max() < 1000) , "unlikely there's more than 1m per day"

    clim = cube.collapsed('time', iris.analysis.MEAN)
    if (inargs.mask):
        apply_mask(clim, inargs.mask)
    plot_data(clim, gridlines = inargs.gridlines, ticks = inargs.ticks)
    plt.savefig(inargs.outfile)


if __name__ == '__main__':
    description='Plot the precipitation climatology.'
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("month", type=str, help="Month to plot", choices=calendar.month_abbr[1:13])
    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("--gridlines", help="add gridlines",
                    action="store_true")
    parser.add_argument('--ticks', nargs='*')

    parser.add_argument("--mask", type=str, nargs=2,
                    metavar=('SFTLF_FILE', 'REALM'), default=None,
                    help='Apply a land or ocean mask (specify the realm to mask)')



    args = parser.parse_args()
    
    main(args)
