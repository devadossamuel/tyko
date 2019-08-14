import QtQuick 2.9
import QtTest 1.0
import Api 1.0
ProjectAdder{
    id: myAdder
    property url sourceURL:"http://127.0.0.1:5000"
    url: sourceURL
    route: "/api/projects/"
    title: "my new Projectaa"
    currentLocation: "Unknown"
    projectCode: "asasasasasas"
    projectStatus: "Something"
    specs: "asdfasdfspecs"
    onSuccess: console.log("success")
    onFailure: console.log("Failed")
    SignalSpy{
        id:spy
        target: myAdder
        signalName: "success"
    }

    TestCase{
        name: "properties"
        function test_urlProperties(){
            compare(myAdder.url, sourceURL)

        }
    }
    TestCase{
        name: "newProject good"
        function test_newProject(){
            myAdder.send()
            compare(spy.count, 1)
        }
    }
}
