import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.0 as UM

Item {
    Button {
        id: resetScaleButton

        anchors.bottom: parent.bottom;

        text: qsTr('Reset')
        iconSource: UM.Theme.icons.scale_reset;
        tooltip: qsTr("Reset the scaling of the current selection.");

        style: UM.Theme.styles.tool_button;

        onClicked: UM.ActiveTool.triggerAction('resetScale');
    }

    Button {
        id: scaleToMaxButotn

        text: qsTr('Scale to Max');
        iconSource: UM.Theme.icons.scale_max;
        tooltip: qsTr('Scale to maximum size');

        anchors.bottom: resetScaleButton.top;
        anchors.bottomMargin: UM.Theme.sizes.default_margin.height;

        style: UM.Theme.styles.tool_button;

        onClicked: UM.ActiveTool.triggerAction('scaleToMax')
    }

    CheckBox {
        id: snapCheckbox;

        anchors.left: resetScaleButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.bottom: parent.bottom;

        text: qsTr("Snap Scaling");

        style: UM.Theme.styles.checkbox;

        checked: UM.ActiveTool.getProperty('ScaleSnap');
        onClicked: UM.ActiveTool.setProperty('ScaleSnap', checked);
    }

    CheckBox {
        anchors.left: resetScaleButton.right;
        anchors.leftMargin: UM.Theme.sizes.default_margin.width;
        anchors.top: resetScaleButton.top;

        text: qsTr("Uniform Scaling");

        style: UM.Theme.styles.checkbox;

        checked: !UM.ActiveTool.getProperty('NonUniformScale');
        onClicked: UM.ActiveTool.setProperty('NonUniformScale', !checked);
    }
}

