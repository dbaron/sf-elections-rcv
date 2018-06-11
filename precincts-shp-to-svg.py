#!/usr/bin/python

import math
import os
import shapefile
import zipfile

BASEDIR = os.path.dirname(os.path.realpath(__file__))
# Download this from:
# https://sfelections.sfgov.org/maps
# https://sfelections.sfgov.org/sites/default/files/Documents/Maps/2017lines.zip
SHAPEFILE_ZIP = os.path.join(BASEDIR, "2017lines.zip")

zf = zipfile.ZipFile(SHAPEFILE_ZIP, "r")
shp = zf.open("SF_DOE_Precincts_2017.shp")
shx = zf.open("SF_DOE_Precincts_2017.shx")
dbf = zf.open("SF_DOE_Precincts_2017.dbf")
sf = shapefile.Reader(shp=shp, dbf=dbf, shx=shx)

precinct_field_index = None
for i, field in enumerate(sf.fields[1:]): # skip deletion flag field at start
    if field[0] == "PREC_2017":
        if precinct_field_index != None:
            raise StandardError("found precinct field twice")
        precinct_field_index = i
if precinct_field_index == None:
    raise StandardError("could not find precinct field")

xmin, ymin, xmax, ymax = sf.bbox

print "<svg viewBox=\"0 0 {} {}\" xmlns=\"http://www.w3.org/2000/svg\">".format(math.ceil(xmax-xmin), math.ceil(ymax-ymin))
for shape, record in zip(sf.shapes(), sf.records()):
    if shape.shapeType != shapefile.POLYGON:
        raise StandardError("unexpected shape type " + str(shape.shapeType))
    precinct_num = record[precinct_field_index]
    if precinct_num == "":
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
    print "<path id=\"p{0}\" d=\"{1}\"/>".format(precinct_num, path)

print "</svg>"
