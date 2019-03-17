#==============================================================
#スタートアップ
#-------------------------------------------------------------------------------------------
import bpy #Blender内部のデータ構造にアクセスするために必要
import os

from bpy.props import\
(#プロパティを使用するために必要
StringProperty,
BoolProperty,
IntProperty,
FloatProperty,
EnumProperty,
PointerProperty,
CollectionProperty
)
from bpy.types import\
(
Panel,
UIList,
Operator,
PropertyGroup
)


from . import DefineCommon as Common


#==============================================================
#使用クラスの宣言
#-------------------------------------------------------------------------------------------
class CR_OT_String(PropertyGroup):#リストデータを保持するためのプロパティグループを作成
    Command : StringProperty(
    default=""
    ) #CR_Var.name


class CR_List_Selector(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        layout.label(text = item.name)
class CR_List_Command(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        layout.label(text = item.name)
class CR_List_Instance(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,active_propname, index):
        layout.label(text = item.name)


#-------------------------------------------------------------------------------------------

def CR_(Data , Num):
    scene = bpy.context.scene
    if Data == "List" :
        return eval("scene.CR_Var.List_Command_{0:03d}".format(Num))
    elif Data == "Index" :
        return eval("scene.CR_Var.List_Index_{0:03d}".format(Num))
    else :
        exec("scene.CR_Var.List_Index_{0:03d} = {1}".format(Num,Data))


def Get_Recent(Return_Bool):#操作履歴にアクセス
    #remove other Recent Reports
    reports = \
    [
    bpy.data.texts.remove(t, do_unlink=True)
    for t in bpy.data.texts
        if t.name.startswith("Recent Reports")
    ]
    # make a report
    bpy.ops.ui.reports_to_textblock()
    # print the report
    if Return_Bool == "Reports_All":
        return bpy.data.texts["Recent Reports"].lines#操作履歴全ての行
    elif Return_Bool == "Reports_Length":
        return len(bpy.data.texts["Recent Reports"].lines)#操作履歴の要素数


def Record(Num , Mode):
    if Mode == "Start" :
        CR_PT_List.Bool_Record = 1
        CR_Prop.Temp_Num = len(Get_Recent("Reports_All"))
    else :
        CR_PT_List.Bool_Record = 0
        for Num_Loop in range (CR_Prop.Temp_Num+1 , len(Get_Recent("Reports_All"))) :
            TempText = Get_Recent("Reports_All")[Num_Loop-1].body
            if TempText.count("bpy") :
                Item = CR_("List",Num).add()
                Item.name = TempText[TempText.find("bpy"):]


def Add(Num) :
    if Num or len(CR_("List",0)) < 250 :
        Item = CR_("List",Num).add()
        if Num :
            if Get_Recent("Reports_All")[-2].body.count("bpy"):
                Name_Temp = Get_Recent("Reports_All")[-2].body
                Item.name = Name_Temp[Name_Temp.find("bpy"):]
            else :
                Name_Temp = Get_Recent("Reports_All")[-3].body
                Item.name = Name_Temp[Name_Temp.find("bpy."):]
        else :
            Item.name = "Untitled_{0:03d}".format(len(CR_("List",Num)))
        CR_( len(CR_("List",Num))-1 , Num )


def Remove(Num) :
    if not Num :
        for Num_Loop in range(CR_("Index",0)+1 , len(CR_("List",0))+1) :
            CR_("List",Num_Loop).clear()
            for Num_Command in range(len(CR_("List",Num_Loop+1))) :
                Item = CR_("List",Num_Loop).add()
                Item.name = CR_("List",Num_Loop+1)[Num_Command].name
            CR_(CR_("Index",Num_Loop+1),Num_Loop)
    if len(CR_("List",Num)):
        CR_("List",Num).remove(CR_("Index",Num))
        if len(CR_("List",Num)) - 1 < CR_("Index",Num):
            CR_(len(CR_("List",Num))-1,Num)
            if CR_("Index",Num) < 0:
                CR_(0,Num)


def Move(Num , Mode) :
    index1 = CR_("Index",Num)
    if Mode == "Up" :
        index2 = CR_("Index",Num) - 1
    else :
        index2 = CR_("Index",Num) + 1
    LengthTemp = len(CR_("List",Num))
    if (2 <= LengthTemp) and (0 <= index1 < LengthTemp) and (0 <= index2 <LengthTemp):
        CR_("List",Num).move(index1, index2)
        CR_(index2 , Num)

        #コマンドの入れ替え処理
        if not Num :
            index1 += 1
            index2 += 1
            CR_("List",254).clear()
            #254にIndex2を逃がす
            for Num_Command in CR_("List",index2) :
                Item = CR_("List",254).add()
                Item.name = Num_Command.name
            CR_(CR_("Index",index2),254)
            CR_("List",index2).clear()
            #Index1からIndex2へ
            for Num_Command in CR_("List",index1) :
                Item = CR_("List",index2).add()
                Item.name = Num_Command.name
            CR_(CR_("Index",index1),index2)
            CR_("List",index1).clear()
            #254からIndex1へ
            for Num_Command in CR_("List",254) :
                Item = CR_("List",index1).add()
                Item.name = Num_Command.name
            CR_(CR_("Index",254),index1)
            CR_("List",254).clear()


def Play(Commands) :
    scene = bpy.context.scene
    if scene.CR_Var.Target_Switch == "Once":
        for Command in Commands :
            if type(Command) == str :
                exec(Command)
            else :
                exec(Command.name)
    else :
        current_mode = bpy.context.mode
        Set_DeSelect = ""
        Set_Select = []
        Set_Active = []
        if current_mode == "OBJECT":
            Set_DeSelect = ("bpy.ops.object.select_all(action='DESELECT')")
            for Target in bpy.context.selected_objects :
                Set_Select.append("bpy.data.objects['{0}'].select = True".format(Target.name))
                Set_Active.append("bpy.context.scene.objects.active = bpy.data.objects['{0}']".format(Target.name))
        elif current_mode == "EDIT_MESH":
            pass

        elif current_mode == "EDIT_ARMATURE":
            Arm = bpy.context.scene.objects.active.name
            Set_DeSelect = ("bpy.ops.armature.select_all(action='DESELECT')")
            for Target in bpy.context.selected_editable_bones :
                Set_Select.append("bpy.data.objects['{0}'].data.edit_bones['{1}'].select = True".format(Arm , Target.name))
                Set_Active.append("bpy.data.objects['{0}'].data.edit_bones.active = bpy.data.objects['{0}'].data.edit_bones['{1}']".format(Arm , Target.name))

        elif current_mode == "POSE":
            Arm = bpy.context.scene.objects.active.name
            Set_DeSelect = ("bpy.ops.pose.select_all(action='DESELECT')")
            for Target in bpy.context.selected_pose_bones :
                print("a")
                Set_Select.append("bpy.data.objects['{0}'].pose.bones['{1}'].bone.select = True".format(Arm , Target.name))
                Set_Active.append("bpy.data.objects['{0}'].data.bones.active = bpy.data.objects['{0}'].data.bones['{1}']".format(Arm , Target.name))

        for Num_Loop in range(len(Set_Select)) :
            print(Set_DeSelect)
            print(Set_Select[Num_Loop])
            print(Set_Active[Num_Loop])
            exec(Set_DeSelect)
            exec(Set_Select[Num_Loop])
            exec(Set_Active[Num_Loop])
            if current_mode == "EDIT_ARMATURE" :
                bpy.ops.object.mode_set(mode='POSE')
                bpy.ops.object.mode_set(mode='EDIT')
            for Command in Commands :
                if type(Command) == str :
                    exec(Command)
                else :
                    exec(Command.name)

def Clear(Num) :
    CR_("List",Num).clear()


class CR_OT_Selector(Operator):
    bl_idname = "cr_selector.button"#大文字禁止
    bl_label = "Button_Selector"#メニューに登録される名前
    bl_options = {'REGISTER', 'UNDO'} # 処理の属性
    Mode : bpy.props.StringProperty(default="")
    def execute(self, context):
        #追加
        if self.Mode == "Add" :
            Add(0)
        #削除
        elif self.Mode == "Remove" :
            Remove(0)
        #上へ
        elif self.Mode == "Up" :
            Move(0 , "Up")
        #下へ
        elif self.Mode == "Down" :
            Move(0 , "Down")
        bpy.context.area.tag_redraw()
        return{'FINISHED'}#UI系の関数の最後には必ず付ける


class Command_OT_Play(Operator):
    bl_idname = "cr_commandplay.button"#大文字禁止
    bl_label = "Command_OT_Play"#メニューに登録される名前
    bl_options = {'REGISTER', 'UNDO'}#アンドゥ履歴に登録
    def execute(self, context):
        #コマンドを実行
        Play(CR_("List",CR_("Index",0)+1))
        return{'FINISHED'}#UI系の関数の最後には必ず付ける



class Command_OT_Add(Operator):
    bl_idname = "cr_commandadd.button"#大文字禁止
    bl_label = "Command_OT_Add"#メニューに登録される名前
    bl_options = {'REGISTER', 'UNDO'}#アンドゥ履歴に登録
    def execute(self, context):
        #コマンドを実行
        Add(CR_("Index",0)+1)
        bpy.context.area.tag_redraw()
        return{'FINISHED'}#UI系の関数の最後には必ず付ける

class CR_OT_Command(Operator):
    bl_idname = "cr_command.button"#大文字禁止
    bl_label = "Button_Command"#メニューに登録される名前
    bl_options = {'REGISTER', 'UNDO'} # 処理の属性
    Mode : bpy.props.StringProperty(default="")
    def execute(self, context):
        #録画を開始
        if self.Mode == "Record_Start" :
            Record(CR_("Index",0)+1 , "Start")
        #録画を終了
        elif self.Mode == "Record_Stop" :
            Record(CR_("Index",0)+1 , "Stop")
        #追加
        elif self.Mode == "Add" :
            Add(CR_("Index",0)+1)
        #削除
        elif self.Mode == "Remove" :
            Remove(CR_("Index",0)+1)
        #上へ
        elif self.Mode == "Up" :
            Move(CR_("Index",0)+1 , "Up")
        #下へ
        elif self.Mode == "Down" :
            Move(CR_("Index",0)+1 , "Down")
        #リストをクリア
        elif self.Mode == "Clear" :
            Clear(CR_("Index",0)+1)

        bpy.context.area.tag_redraw()
        return{'FINISHED'}#UI系の関数の最後には必ず付ける




def StrageFile() :
    Name_File = "CommandRecorder_Storage.txt"
    AddonDirector = os.path.dirname(os.path.abspath(__file__))#アドオン管理システムの絶対パスを取得
    File_Path = os.path.normpath(os.path.join(AddonDirector, '../CommandRecorder/Storage/' + Name_File))
    return File_Path

def Save():
    scene = bpy.context.scene
    File = open(StrageFile() , "w")#書き込みモードでファイルを開く
    Names = scene.CR_Var.Instance_Name
    Commands = scene.CR_Var.Instance_Command
    for Num_Loop in range(len(Names)):
        File.write("CR_Name" + '\n' + Names[Num_Loop] + '\n')
        File.write("CR_Command" + '\n')
        for Command in Commands[Num_Loop]:
            File.write(Command + '\n')
        File.write("CR_End" + '\n\n')
    File.close()#ファイルを閉じる

def Load():
    scene = bpy.context.scene
    File = open(StrageFile() , 'r')#読み込みモードでファイルを開く
    List = []
    for Line in File:
        List.append(Line.replace('\n',''))
    File.close()#ファイルを閉じる

    Bool_Command = 0
    Temp_Command = []
    Num_Count = 0
    scene.CR_Var.Instance_Name.clear()
    scene.CR_Var.Instance_Command.clear()
    for Num_Loop in range(len(List)) :
        if List[Num_Loop] == "CR_Name" :
            scene.CR_Var.Instance_Name.append(List[Num_Loop+1])
        elif List[Num_Loop] == "CR_Command" :
            Bool_Command = 1
        elif List[Num_Loop] == "CR_End" :
            Bool_Command = 0
            scene.CR_Var.Instance_Command.append(Temp_Command)
            Temp_Command = []
            Num_Count += 1
        if Bool_Command > 0:
            if Bool_Command > 1 :
                Temp_Command.append(List[Num_Loop])
            Bool_Command += 1


def Recorder_to_Instance():
    CR_Prop.Instance_Name.append(CR_("List",0)[CR_("Index",0)].name)
    Temp_Command = []
    for Command in CR_("List",CR_("Index",0)+1):
        Temp_Command.append(Command.name)
    CR_Prop.Instance_Command.append(Temp_Command)


def Instance_to_Recorder():
    scene = bpy.context.scene
    Item = CR_("List" , 0 ).add()
    Item.name = CR_Prop.Instance_Name[int(scene.CR_Var.Instance_Index)]
    for Command in CR_Prop.Instance_Command[int(scene.CR_Var.Instance_Index)] :
        Item = CR_("List" , len(CR_("List",0)) ).add()
        Item.name = Command
    CR_( len(CR_("List",0))-1 , 0 )


def Execute_Instance(Num):
    Play(CR_Prop.Instance_Command[Num])


def Rename_Instance():
    scene = bpy.context.scene
    CR_Prop.Instance_Name[int(scene.CR_Var.Instance_Index)] = scene.CR_Var.Rename


def I_Remove():
    scene = bpy.context.scene
    if len(CR_Prop.Instance_Name) :
        Index = int(scene.CR_Var.Instance_Index)
        CR_Prop.Instance_Name.pop(Index)
        CR_Prop.Instance_Command.pop(Index)
        if len(CR_Prop.Instance_Name) and len(CR_Prop.Instance_Name)-1 < Index :
            scene.CR_Var.Instance_Index = str(len(CR_Prop.Instance_Name)-1)


def I_Move(Mode):
    scene = bpy.context.scene
    index1 = int(scene.CR_Var.Instance_Index)
    if Mode == "Up" :
        index2 = int(scene.CR_Var.Instance_Index) - 1
    else :
        index2 = int(scene.CR_Var.Instance_Index) + 1
    LengthTemp = len(CR_Prop.Instance_Name)
    if (2 <= LengthTemp) and (0 <= index1 < LengthTemp) and (0 <= index2 <LengthTemp):
        CR_Prop.Instance_Name[index1] , CR_Prop.Instance_Name[index2] = CR_Prop.Instance_Name[index2] , CR_Prop.Instance_Name[index1]
        CR_Prop.Instance_Command[index1] , CR_Prop.Instance_Command[index2] = CR_Prop.Instance_Command[index2] , CR_Prop.Instance_Command[index1]
        scene.CR_Var.Instance_Index = str(index2)



class CR_OT_Instance(Operator):
    bl_idname = "cr_instance.button"#大文字禁止
    bl_label = "Button_Instance"#メニューに登録される名前
    bl_options = {'REGISTER', 'UNDO'} # 処理の属性
    Mode : bpy.props.StringProperty(default="")
    def execute(self, context):
        #追加
        if self.Mode == "Add" :
            Add(255)
        #削除
        elif self.Mode == "Remove" :
            Remove(255)
        #上へ
        elif self.Mode == "Up" :
            Up(255)
        #下へ
        elif self.Mode == "Down" :
            Down(255)

        #保存
        elif self.Mode == "Save" :
            Save()
        #読み込み
        elif self.Mode == "Load" :
            Load()
        #コマンドをインスタンスに
        elif self.Mode == "Recorder_to_Instance" :
            Recorder_to_Instance()
        #インスタンスをコマンドに
        elif self.Mode == "Instance_to_Recorder" :
            Instance_to_Recorder()
        #削除
        elif self.Mode == "I_Remove" :
            I_Remove()
        #上へ
        elif self.Mode == "I_Up" :
            I_Move("Up")
        #下へ
        elif self.Mode == "I_Down" :
            I_Move("Down")
        #インスタンスのリネーム
        elif self.Mode == "Rename" :
            Rename_Instance()
        #インスタンスを実行
        else :
            Execute_Instance(CR_Prop.Instance_Name.index(self.Mode))

        bpy.context.area.tag_redraw()
        return{'FINISHED'}#UI系の関数の最後には必ず付ける


def Recent_Switch(Mode):
    if Mode == "Standard" :
        bpy.app.debug_wm = 0
    else :
        bpy.app.debug_wm = 1
    CR_PT_List.Bool_Recent = Mode


#==============================================================
#レイアウト
#-------------------------------------------------------------------------------------------
# メニュー
class CR_PT_List(bpy.types.Panel):
    bl_region_type = 'UI'# メニューを表示するリージョン
    bl_category = "CommandRecorder"# メニュータブのヘッダー名
    bl_label = "CommandRecorder"# タイトル
    #変数の宣言
    #-------------------------------------------------------------------------------------------
    Bool_Record = 0
    Bool_Recent = ""

    #レイアウト
    #-------------------------------------------------------------------------------------------
    def draw_header(self, context):
        self.layout.label(text = "", icon = "REC")
    #メニューの描画処理
    def draw(self, context):
        scene = bpy.context.scene
        #-------------------------------------------------------------------------------------------
        layout = self.layout
        box = layout.box()
        box_row = box.row()
        box_row.label(text = "", icon = "SETTINGS")
        if len(CR_("List",0)) :
            box_row.prop(CR_("List",0)[CR_("Index",0)] , "name" , text="")
        box_row = box.row()
        col = box_row.column()
        col.template_list("CR_List_Selector" , "" , scene.CR_Var , "List_Command_000" , scene.CR_Var , "List_Index_000", rows=4)
        col = box_row.column()
        col.operator(CR_OT_Selector.bl_idname , text="" , icon="ADD" ).Mode = "Add"
        col.operator(CR_OT_Selector.bl_idname , text="" , icon="REMOVE" ).Mode = "Remove"
        col.operator(CR_OT_Selector.bl_idname , text="" , icon="TRIA_UP" ).Mode = "Up"
        col.operator(CR_OT_Selector.bl_idname , text="" , icon="TRIA_DOWN" ).Mode = "Down"
        #
        if len(CR_("List",0)) :
            box_row = box.row()
            box_row.label(text = "", icon = "TEXT")
            if len(CR_("List",CR_("Index",0)+1)) :
                box_row.prop(CR_("List",CR_("Index",0)+1)[CR_("Index",CR_("Index",0)+1)],"name" , text="")
            box_row = box.row()
            col = box_row.column()
            col.template_list("CR_List_Command" , "" , scene.CR_Var , "List_Command_{0:03d}".format(CR_("Index",0)+1) , scene.CR_Var , "List_Index_{0:03d}".format(CR_("Index",0)+1), rows=4)
            col = box_row.column()
            if CR_PT_List.Bool_Record :
                col.operator(CR_OT_Command.bl_idname , text="" , icon="PAUSE" ).Mode = "Record_Stop"
            else :
                col.operator(CR_OT_Command.bl_idname , text="" , icon="REC" ).Mode = "Record_Start"
                col.operator(Command_OT_Add.bl_idname , text="" , icon="ADD" )
                col.operator(CR_OT_Command.bl_idname , text="" , icon="REMOVE" ).Mode = "Remove"
                col.operator(CR_OT_Command.bl_idname , text="" , icon="TRIA_UP" ).Mode = "Up"
                col.operator(CR_OT_Command.bl_idname , text="" , icon="TRIA_DOWN" ).Mode = "Down"
            if len(CR_("List",CR_("Index",0)+1)) :
                box.operator(Command_OT_Play.bl_idname , text="Play" )
                box.operator(CR_OT_Instance.bl_idname , text="Recorder to Button" ).Mode = "Recorder_to_Instance"
                box.operator(CR_OT_Command.bl_idname , text="Clear").Mode = "Clear"
        box = layout.box()
        box.label(text = "Options", icon = "PRESET_NEW")
        #box_row = box.row()
        #box_row.label(text = "Target")
        #box_row.prop(scene.CR_Var, "Target_Switch" ,expand = 1)
        box_row = box.row()
        box_row.label(text = "History")
        box_row.prop(scene.CR_Var, "Recent_Switch" ,expand = 1)
        if not(CR_PT_List.Bool_Recent == scene.CR_Var.Recent_Switch) :
            Recent_Switch(scene.CR_Var.Recent_Switch)


class CR_PT_Instance(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'# メニューを表示するエリア
    bl_region_type = 'UI'# メニューを表示するリージョン
    bl_category = "CommandRecorder"# メニュータブのヘッダー名
    bl_label = "CommandButton"# タイトル
    #変数の宣言
    #-------------------------------------------------------------------------------------------
    StartUp = 0
    SelectedInctance = ""
    #レイアウト
    #-------------------------------------------------------------------------------------------
    def draw_header(self, context):
        self.layout.label(text = "", icon = "PREFERENCES")
    #メニューの描画処理
    def draw(self, context):
        if CR_PT_Instance.StartUp == 0:
            Load()
            CR_PT_Instance.StartUp = 1
        scene = bpy.context.scene
        #-------------------------------------------------------------------------------------------
        layout = self.layout
        #

        box = layout.box()
        box.operator(CR_OT_Instance.bl_idname , text="Button to Recorder" ).Mode = "Instance_to_Recorder"
        box_split = box.split(factor=0.2)
        box_col = box_split.column()
        box_col.prop(scene.CR_Var, "Instance_Index" ,expand = 1)
        box_col = box_split.column()
        box_col.scale_y = 0.9493
        for Num_Loop in range(len(CR_Prop.Instance_Name)) :
            box_col.operator(CR_OT_Instance.bl_idname , text=CR_Prop.Instance_Name[Num_Loop]).Mode = CR_Prop.Instance_Name[Num_Loop]
        if len(CR_Prop.Instance_Name) :
            box_row = box.row()
            box_row.operator(CR_OT_Instance.bl_idname , text="" , icon="REMOVE" ).Mode = "I_Remove"
            box_row.operator(CR_OT_Instance.bl_idname , text="" , icon="TRIA_UP" ).Mode = "I_Up"
            box_row.operator(CR_OT_Instance.bl_idname , text="" , icon="TRIA_DOWN" ).Mode = "I_Down"
            box_row.prop(scene.CR_Var , "Rename" , text="")
            box_row.operator(CR_OT_Instance.bl_idname , text="Rename").Mode = "Rename"
        box = layout.box()
        box.operator(CR_OT_Instance.bl_idname , text="Save to File" ).Mode = "Save"
        box.operator(CR_OT_Instance.bl_idname , text="Load from File" ).Mode = "Load"



class CR_List_PT_VIEW_3D(CR_PT_List):
    bl_space_type = 'VIEW_3D'# メニューを表示するエリア
class CR_PT_Instance_VIEW_3D(CR_PT_Instance):
    bl_space_type = 'VIEW_3D'# メニューを表示するエリア
class CR_List_PT_IMAGE_EDITOR(CR_PT_List):
    bl_space_type = 'IMAGE_EDITOR'
class CR_PT_Instance_IMAGE_EDITOR(CR_PT_Instance):
    bl_space_type = 'IMAGE_EDITOR'


def Num_Instance_Updater(self, context):
     items = []
     for Num_Loop in range(len(CR_Prop.Instance_Name)):
        items.append((str(Num_Loop) , "{0}".format(Num_Loop+1) , ""))
     return items

class CR_Prop(PropertyGroup):#何かとプロパティを収納
    Rename : StringProperty(
    ) #CR_Var.name

    Instance_Name = []
    Instance_Command = []

    Instance_Index : EnumProperty(
    items = Num_Instance_Updater
    )
    #コマンド切り替え
    Target_Switch : EnumProperty(
    items = [
    ("Once" , "Once" , ""),
    ("Each" , "Each" , ""),
    ])
    #履歴の詳細
    Recent_Switch : EnumProperty(
    items = [
    ("Standard" , "Standard" , ""),
    ("Extend" , "Extend" , ""),
    ])
    Temp_Command = []
    Temp_Num = 0
    for Num_Loop in range(256) :
        exec("List_Index_{0:03d} : IntProperty(default = 0)".format(Num_Loop))
        exec("List_Command_{0:03d} : CollectionProperty(type = CR_OT_String)".format(Num_Loop))

    #==============================================================
    # (キーが押されたときに実行する bpy.types.Operator のbl_idname, キー, イベント, Ctrlキー, Altキー, Shiftキー)
    addon_keymaps = []
    key_assign_list = \
    [
    (Command_OT_Add.bl_idname, "COMMA", "PRESS", False, False, True),
    (Command_OT_Play.bl_idname, "PERIOD", "PRESS", False, False, True),
    ]



#==============================================================
#プロパティの宣言
#-------------------------------------------------------------------------------------------
def Initialize_Props():# プロパティをセットする関数
    bpy.types.Scene.CR_Var = bpy.props.PointerProperty(type=CR_Prop)
    if bpy.context.window_manager.keyconfigs.addon:
        km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name="Window", space_type="EMPTY")#Nullとして登録
        CR_Prop.addon_keymaps.append(km)
        for (idname, key, event, ctrl, alt, shift) in CR_Prop.key_assign_list:
            kmi = km.keymap_items.new(idname, key, event, ctrl=ctrl, alt=alt, shift=shift)# ショートカットキーの登録

def Clear_Props():
    del bpy.types.Scene.CR_Var
    for km in CR_Prop.addon_keymaps:
        bpy.context.window_manager.keyconfigs.addon.keymaps.remove(km)
    CR_Prop.addon_keymaps.clear()



#==============================================================
#Blenderへ登録
#-------------------------------------------------------------------------------------------
#使用されているクラスを格納
Class_List = \
[
CR_OT_String,
CR_Prop,
CR_List_Selector,
CR_OT_Selector,
CR_List_Command,
Command_OT_Play,
Command_OT_Add,
CR_OT_Command,
CR_List_Instance,
CR_OT_Instance,
CR_List_PT_VIEW_3D,
CR_PT_Instance_VIEW_3D,
CR_List_PT_IMAGE_EDITOR,
CR_PT_Instance_IMAGE_EDITOR,
]
