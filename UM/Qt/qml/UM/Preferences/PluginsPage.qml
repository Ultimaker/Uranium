import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1
import QtQuick.Controls.Styles 1.1
import UM 1.0 as UM

PreferencesPage {
    //: Plugins configuration page
    title: qsTr("Plugins");
    contents: ScrollView 
    {
        anchors.fill: parent;
        ListView 
        {
            id:plugin_list
            delegate: pluginDelegate
            model: UM.Models.pluginsModel
            section.delegate: Label { text: section }
            section.property: "type"
        }
    }

    Component
    {
        id: pluginDelegate
        RowLayout 
        {
            CheckBox
            {
                text: model.name;
                x: 0
                Layout.minimumWidth: 50
                Layout.preferredWidth: 250
                checked: model.enabled
                onClicked: plugin_list.model.setEnabled(model.name, checked)
                enabled: !model.required 
            }
            ToolButton
            {
                style: ButtonStyle { }

                iconSource: UM.Resources.getPath(UM.Resources.ImagesLocation, "icon_info.png")

                onClicked:
                {
                    about_window.about_text = model.description
                    about_window.author_text = model.author
                    about_window.plugin_name = model.name
                    about_window.version_text = model.version
                    about_window.visibility = 1
                }
            }
        }
    }
    
    Window
    {
        id:about_window
        property variant about_text: "No text available"
        property variant author_text: "John doe"
        property variant plugin_name: ""
        property variant version_text: ""

        //: About dialog with info about plugin %1
        title: qsTr("About %1").arg(plugin_name)

        width: 150
        height:150

        ColumnLayout
        {
            Text 
            {
                text: about_window.plugin_name
                font.pointSize: 20
                color:"#404040"
            }
            Text 
            {
                text: about_window.about_text
            }
            Text 
            {
                text: about_window.author_text
            }
            Text
            {
                text: about_window.version_text
            }
            //: Close about plugin dialog
            Button {
                text: qsTr("Close");
                onClicked: about_window.visible = false;
            }
        }
    }
}
