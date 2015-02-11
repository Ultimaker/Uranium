import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

SettingItem {
    id: base;

    control: CheckBox
    {
        anchors.fill: parent;
        checked: base.value
        onCheckedChanged: base.model.settingChanged(base.index, base.key, checked);
    }
}
