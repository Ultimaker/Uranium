pragma Singleton

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

QtObject {
    property color primaryColor: "#24a9e3";
    property color borderColor: "black";

    property real largeTextSize: 18;
    property real normalTextSize: 12;
    property real smallTextSize: 9;
    property real tinyTextSize: 6;

    property real windowLeftMargin: 10;
    property real windowRightMargin: 10;

    property real panelWidth: 250;

    property real defaultMargin: 4;

    property color toolbarBorderColor: "black";

    property real toolbarHeight: 60;
    property real toolbarBorderSize: 2;
    property real toolbarSpacing: 20;

    property real toolbarIconWidth: 32;
    property real toolbarIconHeight: 32;

    property real toolbarButtonWidth: toolbarHeight * 1.25;
    property real toolbarButtonHeight: toolbarHeight;

    property color toolbarButtonBackgroundColor: primaryColor;
    property color toolbarButtonForegroundColor: "white";

    property color toolbarButtonBackgroundHighlightColor: "white";
    property color toolbarButtonForegroundHighlightColor: "black";

    property color toolbarButtonBackgroundDisabledColor: primaryColor;
    property color toolbarButtonForegroundDisabledColor: "#ccc";
}
