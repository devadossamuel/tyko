import QtQuick 2.9
import QtQuick.Controls 2.2
import "resource.js" as Resource

Item{
    id: root
    property url sourceURL
    property string apiRoute
    property alias model: model
    property var get: model.get

    signal updateData

    QtObject{
        id: internal
        property string json
        onJsonChanged:{
            Resource.updateModelData(json, model)
        }
    }

    onUpdateData: {
        Resource.getApiData(apiRoute)
    }

    ListModel{
        id: model
    }
    Component.onCompleted: Resource.getApiData(apiRoute)

}
