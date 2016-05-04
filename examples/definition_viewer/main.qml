import QtQuick 2.4
import QtQuick.Controls 1.4
import QtQuick.Dialogs 1.2
import QtQuick.Layouts 1.0

import Example 1.0 as Example

ApplicationWindow
{
    visible: true
    width: 640
    height: 480

    toolBar: ToolBar
    {
        Row
        {
            anchors.fill: parent
            ToolButton { text: "Open"; onClicked: fileDialog.open() }
        }
    }

    SplitView
    {
        anchors.fill: parent
        orientation: Qt.Vertical

        TextArea
        {
            readOnly: true

            text: "<h2>Metadata</h2>\n" + loader.metaDataText
            textFormat: TextEdit.RichText
        }
        TreeView
        {
            TableViewColumn
            {
                title: "Key"
                role: "key"
            }
            TableViewColumn
            {
                title: "Label"
                role: "label"
            }
            TableViewColumn
            {
                title: "Type"
                role: "type"
            }
            TableViewColumn
            {
                title: "Description"
                role: "description"
            }
            TableViewColumn
            {
                title: "Default Value"
                role: "default_value"
            }
            TableViewColumn
            {
                title: "Warning Description"
                role: "warning_description"
            }
            TableViewColumn
            {
                title: "Error Description"
                role: "error_description"
            }
            TableViewColumn
            {
                title: "Value"
                role: "value"
            }
            TableViewColumn
            {
                title: "Minimum"
                role: "minimum_value"
            }
            TableViewColumn
            {
                title: "Maximum"
                role: "maximum_value"
            }
            TableViewColumn
            {
                title: "Minimum Warning"
                role: "minimum_value_warning"
            }
            TableViewColumn
            {
                title: "Maximum Warning"
                role: "maximum_value_warning"
            }
            TableViewColumn
            {
                title: "Enabled"
                role: "enabled"
            }






            Layout.fillHeight: true;
            model: Example.SettingDefinitionsModel { id: model }
        }
        TextArea
        {
            readOnly: true

            text: loader.errorText
        }
    }

    FileDialog
    {
        id: fileDialog

        onAccepted:
        {
            model.containerId = loader.load(fileUrl)
        }
    }

    Example.DefinitionLoader { id: loader }

    Component.onCompleted:
    {
        if(open_file != "")
        {
            model.containerId = loader.load(open_file)
        }
    }
}
