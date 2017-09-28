// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import UM 1.0 as UM

Item {
    property alias title: titleLabel.text;
    default property alias contents: contentsItem.children;
    property bool resetEnabled: true;

    function reset()
    {
        UM.Application.log("w", "No reset implemented!")
    }
    function boolCheck(value) //Hack to ensure a good match between python and qml.
    {
        if(value == "True")
        {
            return true
        }else if(value == "False" || value == undefined)
        {
            return false
        }
        else
        {
            return value
        }
    }

    Label {
        id: titleLabel;

        anchors {
            top: parent.top;
            left: parent.left;
            right: parent.right;
            margins: 5 * screenScaleFactor;
        }

        font.pointSize: 18;
    }

    Item {
        id: contentsItem;

        anchors {
            top: titleLabel.bottom;
            left: parent.left;
            right: parent.right;
            bottom: parent.bottom;
            margins: 5 * screenScaleFactor;
            bottomMargin: 0;
        }

        clip: true;
    }
}
