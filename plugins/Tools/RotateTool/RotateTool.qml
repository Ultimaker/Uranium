import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.0 as UM

Item {
    Button {
        id: resetRotationButton

        anchors.bottom: parent.bottom;

        //: Reset Rotation tool button
        text: qsTr('Reset')
        iconSource: UM.Theme.icons.rotate_reset;
        //: Reset Rotation tool button tooltip
        tooltip: qsTr("Reset the rotation of the current selection.");

        style: UM.Theme.styles.tool_button;

        onClicked: UM.ActiveTool.triggerAction('resetRotation');
    }

    CheckBox {
        anchors.left: resetRotationButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.bottom: parent.bottom;

        //: Snap Rotation checkbox
        text: qsTr("Snap Rotation");

        style: UM.Theme.styles.checkbox;

        checked: UM.ActiveTool.getProperty('RotationSnap');
        onClicked: UM.ActiveTool.setProperty('RotationSnap', checked);
    }
}
