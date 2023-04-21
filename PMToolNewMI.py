
import sys
from PyQt5.QtWidgets import * #Change this
from PyQt5.QtGui import *
import unreal
import struct
import json
import os


''' 
    Setting global variable, path to JSON
    Replace this with the absolute path to your JSON file
 '''

filename = 'C:/Users/aimmaneni/Desktop/data.json'

try:
    f = open(filename)
    folder_struct = json.load(f)
    f.close()

except IOError as message:
    raise IOError(f'File could not be opened {message}')  #Error handling

class FolderStruc:
    ''' Python class to create folders in unreal '''


    def __init__(self, filename,main_folder):
        '''
        Args:
            filename (str): The first parameter.
            main_folder (str): The name of the outermost folder

        Returns:
            bool: The return value. True for success, False otherwise.

        '''
        self.filename = filename
        self.main_folder = main_folder
        self.obj = unreal.EditorAssetLibrary()
        self.get_folder_struct()
        self.create_directories()

    def get_folder_struct(self):
        self.directories = folder_struct["folder_names"].rsplit(",")

    def create_directories(self):
        parent_directory = "/Game/"+self.main_folder
        self.obj.make_directory(parent_directory)

        for directory in self.directories:
            self.obj.make_directory(parent_directory+"/"+directory)


class AssetDistrib:
    '''Python class to distribute assets is folders'''

    def __init__(self,source_dir,dest_dir):
        '''
        Args:
            source_dir (str) : Source directory to distribute assets from
            dest_dir (str) : Destination directory to distribute into
            source_dir and dest_dir could be the same in certain instances
        '''
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.assetType = {
             'StaticMesh' : 'Meshes',
             'SkeletalMesh' : 'Meshes',
             'Texture2D': 'Textures',
              'AnimSequence': 'Animations',
              'Skeleton': 'Skeletons',
              'PhysicsAsset': 'PhysicsAssets',
              'Material': 'Materials'
              }
        self.obj = unreal.EditorAssetLibrary()
        self.get_assets()
        self.distribute_assets()

    def get_assets(self):
        ''' Get list of assets in a directory '''
        self.listOfAssets = self.obj.list_assets("/Game/"+self.source_dir+"/")

    def distribute_assets(self):
        for asset in self.listOfAssets:
            
            self.place_asset(asset)
            

    def find_assettags(self,asset): 
        assetdata = self.obj.find_asset_data(asset)
        assetname = (((assetdata.get_full_name()).rsplit("/"))[-1]) #Get Asset Name
        assetclass = (assetdata.get_class()).get_name() #Tells us if it belongs to class 'Static Mesh' or 'Material' for example
        return assetname, assetclass

    def place_asset(self,asset):
        #Can be modified based on need
        #Current: Static Mesh, Materials, Textures, Skeletons, Physics Assets, Animations
        assetname, assetclass = self.find_assettags(asset)
        dest_directory = "/Game/"+self.dest_dir
        if str(assetclass) in self.assetType.keys():
            self.obj.rename_asset(asset,dest_directory+"/"+self.assetType[str(assetclass)]+"/"+assetname)        
            print('Success')
        '''
        Old:
        if (assetclass.find("Mesh")!=-1):
            self.obj.rename_asset(asset,dest_directory+"/Meshes/"+assetname)
            print("success")
        elif assetclass.startswith("Material"):
            self.obj.rename_asset(asset,dest_directory+"/Materials/"+assetname)
            print("success")
        elif assetclass.startswith("Texture"):
            self.obj.rename_asset(asset,dest_directory+"/Textures/"+assetname)
            print("success")
        elif assetclass.startswith("Skeleton"):
            self.obj.rename_asset(asset,dest_directory+"/Skeletons/"+assetname)
            print("success")
        elif assetclass.startswith("Physics"):
            self.obj.rename_asset(asset,dest_directory+"/PhysicsAssets/"+assetname)
            print("success")
        elif assetclass.startswith("Anim"):
            self.obj.rename_asset(asset,dest_directory+"/Animations/"+assetname)
            print("success")
        '''


class AssetImport:
    ''' Python class to autoimport assets and assert naming conventions '''

    def __init__(self, import_folder_unreal, import_folder_path): 
        '''
        Args:
            import_folder_unreal (str) : Folder inside Unreal to import into
            import_folder_path (str) : Folder outside Unreal which contains all your assets
        '''
        self.import_folder_unreal = import_folder_unreal 
        self.import_folder_path = import_folder_path 
        self.get_options()
        self.fbx_options = unreal.FbxImportUI()
        self.task_options = unreal.AssetImportTask()
        self.import_tasks = []
        self. traverse_directory()
        self.import_asset()
 

    def get_options(self):
        self.mesh_options = folder_struct["mesh_options"]
        self.skeletal_options = folder_struct["skeletal_options"]
        self.anim_options = folder_struct["anim_options"]

    def get_import_options(self,type, opt): #Defaults to a Static Mesh
        #Setting Asset Import Options
        #Need to make this modifiable, with a variable or a list
        fbxoptions = unreal.FbxImportUI()
        if type == 'SM' or type == 'SKM' or type == 'Anim':
            fbxoptions.set_editor_property('import_mesh',opt['import_mesh'])
            fbxoptions.set_editor_property('import_materials',opt['import_materials'])
            fbxoptions.set_editor_property('import_textures', opt['import_textures'])
            fbxoptions.set_editor_property('import_as_skeletal', opt['import_as_skeletal'])
            fbxoptions.set_editor_property('import_animations', opt['import_animations'])

        if type == 'SM':
            fbxoptions.static_mesh_import_data.set_editor_property('import_translation', opt['import_translation'])
            fbxoptions.static_mesh_import_data.set_editor_property('import_rotation', opt['import_rotation'])
            fbxoptions.static_mesh_import_data.set_editor_property('import_uniform_scale', opt['import_uniform_scale'])
            fbxoptions.static_mesh_import_data.set_editor_property('combine_meshes', opt['combine_meshes'])
            fbxoptions.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', opt['generate_lightmap_u_vs'])
            fbxoptions.static_mesh_import_data.set_editor_property('auto_generate_collision', opt['auto_generate_collision'])

        elif type == 'SKM':
            fbxoptions.skeletal_mesh_import_data.set_editor_property('import_rotation',opt['import_rotation'])
            fbxoptions.skeletal_mesh_import_data.set_editor_property('import_translation',opt['import_translation'])
            fbxoptions.static_mesh_import_data.set_editor_property('combine_meshes', opt['combine_meshes'])
            fbxoptions.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', opt['generate_lightmap_u_vs'])
            fbxoptions.static_mesh_import_data.set_editor_property('auto_generate_collision', opt['auto_generate_collision'])
 
        else:
            #Need a proxy skeleton for all animations
            skpath = self.import_folder_unreal+opt['skeleton_path']
            fbxoptions.skeleton = unreal.load_asset(skpath)
            fbxoptions.anim_sequence_import_data.set_editor_property('import_rotation',opt['import_rotation'])
            fbxoptions.anim_sequence_import_data.set_editor_property('import_translation',opt['import_translation'])

        return fbxoptions
    
    def textureImportOptions(self,new_name):
        fbxoptions = unreal.FbxImportUI()
        fbxoptions.set_editor_property('import_textures', True)
        fbxoptions.texture_import_data.set_editor_property('base_color_name',new_name)
        fbxoptions.texture_import_data.set_editor_property('base_diffuse_texture_name',new_name)
        return fbxoptions

    def assetImpTasks(self, filename, dest_path, dest_name,fbxoptions):
        #Setting import tasks for each asset
        taskoptions = unreal.AssetImportTask()
        taskoptions.set_editor_property('automated', True)
        taskoptions.set_editor_property('destination_name',dest_name)
        taskoptions.set_editor_property('destination_path',dest_path) 
        taskoptions.set_editor_property('filename', filename) 
        taskoptions.set_editor_property('replace_existing', True)
        taskoptions.set_editor_property('save', False)
        taskoptions.set_editor_property('options', fbxoptions)
        self.import_tasks.append(taskoptions)

    def assertName(self,asset_type,filename):
        ''' Unreal Naming Conventions '''
        if filename.rfind('fbx') != -1:
            filename = filename[:filename.rfind('fbx')-1]

        if asset_type == 'SM':
            if filename.startswith('SM_') or filename.startswith('S_'):
                name = 'S_'+filename[filename.index('_')+1:]
                
            else:
                name = 'S_'+filename

        elif asset_type == 'SKM':
            if filename.startswith('SKM_') or filename.startswith('SK_'):
                name = 'SK_'+filename[filename.index('_')+1:]
            else:
                name = 'SK_'+filename
                

        elif asset_type == 'Anim':
            if filename.startswith('Anim_') or filename.startswith('A_'):
                name = 'A_'+filename[filename.index('_')+1:]
            else:
                name = 'A_'+filename

        elif asset_type == 'Tex':
            if filename.rfind('png') != -1:
                filename = filename[:filename.rfind('png')-1]
            name = "T_"+filename
        else:
            name = filename

        return name


    def str_to_bool(self,str):
        ''' Convert string to boolean '''
        if str == "True":
            return True
        else:
            return False

    def traverse_directory(self):
        ''' Going through the asset import folder to grab assets '''
        path = self.import_folder_path
        list_of_files = os.listdir(path)
        dictAssetType = {
                         'SM': 'SM',
                          'SKM': 'SKM',
                          'An': 'Anim'
                            }
        for filen in list_of_files:
            filename = path+"/"+filen  
            if filen.startswith('SM'): #This will change. Can use folder name to deduce this too.
                mtype = dictAssetType[filen[0:2]]
                opt = {
                    'import_mesh': self.str_to_bool(self.mesh_options['import_mesh']),
                    'import_materials': self.str_to_bool(self.mesh_options['import_materials']),
                    'import_textures': self.str_to_bool(self.mesh_options['import_textures']),
                    'import_as_skeletal': self.str_to_bool(self.mesh_options['import_as_skeletal']),
                    'import_animations': self.str_to_bool(self.mesh_options['import_animations']),
                    'import_translation': unreal.Vector(0.0, 0.0, 0.0) ,
                    'import_rotation': unreal.Rotator(0.0, 0.0, 0.0) ,
                    'import_uniform_scale': 1.0 ,
                    'combine_meshes': self.str_to_bool(self.mesh_options['combine_meshes']),
                    'generate_lightmap_u_vs': self.str_to_bool(self.mesh_options['generate_lightmap_u_vs']),
                    'auto_generate_collision':self.str_to_bool(self.mesh_options['auto_generate_collision']),
                    'skeleton_path': self.mesh_options['skeleton_path']
                    }
                fbxoptions = self.get_import_options(mtype,opt)
                new_name = self.assertName(mtype,filen)
                self.assetImpTasks(filename,self.import_folder_unreal, new_name,fbxoptions)

            elif filen.startswith('SKM'):
                mtype = 'SKM'
                opt = {
                    'import_mesh': self.str_to_bool(self.skeletal_options['import_mesh']),
                    'import_materials': self.str_to_bool(self.skeletal_options['import_materials']),
                    'import_textures': self.str_to_bool(self.skeletal_options['import_textures']),
                    'import_as_skeletal': self.str_to_bool(self.skeletal_options['import_as_skeletal']),
                    'import_animations': self.str_to_bool(self.skeletal_options['import_animations']),
                    'import_translation': unreal.Vector(0.0, 0.0, 0.0) ,
                    'import_rotation': unreal.Rotator(0.0, 0.0, 0.0) ,
                    'import_uniform_scale': 1.0 ,
                    'combine_meshes': self.str_to_bool(self.skeletal_options['combine_meshes']),
                    'generate_lightmap_u_vs': self.str_to_bool(self.skeletal_options['generate_lightmap_u_vs']),
                    'auto_generate_collision':self.str_to_bool(self.skeletal_options['auto_generate_collision']),
                    'skeleton_path': self.skeletal_options['skeleton_path']
                    }
                fbxoptions = self.get_import_options(mtype,opt)
                new_name = self.assertName(mtype,filen)
                self.assetImpTasks(filename,self.import_folder_unreal, new_name,fbxoptions)


            elif filen.startswith('Anim'):
                mtype = 'Anim'
                opt = {
                    'import_mesh': self.str_to_bool(self.anim_options['import_mesh']),
                    'import_materials': self.str_to_bool(self.anim_options['import_materials']),
                    'import_textures': self.str_to_bool(self.anim_options['import_textures']),
                    'import_as_skeletal': self.str_to_bool(self.anim_options['import_as_skeletal']),
                    'import_animations': self.str_to_bool(self.anim_options['import_animations']),
                    'import_translation': unreal.Vector(0.0, 0.0, 0.0) ,
                    'import_rotation': unreal.Rotator(0.0, 0.0, 0.0) ,
                    'import_uniform_scale': 1.0 ,
                    'combine_meshes': self.str_to_bool(self.anim_options['combine_meshes']),
                    'generate_lightmap_u_vs': self.str_to_bool(self.anim_options['generate_lightmap_u_vs']),
                    'auto_generate_collision':self.str_to_bool(self.anim_options['auto_generate_collision']),
                    'skeleton_path': self.anim_options['skeleton_path']
                    }
                fbxoptions = self.get_import_options(mtype,opt)
                new_name = self.assertName(mtype,filen)
                self.assetImpTasks(filename,self.import_folder_unreal, new_name,fbxoptions)

            else:
                
                new_name = self.assertName("Tex",filen)
                fbxoptions = self.textureImportOptions(new_name)
                print(new_name)
                self.assetImpTasks(filename,self.import_folder_unreal, new_name,fbxoptions)

    def import_asset(self):
        print(self.import_tasks)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(self.import_tasks)


class MaterialInstanceCreator:

    def __init__(self,materials_folder,base_material,texture_folder,assets_path):
        self.materials_folder = materials_folder
        self.base_material = base_material
        self.texture_folder = texture_folder
        self.assets_path = assets_path
        self.eal = unreal.EditorAssetLibrary()
        self.mel = unreal.MaterialEditingLibrary()
        self.create_asset_material()

    def create_material_instance(self, mi_full_path,mi_name):
        at = unreal.AssetToolsHelpers.get_asset_tools()
        if self.eal.does_asset_exist(mi_full_path):
            minst = self.eal.find_asset_data(mi_full_path).get_asset()
            unreal.log("Asset already exists")
        else:
            minst = at.create_asset(mi_name, self.materials_folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew()) 
            self.mel.set_material_instance_parent(minst, self.eal.find_asset_data(self.base_material).get_asset())
        return minst
    
    def set_material_instance_values(self,minst,asset_name):
        self.set_material_instance_texture(minst,"AO Texture", self.texture_folder+"/" + "T_" + asset_name + "_OcclusionRoughnessMetallic")
        self.set_material_instance_texture(minst,"BaseColor", self.texture_folder+"/" + "T_" + asset_name + "_BaseColor")  #Parameter name should be taken as input. Would depend on Master Material
        self.set_material_instance_texture(minst, "Normal", self.texture_folder + "T_" + asset_name + "_Normal")

    def set_material_instance_texture(self,minst, param_name, texture_path):
        if not self.eal.does_asset_exist(texture_path):
            unreal.log_warning("Can't find texture: " + texture_path)
            return False
        texture = self.eal.find_asset_data(texture_path).get_asset()
        return self.mel.set_material_instance_texture_parameter_value(minst, param_name, texture) 

    def create_asset_material(self):
        listOfAssets = self.eal.list_assets(self.assets_path)
        for asset in listOfAssets:
            print(asset)
            assetdata = self.eal.find_asset_data(asset)
            assetname = (((assetdata.get_full_name()).rsplit("/"))[-1]) #Get Asset Name
            assetname = assetname.rsplit('.')[0]
            assetname = assetname[2:]
            assetclass = (assetdata.get_class()).get_name()
            if assetclass != 'StaticMesh':
                continue
            mi_name = "MI_"+assetname
            mi_full_path = self.materials_folder+'/'+mi_name
            minst = self.create_material_instance(mi_full_path,mi_name)
            self.set_material_instance_values(minst,assetname)
            assetdata.get_asset().set_material(0, minst)

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Asset Management Tool')
        self.layout = QVBoxLayout()       #Main Layout
        centralWidget = QWidget()         #Central Widget
        centralWidget.setLayout(self.layout)
        self.setCentralWidget(centralWidget)
        self.createWidgets()


    def createWidgets(self):
        fsw = QWidget()
        layout_fsw = QHBoxLayout()
        fsw.setLayout(layout_fsw)
        self.button_browse = QPushButton('Browse')
        self.textbox_fs = QLineEdit()
        self.textbox_fs.setPlaceholderText('Select folder to import from')      
        self.textbox_foldername = QLineEdit()
        self.textbox_foldername.setPlaceholderText('Enter main folder name (Ex: Assets or Assets/Amka). External folder has to be created first.')
        self.layout.addWidget(self.textbox_foldername)
        layout_fsw.addWidget(self.textbox_fs)
        layout_fsw.addWidget(self.button_browse)
        self.button_browse.clicked.connect(self.file_dialog)



        self.button_makefs = QPushButton('Create Folders')
        self.layout.addWidget(self.button_makefs)
        self.button_makefs.clicked.connect(self.create_folder_struct)
 
        self.layout.addWidget(fsw)

        self.textbox_whereimport = QLineEdit()
        self.textbox_whereimport.setPlaceholderText('Enter Unreal folder to import into and distribute. (Ex: Assets or Characters/Amka)')
        self.layout.addWidget(self.textbox_whereimport)

        self.button_importassets = QPushButton('Import Assets') 
        self.layout.addWidget(self.button_importassets)
        self.button_importassets.clicked.connect(self.import_assets)


        self.button_createMI = QPushButton('Create Material Instances')
        self.layout.addWidget(self.button_createMI)
        self.button_createMI.clicked.connect(self.create_material_instance)

    def create_folder_struct(self):
        if self.textbox_foldername.text()!= '':
            mainfname = self.textbox_foldername.text()
            fs = FolderStruc('C:/Users/aimmaneni/Desktop/data.json',mainfname)


    def import_assets(self):        
        if (self.textbox_fs.text() != '' and self.textbox_whereimport.text() != ''):
            folder_path = self.textbox_fs.text()
            unreal_folder = "/Game/"+self.textbox_whereimport.text()+"/"
            aiobj = AssetImport(unreal_folder,folder_path)
            disdir = self.textbox_whereimport.text()
            adobj = AssetDistrib(disdir,disdir)
            
        else:
            print('Please insert import path')

    def file_dialog(self):
        self.folder = str(QFileDialog.getExistingDirectory())
        self.textbox_fs.setText(self.folder)
    
    def create_material_instance(self):
        materialsdir = "/Game/"+self.textbox_whereimport.text()+"/Materials"
        texdir = "/Game/"+self.textbox_whereimport.text()+"/Textures"
        meshdir = "/Game/"+self.textbox_whereimport.text()+"/Meshes"
        miobj = MaterialInstanceCreator(materialsdir,'/Game/Material/M_Master.M_Master',texdir,meshdir)

app = QApplication(sys.argv)

window = MainWindow()
winid = window.winId()
window.show()
unreal.parent_external_window_to_slate(winid)
app.exec_()