import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import ".." as UM

SettingItem {
    id: base;

    control: Label
    {
        anchors.verticalCenter: parent.verticalCenter;
        text: base.value + " " + base.unit;
    }
}
