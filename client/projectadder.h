#ifndef PROJECTADDER_H
#define PROJECTADDER_H
#include <QNetworkReply>
#include <QQuickItem>

class ProjectAdder : public QQuickItem
{
    Q_OBJECT
    Q_PROPERTY(QUrl url READ url WRITE setUrl)
    Q_PROPERTY(QString route READ route WRITE setRoute)
    Q_PROPERTY(QString title READ title WRITE setTitle)
    Q_PROPERTY(QString currentLocation READ currentLocation WRITE setCurrentLocation)
    Q_PROPERTY(QString projectCode READ projectCode WRITE setProjectCode)
    Q_PROPERTY(QString specs READ specs WRITE setSpecs)
    Q_PROPERTY(QString projectStatus READ projectStatus WRITE setProjectStatus)

    QUrl mUrl;
    QString mRoute;
    QString mTitle;
    QString mCurrentLocation;
    QString mProjectCode;
    QString mSpecs;
    QString mProjectStatus;
public:
    const QString &projectStatus() const;

    void setProjectStatus(const QString &projectStatus);

public:
    const QString &projectCode() const;

    void setProjectCode(const QString &projectCode);

    const QString &specs() const;

    void setSpecs(const QString &specs);

    const QString &currentLocation() const;

    void setCurrentLocation(const QString &currentLocation);

public:
    ProjectAdder();
    void setUrl(const QUrl &url);
    QUrl url() const;

    void setRoute(const QString &route);
    QString route() const;

    void setTitle(const QString &title);
    QString title() const;

    Q_INVOKABLE void send();


signals:
    void success();
    void failure();

public slots:
    void replyFinished(QNetworkReply*);
};

#endif // PROJECTADDER_H
