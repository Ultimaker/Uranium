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
        anchors 
        {
            bottom: parent.bottom;
            left: parent.left;
            right: parent.right;
        }

        height: UM.Theme.toolbarBorderSize;
        color: UM.Theme.toolbarBorderColor;
    }

    RowLayout 
    {
        id:mainLayout
        anchors.fill: parent;
        spacing: 0;

        Item
        {
            width:100
            anchors.left:parent.left
            //anchors.verticalCenter:parent.verticalCenter
            anchors.top:parent.top
            height:parent.height
            RowLayout 
            {
                anchors.fill: parent;
                Image 
                { 
                    anchors.centerIn: parent;
                    source: UM.Resources.getIcon("scantastic_logo.png");
                }
                Rectangle 
                {
                    color: "black"
                    id:spacer1
                    width: 2
                    //height: parent.height - 15
                    anchors.left: logo.right
                    anchors.leftMargin :25
                    
                }
                Label 
                {
                    text: "SCAN";
                    font.pointSize: UM.Theme.largeTextSize;
                    font.capitalization: Font.AllUppercase;
                    font.bold: true
                    color: "white"
                    width: UM.Theme.panelWidth /2;
                    anchors.left:spacer1.right
                    anchors.leftMargin:25
                    
                }
            }
        }
        
        Item
        {
            anchors.horizontalCenter: parent.horizontalCenter;
            anchors.top:parent.top
            width:500
            ExclusiveGroup {id:toolbarTabGroup}
            RowLayout
            {
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
                    checked: UM.ToolbarData.state > 1 ? false : UM.ToolbarData.state < 2 ? false:true
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
                    checked: UM.ToolbarData.state > 6 ? false : UM.ToolbarData.state < 3 ? false:true
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
                    checked: UM.ToolbarData.state > 8 ? false : UM.ToolbarData.state < 7 ? false:true
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
                        beginState:8
                        state:UM.ToolbarData.state
                    }
                    checked: UM.ToolbarData.state == 9 ? true: false
                    onClicked: {UM.ToolbarData.setState(9)}
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
                        beginState:9
                        state:UM.ToolbarData.state
                    }
                    checked: UM.ToolbarData.state == 10 ? true:false
                    onClicked: {UM.ToolbarData.setState(10)}
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
                    checked: UM.ToolbarData.state == 11 ? true:false
                    onClicked: {UM.ToolbarData.setState(11)}
                }
            }
        }
        Item
        {
            anchors.right: parent.right;
            anchors.top:parent.top
            width:250
            height:parent.height
            RowLayout
            {
                anchors.fill: parent;
                Label
                {
                    id: stepCounterLabel
                    width: UM.Theme.panelWidth
                    text: UM.ToolbarData.state + "/11 step" 
                }
                Label 
                {
                    text: "Wizard"
                    font.bold:true
                }
                
                Switch 
                {
                }
                ToolButton{
                    iconSource: UM.Resources.getIcon("youmagine.png");
                    tooltip: "Youmagine integration"
                }
                ToolButton{
                    iconSource: UM.Resources.getIcon("settings.png");
                    tooltip: "Settings and preferences"
                }
            }
        }
        Item { width: UM.Theme.windowRightMargin; }
        
    }
}