# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# PEP8 compliant (https://www.python.org/dev/peps/pep-0008)

# ----------------------------------------------------------
# File: roof_maker.py
# Automatic generation of roofs
# Author: Antonio Vazquez (antonioya)
#
# ----------------------------------------------------------
# noinspection PyUnresolvedReferences
import bpy
import math
from arch_tools import *


# ------------------------------------------------------------------
# Define UI class
# Rooms
# ------------------------------------------------------------------
class ROOF(bpy.types.Operator):
    bl_idname = "mesh.archimesh_roof"
    bl_label = "Roof"
    bl_description = "Roof Generator"
    bl_category = 'Archimesh'
    bl_options = {'REGISTER', 'UNDO'}

    # Define properties
    roof_width = bpy.props.IntProperty(name='Num tiles X', min=1, max=100, default=6, description='Tiles in X axis')
    roof_height = bpy.props.IntProperty(name='Num tiles Y', min=1, max=100, default=3, description='Tiles in Y axis')

    roof_thick = bpy.props.FloatProperty(name='Tile thickness', min=0.000, max=0.50, default=0.012, precision=3,
                                         description='Thickness of the roof tile')
    roof_angle = bpy.props.FloatProperty(name='Roof slope', min=0.0, max=70.0, default=0.0, precision=1,
                                         description='Roof angle of slope')
    roof_scale = bpy.props.FloatProperty(name='Tile scale', min=0.001, max=10, default=1, precision=3,
                                         description='Scale of roof tile')

    crt_mat = bpy.props.BoolProperty(name="Create default Cycles materials",
                                     description="Create default materials for Cycles render.", default=True)

    model = bpy.props.EnumProperty(items=(('1', "Model 01", ""),
                                          ('2', "Model 02", ""),
                                          ('3', "Model 03", ""),
                                          ('4', "Model 04", "")),
                                   name="Model",
                                   description="Roof tile model")

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    # noinspection PyUnusedLocal
    def draw(self, context):
        layout = self.layout
        space = bpy.context.space_data
        if not space.local_view:
            # Imperial units warning
            if bpy.context.scene.unit_settings.system == "IMPERIAL":
                row = layout.row()
                row.label("Warning: Imperial units not supported", icon='COLOR_RED')
            box = layout.box()
            box.prop(self, 'model')
            box.prop(self, 'roof_width')
            box.prop(self, 'roof_height')
            box.prop(self, 'roof_scale')

            tilesize_x = 0
            tilesize_y = 0
            if self.model == "1":
                tilesize_x = 0.184
                tilesize_y = 0.413

            if self.model == "2":
                tilesize_x = 0.103
                tilesize_y = 0.413

            if self.model == "3":
                tilesize_x = 0.184
                tilesize_y = 0.434

            if self.model == "4":
                tilesize_x = 0.231
                tilesize_y = 0.39

            x = tilesize_x * self.roof_scale * self.roof_width
            y = tilesize_y * self.roof_scale * self.roof_height

            buf = 'Size: {0:.2f} * {1:.2f} aprox.'.format(x, y)
            box.label(buf)

            box = layout.box()
            box.prop(self, 'roof_thick')
            box.prop(self, 'roof_angle')

            box = layout.box()
            box.prop(self, 'crt_mat')
        else:
            row = layout.row()
            row.label("Warning: Operator does not work in local view mode", icon='ERROR')

    # -----------------------------------------------------
    # Execute
    # -----------------------------------------------------
    # noinspection PyUnusedLocal
    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            create_roof_mesh(self)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Archimesh: Option only valid in Object mode")
            return {'CANCELLED'}


# ------------------------------------------------------------------------------
# Generate mesh data
# All custom values are passed using self container (self.myvariable)
# ------------------------------------------------------------------------------
def create_roof_mesh(self):
    # deactivate others
    for o in bpy.data.objects:
        if o.select is True:
            o.select = False
    bpy.ops.object.select_all(False)

    mydata = create_roof(self)
    myroof = mydata[0]

    # active object and deactivate others
    if bpy.context.scene.objects.active is not None:
        bpy.context.scene.objects.active.select = False

    bpy.context.scene.objects.active = myroof
    myroof.select = True

    # Thicknes
    if self.roof_thick > 0.0:
        set_modifier_solidify(myroof, self.roof_thick)
    # Subsurf
    set_modifier_subsurf(myroof)
    set_smooth(myroof)

    a_x = 0.85
    a_y = 0.85

    if self.model == "1":
        a_x = 0.85
        a_y = 0.85

    if self.model == "2":
        a_x = 0.90
        a_y = 0.85

    if self.model == "3":
        a_x = 0.80
        a_y = 0.85

    if self.model == "4":
        a_x = 0.80
        a_y = 0.85

    set_modifier_array(myroof, "X", a_x, self.roof_width)
    set_modifier_array(myroof, "Y", a_y, self.roof_height)

    # Slope
    myroof.rotation_euler = (math.radians(self.roof_angle), 0.0, 0.0)

    # Create materials
    if self.crt_mat:
        # material
        mat = create_diffuse_material("Roof_material", False, 0.482, 0.061, 0.003, 0.581, 0.105, 0.068, 0.01)
        set_material(myroof, mat)

    bpy.ops.object.select_all(False)
    myroof.select = True
    bpy.context.scene.objects.active = myroof
    return


# ------------------------------------------------------------------------------
# Create Roof
# All custom values are passed using self container (self.myvariable)
# ------------------------------------------------------------------------------
def create_roof(self):
    # Retry mesh data
    if self.model == "1":
        mydata = tile_model_01()
    elif self.model == "2":
        mydata = tile_model_02()
    elif self.model == "3":
        mydata = tile_model_03()
    elif self.model == "4":
        mydata = tile_model_04()
    else:
        mydata = tile_model_01()  # default model

    # move data
    verts = mydata[0]
    faces = mydata[1]
    tile_x = mydata[2]
    tile_y = mydata[3]

    mymesh = bpy.data.meshes.new("Roof")
    myobject = bpy.data.objects.new("Roof", mymesh)

    myobject.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(myobject)

    mymesh.from_pydata(verts, [], faces)
    mymesh.update(calc_edges=True)
    # Scale
    myobject.scale = (self.roof_scale, self.roof_scale, self.roof_scale)

    return myobject, tile_x, tile_y


# ----------------------------------------------
# Tile model 01
# ----------------------------------------------
def tile_model_01():
    # ------------------------------------
    # Mesh data
    # ------------------------------------
    minx = -2.60770320892334e-08
    maxx = 0.19982914626598358
    miny = -0.0010638721287250519
    maxy = 0.46471506357192993
    minz = -0.03651249408721924
    maxz = 0.0586184486746788

    # Vertex
    myvertex = [(maxx - 0.0912834107875824, maxy - 0.0017275810241699219, maxz - 0.046515291556715965),
                (maxx - 0.08774729073047638, maxy - 0.0021544992923736572, minz + 0.02855057455599308),
                (minx + 0.007649015635251999, maxy - 0.002105712890625, minz + 0.03084239922463894),
                (minx + 0.012062381953001022, maxy - 0.0016825199127197266, maxz - 0.044397931545972824),
                (minx + 0.023753326386213303, maxy - 0.0013274550437927246, maxz - 0.02770993858575821),
                (minx + 0.04094201326370239, maxy - 0.0010945796966552734, maxz - 0.016765158623456955),
                (minx + 0.061011623591184616, maxy - 0.0010193586349487305, maxz - 0.013229843229055405),
                (minx + 0.09759850427508354, maxy - 0.0013619065284729004, maxz - 0.02933049201965332),
                (minx + 0.0809067152440548, maxy - 0.0011132359504699707, maxz - 0.017642192542552948),
                (minx + 0.04091371223330498, maxy - 0.005662411451339722, maxz - 0.01663973182439804),
                (minx + 0.061012353748083115, maxy - 0.00558704137802124, maxz - 0.013099301606416702),
                (minx + 0.007572557777166367, maxy - 0.006675034761428833, minz + 0.030899077653884888),
                (minx + 0.011992301791906357, maxy - 0.006251156330108643, maxz - 0.044312480837106705),
                (minx + 0.09765215590596199, maxy - 0.005930125713348389, maxz - 0.029223240911960602),
                (maxx - 0.09121392667293549, maxy - 0.006296277046203613, maxz - 0.04643290489912033),
                (minx + 0.02370016649365425, maxy - 0.00589558482170105, maxz - 0.027600344270467758),
                (maxx - 0.08767268061637878, maxy - 0.006723880767822266, minz + 0.028603939339518547),
                (minx + 0.08093622699379921, maxy - 0.005681097507476807, maxz - 0.01751803606748581),
                (minx + 0.06108579412102699, miny + 0.0018242448568344116, maxz),
                (minx + 0.0049602799117565155, miny + 0.0010638684034347534, maxz - 0.03573753498494625),
                (maxx - 0.08424043655395508, miny + 0.0010122060775756836, maxz - 0.038165315985679626),
                (minx + 0.018365193158388138, miny + 0.0014709830284118652, maxz - 0.016602978110313416),
                (maxx - 0.0801858901977539, miny + 0.0005226880311965942, minz + 0.03395887836813927),
                (minx + 0.08389763161540031, miny + 0.0017166286706924438, maxz - 0.005059238523244858),
                (minx + 0.03807384893298149, miny + 0.001738026738166809, maxz - 0.004053622484207153),
                (minx + 1.1175870895385742e-08, miny + 0.0010638725943863392, minz + 0.03651248663663864),
                (maxx - 0.09679263085126877, miny + 0.0014314353466033936, maxz - 0.018461115658283234),
                (minx + 0.06108483672142029, miny + 0.007804900407791138, maxz - 0.00017091631889343262),
                (minx + 0.0050520338118076324, miny + 0.0070457905530929565, maxz - 0.03584941849112511),
                (maxx - 0.08433142304420471, miny + 0.006994202733039856, maxz - 0.03827318921685219),
                (minx + 0.018434803932905197, miny + 0.007452219724655151, maxz - 0.01674646884202957),
                (maxx - 0.08028358221054077, miny + 0.006505459547042847, minz + 0.03388900891877711),
                (minx + 0.08385899290442467, miny + 0.007697448134422302, maxz - 0.005221795290708542),
                (minx + 0.03811090067028999, miny + 0.007718801498413086, maxz - 0.004217840731143951),
                (minx, miny + 0.006561309099197388, minz + 0.036512489430606365),
                (maxx - 0.09686288237571716, miny + 0.007412716746330261, maxz - 0.018601536750793457),
                (maxx - 0.011097520589828491, maxy - 0.00127333402633667, minz + 0.03322591632604599),
                (maxx - 0.007561400532722473, maxy, maxz - 0.041875842958688736),
                (minx + 0.0878349058330059, maxy - 0.00014543533325195312, maxz - 0.04416356980800629),
                (minx + 0.09224827215075493, maxy - 0.0014076828956604004, minz + 0.03111234214156866),
                (maxx - 0.09588995575904846, maxy - 0.0024666786193847656, minz + 0.014454199001193047),
                (maxx - 0.07870127260684967, maxy - 0.003161191940307617, minz + 0.003528997302055359),
                (maxx - 0.05863165855407715, maxy - 0.0033855140209198, minz),
                (maxx - 0.022044777870178223, maxy - 0.0023638010025024414, minz + 0.016071850433945656),
                (maxx - 0.03873656690120697, maxy - 0.0031055212020874023, minz + 0.0044044628739356995),
                (maxx - 0.07872956991195679, maxy - 0.007723212242126465, minz + 0.003790721297264099),
                (maxx - 0.05863092839717865, maxy - 0.007947862148284912, minz + 0.0002566203474998474),
                (minx + 0.08775844797492027, maxy - 0.004703164100646973, maxz - 0.043833211064338684),
                (minx + 0.09217819198966026, maxy - 0.005967140197753906, minz + 0.03141397051513195),
                (maxx - 0.021991118788719177, maxy - 0.006924688816070557, minz + 0.016351722180843353),
                (maxx - 0.01102803647518158, maxy - 0.005832552909851074, minz + 0.03353060130029917),
                (maxx - 0.09594311565160751, maxy - 0.007027685642242432, minz + 0.01473172940313816),
                (maxx - 0.007486790418624878, maxy - 0.004557549953460693, maxz - 0.04154217056930065),
                (maxx - 0.03870706260204315, maxy - 0.007667511701583862, minz + 0.004667460918426514),
                (maxx - 0.05855749547481537, miny, minz + 0.026008986867964268),
                (minx + 0.08514617010951042, miny + 0.0022678226232528687, maxz - 0.033448345959186554),
                (maxx - 0.004054546356201172, miny + 0.0024218857288360596, maxz - 0.031024910509586334),
                (minx + 0.09855108335614204, miny + 0.0010535866022109985, minz + 0.04258226789534092),
                (maxx, miny + 0.0038818269968032837, maxz - 0.008059307932853699),
                (maxx - 0.03574565052986145, miny + 0.00032107532024383545, minz + 0.03105917200446129),
                (maxx - 0.08156943321228027, miny + 0.0002572685480117798, minz + 0.030055356211960316),
                (minx + 0.0801859013736248, miny + 0.004204884171485901, maxz - 0.01064956933259964),
                (maxx - 0.016606733202934265, miny + 0.0011714845895767212, minz + 0.04443708248436451),
                (maxx - 0.058558449149131775, miny + 0.005973652005195618, minz + 0.0256729768589139),
                (minx + 0.08523792400956154, miny + 0.008237749338150024, maxz - 0.03384328447282314),
                (maxx - 0.004145532846450806, miny + 0.008391529321670532, maxz - 0.031423844397068024),
                (minx + 0.0986206941306591, miny + 0.00702551007270813, minz + 0.04221887979656458),
                (maxx - 9.769201278686523e-05, miny + 0.00984904170036316, maxz - 0.008496180176734924),
                (maxx - 0.0357842892408371, miny + 0.0062942057847976685, minz + 0.030714819207787514),
                (maxx - 0.08153238147497177, miny + 0.006230458617210388, minz + 0.029712661169469357),
                (minx + 0.08018588647246361, miny + 0.00968259572982788, maxz - 0.011114969849586487),
                (maxx - 0.016676992177963257, miny + 0.007143184542655945, minz + 0.04407063312828541)]

    # Faces
    myfaces = [(10, 9, 5, 6), (12, 11, 2, 3), (14, 13, 7, 0), (15, 12, 3, 4), (16, 14, 0, 1),
               (17, 10, 6, 8), (9, 15, 4, 5), (13, 17, 8, 7), (27, 33, 9, 10), (28, 34, 11, 12),
               (29, 35, 13, 14), (30, 28, 12, 15), (31, 29, 14, 16), (32, 27, 10, 17), (33, 30, 15, 9),
               (35, 32, 17, 13), (18, 24, 33, 27), (19, 25, 34, 28), (20, 26, 35, 29), (21, 19, 28, 30),
               (22, 20, 29, 31), (23, 18, 27, 32), (24, 21, 30, 33), (26, 23, 32, 35), (46, 45, 41, 42),
               (48, 47, 38, 39), (50, 49, 43, 36), (51, 48, 39, 40), (52, 50, 36, 37), (53, 46, 42, 44),
               (45, 51, 40, 41), (49, 53, 44, 43), (63, 69, 45, 46), (64, 70, 47, 48), (65, 71, 49, 50),
               (66, 64, 48, 51), (67, 65, 50, 52), (68, 63, 46, 53), (69, 66, 51, 45), (71, 68, 53, 49),
               (54, 60, 69, 63), (55, 61, 70, 64), (56, 62, 71, 65), (57, 55, 64, 66), (58, 56, 65, 67),
               (59, 54, 63, 68), (60, 57, 66, 69), (62, 59, 68, 71)]

    return myvertex, myfaces, maxx - minx, maxy - miny


# ----------------------------------------------
# Tile model 02
# ----------------------------------------------
def tile_model_02():
    # ------------------------------------
    # Mesh data
    # ------------------------------------
    minx = -2.60770320892334e-08
    maxx = 0.11964325606822968
    miny = -0.000541184563189745
    maxy = 0.4636957049369812
    minz = -0.007961912080645561
    maxz = 0.0586184561252594

    # Vertex
    myvertex = [(maxx - 0.011097520589828491, maxy - 0.0007082223892211914, minz + 0.020065076649188995),
                (maxx - 0.007561400532722473, maxy - 0.0011351406574249268, minz),
                (minx + 0.007649015635251999, maxy - 0.0010863542556762695, minz + 0.0022918246686458588),
                (minx + 0.012062381953001022, maxy - 0.0006631612777709961, minz + 0.022182436659932137),
                (minx + 0.023753326386213303, maxy - 0.00030809640884399414, maxz - 0.02770993858575821),
                (minx + 0.04094201326370239, maxy - 7.522106170654297e-05, maxz - 0.016765158623456955),
                (maxx - 0.05863165855407715, maxy, maxz - 0.013229843229055405),
                (maxx - 0.022044777870178223, maxy - 0.0003425478935241699, maxz - 0.02933049201965332),
                (maxx - 0.03873656690120697, maxy - 9.387731552124023e-05, maxz - 0.017642192542552948),
                (minx + 0.04091371223330498, maxy - 0.004643052816390991, maxz - 0.01663973182439804),
                (maxx - 0.05863092839717865, maxy - 0.00456768274307251, maxz - 0.013099301606416702),
                (minx + 0.007572557777166367, maxy - 0.0056556761264801025, minz + 0.0023485030978918076),
                (minx + 0.011992301791906357, maxy - 0.005231797695159912, minz + 0.022267887368798256),
                (maxx - 0.021991126239299774, maxy - 0.004910767078399658, maxz - 0.029223240911960602),
                (maxx - 0.01102803647518158, maxy - 0.005276918411254883, minz + 0.02014746330678463),
                (minx + 0.02370016649365425, maxy - 0.004876226186752319, maxz - 0.027600344270467758),
                (maxx - 0.007486790418624878, maxy - 0.005704522132873535, minz + 5.336478352546692e-05),
                (maxx - 0.038707055151462555, maxy - 0.004661738872528076, maxz - 0.01751803606748581),
                (maxx - 0.05855748802423477, miny + 0.0013015568256378174, maxz),
                (minx + 0.0049602799117565155, miny + 0.0005411803722381592, minz + 0.03084283322095871),
                (maxx - 0.004054546356201172, miny + 0.0004895180463790894, minz + 0.028415052220225334),
                (minx + 0.018365193158388138, miny + 0.000948294997215271, maxz - 0.016602978110313416),
                (maxx, miny, minz + 0.005408303812146187),
                (maxx - 0.03574565052986145, miny + 0.0011939406394958496, maxz - 0.005059238523244858),
                (minx + 0.03807384893298149, miny + 0.0012153387069702148, maxz - 0.004053622484207153),
                (minx + 1.1175870895385742e-08, miny + 0.000541184563189745, minz + 0.007961912080645561),
                (maxx - 0.016606740653514862, miny + 0.0009087473154067993, maxz - 0.018461115658283234),
                (maxx - 0.058558445423841476, miny + 0.0072822123765945435, maxz - 0.00017091631889343262),
                (minx + 0.0050520338118076324, miny + 0.006523102521896362, minz + 0.030730949714779854),
                (maxx - 0.004145532846450806, miny + 0.006471514701843262, minz + 0.028307178989052773),
                (minx + 0.018434803932905197, miny + 0.006929531693458557, maxz - 0.01674646884202957),
                (maxx - 9.769201278686523e-05, miny + 0.0059827715158462524, minz + 0.005338434362784028),
                (maxx - 0.0357842892408371, miny + 0.007174760103225708, maxz - 0.005221795290708542),
                (minx + 0.03811090067028999, miny + 0.007196113467216492, maxz - 0.004217840731143951),
                (minx, miny + 0.0060386210680007935, minz + 0.007961914874613285),
                (maxx - 0.016676992177963257, miny + 0.006890028715133667, maxz - 0.018601536750793457)]

    # Faces
    myfaces = [(10, 9, 5, 6), (12, 11, 2, 3), (14, 13, 7, 0), (15, 12, 3, 4), (16, 14, 0, 1),
               (17, 10, 6, 8), (9, 15, 4, 5), (13, 17, 8, 7), (27, 33, 9, 10), (28, 34, 11, 12),
               (29, 35, 13, 14), (30, 28, 12, 15), (31, 29, 14, 16), (32, 27, 10, 17), (33, 30, 15, 9),
               (35, 32, 17, 13), (18, 24, 33, 27), (19, 25, 34, 28), (20, 26, 35, 29), (21, 19, 28, 30),
               (22, 20, 29, 31), (23, 18, 27, 32), (24, 21, 30, 33), (26, 23, 32, 35)]

    return myvertex, myfaces, maxx - minx, maxy - miny


# ----------------------------------------------
# Tile model 03
# ----------------------------------------------
def tile_model_03():
    # ------------------------------------
    # Mesh data
    # ------------------------------------
    minx = -1.1175870895385742e-08
    maxx = 0.19973646104335785
    miny = -0.007466380018740892
    maxy = 0.4636957049369812
    minz = -0.014226417988538742
    maxz = 0.0586184561252594

    # Vertex
    myvertex = [(maxx - 0.09119071066379547, maxy - 0.0007082223892211914, minz + 0.026329582557082176),
                (maxx - 0.08765459060668945, maxy - 0.0011351406574249268, minz + 0.006264505907893181),
                (minx + 0.007649015635251999, maxy - 0.0010863542556762695, minz + 0.00855633057653904),
                (minx + 0.012062381953001022, maxy - 0.0006631612777709961, minz + 0.028446942567825317),
                (minx + 0.023753326386213303, maxy - 0.00030809640884399414, maxz - 0.02770993858575821),
                (minx + 0.04094201326370239, maxy - 7.522106170654297e-05, maxz - 0.016765158623456955),
                (minx + 0.061011623591184616, maxy, maxz - 0.013229843229055405),
                (minx + 0.09759850427508354, maxy - 0.0003425478935241699, maxz - 0.02933049201965332),
                (minx + 0.0809067152440548, maxy - 9.387731552124023e-05, maxz - 0.017642192542552948),
                (maxx, miny, minz + 0.009998040273785591),
                (maxx, maxy - 0.0012684464454650879, minz),
                (maxx - 0.011666849255561829, miny + 5.453824996948242e-06, minz + 0.01025407388806343),
                (maxx - 0.012786239385604858, maxy - 0.0012489855289459229, minz + 0.0009138062596321106),
                (maxx - 0.00027532875537872314, miny + 0.00016899406909942627, minz + 0.017940200865268707),
                (maxx - 0.00027532875537872314, maxy - 0.0010994374752044678, minz + 0.007942160591483116),
                (maxx - 0.011416733264923096, miny + 0.00017443299293518066, minz + 0.018196236342191696),
                (maxx - 0.012485697865486145, maxy - 0.0010799765586853027, minz + 0.008855968713760376),
                (minx + 0.04091371223330498, maxy - 0.004643052816390991, maxz - 0.01663973182439804),
                (minx + 0.061012353748083115, maxy - 0.00456768274307251, maxz - 0.013099301606416702),
                (minx + 0.007572557777166367, maxy - 0.0056556761264801025, minz + 0.008613009005784988),
                (minx + 0.011992301791906357, maxy - 0.005231797695159912, minz + 0.028532393276691437),
                (minx + 0.09765215590596199, maxy - 0.004910767078399658, maxz - 0.029223240911960602),
                (maxx - 0.09112122654914856, maxy - 0.005276918411254883, minz + 0.02641196921467781),
                (minx + 0.02370016649365425, maxy - 0.004876226186752319, maxz - 0.027600344270467758),
                (maxx - 0.08757998049259186, maxy - 0.005704522132873535, minz + 0.006317870691418648),
                (minx + 0.08093622699379921, maxy - 0.004661738872528076, maxz - 0.01751803606748581),
                (maxx, maxy - 0.00583687424659729, minz + 9.720027446746826e-05),
                (maxx - 0.01277536153793335, maxy - 0.0058175623416900635, minz + 0.0010046139359474182),
                (maxx - 0.00027532875537872314, maxy - 0.00566786527633667, minz + 0.008039364591240883),
                (maxx - 0.012475311756134033, maxy - 0.005648583173751831, minz + 0.008946776390075684),
                (minx + 0.06108579412102699, miny + 0.008226752281188965, maxz),
                (minx + 0.0049602799117565155, miny + 0.007466375827789307, maxz - 0.03573753498494625),
                (maxx - 0.08414773643016815, miny + 0.007414713501930237, minz + 0.034679558128118515),
                (minx + 0.018365193158388138, miny + 0.007873490452766418, maxz - 0.016602978110313416),
                (maxx - 0.08009319007396698, miny + 0.0069251954555511475, minz + 0.011672809720039368),
                (minx + 0.08389763161540031, miny + 0.008119136095046997, maxz - 0.005059238523244858),
                (maxx, miny + 0.00688643753528595, minz + 0.009851515293121338),
                (maxx - 0.011683255434036255, miny + 0.006892099976539612, minz + 0.010117188096046448),
                (maxx - 0.00027532875537872314, miny + 0.007055431604385376, minz + 0.017793675884604454),
                (maxx - 0.01143239438533783, miny + 0.007061079144477844, minz + 0.018059348687529564),
                (minx + 0.03807384893298149, miny + 0.008140534162521362, maxz - 0.004053622484207153),
                (minx + 1.1175870895385742e-08, miny + 0.007466380018740892, minz + 0.014226417988538742),
                (maxx - 0.09669993072748184, miny + 0.007833942770957947, maxz - 0.018461115658283234),
                (minx + 0.06108483672142029, miny + 0.014207407832145691, maxz - 0.00017091631889343262),
                (minx + 0.0050520338118076324, miny + 0.01344829797744751, maxz - 0.03584941849112511),
                (maxx - 0.08423872292041779, miny + 0.01339671015739441, minz + 0.03457168489694595),
                (minx + 0.018434803932905197, miny + 0.013854727149009705, maxz - 0.01674646884202957),
                (maxx - 0.08019088208675385, miny + 0.0129079669713974, minz + 0.011602940270677209),
                (minx + 0.08385899290442467, miny + 0.014099955558776855, maxz - 0.005221795290708542),
                (maxx, miny + 0.012868016958236694, minz + 0.00972424354404211),
                (maxx - 0.011697500944137573, miny + 0.012873843312263489, minz + 0.009998289868235588),
                (maxx - 0.00027532875537872314, miny + 0.01303701102733612, minz + 0.017666404135525227),
                (maxx - 0.011445999145507812, miny + 0.013042852282524109, minz + 0.017940450459718704),
                (minx + 0.03811090067028999, miny + 0.01412130892276764, maxz - 0.004217840731143951),
                (minx, miny + 0.012963816523551941, minz + 0.014226420782506466),
                (maxx - 0.09677018225193024, miny + 0.013815224170684814, maxz - 0.018601536750793457)]

    # Faces
    myfaces = [(18, 17, 5, 6), (20, 19, 2, 3), (22, 21, 7, 0), (23, 20, 3, 4), (24, 22, 0, 1),
               (25, 18, 6, 8), (17, 23, 4, 5), (21, 25, 8, 7), (12, 10, 14, 16), (24, 1, 12, 27),
               (29, 16, 14, 28), (9, 11, 15, 13), (36, 9, 13, 38), (27, 12, 16, 29), (43, 53, 17, 18),
               (44, 54, 19, 20), (45, 55, 21, 22), (46, 44, 20, 23), (47, 45, 22, 24), (48, 43, 18, 25),
               (53, 46, 23, 17), (55, 48, 25, 21), (47, 24, 27, 50), (52, 29, 28, 51), (10, 26, 28, 14),
               (50, 27, 29, 52), (49, 36, 38, 51), (15, 39, 38, 13), (11, 37, 39, 15), (30, 40, 53, 43),
               (31, 41, 54, 44), (32, 42, 55, 45), (33, 31, 44, 46), (34, 32, 45, 47), (35, 30, 43, 48),
               (40, 33, 46, 53), (42, 35, 48, 55), (34, 47, 50, 37), (39, 52, 51, 38), (37, 50, 52, 39),
               (26, 49, 51, 28)]

    return myvertex, myfaces, maxx - minx, maxy - miny


# ----------------------------------------------
# Tile model 04
# ----------------------------------------------
def tile_model_04():
    # ------------------------------------
    # Mesh data
    # ------------------------------------
    minx = 0
    maxx = 0.2706337571144104
    miny = -0.0008960736449807882
    maxy = 0.4393549859523773
    minz = -0.021988021209836006
    maxz = 0.01913231611251831

    # Vertex
    myvertex = [(maxx - 0.0009386539459228516, miny + 9.811518248170614e-05, minz + 0.009184492751955986),
                (minx + 2.9802322387695312e-08, miny + 0.0008960723644122481, maxz - 0.01913231797516346),
                (maxx, maxy - 0.000797957181930542, minz + 0.0015743095427751541),
                (minx + 0.0009386688470840454, maxy, minz + 0.014377830550074577),
                (maxx - 0.03795182704925537, miny + 0.00020762975327670574, minz + 0.010941661894321442),
                (minx + 0.03701320290565491, miny + 0.0007865577936172485, minz + 0.020230852998793125),
                (maxx - 0.037013158202171326, maxy - 0.0006884634494781494, minz + 0.003331473097205162),
                (minx + 0.037951841950416565, maxy - 0.00010952353477478027, minz + 0.01262066513299942),
                (minx + 0.1184280663728714, miny + 0.000545668532140553, minz + 0.016365760006010532),
                (maxx - 0.11936667561531067, miny + 0.00044850551057606936, minz + 0.014806757681071758),
                (minx + 0.11936671286821365, maxy - 0.0003504157066345215, minz + 0.008755568414926529),
                (maxx - 0.11842802166938782, maxy - 0.0004475712776184082, minz + 0.007196567952632904),
                (maxx, miny + 0.010358194587752223, maxz - 0.012803521938621998),
                (minx + 0.0009386688470840454, miny + 0.01115613873116672, maxz),
                (minx + 0.037951841950416565, miny + 0.011046637548133731, maxz - 0.0017571654170751572),
                (maxx - 0.037013158202171326, miny + 0.010467695770785213, maxz - 0.011046357452869415),
                (minx + 0.11922238767147064, miny + 0.010617014719173312, maxz - 0.008650526404380798),
                (maxx - 0.11857235431671143, miny + 0.010519851697608829, maxz - 0.010209528729319572),
                (maxx, maxy - 0.0072495341300964355, minz + 0.001976391300559044),
                (minx + 0.037951841950416565, maxy - 0.006561100482940674, minz + 0.01302274689078331),
                (maxx - 0.037013158202171326, maxy - 0.007140040397644043, minz + 0.003733554854989052),
                (minx + 0.11936454474925995, maxy - 0.006804823875427246, minz + 0.009112119674682617),
                (maxx - 0.11843019723892212, maxy - 0.006901979446411133, minz + 0.007553117349743843),
                (minx + 0.0009386688470840454, maxy - 0.0064515769481658936, minz + 0.014779912307858467),
                (minx + 0.00011220574378967285, miny + 0.0021222709910944104, maxz - 0.016845770180225372),
                (maxx - 0.0008264482021331787, miny + 0.0013243272551335394, minz + 0.011471047066152096),
                (minx + 0.03712538629770279, miny + 0.002012769808061421, maxz - 0.01860293745994568),
                (maxx - 0.0378396213054657, miny + 0.001433828438166529, minz + 0.013228209689259529),
                (minx + 0.1185230016708374, miny + 0.0017493232735432684, minz + 0.018290389329195023),
                (maxx - 0.11927174031734467, miny + 0.0016521602519787848, minz + 0.01673138700425625),
                (maxx, miny + 0.01807751110754907, maxz - 0.013284613378345966),
                (minx + 0.037951841950416565, miny + 0.01876595593057573, maxz - 0.0022382568567991257),
                (maxx - 0.037013158202171326, miny + 0.01818701229058206, maxz - 0.011527448892593384),
                (minx + 0.11922498792409897, miny + 0.01833972311578691, maxz - 0.009077141061425209),
                (maxx - 0.1185697615146637, miny + 0.018242560094222426, maxz - 0.010636141523718834),
                (minx + 0.0009386688470840454, miny + 0.018875457113608718, maxz - 0.0004810914397239685),
                (maxx, maxy - 0.09558254480361938, minz + 0.007481573149561882),
                (minx + 0.037951841950416565, maxy - 0.09489411115646362, minz + 0.018527928739786148),
                (maxx - 0.037013158202171326, maxy - 0.09547305107116699, minz + 0.00923873856663704),
                (minx + 0.1202642098069191, maxy - 0.09396132826805115, maxz - 0.00762566365301609),
                (maxx - 0.11753053963184357, maxy - 0.09405851364135742, maxz - 0.009184665977954865),
                (minx + 0.0009386688470840454, maxy - 0.09478458762168884, minz + 0.02028509508818388),
                (maxx - 0.07891011238098145, miny, minz + 0.007610190659761429),
                (maxx - 0.07797147333621979, maxy - 0.0008960962295532227, minz),
                (maxx - 0.07804363965988159, miny + 0.010165706044062972, maxz - 0.0158919645473361),
                (maxx - 0.07797256112098694, maxy - 0.007349073886871338, minz + 0.0003793146461248398),
                (maxx - 0.0788065642118454, miny + 0.0012149333488196135, minz + 0.009715777821838856),
                (maxx - 0.07804234325885773, miny + 0.01788672781549394, maxz - 0.016345815733075142),
                (maxx - 0.07752272486686707, maxy - 0.09509384632110596, minz + 0.015323184430599213),
                (minx + 0.07725311815738678, miny + 5.473045166581869e-05, minz + 0.008488442748785019),
                (minx + 0.07819175720214844, maxy - 0.0008413791656494141, minz + 0.0008782520890235901),
                (minx + 0.07811960577964783, miny + 0.010220450116321445, maxz - 0.015013711526989937),
                (minx + 0.07819066941738129, maxy - 0.007294327020645142, minz + 0.001257568597793579),
                (minx + 0.07735666632652283, miny + 0.0012696638295892626, minz + 0.010594029910862446),
                (minx + 0.07812090218067169, miny + 0.017941456055268645, maxz - 0.015467563644051552),
                (minx + 0.07864050567150116, maxy - 0.09503909945487976, minz + 0.016201436519622803)]

    # Faces
    myfaces = [(20, 18, 2, 6), (23, 19, 7, 3), (45, 20, 6, 43), (52, 21, 10, 50), (21, 22, 11, 10),
               (27, 25, 12, 15), (24, 26, 14, 13), (46, 27, 15, 44), (53, 28, 16, 51), (28, 29, 17, 16),
               (38, 36, 18, 20), (41, 37, 19, 23), (48, 38, 20, 45), (55, 39, 21, 52), (39, 40, 22, 21),
               (4, 0, 25, 27), (1, 5, 26, 24), (42, 4, 27, 46), (49, 8, 28, 53), (8, 9, 29, 28),
               (15, 12, 30, 32), (13, 14, 31, 35), (44, 15, 32, 47), (51, 16, 33, 54), (16, 17, 34, 33),
               (32, 30, 36, 38), (35, 31, 37, 41), (47, 32, 38, 48), (54, 33, 39, 55), (33, 34, 40, 39),
               (22, 45, 43, 11), (29, 46, 44, 17), (40, 48, 45, 22), (9, 42, 46, 29), (17, 44, 47, 34),
               (34, 47, 48, 40), (19, 52, 50, 7), (26, 53, 51, 14), (37, 55, 52, 19), (5, 49, 53, 26),
               (14, 51, 54, 31), (31, 54, 55, 37)]

    return myvertex, myfaces, maxx - minx, maxy - miny
