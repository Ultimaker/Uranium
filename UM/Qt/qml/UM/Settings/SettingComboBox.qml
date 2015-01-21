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
    property variant key;
    width: 180; 
    color: "transparent"

    /*height: collapsed ? 0 : 40
    Behavior on height { NumberAnimation { } }
    
    opacity: collapsed ? 0 : 1
    Behavior on opacity { NumberAnimation { } }*/
    
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
        
        ComboBox
        {
            Layout.preferredHeight: childrenRect.height
            Layout.fillWidth: true
            model: options
            style: ComboBoxStyle {}
            onCurrentIndexChanged: 
            {
                if(base.key != undefined)
                    base.model.settingChanged(base.index,base.key, currentText)
            }
        }     
    }
}