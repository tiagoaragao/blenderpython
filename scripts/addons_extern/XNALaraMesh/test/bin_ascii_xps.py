# -*- coding: utf-8 -*-
import os
import io
import struct
from . import xps_types
from . import read_ascii_xps
from . import read_bin_xps
from . import write_ascii_xps
from . import write_bin_xps

if __name__ == "__main__":
    import imp
    imp.reload(read_ascii_xps)
    imp.reload(read_bin_xps)
    imp.reload(write_ascii_xps)
    imp.reload(write_bin_xps)
    imp.reload(xps_types)

    #readfilename = r'G:\3DModeling\XNALara\XNALara_XPS\data\TESTING\Alice Returns - Mods\Alice 001 Fetish Cat\read.mesh'
    readfilename = r'G:\3DModeling\XNALara\XNALara_XPS\data\TESTING\Alice Returns - Mods\Alice 001 Fetish Cat\write.mesh'

    #writefilename = r'G:\3DModeling\XNALara\XNALara_XPS\data\TESTING\Alice Returns - Mods\Alice 001 Fetish Cat\write1.mesh.ascii'
    writefilename = r'G:\3DModeling\XNALara\XNALara_XPS\data\TESTING\Alice Returns - Mods\Alice 001 Fetish Cat\write2.mesh.ascii'

    print('----READ START----')
    xpsData = read_bin_xps.readXpsModel(readfilename)
    print('----READ END----')
    print('----WRITE START----')
    write_ascii_xps.writeXpsModel(writefilename, xpsData)
    print('----WRITlE END----')
