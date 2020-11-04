#!/usr/bin/env python

import math
import os
import shapefile
import zipfile

def shapefile_to_svg(sf, output_file, precinct_field):
    output = open(output_file, "w")
    precinct_field_index = None
    for i, field in enumerate(sf.fields[1:]): # skip deletion flag field at start
        if field[0] == precinct_field:
            if precinct_field_index != None:
                raise StandardError("found precinct field twice")
            precinct_field_index = i
    if precinct_field_index == None:
        raise StandardError("could not find precinct field")

    # Manually compute the bounds, because the 2002 precincts file has a
    # NONE precinct including all the water areas in the city that we
    # don't want to count.
    xmin = None
    ymin = None
    xmax = None
    ymax = None
    for shape, record in zip(sf.shapes(), sf.records()):
        if shape.shapeType != shapefile.POLYGON:
            raise StandardError("unexpected shape type " + str(shape.shapeType))
        precinct_num = record[precinct_field_index]
        if precinct_num == "" or precinct_num == "NONE":
            continue
        for point in shape.points:
            if xmin is None:
                xmin = point[0]
                ymin = point[1]
                xmax = point[0]
                ymax = point[1]
            else:
                xmin = min(xmin, point[0])
                ymin = min(ymin, point[1])
                xmax = max(xmax, point[0])
                ymax = max(ymax, point[1])

    output.write("<svg viewBox=\"0 0 {} {}\" xmlns=\"http://www.w3.org/2000/svg\">\n".format(math.ceil(xmax-xmin), math.ceil(ymax-ymin)))
    for shape, record in zip(sf.shapes(), sf.records()):
        if shape.shapeType != shapefile.POLYGON:
            raise StandardError("unexpected shape type " + str(shape.shapeType))
        precinct_num = record[precinct_field_index]
        if precinct_num == "" or precinct_num == "NONE":
            continue
        parts = shape.parts
        next_part_index = 0
        path = ""
        for i, point in enumerate(shape.points):
            command = "L"
            if parts[next_part_index] == i:
                # This is the start of a new part
                command = "M"
                next_part_index = next_part_index + 1
                if next_part_index == len(parts):
                    next_part_index = 0 # we won't find it again
            path = path + command + '{0:.0f},{1:.0f} '.format(point[0] - xmin, ymax - point[1])
        path = path[0:-1] # omit last space
        output.write("<path id=\"p{0}\" d=\"{1}\"/>\n".format(precinct_num, path))

    output.write("</svg>\n")
    output.close()

BASEDIR = os.path.dirname(os.path.realpath(__file__))

# Download this from:
# https://data.sfgov.org/City-Management-and-Ethics/Election-Precincts-Historical-Defined-2002/j3dz-virx/data
# https://data.sfgov.org/api/geospatial/j3dz-virx?method=export&format=Original
zf = zipfile.ZipFile(os.path.join(BASEDIR, "Elect_Precincts_2002.zip"), "r")
sf = shapefile.Reader(shp=zf.open("Elect_Precincts_2002.shp"),
                      dbf=zf.open("Elect_Precincts_2002.dbf"),
                      shx=zf.open("Elect_Precincts_2002.shx"))
shapefile_to_svg(sf, os.path.join(BASEDIR, "precincts2002.svg"), "precname");

# Download this from:
# https://sfgov.org/elections/sites/default/files/2012lines.zip
# found via:
# http://web.archive.org/web/20160708194111/https://sfgov.org/elections/data-results-maps-and-archives
# http://web.archive.org/web/20160708194111/https://sfgov.org/elections/sites/default/files/2012lines.zip
zf = zipfile.ZipFile(os.path.join(BASEDIR, "2012lines.zip"), "r")
sf = shapefile.Reader(shp=zf.open("2012lines/SF_DOE_Precincts_20120702.shp"),
                      dbf=zf.open("2012lines/SF_DOE_Precincts_20120702.dbf"),
                      shx=zf.open("2012lines/SF_DOE_Precincts_20120702.shx"))
shapefile_to_svg(sf, os.path.join(BASEDIR, "precincts2012.svg"), "PREC_2012");

# Download this from:
# https://sfelections.sfgov.org/maps
# https://sfelections.sfgov.org/sites/default/files/Documents/Maps/2017lines.zip
zf = zipfile.ZipFile(os.path.join(BASEDIR, "2017lines.zip"), "r")
sf = shapefile.Reader(shp=zf.open("SF_DOE_Precincts_2017.shp"),
                      dbf=zf.open("SF_DOE_Precincts_2017.dbf"),
                      shx=zf.open("SF_DOE_Precincts_2017.shx"))
shapefile_to_svg(sf, os.path.join(BASEDIR, "precincts2017.svg"), "PREC_2017");

# Download this from:
# https://sfelections.sfgov.org/maps
# https://sfelections.sfgov.org/sites/default/files/Documents/Maps/2019lines_20190628.zip
zf = zipfile.ZipFile(os.path.join(BASEDIR, "2019lines_20190628.zip"), "r")
sf = shapefile.Reader(shp=zf.open("SF_DOE_PREC_2019.shp"),
                      dbf=zf.open("SF_DOE_PREC_2019.dbf"),
                      shx=zf.open("SF_DOE_PREC_2019.shx"))
shapefile_to_svg(sf, os.path.join(BASEDIR, "precincts2019.svg"), "PREC_2019");

