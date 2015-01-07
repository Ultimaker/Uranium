import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

import "Settings"
import "Preferences"

UM.MainWindow {
    id: base
    visible: true

    width: 1024
    height: 768

    Item {
        id: backgroundItem;
        anchors.fill: parent;

        ApplicationMenu {
            id: menu
            window: base

            Menu {
                title: '&File';

                MenuItem { action: quitAction; }
            }

            Menu {
                title: '&Edit';

                MenuItem { action: undoAction; }
                MenuItem { action: redoAction; }
            }

            Menu {
                title: '&View';

            }

            Menu {
                title: '&Extensions';
            }

            Menu {
                title: '&Settings';
            }

            Menu {
                title: '&Help';

                MenuItem { action: helpAction; }
                MenuItem { text: '&About'; }
            }
        }

        Item {
            id: contentItem;

            y: menu.height
            width: parent.width;
            height: parent.height - menu.height;

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

            FilePanel {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
            }

            Panel {
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

            ToolPanel {
                anchors.top: parent.top;
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Panel {
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

            SettingsPanel {
                anchors.right: parent.right;
                anchors.verticalCenter: parent.verticalCenter

                onSettingConfigurationRequested: {
                    preferences.visible = true;
                    preferences.setPage(1);
                }
            }

            JobList { anchors.left: parent.left; anchors.bottom: parent.bottom; width: parent.width / 10; height: parent.height / 5; }
        }
    }

    PreferencesDialog { id: preferences }

    Action {
        id: undoAction;
        text: "&Undo";
        iconName: "edit-undo";
        shortcut: StandardKey.Undo;
        onTriggered: UM.OperationStack.undo();
        enabled: UM.OperationStack.canUndo;
    }

    Action {
        id: redoAction;
        text: "&Redo";
        iconName: "edit-redo";
        shortcut: StandardKey.Redo;
        onTriggered: UM.OperationStack.redo();
        enabled: UM.OperationStack.canRedo;
    }

    Action {
        id: quitAction;
        text: "&Quit";
        iconName: "quit";
        shortcut: StandardKey.Quit;
        onTriggered: Qt.quit();
    }

    Action {
        id: helpAction;
        text: "Show &Manual";
        iconName: "help";
        shortcut: StandardKey.Help;
    }
}
