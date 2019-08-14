#include "projectadder.h"
//#include <QHttpMultiPart>
//#include <QNetworkAccessManager>
//#include <QNetworkReply>
//#include <QJsonObject>

#include <QDebug>
#include "CurlPostBehavior.h"

ProjectAdder::ProjectAdder()
{

}

void ProjectAdder::setUrl(const QUrl &url)
{
    mUrl = url;
}

QUrl ProjectAdder::url() const
{
    return mUrl;
}

void ProjectAdder::setRoute(const QString &route)
{
    mRoute = route;
}

QString ProjectAdder::route() const
{
    return mRoute;
}

void ProjectAdder::send()
{
    auto senderURL = mUrl;
    senderURL.setPath(mRoute);
    CurlPostBehavior stat = CurlPostBehavior();
    const std::string send_url = senderURL.toString().toStdString();
    std::string response_text;
    std::map<std::string, std::string> my_data;
    my_data["project_code"] = mProjectCode.toStdString();
    my_data["current_location"] = mCurrentLocation.toStdString();
    my_data["status"] = mProjectStatus.toStdString();
    my_data["specs"] = mSpecs.toStdString();
    my_data["title"] = mTitle.toStdString();
    long rc = stat.send(send_url, response_text, my_data);
    if(rc == 200){
        success();
    } else{
        failure();
        qDebug() << QString(response_text.c_str());
    }


}

void ProjectAdder::replyFinished(QNetworkReply *reply)
{
    qDebug() << "HERE " << reply->error();
    if(reply->error() == QNetworkReply::NoError){
        emit success();
    }
    else{
        emit failure();
    }
    ;
}

QString ProjectAdder::title() const {
    return mTitle;
}

void ProjectAdder::setTitle(const QString &title) {
    mTitle=title;
}

const QString &ProjectAdder::currentLocation() const {
    return mCurrentLocation;
}

void ProjectAdder::setCurrentLocation(const QString &currentLocation) {
    ProjectAdder::mCurrentLocation = currentLocation;
}

const QString &ProjectAdder::projectCode() const {
    return mProjectCode;
}

void ProjectAdder::setProjectCode(const QString &projectCode) {
    ProjectAdder::mProjectCode = projectCode;
}

const QString &ProjectAdder::specs() const {
    return mSpecs;
}

void ProjectAdder::setSpecs(const QString &specs) {
    ProjectAdder::mSpecs = specs;
}

const QString &ProjectAdder::projectStatus() const {
    return mProjectStatus;
}

void ProjectAdder::setProjectStatus(const QString &projectStatus) {
    ProjectAdder::mProjectStatus = projectStatus;
}
