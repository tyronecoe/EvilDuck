#pragma once
// Independent bounded language preview. Not part of EvilDuckS3 Arduino sources.
#include <stddef.h>
#include <stdint.h>
namespace ds_preview {
constexpr size_t MaxSource=8192, MaxLine=256, MaxCode=128, MaxText=4096;
constexpr size_t MaxSymbols=32, MaxFunctions=16, MaxConstants=16;
constexpr size_t MaxNesting=16, MaxCalls=8, MaxExprTokens=64, MaxExprDepth=16;
constexpr uint32_t MaxSteps=10000, MaxElapsedMs=30000, MaxTicks=100000;
enum class ErrorCode : uint8_t { None, InputLimit, InvalidSource, LineLimit, CodeLimit,
 TextLimit, Identifier, SymbolLimit, FunctionLimit, ConstantLimit, ConstantExpansion,
 DuplicateConstant, DuplicateFunction, UnknownStatement, Unsupported, Syntax,
 Structure, NestingLimit, UndefinedSymbol, Uninitialized, UndefinedFunction,
 ExpressionLimit, Arithmetic, CallLimit, StepLimit, TickLimit, Timeout, InvalidBudget, SinkFailure, NotCompiled, Busy };
struct Error { ErrorCode code=ErrorCode::None; uint16_t line=0, column=0; };
const char* message(ErrorCode code);
enum class Op : uint8_t { Set, Text, TextLn, Delay, Key, If, Jump, Function, Call, Return, EndFunction, Stop };
struct Instruction { uint16_t line=0, offset=0, length=0, target=0, owner=0; Op op=Op::Stop; uint8_t symbol=0; };
struct Function { char name[24]={}; uint16_t entry=0, end=0; };
class Compiler;
class Expression;
class Runtime;
class Program {
    friend class Compiler; friend class Expression; friend class Runtime;
    char text_[MaxText]={}, names_[MaxSymbols][24]={}, source_[64]={};
    Instruction code_[MaxCode]={}; Function functions_[MaxFunctions]={};
    uint16_t used_=0, count_=0; uint8_t symbols_=0, functionsCount_=0;
    uint32_t revision_=0; bool ready_=false; mutable bool borrowed_=false; Error error_{};
public:
    Program()=default;
    Program(const Program&)=delete;
    Program& operator=(const Program&)=delete;
    bool compile(const char* source, size_t bytes, const char* location="preview.duck");
    const Error& error() const { return error_; }
    const char* location() const { return source_; }
    bool ready() const { return ready_; }
    size_t instructions() const { return count_; }
};
enum class EventType : uint8_t { Character, KeyTap, Delay };
struct Event { EventType type; uint16_t value; }; // ASCII byte, HID page07 usage, or milliseconds.
enum class Accept : uint8_t { Accepted, Retry, Failed };
using Sink = Accept(*)(void*, const Event&);
enum class State : uint8_t { Idle, Running, Completed, Cancelled, Error };
class Runtime {
    friend class Expression;
    const Program* program_=nullptr; Sink sink_=nullptr; void* context_=nullptr;
    uint16_t values_[MaxSymbols]={}; bool initialized_[MaxSymbols]={};
    uint16_t returns_[MaxCalls]={}; uint8_t depth_=0;
    uint16_t pc_=0, textPos_=0; bool typing_=false, enter_=false, pending_=false, delayed_=false;
    Event event_{EventType::Character,0}; uint32_t started_=0, delayAt_=0, steps_=0;
    uint32_t stepLimit_=MaxSteps, elapsedLimit_=MaxElapsedMs, ticks_=0, programRevision_=0;
    bool ownsProgram_=false, inTick_=false;
    State state_=State::Idle; Error error_{}; bool hasReturn_=false; uint16_t lastReturn_=0;
    void fail(ErrorCode code,uint16_t column=1);
    void releaseProgram();
    void returnFromCall(bool hasValue,uint16_t value);
    void deliver(uint32_t now);
public:
    Runtime()=default;
    Runtime(const Runtime&)=delete;
    Runtime& operator=(const Runtime&)=delete;
    ~Runtime(){cancel();}
    bool start(const Program&, Sink, void*, uint32_t now=0, uint32_t stepLimit=MaxSteps, uint32_t elapsedLimit=MaxElapsedMs);
    void tick(uint32_t now); // One instruction or one event attempt, no blocking waits.
    void cancel();
    State state() const { return state_; }
    const Error& error() const { return error_; }
    uint32_t steps() const { return steps_; }
    bool variable(const char* name,uint16_t& out) const;
    bool returned(uint16_t& out) const { if(!hasReturn_)return false;out=lastReturn_;return true; }
};
}
