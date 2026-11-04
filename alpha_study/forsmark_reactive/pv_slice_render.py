"""
pvbatch renderer: horizontal slice (z = Z0) through the fracture polygons of one state -> fracture traces seen from above,
coloured by one cell field.  One job per call keeps colour maps separate.

  /Applications/ParaView-5.13.3.app/Contents/bin/pvbatch forsmark_reactive/pv_slice_render.py jobs.json
jobs.json: list of {"vtu", "field", "range": [lo, hi], "preset", "png", "z0": 0}
"""
import json
import sys

from paraview.simple import (ColorBy, CreateView, Delete, GetColorTransferFunction, Render, SaveScreenshot, Show, Slice,
                             XMLUnstructuredGridReader)

for j in json.load(open(sys.argv[1])):
    v = CreateView("RenderView")
    v.ViewSize = [1800, 470]
    v.Background = [1, 1, 1]
    try:
        v.UseColorPaletteForBackground = 0
    except AttributeError:
        pass
    v.OrientationAxesVisibility = 0
    r = XMLUnstructuredGridReader(FileName=[j["vtu"]])
    sl = Slice(Input=r)
    sl.SliceType = "Plane"
    sl.SliceType.Origin = [0, 0, j.get("z0", 0)]
    sl.SliceType.Normal = [0, 0, 1]
    d = Show(sl, v)
    d.LineWidth = 2.2
    ColorBy(d, ("CELLS", j["field"]))
    lut = GetColorTransferFunction(j["field"])
    lut.UseLogScale = 0
    lut.ApplyPreset(j["preset"], True)
    lut.UseLogScale = 0
    lut.AutomaticRescaleRangeMode = "Never"
    lut.RescaleTransferFunction(*j["range"])
    d.SetScalarBarVisibility(v, False)
    Render(v)
    v.CameraPosition = [0, 0, 3000]
    v.CameraFocalPoint = [0, 0, 0]
    v.CameraViewUp = [0, 1, 0]
    v.CameraParallelProjection = 1
    v.CameraParallelScale = 132
    Render(v)
    SaveScreenshot(j["png"], v, ImageResolution=[1800, 470], TransparentBackground=0)
    Delete(d)
    Delete(sl)
    Delete(r)
    Delete(v)
