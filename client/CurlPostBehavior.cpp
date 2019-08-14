//
// Created by Borchers, Henry Samuel on 2019-06-28.
//

#include "CurlPostBehavior.h"

#include <iostream>
#include <sstream>

//
//#pragma comment(lib, "Wldap32.lib" )
//#pragma comment(lib, "Crypt32.lib" )
//#pragma comment(lib, "Ws2_32.lib"  )

extern "C"{

//#define CURL_STATICLIB
#include <curl/curl.h>
}

long
CurlPostBehavior::send(const std::string &url, std::string &response_text, const std::map<std::string, std::string> &form_data) {
    CURL *hnd = curl_easy_init();
    curl_easy_setopt(hnd, CURLOPT_CUSTOMREQUEST, "POST");
    curl_easy_setopt(hnd, CURLOPT_URL, url.c_str());

    struct curl_slist *headers = nullptr;

    headers = curl_slist_append(headers, "cache-control: no-cache");
    const std::string boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
    std::string content_header = "content-type: multipart/form-data; boundary=" + boundary;
    headers = curl_slist_append(headers, content_header.c_str());

    curl_easy_setopt(hnd, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(hnd, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(hnd, CURLOPT_WRITEDATA, &response_text);

    const std::string data = getFormData(boundary, form_data);
    const char *postData = data.c_str();

    curl_easy_setopt(hnd, CURLOPT_POSTFIELDS, postData);
    CURLcode ret = curl_easy_perform(hnd);
    long rc = ret;
    if(ret == CURLE_OK){
        curl_easy_getinfo(hnd, CURLINFO_RESPONSE_CODE, &rc);
    }
    curl_easy_cleanup(hnd);

    return rc;
}

std::string CurlPostBehavior::getFormData(const std::string &boundary, const std::map<std::string, std::string> &form_data) const {
    std::ostringstream data;

    for(auto & kv: form_data){
        data <<  "--" << boundary << "\r\n";
        data <<  "Content-Disposition: form-data; name=\"" << kv.first << "\"\r\n";
        data <<  "\r\n";
        data << kv.second << "\r\n";
    }
    data <<  "--" << boundary << "--";
    return data.str();
}

size_t CurlPostBehavior::WriteCallback(void *content, size_t size, size_t nmemb, void *userp) {

    ((std::string*)userp)->append((char*)content, size, nmemb);
    return size * nmemb;
}
