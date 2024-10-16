import adsk.core, adsk.fusion, adsk.cam, traceback
import math as m

"""
This skript adds spans calculated by Hügelschäffer equation to Fusion 360 fitting 3 splines ready for lofting.
"""

handlers = []




ui = None
rowNumber = 0

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

val_ids_list =[]

COMMAND_ID = "SpanCMDDef"
INPUT_ORIENTIERUNG = ""
SE01_SELECTION_INPUT_ID = "Spline oben"
SE02_SELECTION_INPUT_ID = "Spline unten"
SE03_SELECTION_INPUT_ID = "Spline mitte"
IN01_VALUE_INPUT_ID = "Abstand bei gleichem Abstand"
SE04_SELECTION_INPUT_ID = "Parallele Ursprungsebene"
IN02_VALUE_INPUT_ID = "Abstand Spanten"
IN03_VALUE_INPUT_ID ='Anzahl Spanten gleichen Abstands'
CH01_BOOLEAN_INPUT_ID = 'checkbox'
CH02_BOOLEAN_INPUT_ID = 'checkbox2'



# Adds a new row to the table.
def addRowToTable(tableInput):
    global rowNumber, val_ids_list

    cmdInputs = adsk.core.CommandInputs.cast(tableInput.commandInputs)
    
    valueInput = cmdInputs.addValueInput('TableInput_value{}'.format(rowNumber), 'Value', 'mm', adsk.core.ValueInput.createByReal(0.0))
    val_ids_list.append((f'TableInput_value{rowNumber}', rowNumber, valueInput.value))         # ids to read values later
    row = tableInput.rowCount
    tableInput.addCommandInput(valueInput, row, 0)
    
    # Increment a counter used to make each row unique.
    rowNumber = rowNumber + 1


# Event handler that reacts to any changes the user makes to any of the command inputs.
class MyCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            inputs = eventArgs.inputs
            cmdInput = eventArgs.input

            global abstand, val_ids_list
            if cmdInput.id == IN02_VALUE_INPUT_ID:
                abstand = inputs.itemById(IN02_VALUE_INPUT_ID)
           
            tableInput = inputs.itemById('table')
            if cmdInput.id == 'tableAdd':
                addRowToTable(tableInput)
            elif cmdInput.id == 'tableDelete':
                if tableInput.selectedRow == -1:
                    ui.messageBox('Select one row to delete.')
                else:              

                    del val_ids_list[int(tableInput.selectedRow)]
                    tableInput.deleteRow(tableInput.selectedRow)
          
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))




class SpanCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            
            command = args.firingEvent.sender
            inputs = command.commandInputs


            sel0 = inputs.itemById(SE01_SELECTION_INPUT_ID).selection(0)
            sel1 = inputs.itemById(SE02_SELECTION_INPUT_ID).selection(0)
            sel2 = inputs.itemById(SE03_SELECTION_INPUT_ID).selection(0)
            sel3 = inputs.itemById(SE04_SELECTION_INPUT_ID).selection(0)
            input4 = inputs.itemById(IN01_VALUE_INPUT_ID) # points / 4
            delta_span = float((inputs.itemById(IN02_VALUE_INPUT_ID)).value) # distance
            anzahl_span = float((inputs.itemById(IN03_VALUE_INPUT_ID).value))  # number of spans


            if inputs.itemById(CH01_BOOLEAN_INPUT_ID) == True:
                faktor = i
                anzahl_span -= 1

            if (inputs.itemById(CH02_BOOLEAN_INPUT_ID)).value == True:
                dir_off = -1
            else:
                dir_off = 1

            for i in range(int(anzahl_span)):
                if (inputs.itemById(CH01_BOOLEAN_INPUT_ID)).value == True:
                    faktor = i
                else:
                    faktor = i + 1
                temp = float(faktor * delta_span)
                l_off.append(dir_off * temp)
    
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
            
            entities_all = entities_o + entities_u + entities_m  # del?

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

            
            # val_ids_list get rid of dublets add append l_off
            def prepare_val_ids():
                global val_ids_list

                names_ids = [val_ids_list[i][0] for i in range(len(val_ids_list))]
                values = [float(inputs.itemById(names_ids[i]).value) for i in range(len(names_ids))]
                cleaned_vals = list(set(values))
                for i in range(len(cleaned_vals)):
                    l_off.append( float(cleaned_vals[i]))

            prepare_val_ids()
            
            for i in range(len(l_off)):
                intersection_ebene(l_off[i], entities_o, entities_u, entities_m, INPUT_ORIENTIERUNG)

            

            # execute the calculation programm with the user selected values
            span = Span()
            for i in range(len(l_off)):
                span.Execute(l_xmax[i], l_xmin[i], l_xmit[i], l_ymax[i], 4 * input4.value, -1 * l_off[i], INPUT_ORIENTIERUNG)

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
    def notify(self, args: adsk.core.CommandEventArgs):
        try:

            onExecute = SpanCommandExecuteHandler()
            args.command.execute.add(onExecute)
            handlers.append(onExecute) 

            onDestroy = SpanCommandDestroyHandler()
            args.command.destroy.add(onDestroy)
            handlers.append(onDestroy)

            onInputChanged = MyCommandInputChangedHandler()
            args.command.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)  


            inputs = args.command.commandInputs

            tabCmdInput1 = inputs.addTabCommandInput('tab_1', 'Settings')
            tab1ChildInputs = tabCmdInput1.children



            groupCmdInput = tab1ChildInputs.addGroupCommandInput('group', 'Auswahl der Splines und Projektionsebene:')
            groupCmdInput.isExpanded = True
            groupCmdInput.isEnabledCheckBoxDisplayed = False
            groupChildInputs = groupCmdInput.children


            group2CmdInput = tab1ChildInputs.addGroupCommandInput('group2', 'Eiform Punkte pro Quadrant:')
            group2CmdInput.isExpanded = False
            group2CmdInput.isEnabledCheckBoxDisplayed = False
            group2ChildInputs = group2CmdInput.children
            

            group3CmdInput = tab1ChildInputs.addGroupCommandInput('group3', 'Spanten gleichen Abstands erzeugen:')
            group3CmdInput.isExpanded = False
            group3CmdInput.isEnabledCheckBoxDisplayed = False
            group3ChildInputs = group3CmdInput.children

            group4CmdInput = tab1ChildInputs.addGroupCommandInput('group3', 'Spanten unterschiedlichen Abstands zur Usrprungsebene erzeugen:')
            group4CmdInput.isExpanded = True
            group4CmdInput.isEnabledCheckBoxDisplayed = False
            group4ChildInputs = group4CmdInput.children

    
            
            i1 = groupChildInputs.addSelectionInput(SE01_SELECTION_INPUT_ID, SE01_SELECTION_INPUT_ID, "Select curve")
            
            i1.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
            i1.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i2 = groupChildInputs.addSelectionInput(SE02_SELECTION_INPUT_ID, SE02_SELECTION_INPUT_ID, "Select curve")
            i2.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
            #i2.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i3 = groupChildInputs.addSelectionInput(SE03_SELECTION_INPUT_ID, SE03_SELECTION_INPUT_ID, "Select curve")
            i3.addSelectionFilter(adsk.core.SelectionCommandInput.SketchCurves)
            #i3.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i4 = group2ChildInputs.addValueInput(IN01_VALUE_INPUT_ID, '1/4 Punkte Eiform', '', adsk.core.ValueInput.createByReal(9))
            i5 = groupChildInputs.addSelectionInput(SE04_SELECTION_INPUT_ID, SE04_SELECTION_INPUT_ID, "Select Plane")
            i5.addSelectionFilter(adsk.core.SelectionCommandInput.ConstructionPlanes)
            #i5.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            i6 = group3ChildInputs.addValueInput(IN02_VALUE_INPUT_ID, IN01_VALUE_INPUT_ID, "mm", adsk.core.ValueInput.createByReal(0.5))
            i7 = group3ChildInputs.addValueInput(IN03_VALUE_INPUT_ID, IN03_VALUE_INPUT_ID, '', adsk.core.ValueInput.createByString("0"))
            i8 = group3ChildInputs.addBoolValueInput(CH01_BOOLEAN_INPUT_ID, "Erster Spant bei 0.0", True, '', False)
            i9 = group3ChildInputs.addBoolValueInput(CH02_BOOLEAN_INPUT_ID, "Richtung invertieren", True, '', False)


            tableInput = group4ChildInputs.addTableCommandInput('table', 'Table', 1, '1:0:0')
            addRowToTable(tableInput)

            # Add inputs into the table.            
            addButtonInput = tab1ChildInputs.addBoolValueInput('tableAdd', 'Add', False, '', True)
            tableInput.addToolbarCommandInput(addButtonInput)
            deleteButtonInput = tab1ChildInputs.addBoolValueInput('tableDelete', 'Delete', False, '', True)
            tableInput.addToolbarCommandInput(deleteButtonInput)

            tabCmdInput2 = inputs.addTabCommandInput('tab_2', 'Help')
            tab2ChildInputs = tabCmdInput2.children

           

            inst_text1 = """ <p><strong>Instructions:</strong></p> \
                <p>Select rails from side and topview of the fusselage.\
                <p>Select the origin plane from which the offset planes are generated.</p> \
                <p>Either choose to create spans of equal distance or manually add offsets to the table</p> \
                <p>If fussellage is drawn in z-direction (sideview on yZ-plane), top view should be drawn on xZ-plane (and projected to a surface). x-values should be positive.</p>
                <p>Other orientations might cause errors. In these cases it might help to use the mirror side of the top view. Other orientations that work are:</p>
                <p>Fusellage on x-axis topview with pos y-values, sideview on xZ-plane, top with pos z-values</p>
                <p>Fusselage on y-axis topview with pos x-values, sideview on yZ-plane, top with pos z-values</p>


                
            """
            tab2ChildInputs.addTextBoxCommandInput('fullWidth_textBox', '', inst_text1, 12, True)


        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



def run(context):
    try:
        global app, ui
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        
        
        title = 'Hügelschäffer Spans'

        if not design:
            ui.messageBox('No active Fusion design', title)
            return

        commandDefinitions = ui.commandDefinitions
        
        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = commandDefinitions.itemById(COMMAND_ID)
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition(COMMAND_ID, "Span Parameters", "Creates span spline on selected construction plane")
        
        # Connect to the command created event.
        onCommandCreated = SpanCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
          
        # Execute the command definition.
        inputs = adsk.core.NamedValues.create()             ##### ?
        cmdDef.execute(inputs)

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
