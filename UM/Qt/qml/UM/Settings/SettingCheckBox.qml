import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

Rectangle {
    id: base;

    property int index;
    property string key;
    property variant value;

    width: 180; 
    color: "transparent"
    
    RowLayout 
    {
        spacing: 2
        x: 2

        Label
        { 
            text: name
            Layout.preferredWidth: 130
            Layout.maximumWidth: 150
        }

        CheckBox
        {
            checked: base.value
            onCheckedChanged: base.model.settingChanged(base.index, base.key, checked);
        }
    }
}
