import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

import "."

Rectangle {
    id: base;

    color: UM.Theme.primaryColor;
    height: UM.Theme.toolbarHeight;

    property Action undo;
    property Action redo;
    property Action settings;

    Rectangle 
    {
        anchors {
            bottom: parent.bottom;
            left: parent.left;
            right: parent.right;
        }

        height: UM.Theme.toolbarBorderSize;
        color: UM.Theme.toolbarBorderColor;
    }

    RowLayout 
    {
        anchors.fill: parent;
        spacing: 0;

        Item 
        {
            width: UM.Theme.panelWidth / 2 ;
            Image 
            { 
                anchors.centerIn: parent;
                source: UM.Resources.getIcon("scantastic_logo.png");
            }
        }
        Label 
        {
            text: "SCAN";
            font.pointSize: UM.Theme.largeTextSize;
            font.capitalization: Font.AllUppercase;
            font.bold: true
            color: "white"
            width: UM.Theme.panelWidth /2;
        }

    
        ExclusiveGroup {id:toolbarTabGroup}
        Button 
        {
            id: setupButton
            text: qsTr("Setup")
            checkable: true
            exclusiveGroup: toolbarTabGroup
            style: ToolBarButtonStyleScan
            {
                numCircles:2
                beginState:0
                state:UM.ToolbarData.state
            }
            onClicked: {UM.ToolbarData.setState(1)}
        }
        Button 
        {
            id: calibrateButton
            text: qsTr("Calibrate")
            checkable: true
            exclusiveGroup: toolbarTabGroup
            style: ToolBarButtonStyleScan
            {
                beginState:2 
                numCircles:4
                   
                state:UM.ToolbarData.state
            }
            onClicked: {UM.ToolbarData.setState(3)}
        }
        
        Button 
        {
            id: objectButton
            text: qsTr("Object")
            checkable: true
            exclusiveGroup: toolbarTabGroup
            style: ToolBarButtonStyleScan
            {
                numCircles:2
                beginState:6
                state:UM.ToolbarData.state
            }
            onClicked: {UM.ToolbarData.setState(7)}
        }
        Button 
        {
            id: scanningButton
            text: qsTr("Scanning ")
            checkable: true
            exclusiveGroup: toolbarTabGroup
            style: ToolBarButtonStyleScan
            {
                numCircles:1
                beginState:7
                state:UM.ToolbarData.state
            }
            onClicked: {UM.ToolbarData.setState(8)}
        }
        
        Button 
        {
            id: editButton
            text: qsTr("Edit ")
            checkable: true
            exclusiveGroup: toolbarTabGroup
            style: ToolBarButtonStyleScan
            {
                numCircles:1
                beginState:8
                state:UM.ToolbarData.state
            }
            onClicked: {UM.ToolbarData.setState(9)}
        }
        Button 
        {
            id: exportButton
            text: qsTr("Export ")
            checkable: true
            exclusiveGroup: toolbarTabGroup
            style: ToolBarButtonStyleScan
            {
                numCircles:1
                beginState:10
                state:UM.ToolbarData.state
            }
            onClicked: {UM.ToolbarData.setState(11)}
        }
        
        Item { width: UM.Theme.windowRightMargin; }
    }
}