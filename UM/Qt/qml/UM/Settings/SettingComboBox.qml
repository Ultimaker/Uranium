import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import ".." as UM

SettingItem {
    id: base;
    property variant options;
    width:parent.width > 0 ? parent.width : 234
    control: ComboBox
    {
        anchors.fill: parent;
        model: base.options
        currentIndex:0
        style: ComboBoxStyle {}
        width:base.width > 0 ? base.width:50
        onCurrentIndexChanged:
        {
            if(base.key != undefined)
                base.model.settingChanged(base.index,base.key, currentText)
        }
    }
}
