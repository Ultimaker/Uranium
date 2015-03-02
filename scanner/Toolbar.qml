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
            Row
            {
                anchors.horizontalCenter:parent.horizontalCenter
                Layout.preferredWidth:500
                spacing:5
                //move: Transition {
                //    NumberAnimation { properties: "x,y"; }
                //}
                Button 
                {
                    id: setupButton
                    text: qsTr("Setup")
                    checkable: true
                    exclusiveGroup: toolbarTabGroup
                    style: ToolBarButtonStyleScan
                    {
                        numCircles: 2 
                        beginState:0
                        state:UM.ToolbarData.state
                    }
                    checked: UM.ToolbarData.state > 1 ? false : UM.ToolbarData.state < 2 ? false:true
                    onClicked: {UM.ToolbarData.setState(1)}
                    Behavior on opacity { NumberAnimation { } }
                    Behavior on width {NumberAnimation{}}
                    width: UM.ToolbarData.wizardActive ? 75: 0
                    opacity: UM.ToolbarData.wizardActive ? 1 : 0
                    
                }
                
                Button 
                {
                    id: calibrateButton
                    text: qsTr("Calibrate")
                    checkable: true
                    exclusiveGroup: toolbarTabGroup
                    style: ToolBarButtonStyleScan
                    {
                        numCircles: 5 
                        beginState:2    
                        state:UM.ToolbarData.state
                    }
                    checked: UM.ToolbarData.state > 7 ? false : UM.ToolbarData.state < 3 ? false:true
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
                        numCircles: 2 
                        beginState:7
                        state:UM.ToolbarData.state
                    }
                    checked: UM.ToolbarData.state == 9 ? true : UM.ToolbarData.state == 8 ? true:false
                    onClicked: {UM.ToolbarData.setState(8)}
                    Behavior on opacity { NumberAnimation { } }
                    Behavior on width {NumberAnimation{}}
                    width: UM.ToolbarData.wizardActive ? 75: 0
                    opacity: UM.ToolbarData.wizardActive ? 1 : 0
                }
                Button 
                {
                    id: scanningButton
                    text: qsTr("Scan ")
                    checkable: true

                    exclusiveGroup: toolbarTabGroup
                    style: ToolBarButtonStyleScan
                    {
                        numCircles: 1 
                        beginState:9
                        state:UM.ToolbarData.state
                    }
                    checked: UM.ToolbarData.state == 10 ? true: false
                    onClicked: {UM.ToolbarData.setState(10)}
                }
                
                Button 
                {
                    id: editButton
                    text: qsTr("Edit ")
                    checkable: true
                    exclusiveGroup: toolbarTabGroup
                    style: ToolBarButtonStyleScan
                    {
                        numCircles: 1 
                        beginState:10
                        state:UM.ToolbarData.state
                    }
                    checked: UM.ToolbarData.state == 11 ? true:false
                    onClicked: {UM.ToolbarData.setState(11)}
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
                        beginState:11
                        state:UM.ToolbarData.state
                    }
                    checked: UM.ToolbarData.state == 12 ? true:false
                    onClicked: {UM.ToolbarData.setState(12)}
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
                    visible: UM.ToolbarData.wizardActive
                }
                Label 
                {
                    id:wizardSwitchText
                    anchors.right:wizardSwitch.left
                    anchors.rightMargin:10
                    text: "Wizard"
                    font.bold:true
                }
                
                Switch 
                {
                    id:wizardSwitch
                    anchors.right:youmagineButton.left 
                    anchors.rightMargin:10
                    checked:UM.ToolbarData.wizardActive
                    onCheckedChanged: {UM.ToolbarData.setWizardState(checked)}
                    style: SwitchStyle
                    {
                        handle: Rectangle
                        {
                            width: wizardSwitch.width / 2
                            height:wizardSwitch.height
                            radius:2
                            Label 
                            {
                                anchors.horizontalCenter:parent.horizontalCenter
                                anchors.verticalCenter:parent.verticalCenter
                                text: wizardSwitch.checked ? "ON" : "OFF"
                            }
                        }
                        groove: Rectangle
                        {
                            implicitWidth: 50
                            implicitHeight: 20
                            color:"black"
                            
                        }
                    }
                }
                ToolButton
                {
                    id:youmagineButton
                    anchors.right:settingsButton.left
                    anchors.rightMargin:10
                    iconSource: UM.Resources.getIcon("youmagine.png");
                    tooltip: "Youmagine integration"
                }
                ToolButton
                {
                    id:settingsButton
                    anchors.right:parent.right
                    anchors.rightMargin:10
                    iconSource: UM.Resources.getIcon("settings.png");
                    tooltip: "Settings and preferences"
                }
            }
        }
        Item { width: UM.Theme.windowRightMargin; }
        
    }
}