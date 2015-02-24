import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM
import ".."

Rectangle {
    id: base;

    width: 200;
    height: 200;

    visible: false;

    Label {
        id: description;
        anchors.fill: parent;
    }

    function show(text) {
        description.text = text;
        base.visible = true;
    }
}
