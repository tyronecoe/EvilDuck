#include "core.h"
#include <fstream>
#include <iterator>
#include <iostream>
static ds_preview::Accept count(void*context,const ds_preview::Event&){auto &n=*static_cast<unsigned*>(context);return ++n<=2048?ds_preview::Accept::Accepted:ds_preview::Accept::Failed;}
int main(int argc,char**argv){if(argc!=5)return 2;for(int i=1;i<argc;i++){std::ifstream file(argv[i]);if(!file)return 1;std::string source((std::istreambuf_iterator<char>(file)),{});ds_preview::Program p;if(!p.compile(source.c_str(),source.size(),"public-new-launcher")){std::cerr<<"compile error "<<unsigned(p.error().code)<<" at "<<p.error().line<<"\n";return 1;}unsigned events=0;ds_preview::Runtime runtime; if(!runtime.start(p,count,&events,0))return 1;for(uint32_t now=0;now<30000&&runtime.state()==ds_preview::State::Running;now+=10)runtime.tick(now);if(runtime.state()!=ds_preview::State::Completed)return 1;std::cout<<"PASS public launcher compile + mock sink execution "<<i<<" events="<<events<<"; no HID/host API\n";}return 0;}
