import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import ".." as UM

Item {
    id: base;

    property string name;
    property variant value;
    property string unit;

    property variant model;
    property int valid;
    property int index;
    property variant key;

    property alias control: controlContainer.children;

    RowLayout
    {
        anchors.fill: parent;
        spacing: UM.Styles.defaultMargin;

        Label
        {
            id: label;

            text: base.name
            Layout.fillWidth: true;
            horizontalAlignment: Text.AlignRight;
            fontSizeMode: Text.HorizontalFit;
            minimumPointSize: UM.Styles.smallTextSize;
            elide: Text.ElideRight;
        }

        Item {
            id: controlContainer;

            Layout.fillHeight: true
            width: base.width * 0.4;
        }
    }
}
