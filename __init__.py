#==============================================================
#スタートアップ
#-------------------------------------------------------------------------------------------
import bpy #Blender内部のデータ構造にアクセスするために必要

from . import CommandRecorder as CommandRecorder
from . import DefineCommon as Common

#==============================================================
# プラグインに関する情報
#==============================================================
bl_info = {
"name" : "CommandRecorder",# プラグイン名
"author" : "BuuGraphic",# 作者
"version": (2, 0, 2),# プラグインのバージョン
"blender": (2, 80, 0),# プラグインが動作するBlenderのバージョン
"location" : "View 3D",# Blender内部でのプラグインの位置づけ
"description" : "Thank you for using our services",# プラグインの説明
"warning" : "",
"wiki_url" : "https://twitter.com/Sample_Mu03",# プラグインの説明が存在するWikiページのURL
"tracker_url" : "https://twitter.com/Sample_Mu03",# Blender Developer OrgのスレッドURL
'link': 'https://twitter.com/Sample_Mu03',
"category" : "System"# プラグインのカテゴリ名
}



#==============================================================
#レイアウト
#-------------------------------------------------------------------------------------------
# メニュー
class Muthird_UI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'# メニューを表示するエリア
    bl_region_type = 'TOOLS'# メニューを表示するリージョン
    bl_category = "CommandRecorder"# メニュータブのヘッダー名
    bl_label = "Information"# タイトル
    #-------------------------------------------------------------------------------------------
    #bl_context = "objectmode"# パネルを表示するコンテキスト
    Header_Icon = Common.CustomIcons("BuuLogo32.png" , "BUULOGO")
    def draw_header(self, context):
        self.layout.label(text = "", icon_value = self.Header_Icon)
    #メニューの描画処理
    def draw(self, context):
        self.layout.label(text="") #文字列表示するだけ



#==============================================================
# blenderへ登録
#==============================================================
Class_List = [
]
#Class_List.insert(0,Muthird_UI)
Class_List += CommandRecorder.Class_List

def register():
    for Temp in Class_List:
        bpy.utils.register_class(Temp)
    CommandRecorder.Initialize_Props()
    print("Register")

def unregister():
    for Temp in Class_List:
        bpy.utils.unregister_class(Temp)
    CommandRecorder.Clear_Props()
    print("UnRegister")



if __name__ == "__main__":
    register()
