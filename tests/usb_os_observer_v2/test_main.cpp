// Actual composed V2 observer/backend; original driver bodies remain compile-only.
#include "observer_v1_parent.inc"
static void at(uint32_t n){usb_observer::setClockForTest(n);}
static void sample(uint32_t n,bool value,uint32_t expected=UINT32_MAX){at(n);usb_observer::service(n,value,expected==UINT32_MAX?usb_observer::sampleGeneration():expected);}
static void setupAt(uint32_t n,uint8_t type=0x80,uint8_t request=6,uint16_t value=0x1234,uint16_t index=0,uint16_t length=18){at(n);auto e=oq(type,request,value,index,length);of(e,true);}
static void resetAt(uint32_t n){at(n);auto e=oe(DCD_EVENT_BUS_RESET);of(e,true);}
static void prefix(bool configured=true){ob();setupAt(10);sample(100,configured);}
int main(int argc,char**argv){if(argc!=2)return 2;try{const std::string id=argv[1];
 if(id=="V201"){
  auto s=os();check(s.state==usb_observer::State::Boot&&!s.live.present&&!s.generationTimeKnown&&!s.firstUnsupported.present,"BSS ready before setup with explicit absent evidence");check(sizeof(usb_observer::Record)==20&&sizeof(usb_observer::Witness)<=24&&sizeof(s)<2048,"bounded timestamp records and witness");
 }else if(id=="V202"){
  ob();setupAt(0);auto s=os();check(s.count==1&&s.records[0].atMs==0&&s.generationTimeKnown&&s.generationStartedMs==0,"clockzero is valid event/generation timestamp");sample(0,true);check(os().firstConfiguredKnown&&os().firstConfiguredAtMs==0&&os().configuredKnown,"zero firsttrue SDK sample is explicitknown");
 }else if(id=="V203"){
  prefix();setupAt(120,0,9,0);auto s=os();check(s.firstConfigurationKnown&&s.firstConfigurationAtMs==120&&s.records[1].wValue==0,"SET_CONFIGURATION zero retained as raw deconfiguration attempt");check(s.records[0].order==1&&s.records[0].atMs==10,"early preforeground header stays in prefix");
 }else if(id=="V204"){
  prefix();setupAt(5099);check(os().count==2&&!os().windowClosed,"4999ms remains prefix");setupAt(5100);auto s=os();check(s.count==2&&s.observed==2&&s.windowClosed&&s.windowFinishedMs==5100&&s.captureClosedObservedAtMs==5100,"ISR exactly5s seals prefix before appending");check(s.tail.firstSetup.present&&s.tail.firstSetup.record.atMs==5100&&s.tail.firstSetup.record.order==1,"exactboundary enters phase-local tail");
 }else if(id=="V205"){
  prefix();setupAt(6000);auto s=os();check(s.count==1&&s.observed==1&&s.captureClosedObservedAtMs==6000&&s.windowFinishedMs==5100,"delayed foreground cannot extend64prefix");check(s.configuredKnown&&s.configured&&s.configuredSampleAtMs==100,"sealing preserves explicitly dated earlier SDK sample");sample(9000,false);auto t=os();check(t.state==s.state&&t.configured==s.configured&&t.configuredSampleAtMs==s.configuredSampleAtMs,"later false sample cannot rewrite prefix");
 }else if(id=="V206"){
  prefix(false);sample(6000,true);auto s=os();check(s.state==usb_observer::State::Incomplete&&s.configuredKnown&&!s.configured&&s.configuredSampleAtMs==100,"late true never retroactively validates original prefix");check(s.tail.firstConfiguredKnown&&s.tail.firstConfiguredAtMs==6000&&s.live.configured&&s.live.known,"late true separately dated tail/live SDK observation");
 }else if(id=="V207"){
  prefix();sample(5100,true);auto before=os();sample(5101,false);auto s=os();check(s.state==usb_observer::State::Complete&&s.configured&&s.configuredKnown&&s.windowFinishedMs==before.windowFinishedMs,"old post-completion downgrade removed");check(s.live.present&&s.live.known&&!s.live.configured&&s.live.atMs==5101,"current loss remains visible separately");
 }else if(id=="V208"){
  ob();setupAt(1);const auto old=usb_observer::sampleGeneration();resetAt(2);sample(3,true,old);auto s=os();check(s.live.present&&!s.live.known&&s.live.mismatch&&s.live.expectedGeneration==old&&s.live.generation==old+1,"sample racing reset is explicit unknown");check(!s.configuredKnown&&!s.firstConfiguredKnown,"stale true cannot enter fresh capture");setupAt(4);sample(5003,true,old);check(os().state==usb_observer::State::Capturing&&!os().configuredKnown&&!os().windowStarted,"mismatched sample cannot start/backdate freshwindow");sample(5004,false);setupAt(5005);sample(10004,false);check(os().state==usb_observer::State::Incomplete,"freshcoherentsamples remainindependentfromstale true");
 }else if(id=="V209"){
  prefix();setupAt(140,0xa1,0xfe,0,0,1);auto s=os();check(s.observed==2&&s.count==1&&s.ignored==1&&s.unsupported==1&&s.unsupportedReasons==2,"rejected classheader accounting retained");check(s.firstUnsupported.present&&s.firstUnsupported.reason==2&&s.firstUnsupported.record.bRequest==0xfe&&s.firstUnsupported.phase==usb_observer::Phase::Prefix&&s.firstUnsupported.record.order==2&&s.firstUnsupported.record.atMs==140,"exact first rejected header retained outsideprefix");sample(5100,true);check(os().state==usb_observer::State::Unsupported,"witness doesnot clear reason or promote");
 }else if(id=="V210"){
  prefix();setupAt(140,0xa1,0xfe,0,0,1);setupAt(141,0xa1,0xfe,0,0,1);check(!os().additionalUnsupportedDistinct&&os().unsupported==2,"same rejected header repeat counter notdistinct");setupAt(142,0xa1,2,0,1,1);check(os().additionalUnsupportedDistinct&&os().firstUnsupported.record.bRequest==0xfe,"additional distinct rejected shape flags insufficiency withoutoverwrite");
 }else if(id=="V211"){
  prefix();setupAt(5100);setupAt(5101,0xc0,6);setupAt(5102,0xa1,0xfe,0,0,1);setupAt(5103,0,9,1,0,0);auto s=os();check(s.tail.observed==4&&s.tail.selected==2&&s.tail.ignored==2&&s.tail.unsupported==1,"tail selected/ignored/unsupported counters phase-local");check(s.tail.firstSetup.record.order==1&&s.tail.firstConfiguration.record.order==4&&s.tail.firstConfiguration.record.atMs==5103,"late witnesses exactphaseorder and rawfields");check(s.count==1&&s.observed==1&&s.unsupported==0&&s.firstUnsupported.present&&s.firstUnsupported.phase==usb_observer::Phase::Tail&&s.firstUnsupported.record.order==3,"tail standaloneunsupportedwitness never modifies prefix");
 }else if(id=="V212"){
  prefix();setupAt(10099);auto s=os();check(s.tail.active&&s.tail.observed==1&&s.tail.firstSetup.record.atMs==10099,"9999ms tail accepted");setupAt(10100,0,9,1,0,0);s=os();check(s.tail.closed&&!s.tail.active&&s.tail.finishedKnown&&s.tail.finishedMs==10100&&!s.tail.firstConfiguration.present&&s.tail.observed==1,"10s hardIRQ stop excludes boundary configuration");setupAt(20000);check(os().tail.observed==1,"foreground stall cannot extendtail");
 }else if(id=="V213"){
  prefix(false);setupAt(20000,0,9,1,0,0);sample(20000,true);auto s=os();check(s.count==1&&s.tail.observed==0&&!s.tail.firstConfiguration.present&&!s.tail.firstConfiguredKnown,"first activity beyond10s storesno tailheader/statushistory");check(s.maxServiceGapMs==19900&&s.lastServiceMs==20000,"first closing servicegap records actualstall withoutclamping");sample(40000,false);check(os().maxServiceGapMs==19900&&os().lastServiceMs==20000,"bounded service metrics freeze after first deadline-crossing service");check(os().live.atMs==40000&&!os().live.configured,"live status current independent from frozen collection");
 }else if(id=="V214"){
  ob();at(UINT32_MAX-100);resetAt(UINT32_MAX-100);setupAt(UINT32_MAX-50);sample(UINT32_MAX-20,true);setupAt(4979);auto s=os();check(s.windowClosed&&s.windowFinishedMs==4979&&s.tail.observed==1&&!s.clockError,"naturaluint32wrap respects5s cutoff");setupAt(9979);check(os().tail.closed&&os().tail.finishedMs==9979,"naturalwrap respects10s hardstop");
 }else if(id=="V215"){
  prefix();setupAt(120);setupAt(119);auto s=os();check(s.clockError&&s.state==usb_observer::State::ClockError&&s.windowClosed,"backward eventclock invalidates prefix");check(s.count==2,"clock-invalid event notappended");
 }else if(id=="V216"){
  prefix();sample(200,true);sample(199,true);check(os().state==usb_observer::State::ClockError&&!os().live.known,"backwardserviceclock isnot inventedvalidtime");
 }else if(id=="V217"){
  prefix();sample(5100,true);auto s=os();setupAt(5200);setupAt(5199);auto t=os();check(t.state==s.state&&t.configured==s.configured&&!t.clockError&&t.tail.invalid,"tailclockfailure cannot rewrite prefixhistory");
 }else if(id=="V218"){
  ob();for(unsigned i=0;i<64;++i)setupAt(i,0x80,6,i);check(os().count==64&&!os().overflow,"all64timestampedrecordsfit");setupAt(64);check(os().overflow&&os().count==64&&os().records[63].wValue==63,"65threfusedwithoutoverwrite");sample(100,true);setupAt(7000);check(os().tail.observed==0&&os().tail.invalid,"prefixoverflow cannotcreateusabletail");
 }else if(id=="V219"){
  prefix();setupAt(140,0xa1,2,0,1,1);sample(5100,true);resetAt(5200);auto s=os();check(s.count==0&&!s.firstUnsupported.present&&!s.tail.started&&!s.live.present&&!s.firstConfiguredKnown&&s.generation==2,"reset clears allcapture/live/tail/witness state");setupAt(5201);sample(5202,true);sample(10202,true);check(os().state==usb_observer::State::Complete,"subsequentgeneration isolated");
 }else if(id=="V220"){
  prefix();at(1000);auto e=oe(DCD_EVENT_UNPLUGGED);of(e,true);auto s=os();check(s.state==usb_observer::State::Unplugged&&s.windowClosed&&!s.windowStarted&&s.count==0&&!s.live.present,"unplug invalidates entiregeneration");setupAt(1001);sample(1002,true);sample(6002,true);check(os().missingReset&&os().state==usb_observer::State::Incomplete,"setupwithoutnewreset nevercomplete");
 }else if(id=="V221"){
  prefix();for(uint8_t code:{uint8_t(3),uint8_t(4),uint8_t(5),uint8_t(7),uint8_t(8)}){std::unique_lock<std::mutex> held(usb_observer::captureMux);auto e=oe(code);of(e,true);}check(os().observed==1&&os().unsupported==0,"ordinarypoisonedunionsfastforwardwithoutlock");
 }else if(id=="V222"){
  prefix();auto e=oe(255);at(125);of(e,true);auto s=os();check(s.unsupportedReasons==4&&s.unsupported==1&&!s.firstUnsupported.present,"unknownDCD hasreasonnotfabricatedSETUPheader");
 }else if(id=="V223"){
  ob();auto e=oq(0x80,6,1,2,3,1);at(5);of(e,true);auto n=evilduck_mock_dcd_calls();__wrap_dcd_event_handler(nullptr,true);check(evilduck_mock_dcd_calls()==n+1&&os().observed==0,"foreignport/null forwardexactoncewithoutcapture");
 }else if(id=="V224"){
  prefix();setupAt(140,0x81,6,65535,65535,65535);auto s=os();check(s.records[1].wValue==65535&&s.records[1].wIndex==65535&&s.records[1].wLength==65535,"unsigned16bitheaderfieldsremainrawnotvalidatedasOS");const uint8_t*b=reinterpret_cast<const uint8_t*>(&s.records[1]);for(size_t i=17;i<sizeof(usb_observer::Record);++i)check(b[i]==0,"recordtailpaddinginitialized");
 }else if(id=="V225"){
  prefix();const auto old=native_alloc::calls();setupAt(120);check(native_alloc::calls()==old,"timestampedcaptureallocatesnoheap");
 }else if(id=="V226"){
  ob();auto producer=[](){for(unsigned n=0;n<20;++n){auto e=oq();__wrap_dcd_event_handler(&e,true);}};std::thread a(producer),b(producer);for(unsigned n=0;n<20;++n)check(os().count<=40,"concurrentcoherentsnapshots");a.join();b.join();auto s=os();check(s.count==40&&s.observed==40&&evilduck_mock_dcd_calls()==41,"concurrenteachheaderforwardedonce");for(unsigned n=0;n<40;++n)check(s.records[n].order==n+1&&s.records[n].atMs==0,"orderedinitializedtimestamps");
 }else if(id=="V227"){
  nvsMock::reset();mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actualstartupowner");lower::reset();ob();setupAt(0);completed("STRING a\n");oneA();check(os().count==1,"ordinaryHIDreportcontentsnotcaptured");
 }else if(id=="V228"){
  nvsMock::reset();mscMock::reset();mock::reset();setup();check(startupControlledReady&&route_u::bindOwner(),"actualSTOPowner");lower::reset();ob();setupAt(0);put("/x.txt","HOLD RSHIFT\nDELAY 10000\nSTRING BAD\n");start();reports(1);route_u::stop();prCancelled();check(os().count==1,"STOPdoesnotcollectreportpayloads");lower::reset();completed("STRING a\n");oneA();
 }else if(id=="V229"){
  prefix();usb_observer::countersForTest(UINT32_MAX,0,1,0);setupAt(120);check(os().exhausted&&os().observed==UINT32_MAX&&os().tail.invalid,"prefixcounterexhaustionexplicitnowrap");ob();usb_observer::generationForTest(UINT32_MAX);resetAt(10);check(os().exhausted&&os().generation==UINT32_MAX,"generationexhaustionrefusesfalseepoch");
 }else if(id=="V230"){
  prefix();for(auto pair:{std::pair<uint8_t,uint8_t>{0xa1,1},{0x21,9},{0x21,10},{0x21,11}})setupAt(120,pair.first,pair.second);for(auto pair:{std::pair<uint8_t,uint8_t>{0x21,0x20},{0xa1,0x21}})setupAt(121,pair.first,pair.second,0,0,7);setupAt(122,0xc0,6);auto s=os();check(s.count==5&&s.ignored==3&&s.unsupported==0&&!s.firstUnsupported.present,"originalwhitelist/exclusions unchanged");
 }else if(id=="V231"){
  prefix();sample(5100,true);setupAt(10100);auto a=os();at(1);auto e=oe(255);of(e,true);auto b=os();check(a.state==b.state&&a.tail.invalid==b.tail.invalid&&a.tail.observed==b.tail.observed,"closedtailimmune tolaterclock/eventnoise");
 }else if(id=="V232"){
  prefix();sample(5100,true);sample(5200,true);at(6000);auto e=oe(DCD_EVENT_UNPLUGGED);of(e,true);sample(6001,true,1);auto s=os();check(!s.live.known&&s.live.mismatch&&s.state==usb_observer::State::Unplugged,"staleSDKtrueafterunplugnotassignedfreshgeneration");
 }else if(id=="V233"){
  ob();setupAt(1);sample(100,true);sample(4000,false);sample(5099,true);sample(6000,false);auto s=os();check(s.firstConfiguredKnown&&s.firstConfiguredAtMs==100&&s.configured&&s.configuredSampleAtMs==5099,"firstSDKtrueandlastcoherentprefixsampledistinguished");check(!s.live.configured&&s.live.atMs==6000&&s.windowFinishedMs==5100&&s.captureClosedObservedAtMs==6000,"nominalcutoff actualclose andlaterSDKsampleseparate");
 }else if(id=="V234"){
  ob();uint32_t seed=0x725a9U;for(unsigned gen=0;gen<100;++gen){resetAt(gen*20000);const uint32_t start=gen*20000+5;sample(start,false);for(unsigned i=0;i<50;++i){seed=seed*1664525U+1013904223U;const uint32_t delta=seed%12000;at(start+delta);auto e=oq((seed&1)?0x80:0xc0,6);__wrap_dcd_event_handler(&e,true);auto s=os();check(s.count<=64&&s.generation==gen+2,"deterministicfabricatedsequencesstaybounded/sessionisolated");if(s.windowClosed)check(s.windowFinishedMs==start+5000||s.clockError,"no inventedcutoffwhenclockfault");}auto s=os();check(s.unsupportedReasons==0,"vendornoiseisnotguessedunsupportedOS");}
 }else check(false,"unknownV2case");
 std::cout<<"PASS "<<id<<" ("<<assertions<<" assertions)\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<argv[1]<<": "<<e.what()<<" ("<<assertions<<")\n";return 1;}}
