import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import ".." as UM

SettingItem {
    id: base;
    property variant options;

    control: ComboBox
    {
        anchors.fill: parent;
        model: base.options

        style: ComboBoxStyle {}
        onCurrentIndexChanged:
        {
            if(base.key != undefined)
                base.model.settingChanged(base.index,base.key, currentText)
        }
    }
}
