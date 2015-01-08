import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

Panel {
    title: "Layers"

    contents: ColumnLayout 
    {
        Layout.preferredWidth: 200
        Layout.preferredHeight: 400

        TableView 
        {
            Layout.fillWidth: true
            Layout.fillHeight: true

            TableViewColumn { role: "text" }

            headerVisible: false

            model: ListModel 
            {
                id: fileModel
            }
        }

    }
}
