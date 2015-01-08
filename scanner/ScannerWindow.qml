import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

UM.MainWindow {
    id: base
    visible: true

    width: 1024
    height: 768

    Item {
        id: backgroundItem;
        anchors.fill: parent;

        UM.ApplicationMenu {
            id: menu
            window: base

            Menu {
                title: '&File';

                MenuItem { action: loadFileAction; }
                MenuItem { action: saveFileAction; }

                MenuSeparator { }

                MenuItem { action: quitAction; }
            }

            Menu {
                title: '&Edit';

                MenuItem { action: undoAction; }
                MenuItem { action: redoAction; }
                MenuSeparator { }
                MenuItem { action: deleteAction; }
                MenuItem { action: deleteAllAction; }
            }

            Menu {
                title: "&Machine";

                MenuSeparator { }
                MenuItem { text: "Add new machine..."; enabled: false; }
            }

            Menu {
                title: 'E&xtensions';

                MenuItem { text: "No extensions loaded"; enabled: false; }
            }

            Menu {
                title: '&Settings';

                MenuItem { action: preferencesAction; }
            }

            Menu {
                title: '&Help';

                MenuItem { action: helpAction; enabled: false; }
                MenuItem { action: aboutAction; enabled: false; }
            }
        }

        Item {
            id: contentItem;

            y: menu.height
            width: parent.width;
            height: parent.height - menu.height;

            Keys.forwardTo: menu

            DropArea {
                anchors.fill: parent

                onDropped: {
                    if(drop.urls.length > 0) {
                        for(var i in drop.urls) {
                            UM.Controller.addMesh(drop.urls[i]);
                        }
                    }
                }
            }

            UM.MeshListPanel 
            {
                id: mesh_list_panel;
 
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
            }

            UM.Panel {
                anchors.top: parent.top
                anchors.left: parent.left

                contents: RowLayout {
                    ToolButton { action: undoAction }
                    ToolButton { action: redoAction }

                    Item { width: 10; }

                    ToolButton { text: "3D"; onClicked: UM.Scene.setActiveCamera('3d'); }
                    ToolButton { text: "Left"; onClicked: UM.Scene.setActiveCamera('left'); }
                    ToolButton { text: "Top"; onClicked: UM.Scene.setActiveCamera('top'); }
                    ToolButton { text: "Front"; onClicked: UM.Scene.setActiveCamera('front'); }
                }
            }

            UM.ToolPanel {
                anchors.top: parent.top;
                anchors.horizontalCenter: parent.horizontalCenter
            }

            UM.Panel {
                anchors.top: parent.top
                anchors.right: parent.right

                contents: RowLayout {
                    ComboBox {
                        model: UM.Models.viewModel

                        onCurrentIndexChanged: UM.Controller.setActiveView(model.items[currentIndex].text)
                    }

                    ToolButton { text: "Settings"; onClicked: preferences.visible = true; }
                    ToolButton { text: "Help"; }
                }
            }

            UM.SettingsPanel {
                anchors.right: parent.right;
                anchors.verticalCenter: parent.verticalCenter

                onSettingConfigurationRequested: {
                    preferences.visible = true;
                    preferences.setPage(1);
                }
            }

            UM.JobList { anchors.left: parent.left; anchors.bottom: parent.bottom; width: parent.width / 10; height: parent.height / 5; }
        }
    }

    UM.PreferencesDialog { id: preferences }

    Action {
        id: undoAction;
        text: "Undo";
        iconName: "edit-undo";
        shortcut: StandardKey.Undo;
        onTriggered: UM.OperationStack.undo();
        enabled: UM.OperationStack.canUndo;
    }

    Action {
        id: redoAction;
        text: "Redo";
        iconName: "edit-redo";
        shortcut: StandardKey.Redo;
        onTriggered: UM.OperationStack.redo();
        enabled: UM.OperationStack.canRedo;
    }

    Action {
        id: quitAction;
        text: "Quit";
        iconName: "application-exit";
        shortcut: StandardKey.Quit;
        onTriggered: Qt.quit();
    }

    Action {
        id: preferencesAction;
        text: "Preferences";
        iconName: "configure";
        onTriggered: preferences.visible = true;
    }

    Action {
        id: helpAction;
        text: "Show Manual";
        iconName: "help-contents";
        shortcut: StandardKey.Help;
    }

    Action {
        id: aboutAction;
        text: "About...";
        iconName: "help-about";
    }

    Action {
        id: deleteAction;
        text: "Delete Selection";
        iconName: "edit-delete";
        shortcut: StandardKey.Delete;
        onTriggered: UM.Controller.removeSelection();
    }

    Action {
        id: deleteAllAction;
        text: "Clear Build Platform";
        iconName: "edit-clear";
        enabled: false;
    }

    Action {
        id: loadFileAction;
        text: "Open...";
        iconName: "document-open";
        shortcut: StandardKey.Open;
        onTriggered: filePanel.openFile();
    }

    Action {
        id: saveFileAction;
        text: "Save...";
        iconName: "document-save";
        shortcut: StandardKey.Save;
        enabled: false;
    }

    Menu {
        id: contextMenu;

        MenuItem { action: deleteAction; }
    }
}
