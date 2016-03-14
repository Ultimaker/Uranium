// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1

QtObject {
    property font labelFont;
    property color labelColor: Qt.rgba(0.0, 0.0, 0.0, 1.0);

    property real spacing: 10;

    property real fixedHeight: 0;

    property real controlWidth: 100;
    property real controlRightMargin: 10;
    property real controlBorderWidth: 1;
    property color controlColor: Qt.rgba(1.0, 1.0, 1.0, 1.0);
    property color controlBorderColor: Qt.rgba(0.0, 0.0, 0.0, 1.0);
    property color controlTextColor: Qt.rgba(0.0, 0.0, 0.0, 1.0);
    property color controlHighlightColor: Qt.rgba(0.9, 0.9, 0.9, 1.0);
    property color controlBorderHighlightColor: Qt.rgba(0.1, 0.1, 0.1, 1.0);
    property color controlDisabledColor: Qt.rgba(0.8, 0.8, 0.8, 1.0);
    property color controlDisabledTextColor: Qt.rgba(0.4, 0.4, 0.4, 1.0);
    property color controlDisabledBorderColor: Qt.rgba(0.8, 0.8, 0.8, 1.0);
    property font controlFont;

    property color validationErrorColor: Qt.rgba(1.0, 0.0, 0.0, 1.0);
    property color validationWarningColor: Qt.rgba(1.0, 1.0, 0.0, 1.0);
    property color validationOkColor: Qt.rgba(1.0, 1.0, 1.0, 1.0);

    property real unitRightMargin: 10;
    property color unitColor: Qt.rgba(0.0, 0.0, 0.0, 1.0);
    property font unitFont;
}
