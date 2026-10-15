// Included only with EVILDUCK_NATIVE_SCHEDULER_ROUTE_B in scratch com.cpp.
namespace {
struct RouteOwner {
 bool active=false,internal=false,cancelled=false;
 uint64_t session=0,nextSession=0,nextOperation=0,backendOperation=0;
 route_b::Result result{};
 uint32_t priorDefaultDelay=0;uint16_t low=0,high=0,jitter=0;bool jitterOn=false;
} route;
void routeFinish(route_b::ResultKind k){
 if(route.result.kind==route_b::ResultKind::Pending)route.result.kind=k;
}
bool routeExternal(){return route.active&&!route.internal;}
}
namespace route_b {
bool active(){return route.active;}
bool drive(uint64_t owner){
 execution::Guard guard;
 if(!route.active||owner!=route.session)return false;
 backend_b::Scope permissionScope(owner,route.backendOperation);if(!permissionScope)return false;
 com::update();
 if(!route.cancelled&&backend_b::fatal()){session.error="RouteB ambiguous/invalid backend observation";fail();}
 return true;
}
bool environment(){return attackmode::hidEnabled()&&keyboard_locale::getLocale()==&locale_us;}
bool acquire(uint64_t &out){
 execution::Guard guard;
 if(route.active||session.scriptOwned||session.phase!=Phase::Idle||hid_backend::clearing()||hid_backend::hasPersistent()||!environment()||route.nextSession==UINT64_MAX)return false;
 if(!backend_b::acquire(route.nextSession+1))return false;
 // No callback slot is replaced. Capture ownership before requesting a fresh clear.
 route.session=++route.nextSession;route.backendOperation=0;route.active=true;route.cancelled=false;route.result={};
 route.priorDefaultDelay=session.defaultDelay;route.low=duck_random::minimum();route.high=duck_random::maximum();route.jitter=duck_random::jitterMaximum();route.jitterOn=duck_random::jitterEnabled();
 backend_b::Scope permissionScope(route.session,0);if(!permissionScope)return false;
 route.internal=true;com::beginScript();route.internal=false;
 duck_random::setMinimum(route.low);duck_random::setMaximum(route.high);duck_random::setJitterMaximum(route.jitter);duck_random::setJitterEnabled(route.jitterOn);
 out=route.session;hid_backend::cancelReport();return true;
}
static Admission admit(uint64_t owner,uint16_t v,bool text,Id &id){
 execution::Guard guard;
 if(!route.active||owner!=route.session||route.cancelled||route.result.kind!=ResultKind::None||session.phase!=Phase::Idle||hid_backend::clearing()||!environment()||route.nextOperation==UINT64_MAX)return Admission::Rejected;
 bool valid=text?(v==9||v==10||(v>=32&&v<=126)):(v==0x28||v==0x2b||v==0x2c||v==0x29||v==0x2a||v==0x4c||(v>=0x4f&&v<=0x52));
 if(!valid)return Admission::Rejected;
 if(!backend_b::bind(owner,route.nextOperation+1))return Admission::Rejected;
 id={owner,++route.nextOperation};route.backendOperation=id.operation;route.result={id,ResultKind::Pending};
 session.error="";session.remember=false;session.lockCommand=-1;
 if(text)startText(String(static_cast<char>(v)),false,Phase::Finish); // literal: no interpolation/trim/parser
 else{const uint8_t k=static_cast<uint8_t>(v);report(0,&k,1,Phase::Finish);}
 return Admission::Admitted;
}
Admission character(uint64_t s,uint16_t v,Id &id){return admit(s,v,true,id);}
Admission key(uint64_t s,uint16_t v,Id &id){return admit(s,v,false,id);}
Result result(uint64_t owner){execution::Guard guard;return route.active&&owner==route.session?route.result:Result{};}
bool consume(Result r){
 execution::Guard guard;
 if(!route.active||!equal(r.id,route.result.id)||r.kind!=route.result.kind||r.kind==ResultKind::Pending||r.kind==ResultKind::None)return false;
 route.result={};return true;
}
bool cancel(uint64_t owner){
 execution::Guard guard;
 if(!route.active||owner!=route.session)return false;
 if(!route.cancelled){backend_b::cleanup(owner);backend_b::Scope permissionScope(owner,route.backendOperation);if(!permissionScope)return false;route.cancelled=true;routeFinish(ResultKind::Cancelled);bool had=session.ownsKeys||hid_backend::hasPersistent();route.internal=true;com::endScript();route.internal=false;duck_random::setMinimum(route.low);duck_random::setMaximum(route.high);duck_random::setJitterMaximum(route.jitter);duck_random::setJitterEnabled(route.jitterOn);if(!had)hid_backend::cancelReport();}
 return true;
}
bool clearing(uint64_t owner){execution::Guard guard;return route.active&&owner==route.session&&hid_backend::clearing();}
bool detach(uint64_t owner){
 execution::Guard guard;
 if(!route.active||owner!=route.session||!route.cancelled||hid_backend::clearing()||session.phase!=Phase::Idle)return false;
 if(!backend_b::release(owner))return false;
 session.defaultDelay=route.priorDefaultDelay;route.active=false;route.result={};return true;
}
const char* phase(){
 switch(session.phase){case Phase::Idle:return "Idle";case Phase::Text:return "Text";case Phase::Press:return "Press";case Phase::Release:return "Release";case Phase::Wait:return "Wait";case Phase::Finish:return "Finish";default:return "Other";}
}
void exhaustForTest(bool s,bool op){if(!route.active){if(s)route.nextSession=UINT64_MAX;if(op)route.nextOperation=UINT64_MAX;}}
}
