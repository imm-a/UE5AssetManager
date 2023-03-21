
import unreal
import sys
path = "C:/MyScripts"
if path not in sys.path:
    sys.path.append(path)

def main():
    print("Creating Menus!")
    menus = unreal.ToolMenus.get()
    main_menu = menus.find_menu("LevelEditor.MainMenu")
    if not main_menu:
        print("Failed to find the 'Main' menu. Something is wrong in the force!")

    entry = unreal.ToolMenuEntry(
                                name="Python.Tools",
                                type=unreal.MultiBlockType.MENU_ENTRY,
                                insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST)
    )
    entry.set_label("AMTool!")
    entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,'', string="import PMToolNewMI.py;")
    script_menu = main_menu.add_sub_menu(main_menu.get_name(), "PythonTools", "PyTool", "PyTools")

    script_menu.add_menu_entry("Scripts",entry)
    menus.refresh_all_widgets()


if __name__ == '__main__':
  main()