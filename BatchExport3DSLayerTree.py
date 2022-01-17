"""Exports one Rhino .3DM file per layer, export folder is same as current
folder if file has been saved; otherwise, choice of file name/location.
Each parent layer will produce an individual file with all the sublayers and
objects, scripts crawl down the tree to export all parent layer with all of their sublayers.

parent
- subparent1
- - child1
- - child2
- subparent1
- - child 1
- - child 2

will produce:
parent.3ds
parent_subparent1.3ds
parent_subparent1_child1.3ds
parent_subparent1_child2.3ds
parent_subparent2.3ds
parent_subparent2_child1.3ds
parent_subparent2_child2.3ds

Script by Luca Carcano (https://github.com/lucarc) based on Mitch Heynick 21.05.20"""

import rhinoscriptsyntax as rs
import scriptcontext as sc
import os
import re


def SelObjsOnLayerAndSublayers(layer):
    #recursive function
    #select objects on layer
    rs.ObjectsByLayer(layer,True)
    children = rs.LayerChildren(layer)
    if children:
        for child in children:
            SelObjsOnLayerAndSublayers(child)
            objs=rs.ObjectsByLayer(child,True)

def BatchExport3DMByParentLayer():
    doc_name=sc.doc.Name
    ft="3ds"
    filt = "{} Files (*.{})|*.{}||".format(ft,ft.lower(),ft.lower())
    if not doc_name:
        #document hasn't been saved
        msg="Main file name/folder for {} export?".format(ft)
        filename=rs.SaveFileName(msg, filt)
        #SaveFileName returns the complete path plus file name
        if filename==None: return
    else:
        #document has been saved, get path
        msg="Folder for {} export? (Enter to save in current folder)".format(ft)
        folder = rs.BrowseForFolder(rs.WorkingFolder(), msg)
        if not folder: return
        filename=os.path.join(folder,doc_name)

    #start the export sequence
    rs.EnableRedraw(False)

    #Find all parent layers
    parent_layers=[]
    all_layers = rs.LayerNames()
    for layer in all_layers:
        if not rs.ParentLayer(layer):
            #layer is top level
            parent_layers.append(layer)

    layer_dict = {}

    for layer in parent_layers:
        sub_layers = rs.LayerChildren(layer)
        layer_dict[layer] = re.sub("::","_",layer)
        for sub_layer in sub_layers:
            layer_dict[sub_layer] = re.sub("::","_",sub_layer)




    for k,v in layer_dict.items():
        if rs.IsLayerSelectable(k):
            SelObjsOnLayerAndSublayers(k)
            e_file_name = '"{}.{}" '.format(v,ft.lower())
            if rs.SelectedObjects():
                #runs the export using the file name/path
                rs.Command("-_Export "+e_file_name+" _Enter", False)
            rs.UnselectAllObjects()

    rs.EnableRedraw(True)

BatchExport3DMByParentLayer()
