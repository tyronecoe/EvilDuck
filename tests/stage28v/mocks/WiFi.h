#pragma once
#include "network.h"
constexpr int WIFI_AP=1,WIFI_OFF=0;
struct Address{String toString(){return "mock-address";}};
struct FakeWiFi{bool mode(int){++networkMock::modes;return true;}bool softAP(const char*,const char*,int,int){++networkMock::aps;return true;}Address softAPIP(){return {};}};
inline FakeWiFi WiFi;
