import QtQuick 2.1
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
            ToolButton { text: "Undo"; onClicked: UM.OperationStack.undo(); }
            ToolButton { text: "Redo"; onClicked: UM.OperationStack.redo(); }

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

    PreferencesDialog { id: preferences }
}
