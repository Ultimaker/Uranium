// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1


import UM 1.0 as UM


Rectangle{
    id: toolTip
    property string text
    property int delay
    property int animationLength
    property int xPos
    property int yPos
    SystemPalette{id: palette}
    opacity: 0
    width: UM.Theme.getSize("tooltip").width
    x: xPos
    y: yPos

    function show(_text, _delay, _animationLength, _xPos, _yPos){
        toolTip.text = _text
        toolTip.delay = _delay
        toolTip.animationLength = _animationLength

        if (_xPos == undefined && _yPos == undefined){
            standardPlacement()
        }
        else {
            toolTip.xPos = _xPos + UM.Theme.getSize("default_margin").width
            toolTip.yPos = _yPos + UM.Theme.getSize("default_margin").height
        }
        toolTipTimer.restart()
    }

    function hide(_delay, _animationLength){
        toolTip.delay = _delay
        toolTip.animationLength = _animationLength
        toolTipTimer.restart()
    }

    function standardPlacement(){
        toolTip.anchors.top = base.top
        toolTip.anchors.topMargin = base.height - settingsScrollView.height
        toolTip.anchors.right = base.right
        toolTip.anchors.rightMargin = UM.Theme.getSize("default_margin").width
    }

    Timer {
        id: toolTipTimer
        repeat: false
        interval: toolTip.delay
        onTriggered: toolTip.opacity == 0 ? toolTip.opacity = 1 : toolTip.opacity = 0 //from opacty 0 to 1 and from 1 to 0
    }

    Behavior on opacity{
        NumberAnimation {
            alwaysRunToEnd: true;
            from: toolTip.opacity == 0 ? 0 : 1 //from 0 or 1
            to: toolTip.opacity == 0 ? 1 : 0 //to 1 or 0
            duration: toolTip.animationLength
        }
    }

    Label {
        width: parent.width - UM.Theme.getSize("default_margin").width
        wrapMode: Text.Wrap
        text: parent.text
        renderType: Text.NativeRendering
        color: palette.text
        Rectangle {
            //a rectangle is used for the background because the childrenRect property generates an unjustified binding loop
            z: parent.z - 1
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            width: UM.Theme.getSize("tooltip").width
            height: parent.height + UM.Theme.getSize("default_margin").width
            color: palette.light
            border.color: "black"
        }
    }
}
