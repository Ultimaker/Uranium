import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import ".." as UM

Label {
    signal valueChanged(string value);

    property variant value;
    property string unit;

    text: value + " " + unit;
}
