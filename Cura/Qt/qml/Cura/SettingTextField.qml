import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

Rectangle {
    id: base;
    
    property variant model;
    property int valid;
    property variant value;
    property int index;
    width: 180; 

    height: collapsed ? 0 : 40
    Behavior on height { NumberAnimation { } }
    
    opacity: collapsed ? 0 : 1
    Behavior on opacity { NumberAnimation { } }
    
    RowLayout 
    {
        spacing: 2
        x: 2
        
        Text 
        { 
            text: name
            Layout.preferredWidth: 130
            Layout.maximumWidth: 150
        }  
        
        TextField
        {
            Layout.preferredHeight: childrenRect.height
            Layout.fillWidth: true
            style: TextFieldStyle 
            {
                textColor: "black"
                background: Rectangle 
                {
                    radius: 2
                    implicitWidth: 100
                    implicitHeight: 24
                    color:  {
                        switch(base.valid)
                        {
                            case 0:
                                return "red"
                            case 1:
                                return "red"
                            case 2:
                                return "red"
                            case 3:
                                return "yellow"
                            case 4:
                                return "yellow"
                            case 5:
                                return "green"
                            
                            default: 
                                console.log(base.valid)
                                return "black" 
                        }
                    }
                }
            }
            text: value
            onEditingFinished: base.model.settingChanged(base.index,name,text)
        }     
    }
}