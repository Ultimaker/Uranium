import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import Cura 1.0 as Cura

import "Settings"
import "Preferences"

Cura.MainWindow {
    id: base
    visible: true

    width: 1024
    height: 768

    FilePanel {
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
    }

    Panel {
        anchors.top: parent.top
        anchors.left: parent.left

        title: "Camera"

        contents: RowLayout {
            ToolButton { text: "3D"; onClicked: Cura.Scene.setActiveCamera('3d'); }
            ToolButton { text: "Left"; onClicked: Cura.Scene.setActiveCamera('left'); }
            ToolButton { text: "Top"; onClicked: Cura.Scene.setActiveCamera('top'); }
            ToolButton { text: "Front"; onClicked: Cura.Scene.setActiveCamera('front'); }
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
                model: Cura.Models.viewModel

                onCurrentIndexChanged: Cura.Controller.setActiveView(model.items[currentIndex].text)
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
