import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1

import "."
import UM 1.0 as UM
ButtonStyle 
{
    id: base;
    property bool down: control.pressed || (control.checkable && control.checked);

    property color backgroundColor: UM.Styles.toolbarButtonBackgroundColor;
    property color foregroundColor: UM.Styles.toolbarButtonForegroundColor;

    property color backgroundHighlightColor: UM.Styles.toolbarButtonBackgroundHighlightColor;
    property color foregroundHighlightColor: UM.Styles.toolbarButtonForegroundHighlightColor;

    property color backgroundDisabledColor: UM.Styles.toolbarButtonBackgroundDisabledColor;
    property color foregroundDisabledColor: UM.Styles.toolbarButtonForegroundDisabledColor;
    
    property int numCircles:0
    property int beginState:0
    property int state:0
    
    background: Item 
    {
        implicitWidth: control.width > 0 ? control.width : UM.Styles.toolbarButtonWidth;
        implicitHeight: control.height > 0 ? control.height : UM.Styles.toolbarButtonHeight;

        Rectangle 
        {
            id: backgroundItem;

            anchors.fill: parent;
            color: base.backgroundColor;
        }

        Rectangle 
        {
            anchors.horizontalCenter: parent.left;
            anchors.top: parent.top;
            anchors.bottom: parent.bottom;
            width: 2;
            color: down ? UM.Styles.toolbarBorderColor: "transparent";
        }

        Rectangle 
        {
            anchors.horizontalCenter: parent.right;
            anchors.top: parent.top;
            anchors.bottom: parent.bottom;
            width: 2;
            color: down ? UM.Styles.toolbarBorderColor: "transparent";
        }
        Rectangle
        {
            anchors.bottom: parent.bottom;
            anchors.left:parent.left;
            anchors.right:parent.right;
            height: 2;
            color: down ? "transparent": UM.Styles.toolbarBorderColor;
        }
        
        Rectangle
        {
            anchors.top: parent.top;
            anchors.left:parent.left;
            anchors.right:parent.right;
            height: 2;
            color: down ? UM.Styles.toolbarBorderColor: "transparent";
        }

        states: 
        [
            State 
            {
                name: 'down';
                when: base.down;

                PropertyChanges { target: backgroundItem; color: base.backgroundHighlightColor; }
            }
        ]

        transitions:
        [
            Transition 
            {
                ColorAnimation { duration: 100; }
            }
        ]
    }
    
    label: Item
    {
        id:item
        property bool down: control.pressed || (control.checkable && control.checked);
        ColumnLayout 
        {  
            anchors.horizontalCenter:parent.horizontalCenter
            anchors.fill: parent;
            Label 
            {
                id: text;
                anchors 
                {
                    horizontalCenter:parent.horizontalCenter
                    verticalCenter:parent.verticalCenter
                    //horizontalCenter:parent.horizontalCenter
                    
                    //verticalCenter:parent.verticalCenter
                    //right: parent.right;
                }
                text: control.text;
                color: base.foregroundColor;
                height:25
                width:100
                font.capitalization: Font.AllUppercase;
                font.pointSize: UM.Styles.smallTextSize;
                font.bold: true
                horizontalAlignment: Text.AlignHCenter;
                wrapMode: Text.Wrap;
            }
            
            RowLayout
            {
                id:container
                anchors.horizontalCenter: parent.horizontalCenter
                x:50
                // Magical code to calculate how many of the circles are filled. 
                property int filledCircles: (base.state-base.beginState) < 0 ? 0 : base.state - base.beginState > base.numCircles ? base.numCircles: base.state - base.beginState 
                Repeater 
                {
                    model: base.numCircles
                    Rectangle 
                    {
                        width: 10;
                        height: 10;
                        radius: 5;
                        Behavior on color { ColorAnimation{}}
                        color: index < container.filledCircles ? "black":"white";
                        border.color: "black";
                        Behavior on opacity { NumberAnimation { } }
                        opacity: UM.ToolbarData.wizardActive? 1:0
                    }
                }
            }
        }  
            
        
        states: 
        [
            State 
            {
                name: 'down';
                when: base.down;

                //PropertyChanges { target: icon; color: base.foregroundHighlightColor; }
                PropertyChanges { target: text; color: base.foregroundHighlightColor; }
            },
            State 
            {
                name: 'disabled';
                when: !control.enabled;

                //PropertyChanges { target: icon; color: base.foregroundDisabledColor; }
                PropertyChanges { target: text; color: base.foregroundDisabledColor; }
            }
        ]

        transitions: 
        [
            Transition 
            {
                ColorAnimation { duration: 100; }
            }
        ]
    }
    
    
}
