import QtQuick 2.4
import QtQuick.Controls 1.4
import QtQuick.Dialogs 1.2
import QtQuick.Layouts 1.0

import Example 1.0 as Example

ApplicationWindow
{
    visible: true
    width: 640 * screenScaleFactor
    height: 480 * screenScaleFactor

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
            id: metaDataText
            readOnly: true

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
                title: "Default Value"
                role: "default_value"
            }

            Layout.fillHeight: true;
            model: Example.DefinitionTreeModel { id: model; }

            onActivated:
            {
                var setting = model.get(index)
                detailsText.text = "<h2>%1</h2><ul>".arg(setting["key"])

                for(var i in setting)
                {
                    detailsText.text += "<li><b>%1:</b> %2".arg(i).arg(setting[i])
                }

                detailsText.text += "</ul>"
            }
        }
        TextArea
        {
            id: detailsText
            readOnly: true
            textFormat: TextEdit.AutoText
        }
    }

    FileDialog
    {
        id: fileDialog

        onAccepted:
        {
            loader.load(fileUrl)
        }
    }

    Example.DefinitionLoader
    {
        id: loader;

        onLoaded:
        {
            detailsText.text = ""
            metaDataText.text = ""

            var text = ""
            for(var i in loader.metaData)
            {
                text += "<li><b>%1:</b> %2</li>".arg(i).arg(loader.metaData[i])
            }

            if(text != "")
            {
                metaDataText.text = "<h2>Metadata</h2><ul>%1</ul>".arg(text)
            }

            model.containerId = loader.definitionId
        }
        onError: detailsText.text = errorText
    }

    Component.onCompleted:
    {
        if(open_file != undefined && open_file != "")
        {
            loader.load(open_file)
        }
    }
}
