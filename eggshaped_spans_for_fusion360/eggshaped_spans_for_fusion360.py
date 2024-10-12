import adsk.core, adsk.fusion, adsk.cam, traceback
import math as m

"""
This skript adds spans calculated by Hügelschäffer equation to Fusion 360 fitting 3 splines ready for lofting.
"""

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

INPUT_ORIENTIERUNG = ""
SE01_SELECTION_INPUT_ID = "Spline oben"
SE02_SELECTION_INPUT_ID = "Spline unten"
SE03_SELECTION_INPUT_ID = "Spline mitte"
IN01_VALUE_INPUT_ID = "Anzahl Punkte"
SE04_SELECTION_INPUT_ID = "Parallele Ursprungsebene"
IN02_VALUE_INPUT_ID = "Abstand Spanten"
IN03_VALUE_INPUT_ID ='Anzahl Spanten gleichen Abstands'
CH01_BOOLEAN_INPUT_ID = 'checkbox'
IN04_STRING_INPUT_ID = "Spanten semikolngetrennt"

class SpanCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.firingEvent.sender
            inputs = command.commandInputs
            input1 = inputs[0]
            sel0 = input1.selection(0)
            input2 = inputs[1]
            sel1 = input2.selection(0)
            input3 = inputs[2]
            sel2 = input3.selection(0)
            input4 = inputs[3]     # number of points / 4
            input5 = inputs[4]   #plane
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
                INPUT_ORIENTIERUNG = "xY"

            elif sel3.entity == root.yZConstructionPlane:
                INPUT_ORIENTIERUNG = "yZ"
                
            elif sel3.entity == root.xZConstructionPlane:
                INPUT_ORIENTIERUNG = "xZ"
                

            spline_o = sel0.entity
            spline_u = sel1.entity
            spline_m = sel2.entity

            entities_o = []
            entities_u = []
            entities_m = []

            entities_o.append(spline_o) # sketch curve
            entities_u.append(spline_u)
            entities_m.append(spline_m)
            
            entities_all = entities_o + entities_u + entities_m                ################## del?

            def intersection_ebene(offset_z, entities_o, entities_u, entities_m, INPUT_ORIENTIERUNG):

                if INPUT_ORIENTIERUNG == "xY":
                    offset_z = -float(offset_z)
                    sketch3d = sketches.add(root.xYConstructionPlane)
                elif INPUT_ORIENTIERUNG == "yZ":
                    offset_z = float(offset_z)
                    sketch3d = sketches.add(root.yZConstructionPlane)
                elif INPUT_ORIENTIERUNG == "xZ":
                    offset_z = float(offset_z)
                    sketch3d = sketches.add(root.xZConstructionPlane)

                # create offset plane
                planeInput = planes.createInput()
                valueInput = adsk.core.ValueInput.createByReal(offset_z)
                planeInput.setByOffset(sel3.entity, valueInput)
                planes.add(planeInput)

                plane3d = planes[len(planes) - 1]
                plane3d.name="offsetPlane"

                sketch2o = sketches.add(plane3d)
                sketchEntities_o = sketch2o.intersectWithSketchPlane(entities_o)

                sketch2u = sketches.add(plane3d)
                sketchEntities_u = sketch2u.intersectWithSketchPlane(entities_u)

                sketch2m = sketches.add(plane3d)
                sketchEntities_m = sketch2m.intersectWithSketchPlane(entities_m)

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

                if INPUT_ORIENTIERUNG == "yZ":
                    xmax = 1 * pt_o[2]
                    xmin = 1 * pt_u[2]
                    xmit = 1 * pt_m[2]
                    ymax = 1 * pt_m[1]

                elif INPUT_ORIENTIERUNG == "xY": 
                    xmax = 1 * pt_o[1]
                    xmin = 1 * pt_u[1]
                    xmit = 1 * pt_m[1]
                    ymax = 1 * pt_m[0]
                
                elif INPUT_ORIENTIERUNG == "xZ":
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
                intersection_ebene(l_off[i], entities_o, entities_u, entities_m, INPUT_ORIENTIERUNG)


            # execute the calculation programm with the user selected values
            span = Span()
            for i in range(len(l_off)):
                span.Execute(l_xmax[i], l_xmin[i], l_xmit[i], l_ymax[i], 4 * input4.value, l_off[i], INPUT_ORIENTIERUNG)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


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


class SpanCalc:
    def __init__(self, xmax, xmin, xmit, ymax, anzahl_punkte):

        self.xmax = xmax
        self.xmin = xmin
        self.xmit = xmit
        self.ymax = ymax
        self.anzahl_punkte = anzahl_punkte
        self.xwerte, self.ywerte = self.calc_egg(anzahl_punkte, ymax, xmit, xmin, xmax)
        self.xwerte_offset = self.move_x(xmax, xmin, self.xwerte)
          
    
    # calculation of the eggshape around the origin → will be moved later
    @classmethod
    def calc_egg(cls, anzahl_punkte, ymax, xmit, xmin, xmax):

        a = 0.5 * abs(xmax - xmin)
        b = abs(ymax)
        d = xmax - xmit - 0.5 * abs(xmax - xmin)
        xwerte = []  # lists of the calculated values
        ywerte = []

        # fritz huegel schaeffer calculation depending on the angle
        punkt = 0
        while punkt < anzahl_punkte + 1:  # first and last point identical for a closed spline
            kreisteiler = 360 / anzahl_punkte
            t = punkt * kreisteiler  # kreisteiler (example: divider of the circle by 5° angles results in 72 points)
            if t == 90:  # avoid errors from rounding at the points the spline cuts the splines from the fusselage
                # shape. Use the original inputs.
                y = ymax
            elif t == 270:
                y = -ymax
            else:
                y = b * m.sin(m.radians(t))
            ywerte.append(y)
            x = (m.sqrt((a ** 2) - (d ** 2) * ((m.sin(m.radians(t))) ** 2)) + d * m.cos(m.radians(t))) * m.cos(m.radians(t))
            xwerte.append(x)
            punkt += 1


        return xwerte, ywerte

    # moving the x-values by comparing the calculated top around the origin with the top from the input data

    @classmethod
    def move_x(cls, xmax, xmin, xwerte):

        xwerte_offset = []

        offset = xmax - xwerte[0]

        for w in range(len(xwerte)):
            x_new = xwerte[w] + offset
            xwerte_offset.append(x_new)

        xwerte_offset[0] = xmax
        xwerte_offset[len(xwerte) - 1] = xmax
        xwerte_offset[int(0.5 * (len(xwerte)-1))] = xmin

        return xwerte_offset
    
    def export(self):
        return self.xwerte_offset, self.ywerte

             
class Span:
    def Execute(self, xmax, xmin, xmit, ymax, anzahl_punkte, offset_z, INPUT_ORIENTIERUNG):
  
        try:
            root = design.rootComponent
        except RuntimeError:
            ui.messageBox('You should select origin plane or construction plane.', 'Error')
            return

        points = adsk.core.ObjectCollection.create()

        span_obj = SpanCalc(xmax, xmin, xmit, ymax, anzahl_punkte)

        xwerte_offset, ywerte = SpanCalc.export(span_obj)

        if INPUT_ORIENTIERUNG == "xY":
                x_coord = [ywerte[i] for i in range(len(ywerte))]
                y_coord = [xwerte_offset[i] for i in range(len(xwerte_offset))]
                z_coord = [-1 * offset_z for i in range(len(ywerte))]
                c_plane = root.xYConstructionPlane

        elif INPUT_ORIENTIERUNG == "yZ":
                x_coord = [xwerte_offset[i] for i in range(len(xwerte_offset))]
                y_coord = [ywerte[i] for i in range(len(ywerte))]
                z_coord = [offset_z for i in range(len(ywerte))]
                c_plane = root.yZConstructionPlane

        elif INPUT_ORIENTIERUNG == "xZ":
                x_coord = [ywerte[i] for i in range(len(ywerte))]
                y_coord = [-1 * xwerte_offset[i] for i in range(len(xwerte_offset))]
                z_coord = [offset_z for i in range(len(ywerte))]
                c_plane = root.xZConstructionPlane

        for i in range(len(x_coord)):
            point = adsk.core.Point3D.create(x_coord[i], y_coord[i], z_coord[i])         
            points.add(point)
                    
        sketchSpan = root.sketches.add(c_plane)
        sketchSpan.sketchCurves.sketchFittedSplines.add(points)
        sketchSpan.name = "span_at_" + str(z_coord * 10) + " mm"


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

            i1 = inputs.addSelectionInput(SE01_SELECTION_INPUT_ID, SE01_SELECTION_INPUT_ID, "Select curve")
            i1.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
            i1.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i2 = inputs.addSelectionInput(SE02_SELECTION_INPUT_ID, SE02_SELECTION_INPUT_ID, "Select curve")
            i2.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
            i2.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i3 = inputs.addSelectionInput(SE03_SELECTION_INPUT_ID, SE03_SELECTION_INPUT_ID, "Select curve")
            i3.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
            i3.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i4 = inputs.addValueInput(IN01_VALUE_INPUT_ID, '1/4 Punkte Eiform', '', adsk.core.ValueInput.createByReal(9))
            i5 = inputs.addSelectionInput(SE04_SELECTION_INPUT_ID, SE04_SELECTION_INPUT_ID, "Select Plane")
            i5.addSelectionFilter(adsk.core.SelectionCommandInput.ConstructionPlanes)
            i5.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i6 = inputs.addValueInput(IN02_VALUE_INPUT_ID, IN01_VALUE_INPUT_ID, "mm", adsk.core.ValueInput.createByReal(0.5))
            i7 = inputs.addValueInput(IN03_VALUE_INPUT_ID, IN03_VALUE_INPUT_ID, '', adsk.core.ValueInput.createByReal(0))
            i8 = inputs.addBoolValueInput(CH01_BOOLEAN_INPUT_ID, "Erster Spant bei 0.0", True, '', False)
            i9 = inputs.addStringValueInput(IN04_STRING_INPUT_ID, 'Offsetwerte, semikolongetrennt in mm', "")

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
