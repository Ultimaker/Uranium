import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1
import UM 1.0 as UM
PreferencesPage {
    title: "Plugins"
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
                checked: model.enabled
                onClicked: plugin_list.model.setEnabled(model.name, checked)
                enabled: !model.required 
            }
            Button 
            {
                text:"i"
                onClicked:
                {
                    about_window.about_text = plugin_list.model.getAboutText(model.name)
                    about_window.author_text = plugin_list.model.getAuthorText(model.name)
                    about_window.plugin_name = model.name
                    about_window.version_text = plugin_list.model.getVersionText(model.name)
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
        title: "About " + plugin_name
        width: 150
        height:150
        ColumnLayout
        {
            Text 
            {
                text: about_window.about_text
                font.pointSize: 20
                color:"#404040"
            }
            Text 
            {
                text: about_window.author_text
            }
            Text
            {
                text: about_window.version_text
            }
        }
        
    }
}
