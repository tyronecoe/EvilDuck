#pragma once
#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <type_traits>
#define PROGMEM

// Minimal Arduino API used by the real firmware sources in this test target.
class String {
  std::string value;
public:
  String() = default;
  String(const char *s) : value(s ? s : "") {}
  String(const std::string &s) : value(s) {}
  String(char c) : value(1, c) {}
  template<class T, typename std::enable_if<std::is_integral<T>::value, int>::type = 0>
  String(T n) : value(std::to_string(n)) {}
  const char *c_str() const { return value.c_str(); }
  size_t length() const { return value.size(); }
  char operator[](size_t n) const { return n < value.size() ? value[n] : 0; }
  void remove(size_t from) { if (from < value.size()) value.erase(from); }
  void reserve(size_t n) { value.reserve(n); }
  bool startsWith(const String &s) const { return value.compare(0, s.length(), s.value) == 0; }
  bool endsWith(const String &s) const {
    return value.size() >= s.length() && value.compare(value.size()-s.length(), s.length(), s.value)==0;
  }
  int indexOf(const String &s, size_t from = 0) const {
    auto p = value.find(s.value, from); return p == std::string::npos ? -1 : int(p);
  }
  int indexOf(char c, size_t from = 0) const { return indexOf(String(c), from); }
  int lastIndexOf(char c) const { auto p=value.rfind(c); return p==std::string::npos ? -1 : int(p); }
  String substring(size_t from, size_t to = std::string::npos) const {
    if (to < from) std::swap(from, to);
    from = std::min(from, value.size());
    return value.substr(from, std::min(to, value.size()) - from);
  }
  long toInt() const { return std::strtol(value.c_str(), nullptr, 10); }
  void trim() {
    auto a=value.find_first_not_of(" \t\r\n"), b=value.find_last_not_of(" \t\r\n");
    value = a==std::string::npos ? "" : value.substr(a,b-a+1);
  }
  void toLowerCase() { for (char &c:value) c=std::tolower(static_cast<unsigned char>(c)); }
  void toUpperCase() { for (char &c:value) c=std::toupper(static_cast<unsigned char>(c)); }
  void replace(const String &from, const String &to) {
    if (!from.length()) return;
    size_t p=0;
    while ((p=value.find(from.value,p)) != std::string::npos) {
      value.replace(p,from.length(),to.value); p+=to.length();
    }
  }
  String &operator+=(const String &s) { value += s.value; return *this; }
  friend String operator+(String a,const String &b) { return a+=b; }
  friend bool operator==(const String &a,const String &b) { return a.value==b.value; }
  friend bool operator!=(const String &a,const String &b) { return !(a==b); }
};

uint32_t millis();
void delay(uint32_t ms);
namespace serialMock {inline std::string input,output;inline size_t cursor=0,reads=0;inline bool continuous=false;inline void set(std::string s){input=s;cursor=0;continuous=false;}}
struct MockSerial {
 int available(){return serialMock::cursor<serialMock::input.size()||serialMock::continuous;}
 int read(){++serialMock::reads;if(serialMock::cursor<serialMock::input.size())return static_cast<unsigned char>(serialMock::input[serialMock::cursor++]);return serialMock::continuous?'x':-1;}
 void println(const char*s){serialMock::output+=s;serialMock::output+='\n';}
};inline MockSerial Serial;

struct MockESP { unsigned restarts=0;void restart(){++restarts;} unsigned getFreeHeap() { return 100000; } };
inline MockESP ESP;

template<class T> T constrain(T x,T a,T b){return std::min(b,std::max(a,x));}

uint32_t esp_random();
