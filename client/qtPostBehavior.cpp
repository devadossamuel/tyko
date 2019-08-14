//
// Created by Borchers, Henry Samuel on 2019-06-28.
//

#include "qtPostBehavior.h"

#include <QHttpMultiPart>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QJsonObject>

long
qtPostBehavior::send(const std::string &url, std::string &response_text, const std::map<std::string, std::string> &form_data) {
    QHttpMultiPart *multiPart = new QHttpMultiPart(QHttpMultiPart::RelatedType);
    QNetworkRequest request(QUrl(url.c_str()));
    request.setHeader(QNetworkRequest::ContentTypeHeader, "text/plain");
    QNetworkAccessManager *manager = new QNetworkAccessManager();

//    connect(manager, SIGNAL(finished(QNetworkReply*)), this, SLOT(replyFinished(QNetworkReply *)));

    QByteArray data = "ddd";
    QNetworkReply *reply = manager->post(request, data);

    return 0;
//    connect(reply, SIGNAL(metaDataChanged()), this, SLOT(onRequestFinished()));
//    connect(reply, SIGNAL(error(QNetworkReply::NetworkError)), this, SLOT(onError(QNetworkReply::NetworkError)));
}

