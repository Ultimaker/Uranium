// Copyright (c) 2022 UltiMaker
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.15

RegularExpressionValidator
{
    property int maxNumbers: 12
    readonly property string regexString: "^-?[0-9]{0,%0}$".arg(maxNumbers)

    regularExpression: new RegExp(regexString)
}