//
// Created by Borchers, Henry Samuel on 2019-06-28.
//

#ifndef AVDATABASEEDITOR_CURLPOSTBEHAVIOR_H
#define AVDATABASEEDITOR_CURLPOSTBEHAVIOR_H

#include "postBehavior.h"
#include <map>

class CurlPostBehavior: public PostBehavior {
    static size_t WriteCallback(void *content, size_t size, size_t nmemb, void *userp);
public:
    long send(const std::string &url, std::string &response_text, const std::map<std::string, std::string> &form_data) override;

    std::string getFormData(const std::string &boundary, const std::map<std::string, std::string> &form_data) const;
};


#endif //AVDATABASEEDITOR_CURLPOSTBEHAVIOR_H
