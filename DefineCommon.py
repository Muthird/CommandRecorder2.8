import bpy #Blender内部のデータ構造にアクセスするために必要
import os
import bpy.utils.previews

def CustomIcons(Name_File , Name_Icon) :
    custom_icons = bpy.utils.previews.new()
    AddonDirector = os.path.dirname(os.path.abspath(__file__))#アドオン管理システムの絶対パスを取得
    icons_dir = os.path.normpath(os.path.join(AddonDirector, '../CommandRecorder/Icons/'+Name_File))
    custom_icons.load(Name_Icon, icons_dir , 'IMAGE')
    return custom_icons[Name_Icon].icon_id
