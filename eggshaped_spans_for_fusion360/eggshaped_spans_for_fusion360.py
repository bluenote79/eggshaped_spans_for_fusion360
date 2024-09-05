

#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math as m

# Global set of event handlers to keep them referenced for the duration of the command
handlers = []
ui = None
app = adsk.core.Application.get()
if app:
    ui  = app.userInterface

product = app.activeProduct
design = adsk.fusion.Design.cast(product)
root = design.rootComponent
sketches = root.sketches
planes = root.constructionPlanes
l_xmax = []
l_xmin = []
l_xmit = []
l_ymax = []
l_off = []
l_Plane = []

class SpanCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.firingEvent.sender
            inputs = command.commandInputs
            input1 = inputs[0];
            sel0 = input1.selection(0)
            input2 = inputs[1];
            sel1 = input2.selection(0)
            input3 = inputs[2];
            sel2 = input3.selection(0)
            input4 = inputs[3];     # number of points / 4
            input5 = inputs[4];    #plane
            sel3 = input5.selection(0)
            input6 = inputs[5]     # abstand
            input7 = inputs[6]      # number of spans
            input8 = inputs[7]     
            input9 = inputs[8]    # weitere Spanten mit offsetwert angeben

            anzahl_span = float(input7.value)

            delta_span = float(input6.value)

            if input9.value != "":
                temp = input9.value
                temp = temp.split(";")
                temp = list(map(int, temp))
                for i in range(len(temp)):
                    l_off.append(float(temp[i]/10))

            if input8 == True:
                faktor = i
                anzahl_span -= 1

            for i in range(int(anzahl_span)):
                if input8.value == True:
                    faktor = i
                else:
                    faktor = i + 1
                temp = float(faktor * delta_span)
                l_off.append(temp)
    
            if sel3.entity == root.xYConstructionPlane:
                input_orientierung = "xY"

            elif sel3.entity == root.yZConstructionPlane:
                input_orientierung = "yZ"
                
            elif sel3.entity == root.xZConstructionPlane:
                input_orientierung = "xZ"
                

            spline_o = sel0.entity
            spline_u = sel1.entity
            spline_m = sel2.entity

            entities_o = []
            entities_u = []
            entities_m = []
            entities_o.append(spline_o) # sketch curve
            entities_u.append(spline_u)
            entities_m.append(spline_m)
            entities_all = []
            entities_all.append(spline_o)
            entities_all.append(spline_u)
            entities_all.append(spline_m)
            
            def intersection_ebene(offset_z, entities_o, entities_u, entities_m, input_orientierung):

                if input_orientierung == "xY":
                    offset_z = -float(offset_z)
                    sketch3d = sketches.add(root.xYConstructionPlane)
                elif input_orientierung == "yZ":
                    offset_z = float(offset_z)
                    sketch3d = sketches.add(root.yZConstructionPlane)
                elif input_orientierung == "xZ":
                    offset_z = float(offset_z)
                    sketch3d = sketches.add(root.xZConstructionPlane)

                planeInput = planes.createInput()
                # Create three sketch points
                sketchPoints = sketch3d.sketchPoints
                positionOne = adsk.core.Point3D.create(0.0, 0.0, offset_z)
                sketchPointOne = sketchPoints.add(positionOne)
                positionTwo = adsk.core.Point3D.create(0, 10.0, offset_z)
                sketchPointTwo = sketchPoints.add(positionTwo)
                positionThree = adsk.core.Point3D.create(10.0, 10.0, offset_z)
                sketchPointThree = sketchPoints.add(positionThree)
                # Add construction plane by three points
                planeInput.setByThreePoints(sketchPointOne, sketchPointTwo, sketchPointThree)
                planes.add(planeInput)

                plane3d = planes[len(planes) - 1]
                #l_Plane.append(plane3d)
                plane3d.name="offset_3_points"

                sketch2o = sketches.add(plane3d)
                sketchEntities_o = sketch2o.intersectWithSketchPlane(entities_o)

                sketch2u = sketches.add(plane3d)
                sketchEntities_u = sketch2o.intersectWithSketchPlane(entities_u)

                sketch2o = sketches.add(plane3d)
                sketchEntities_m = sketch2o.intersectWithSketchPlane(entities_m)

                # Get the value of the property.
                pt_o = []
                pt_u = []
                pt_m = []

                for po in sketchEntities_o:
                    if po.objectType == adsk.fusion.SketchPoint.classType():
                        temp = po.worldGeometry.asArray()
                        
                        pt_o.append(temp[0])
                        pt_o.append(temp[1])
                        pt_o.append(temp[2])

                for pu in sketchEntities_u:
                    if po.objectType == adsk.fusion.SketchPoint.classType():
                        temp = pu.worldGeometry.asArray()
                      
                        pt_u.append(temp[0])
                        pt_u.append(temp[1])
                        pt_u.append(temp[2])
                
                for pm in sketchEntities_m:
                    if po.objectType == adsk.fusion.SketchPoint.classType():
                        temp = pm.worldGeometry.asArray()
                      
                        pt_m.append(temp[0])
                        pt_m.append(temp[1])
                        pt_m.append(temp[2])

                pt_o = list(map(float, pt_o))
                pt_u = list(map(float, pt_u))
                pt_m = list(map(float, pt_m))

                if input_orientierung == "yZ":
                    xmax = 1 * pt_o[2]
                    xmin = 1 * pt_u[2]
                    xmit = 1 * pt_m[2]
                    ymax = 1 * pt_m[1]

                elif input_orientierung == "xY": 
                    xmax = 1 * pt_o[1]
                    xmin = 1 * pt_u[1]
                    xmit = 1 * pt_m[1]
                    ymax = 1 * pt_m[0]
                
                elif input_orientierung == "xZ":
                    xmax = 1 * pt_o[2]
                    xmin = 1 * pt_u[2]
                    xmit = 1 * pt_m[2]
                    ymax = 1 * pt_m[0]

                else:
                    ui.messageBox("orientierung?")

                l_xmax.append(xmax)
                l_xmin.append(xmin)
                l_xmit.append(xmit)
                l_ymax.append(ymax)

                # to get the offset in the thired dimension right reference to the original plane of the sketch with the selected intersections
                ents = []
                for ent in sketchEntities_o:
                    ents.append(ent)
                for ent in sketchEntities_u:
                    ents.append(ent)
                for ent in sketchEntities_m:
                    ents.append(ent)
                    
                sketch3 = ents[0].parentSketch
                sketch3.name="Sketch3"
                Plane = sketch3.referencePlane   
                Plane = plane3d
                l_Plane.append(Plane)
                del ents
                
                letzter_sketch = len(sketches) - 1
                sketches[letzter_sketch].deleteMe()   
                sketches[letzter_sketch - 1].deleteMe()
                sketches[letzter_sketch - 2].deleteMe()
                sketches[letzter_sketch - 3].deleteMe()
                letzte_ebene = len(planes) - 1
                planes[letzte_ebene].deleteMe()

            for i in range(len(l_off)):
                intersection_ebene(l_off[i], entities_o, entities_u, entities_m, input_orientierung)


            # execute the calculation programm with the user selected values
            span = Span()
            for i in range(len(l_off)):
                span.Execute(l_Plane[i], l_xmax[i], l_xmin[i], l_xmit[i], l_ymax[i], input4.value, l_off[i], input_orientierung);

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler that reacts to when the command is destroyed. This terminates the script.
class SpanCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class Span:
    def Execute(self, Plane, xmax, xmin, xmit, ymax, anzahl_punkte_4, offset_z, input_orientierung):
        x_coord = [] # list of coordinates for spline
        y_coord = [] # list of coordinates for spline
  
        # multiply the input by 4 to get the number of points to be created
        anzahl_punkte = anzahl_punkte_4 * 4
        global sketches
        global planes

        try:
            root = design.rootComponent
        except RuntimeError:
            ui.messageBox('You should select origin plane or construction plane.', 'Error')
            return

        points = adsk.core.ObjectCollection.create()

        # calculate parameters a, b, d from input coordinates
        a = 0.5 * abs(xmax - xmin)
        b = abs(ymax)

        # moved position off the circle midpoint M1 from (0, 0) bei (x_m1, 0)
        x_m1 = xmax - a
        d = -(xmit - x_m1)

        # calculation of the eggshape around the origin → will be moved later
        xwerte = [] # lists of the calculated values
        ywerte = []
        xwerte_offset = []

        # fritz huegel schaeffer calculation depending on the angle
        punkt = 0
        while punkt < anzahl_punkte + 1:  # first and last point identical for a closed spline
            kreisteiler = 360 / anzahl_punkte
            t = punkt * kreisteiler  # kreisteiler (example: divider of the circle by 5° angles results in 72 points)
            if t == 90:   # avoid errors from rounding at the points the spline cuts the splines from the fusselage shape. Use the original inputs.
                y2 = ymax
            elif t == 270:
                y2 = -ymax
            else:
                y2 = b * m.sin(m.radians(t))
            ywerte.append(y2)
            x1 = (m.sqrt((a ** 2) - (d ** 2) * ((m.sin(m.radians(t))) ** 2)) + d * m.cos(m.radians(t))) * m.cos(
                m.radians(t))
            xwerte.append(x1)
            punkt += 1

        # moving the x-values by comparing the calculated top around the origin with the top from the input data
        offset = xmax - xwerte[0]

        for w in range(len(xwerte)):
            x_new = xwerte[w] + offset
            xwerte_offset.append(x_new)

        k = len(xwerte) - 1
        l = int(0.5*k)

        xwerte_offset[0] = xmax
        xwerte_offset[k] = xmax
        xwerte_offset[l] = xmin

        for h in range(len(xwerte)):
            x_coord.append(ywerte[h])
            y_coord.append(xwerte_offset[h])

        if input_orientierung == "xY":
                for i in range(len(x_coord)):
                    point = adsk.core.Point3D.create(ywerte[i], xwerte_offset[i], -offset_z)         
                    points.add(point)
                    
                sketch3 = root.sketches.add(root.xYConstructionPlane)
                sketch3.sketchCurves.sketchFittedSplines.add(points)

        if input_orientierung == "yZ":
                for i in range(len(x_coord)):
                    point = adsk.core.Point3D.create(xwerte_offset[i], ywerte[i], offset_z)           
                    points.add(point)
                
                sketch3 = root.sketches.add(root.yZConstructionPlane)
                sketch3.sketchCurves.sketchFittedSplines.add(points)
              
        if input_orientierung == "xZ":
                for i in range(len(x_coord)):
                    point = adsk.core.Point3D.create(ywerte[i], -xwerte_offset[i], offset_z)         
                    points.add(point)
                
                sketch3 = root.sketches.add(root.xZConstructionPlane)
                sketch3.sketchCurves.sketchFittedSplines.add(points)

        name = "span_at_" + str(offset_z * 10) + " mm"

        sketch3.name=name

# Event handler that reacts when the command definitio is executed which
# results in the command being created and this event being fired.
class SpanCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:

            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            onExecute = SpanCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute) 

            # Connect to the command destroyed event.
            onDestroy = SpanCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            handlers.append(onDestroy)

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            # Create the inputs       

            i1 = inputs.addSelectionInput("SketchCurve", "Kurve oben", "Please select curve")
            i1.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
            i1.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i2 = inputs.addSelectionInput("SketchCurve", "Kurve unten", "Please select curve")
            i2.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
            i2.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i3 = inputs.addSelectionInput("SketchCurve", "Kurve mitte", "Please select curve")
            i3.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
            i3.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i4 = inputs.addValueInput('anzahl_punkte_4', '1/4 Punkte Eiform', '', adsk.core.ValueInput.createByReal(9))
            i5 = inputs.addSelectionInput("ConstructionPlane", "Parallele Ursprungsebene", "Select Plane")
            i5.addSelectionFilter(adsk.core.SelectionCommandInput.ConstructionPlanes)
            i5.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i6 = inputs.addValueInput("ValueInput", "Abstand Spanten", "mm", adsk.core.ValueInput.createByReal(0.5))
            i7 = inputs.addValueInput('anzahl_spans', 'Anzahl Spanten gleichen Abstands', '', adsk.core.ValueInput.createByReal(0))
            i8 = inputs.addBoolValueInput('checkbox', 'Erster Spant bei 0.0', True, '', False)
            i9 = inputs.addStringValueInput("Spanten semikolongetrennt", "Offsetwerte, semikolongetrennt in mm", "")

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        title = 'Select Construction Plane'

        if not design:
            ui.messageBox('No active Fusion design', title)
            return

        commandDefinitions = ui.commandDefinitions
        
        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = commandDefinitions.itemById("SpanCMDDef")
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition("SpanCMDDef",
                                                            "Span Parameters", "Creates span spline on selected construction plane")
        
        # Connect to the command created event.
        onCommandCreated = SpanCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
          
        # Execute the command definition.
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

