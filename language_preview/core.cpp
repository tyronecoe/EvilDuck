#include "core.h"
#include <string.h>
#include <new>
namespace ds_preview {
namespace {
bool white(char c){return c==' '||c=='\t';}
bool letter(char c){return (c>='A'&&c<='Z')||(c>='a'&&c<='z')||c=='_';}
bool digit(char c){return c>='0'&&c<='9';}
bool ident(const char* s){if(!letter(*s))return false;for(++s;*s;++s)if(!letter(*s)&&!digit(*s))return false;return true;}
char* left(char* p){while(white(*p))++p;return p;}
void right(char* p){size_t n=strlen(p);while(n&&white(p[n-1]))p[--n]=0;}
bool exact(const char* p,const char* word){return strcmp(p,word)==0;}
bool whole(const char* p,const char* word){while(white(*p))++p;size_t n=strlen(word);if(strncmp(p,word,n))return false;p+=n;while(white(*p))++p;return !*p;}
bool command(const char* p,const char* word){size_t n=strlen(word);return strncmp(p,word,n)==0&&(p[n]==0||white(p[n]));}
char* argument(char* p){while(*p&&!white(*p))++p;return *p?p+1:p;}
int findName(const char names[][24],size_t n,const char* name){for(size_t i=0;i<n;++i)if(exact(names[i],name))return static_cast<int>(i);return -1;}
bool functionName(const char* p,char (&name)[24]){size_t n=strlen(p);if(n<3||n>25||p[n-2]!='('||p[n-1]!=')')return false;memcpy(name,p,n-2);name[n-2]=0;return ident(name);}
uint8_t key(const char* p){
 const char* names[]={"ENTER","TAB","SPACE","ESCAPE","BACKSPACE","DELETE","UPARROW","DOWNARROW","LEFTARROW","RIGHTARROW"};
 const uint8_t codes[]={0x28,0x2b,0x2c,0x29,0x2a,0x4c,0x52,0x51,0x50,0x4f};
 for(size_t i=0;i<10;++i)if(exact(p,names[i]))return codes[i];return 0;
}
// Deliberately narrow reference-backed ownership operand domain. No modifier prefix guesses.
uint8_t ownedKey(const char* p){
 if(uint8_t named=key(p))return named;
 if(!p[0]||p[1])return 0;
 if(p[0]>='a'&&p[0]<='z')return static_cast<uint8_t>(4+p[0]-'a');
 if(p[0]>='1'&&p[0]<='9')return static_cast<uint8_t>(0x1e + p[0]-'1');
 return p[0]=='0'?0x27:0;
}
bool reserved(const char* p){
 const char* names[]={"REM","REM_BLOCK","END_REM","STRING","STRINGLN","END_STRING","END_STRINGLN","DELAY","VAR","DEFINE","IF","ELSE","END_IF","WHILE","END_WHILE","FUNCTION","END_FUNCTION","RETURN","STOP_PAYLOAD","ATTACKMODE","HOLD","RELEASE","RESET","INJECT_MOD","INJECT_VAR"};
 if(key(p))return true;for(const char* n:names)if(exact(p,n))return true;return false;
}
}
const char* message(ErrorCode c){
 switch(c){
 case ErrorCode::None:return "No error";case ErrorCode::InputLimit:return "Source exceeds 8192-byte bound";
 case ErrorCode::InvalidSource:return "Invalid source byte or line ending";case ErrorCode::LineLimit:return "Physical line exceeds 256 bytes";
 case ErrorCode::CodeLimit:return "Instruction limit exceeded";case ErrorCode::TextLimit:return "Expanded operand storage exceeded";
 case ErrorCode::Identifier:return "Invalid, reserved or overlong identifier";case ErrorCode::SymbolLimit:return "Variable limit exceeded";
 case ErrorCode::FunctionLimit:return "Function limit exceeded";case ErrorCode::ConstantLimit:return "Constant limit exceeded";
 case ErrorCode::ConstantExpansion:return "Constant expansion exceeds line limit";case ErrorCode::DuplicateConstant:return "Duplicate constant rejected";
 case ErrorCode::DuplicateFunction:return "Duplicate function rejected";case ErrorCode::UnknownStatement:return "Unknown or unsupported statement";
 case ErrorCode::Unsupported:return "Recognized feature not supported in this preview";case ErrorCode::Syntax:return "Malformed statement or expression";
 case ErrorCode::Structure:return "Unmatched, misordered or unterminated block";case ErrorCode::NestingLimit:return "Block nesting limit exceeded";
 case ErrorCode::UndefinedSymbol:return "Variable has no declaration";case ErrorCode::Uninitialized:return "Variable declaration has not executed";
 case ErrorCode::UndefinedFunction:return "Function is undefined";case ErrorCode::ExpressionLimit:return "Expression token or depth limit exceeded";
 case ErrorCode::Arithmetic:return "Arithmetic outside uint16 domain, invalid shift or division by zero";
 case ErrorCode::CallLimit:return "Function call depth exceeded";case ErrorCode::StepLimit:return "Execution step budget exhausted";
 case ErrorCode::TickLimit:return "Tick budget exhausted (clock/backpressure/no progress)";
 case ErrorCode::Timeout:return "Elapsed work budget exhausted";case ErrorCode::InvalidBudget:return "Execution budget outside preview bounds";
 case ErrorCode::VoidValue:return "Function returned no value in a numeric context";
 case ErrorCode::SinkFailure:return "Mock sink rejected event";
 case ErrorCode::NotCompiled:return "Program did not pass preflight";case ErrorCode::Busy:return "Cannot restart an active preview session";
 case ErrorCode::ReadError:return "Mock source read failed or changed";case ErrorCode::SeekError:return "Mock source seek failed";case ErrorCode::CompileLimit:return "Compiler step budget exhausted";
 }
 return "Unknown preview error";
}
bool Program::ownershipCommands()const{
 if(!ready_)return false;
 for(size_t i=0;i<count_;++i)if(code_[i].op==Op::Hold||code_[i].op==Op::Release)return true;
 return false;
}
// One evaluator used for validation and every runtime numeric consumer. No AST/allocation.
class Expression {
 struct Value{uint16_t v=0;bool known=false;};
 const Program& p_;const char* input_;Continuation* output_;bool enforceValues_;size_t pos_=0,column_=0,tokens_=0,start_=0;
 enum Token{End,Number,Variable,FunctionCall,Open,Close,Binary,Invalid};Token token_=End;
 uint16_t number_=0;char name_[24]={};char op_[3]={};ErrorCode error_=ErrorCode::None;
 void fail(ErrorCode c){if(error_==ErrorCode::None){error_=c;column_=pos_+1;}}
 void next(){
  if(error_!=ErrorCode::None)return;while(white(input_[pos_]))++pos_;
  start_=pos_+1;char c=input_[pos_];if(!c){token_=End;return;}
  if(++tokens_>MaxExprTokens){fail(ErrorCode::ExpressionLimit);return;}
  if(digit(c)){
   uint32_t v=0;unsigned base=10;if(c=='0'&&input_[pos_+1]=='x'){base=16;pos_+=2;}
   size_t start=pos_;for(;;){char x=input_[pos_];int d=digit(x)?x-'0':(x>='a'&&x<='f'?x-'a'+10:(x>='A'&&x<='F'?x-'A'+10:-1));if(d<0||static_cast<unsigned>(d)>=base)break;
    if(v>(65535u-static_cast<unsigned>(d))/base){fail(ErrorCode::Arithmetic);return;}v=v*base+static_cast<unsigned>(d);++pos_;}
   if(pos_==start){fail(ErrorCode::Syntax);return;}number_=static_cast<uint16_t>(v);token_=Number;return;
  }
  if(c=='$'||letter(c)){
   bool var=c=='$';size_t start=pos_;if(var)++pos_;while(letter(input_[pos_])||digit(input_[pos_]))++pos_;
   size_t n=pos_-start;if(n>=sizeof(name_)){fail(ErrorCode::Identifier);return;}memcpy(name_,input_+start,n);name_[n]=0;
   if(var){if(n<2||!letter(name_[1])||name_[1]=='_'){fail(ErrorCode::Identifier);return;}token_=Variable;return;}
   if(exact(name_,"TRUE")||exact(name_,"FALSE")){number_=exact(name_,"TRUE")?1:0;token_=Number;return;}
   if(input_[pos_]=='('){
    if(input_[pos_+1]!=')'){fail(ErrorCode::Syntax);return;}
    tokens_+=2;if(tokens_>MaxExprTokens){fail(ErrorCode::ExpressionLimit);return;}pos_+=2;
    int function=-1;for(size_t i=0;i<p_.functionsCount_;++i)if(exact(name_,p_.functions_[i].name))function=static_cast<int>(i);
    if(function<0){fail(ErrorCode::UndefinedFunction);return;}
    if(enforceValues_&&!(p_.valueFunctions_&(1u<<function))){fail(ErrorCode::VoidValue);return;}
    number_=static_cast<uint16_t>(function);token_=FunctionCall;return;
   }
   fail(ErrorCode::Syntax);return;
  }
  ++pos_;if(c=='('){token_=Open;return;}if(c==')'){token_=Close;return;}
  op_[0]=c;op_[1]=0;op_[2]=0;
  if((c=='&'&&input_[pos_]=='&')||(c=='|'&&input_[pos_]=='|')||((c=='<'||c=='>')&&input_[pos_]==c)||((c=='='||c=='!'||c=='<'||c=='>')&&input_[pos_]=='=')){op_[1]=input_[pos_++];}
  if(!strcmp(op_,"=")||!strcmp(op_,"!")||!strchr("+-*/%^<>=!&|",c)){fail(ErrorCode::Syntax);return;}
  token_=Binary;
 }
 static int precedence(const char* op){if(exact(op,"||"))return 1;if(exact(op,"&&"))return 2;if(exact(op,"|"))return 3;if(exact(op,"&"))return 4;if(exact(op,"==")||exact(op,"!="))return 5;if(exact(op,"<")||exact(op,">")||exact(op,"<=")||exact(op,">="))return 6;if(exact(op,"<<")||exact(op,">>"))return 7;if(exact(op,"+")||exact(op,"-"))return 8;if(exact(op,"*")||exact(op,"/")||exact(op,"%"))return 9;return 10;}
 Value apply(const char* op,Value a,Value b){
  if(b.known&&((exact(op,"/")||exact(op,"%"))&&b.v==0)){fail(ErrorCode::Arithmetic);return {};}
  if(b.known&&(exact(op,"<<")||exact(op,">>"))&&b.v>15){fail(ErrorCode::Arithmetic);return {};}
  if(!a.known||!b.known){
   // Compile-time truth facts only. Postfix still contains both operands/calls.
   if(exact(op,"&&")&&((a.known&&!a.v)||(b.known&&!b.v)))return {0,true};
   if(exact(op,"||")&&((a.known&&a.v)||(b.known&&b.v)))return {1,true};
   return {};
  }
  uint32_t v=0;
  if(exact(op,"+"))v=uint32_t(a.v)+b.v;
  else if(exact(op,"-")){if(a.v<b.v){fail(ErrorCode::Arithmetic);return {};}v=a.v-b.v;}
  else if(exact(op,"*"))v=uint32_t(a.v)*b.v;
  else if(exact(op,"/"))v=a.v/b.v;else if(exact(op,"%"))v=a.v%b.v;
  else if(exact(op,"^")){
   uint32_t result=1,base=a.v,e=b.v;if(!base&&!e){fail(ErrorCode::Arithmetic);return {};}
   while(e){if(e&1){result*=base;if(result>65535){fail(ErrorCode::Arithmetic);return {};}}e>>=1;if(e){base*=base;if(base>65535){fail(ErrorCode::Arithmetic);return {};}}}v=result;
  }else if(exact(op,"=="))v=a.v==b.v;else if(exact(op,"!="))v=a.v!=b.v;
  else if(exact(op,"<"))v=a.v<b.v;else if(exact(op,">"))v=a.v>b.v;
  else if(exact(op,"<="))v=a.v<=b.v;else if(exact(op,">="))v=a.v>=b.v;
  else if(exact(op,"&&"))v=a.v&&b.v;else if(exact(op,"||"))v=a.v||b.v;
  else if(exact(op,"&"))v=a.v&b.v;else if(exact(op,"|"))v=a.v|b.v;
  else if(exact(op,"<<"))v=uint32_t(a.v)<<b.v;else if(exact(op,">>"))v=a.v>>b.v;
  if(v>65535){fail(ErrorCode::Arithmetic);return {};}return {static_cast<uint16_t>(v),true};
 }
 void emit(ExprKind kind,uint16_t value,uint16_t column){
  if(!output_)return;if(output_->length==MaxExprTokens){fail(ErrorCode::ExpressionLimit);return;}
  output_->tokens[output_->length++]={value,column,kind};
 }
 static const char* binaryName(uint16_t code){
  static const char* const names[]={"||","&&","|","&","==","!=","<",">","<=",">=","<<",">>","+","-","*","/","%","^"};return code<18?names[code]:"";
 }
 static uint16_t binaryCode(const char* op){for(uint16_t i=0;i<18;++i)if(exact(op,binaryName(i)))return i;return 65535;}
 Value parse(int min,unsigned depth){
  if(depth>MaxExprDepth){fail(ErrorCode::ExpressionLimit);return {};}
  Value v{};
  if(token_==Number){v={number_,true};emit(ExprKind::Literal,number_,static_cast<uint16_t>(start_));next();}
  else if(token_==Variable){int i=findName(p_.names_,p_.symbols_,name_);if(i<0){fail(ErrorCode::UndefinedSymbol);return {};}
   emit(ExprKind::Variable,static_cast<uint16_t>(i),static_cast<uint16_t>(start_));next();
  }else if(token_==FunctionCall){emit(ExprKind::Call,number_,static_cast<uint16_t>(start_));next();}
  else if(token_==Open){next();v=parse(1,depth+1);if(token_!=Close){fail(ErrorCode::Syntax);return {};}next();}
  else{fail(ErrorCode::Syntax);return {};}
  while(error_==ErrorCode::None&&token_==Binary&&precedence(op_)>=min){char op[3];memcpy(op,op_,3);uint16_t at=static_cast<uint16_t>(start_);int level=precedence(op);next();Value rhs=parse(level+(exact(op,"^")?0:1),depth+1);v=apply(op,v,rhs);emit(ExprKind::Binary,binaryCode(op),at);}
  return v;
 }
public:
 Expression(const Program& p,const Runtime*,const char* input,Continuation* output=nullptr,bool enforceValues=false):p_(p),input_(input),output_(output),enforceValues_(enforceValues){}
 Error evaluate(uint16_t& out,bool* known=nullptr){if(output_)output_->clear();next();Value v=parse(1,1);if(token_!=End)fail(ErrorCode::Syntax);out=v.v;if(known)*known=v.known;if(output_&&error_==ErrorCode::None)output_->active=true;return {error_,0,static_cast<uint16_t>(column_)};}
 static Error operate(const Program& p,uint16_t code,uint16_t left,uint16_t right,uint16_t& out){
  if(code>=18){out=0;return {ErrorCode::Structure,0,0};}
  Expression e(p,nullptr,"");Value result=e.apply(binaryName(code),{left,true},{right,true});out=result.v;return {e.error_,0,0};
 }
};
class Compiler {
 struct Constant{char name[24]={},value[64]={};};Constant constants_[MaxConstants]{};size_t constantsCount_=0;
 struct Block{Op kind;uint16_t start,lastFalse;bool otherwise=false;};Block blocks_[MaxNesting]{};size_t depth_=0;
 Program& p_;Reader reader_;size_t received_=0,seen_=0;uint16_t line_=1;
 char raw_[MaxLine+1]={},chunk_[ReadChunk]={};size_t rawUsed_=0,chunkUsed_=0,chunkPos_=0;
 unsigned pass_=0;bool cr_=false,eof_=false;uint8_t bom_=0;
 uint64_t hash_=1469598103934665603ull,firstHash_=0;
 bool visited_[MaxCode]={};uint16_t work_[MaxCode]={};size_t workUsed_=0,function_=0,validate_=0;
 CompilePhase phase_=CompilePhase::SeekFirst;bool comment_=false;uint8_t textMode_=0;uint16_t textInstruction_=0,textOpening_=0;
 bool fail(ErrorCode c,uint16_t column=1){if(p_.error_.code==ErrorCode::None)p_.error_={c,line_,column};return false;}
 bool skip(char* text){
  if(comment_){if(exact(text,"END_REM"))comment_=false;return true;}
  if(command(text,"REM"))return true;
  if(command(text,"REM_BLOCK")){
   char* arg=left(argument(text));if(*arg&&!exact(arg,"DOCUMENTATION")){fail(ErrorCode::Syntax);return true;}comment_=true;return true;
  }return false;
 }
 bool addSymbol(const char* name){
  if(strlen(name)>=24||name[0]!='$'||!ident(name+1)||name[1]=='_')return fail(ErrorCode::Identifier);
  if(findName(p_.names_,p_.symbols_,name)>=0)return true;
  if(p_.symbols_==MaxSymbols)return fail(ErrorCode::SymbolLimit);strcpy(p_.names_[p_.symbols_++],name);return true;
 }
 bool constant(char* text){
  char* label=left(argument(text));char* value=label;while(*value&&!white(*value))++value;
  if(!*value)return fail(ErrorCode::Syntax);*value++=0;
  if(strlen(label)>=24||strlen(value)>=64||!ident(label+(*label=='#'))||!*value)return fail(ErrorCode::Identifier);
  for(size_t i=0;i<constantsCount_;++i)if(exact(label,constants_[i].name))return fail(ErrorCode::DuplicateConstant);
  if(constantsCount_==MaxConstants)return fail(ErrorCode::ConstantLimit);
  strcpy(constants_[constantsCount_].name,label);strcpy(constants_[constantsCount_++].value,value);return true;
 }
 bool expand(const char* input,char (&output)[MaxLine+1]){
  size_t i=0,n=0;
  while(input[i]){
   const Constant* best=nullptr;size_t match=0;
   for(size_t c=0;c<constantsCount_;++c){const Constant& k=constants_[c];size_t z=strlen(k.name);
    if(z>match&&strncmp(input+i,k.name,z)==0&&(k.name[0]=='#'||((i==0||input[i-1]==' ')&&(input[i+z]==0||input[i+z]==' ')))){best=&k;match=z;}}
   if(best){size_t z=strlen(best->value);if(n+z>MaxLine)return fail(ErrorCode::ConstantExpansion);memcpy(output+n,best->value,z);n+=z;i+=match;}
   else{if(n==MaxLine)return fail(ErrorCode::ConstantExpansion);output[n++]=input[i++];}
  }output[n]=0;return true;
 }
 bool emit(Op op,const char* arg="",uint16_t target=0,uint8_t symbol=0,uint16_t owner=0){
  if(p_.count_==MaxCode)return fail(ErrorCode::CodeLimit);size_t n=strlen(arg);
  if(p_.used_+n+1>MaxText)return fail(ErrorCode::TextLimit);
  Instruction& ins=p_.code_[p_.count_++];ins={line_,p_.used_,static_cast<uint16_t>(n),target,owner,op,symbol};
  memcpy(p_.text_+p_.used_,arg,n+1);p_.used_+=static_cast<uint16_t>(n+1);return true;
 }
 // Blocks use one IR instruction and checked, byte-addressed arena records.
 bool textLine(char* raw,unsigned pass){
  const char* close=textMode_==1?"END_STRING":"END_STRINGLN";
  if(whole(raw,close)){if(pass)p_.code_[textInstruction_].length=p_.used_-p_.code_[textInstruction_].offset;textMode_=0;return true;}
  char* trimmed=left(raw);
  if(command(trimmed,"END_STRING")||command(trimmed,"END_STRINGLN")||whole(raw,"STRING")||whole(raw,"STRINGLN"))return fail(ErrorCode::Structure,static_cast<uint16_t>(trimmed-raw+1));
  if(!pass)return true;
  const char* content=textMode_==1?trimmed:(raw[0]=='\t'?raw+1:raw);
  char expanded[MaxLine+1]={};if(!expand(content,expanded))return false;
  size_t length=strlen(expanded),required=4+length;
  if(required>MaxText-p_.used_)return fail(ErrorCode::TextLimit);
  char* record=p_.text_+p_.used_;record[0]=static_cast<char>(line_&255);record[1]=static_cast<char>(line_>>8);
  record[2]=static_cast<char>(length&255);record[3]=static_cast<char>(length>>8);memcpy(record+4,expanded,length);
  p_.used_+=static_cast<uint16_t>(required);return true;
 }
 bool openText(const char* text,unsigned pass){
  textMode_=exact(text,"STRING")?1:2;textOpening_=line_;
  if(pass){if(p_.count_==MaxCode)return fail(ErrorCode::CodeLimit);textInstruction_=p_.count_++;
   p_.code_[textInstruction_]={line_,p_.used_,0,0,0,textMode_==1?Op::TextBlock:Op::TextLnBlock,0};}
  return true;
 }
 bool expr(const char* arg){uint16_t ignored;Error e=Expression(p_,nullptr,arg).evaluate(ignored);return e.code==ErrorCode::None||fail(e.code,e.column);}
 int fn(const char* name){for(size_t i=0;i<p_.functionsCount_;++i)if(exact(name,p_.functions_[i].name))return static_cast<int>(i);return -1;}
 bool push(Op op,uint16_t start){if(depth_==MaxNesting)return fail(ErrorCode::NestingLimit);blocks_[depth_++]={op,start,start,false};return true;}
 bool condition(char* text,char (&expanded)[MaxLine+1],bool then){
  right(text);if(then){size_t n=strlen(text);if(n<5||strcmp(text+n-4,"THEN")||!white(text[n-5]))return fail(ErrorCode::Syntax);text[n-4]=0;right(text);}
  return expand(text,expanded)&&expr(expanded);
 }
 bool statement(char* text){
  right(text);if(!*text||skip(text))return p_.error_.code==ErrorCode::None;
  if(command(text,"DEFINE"))return true;
  if(exact(text,"END_REM"))return fail(ErrorCode::Structure);
  char expanded[MaxLine+1]={};char name[24]={};
  if(command(text,"VAR")||text[0]=='$'){
   bool declare=command(text,"VAR");char* start=declare?left(argument(text)):text;char* end=start;while(*end&&!white(*end)&&*end!='=')++end;
   if(*end=='='){*end++=0;}else{if(!*end)return fail(ErrorCode::Syntax);*end++=0;end=left(end);if(*end++!='=')return fail(ErrorCode::Syntax);}
   int id=findName(p_.names_,p_.symbols_,start);if(id<0)return fail(ErrorCode::UndefinedSymbol);
   if(!expand(left(end),expanded)||!expr(expanded))return false;
   // target differentiates declaration from assignment: only VAR may initialize.
   return emit(Op::Set,expanded,declare?1:0,static_cast<uint8_t>(id));
  }
  if(command(text,"STRING")||command(text,"STRINGLN")){
   bool enter=command(text,"STRINGLN");char* arg=argument(text);if(!*arg)return fail(ErrorCode::Unsupported);
   if(!expand(arg,expanded))return false;right(expanded);return emit(enter?Op::TextLn:Op::Text,expanded);
  }
  if(command(text,"DELAY")){if(!expand(left(argument(text)),expanded)||!expr(expanded))return false;return emit(Op::Delay,expanded);}
  if(command(text,"IF")){if(!condition(left(argument(text)),expanded,true))return false;uint16_t pc=p_.count_;return emit(Op::If,expanded)&&push(Op::If,pc);}
  if(command(text,"ELSE")){
   if(!depth_||blocks_[depth_-1].kind!=Op::If||blocks_[depth_-1].otherwise)return fail(ErrorCode::Structure);
   Block& b=blocks_[depth_-1];char* arg=left(argument(text));bool elseif=command(arg,"IF");
   if(*arg&&!elseif)return fail(ErrorCode::Syntax);
   if(elseif&&!condition(left(argument(arg)),expanded,true))return false;
   p_.code_[b.lastFalse].target=p_.count_+1;if(!emit(Op::Jump,"",0,0,b.start))return false;
   if(elseif){b.lastFalse=p_.count_;return emit(Op::If,expanded);}b.otherwise=true;return true;
  }
  if(exact(text,"END_IF")){
   if(!depth_||blocks_[depth_-1].kind!=Op::If)return fail(ErrorCode::Structure);Block b=blocks_[--depth_];
   if(!b.otherwise)p_.code_[b.lastFalse].target=p_.count_;
   for(size_t i=b.start;i<p_.count_;++i)if(p_.code_[i].op==Op::Jump&&p_.code_[i].owner==b.start)p_.code_[i].target=p_.count_;
   return true;
  }
  if(command(text,"WHILE")){if(!condition(left(argument(text)),expanded,false))return false;uint16_t pc=p_.count_;return emit(Op::If,expanded)&&push(Op::Jump,pc);}
  if(exact(text,"END_WHILE")){if(!depth_||blocks_[depth_-1].kind!=Op::Jump)return fail(ErrorCode::Structure);Block b=blocks_[--depth_];p_.code_[b.start].target=p_.count_+1;return emit(Op::Jump,"",b.start,0,65535);}
  if(command(text,"FUNCTION")){
   if(depth_||!functionName(left(argument(text)),name))return fail(ErrorCode::Structure);int id=fn(name);if(id<0)return fail(ErrorCode::UndefinedFunction);
   uint16_t pc=p_.count_;p_.functions_[id].entry=pc+1;return emit(Op::Function,"",0,static_cast<uint8_t>(id))&&push(Op::Function,pc);
  }
  if(exact(text,"END_FUNCTION")){
   if(!depth_||blocks_[depth_-1].kind!=Op::Function)return fail(ErrorCode::Structure);Block b=blocks_[--depth_];uint8_t id=p_.code_[b.start].symbol;
   p_.functions_[id].end=p_.count_;p_.code_[b.start].target=p_.count_+1;return emit(Op::EndFunction);
  }
  if(command(text,"RETURN")){
   if(!depth_||blocks_[0].kind!=Op::Function)return fail(ErrorCode::Structure);
   char* arg=left(argument(text));if(*arg&&(!expand(arg,expanded)||!expr(expanded)))return false;return emit(Op::Return,expanded);
  }
  if(exact(text,"STOP_PAYLOAD"))return emit(Op::Stop);
  if(command(text,"HOLD")||command(text,"RELEASE")){
   bool acquire=command(text,"HOLD");if(!expand(left(argument(text)),expanded))return false;
   right(expanded);uint8_t usage=ownedKey(expanded);if(!usage)return fail(ErrorCode::Unsupported);
   return emit(acquire?Op::Hold:Op::Release,"",usage);
  }
  if(uint8_t k=key(text))return emit(Op::Key,"",k);
  if(functionName(text,name)){int id=fn(name);if(id<0)return fail(ErrorCode::UndefinedFunction);return emit(Op::Call,"",0,static_cast<uint8_t>(id));}
  return fail(ErrorCode::UnknownStatement);
 }
 void enqueue(uint16_t pc){const Function& f=p_.functions_[function_];if(pc>=f.entry&&pc<=f.end&&!visited_[pc]){visited_[pc]=true;work_[workUsed_++]=pc;}}
 bool line(){
  if(textMode_)return textLine(raw_,pass_);
  char* text=left(raw_);right(text);
  if(!comment_&&(exact(text,"STRING")||exact(text,"STRINGLN")))return openText(text,pass_);
  if(!comment_&&(command(text,"END_STRING")||command(text,"END_STRINGLN")))return fail(ErrorCode::Structure,static_cast<uint16_t>(text-raw_+1));
  if(pass_)return statement(text);
  if(!*text||skip(text))return p_.error_.code==ErrorCode::None;
  if(command(text,"DEFINE"))return constant(text);
  if(command(text,"VAR")){char* name=left(argument(text));char* end=name;while(*end&&!white(*end)&&*end!='=')++end;*end=0;return addSymbol(name);}
  if(command(text,"FUNCTION")){
   char name[24]={};if(!functionName(left(argument(text)),name)||reserved(name))return fail(ErrorCode::Identifier);
   if(fn(name)>=0)return fail(ErrorCode::DuplicateFunction);if(p_.functionsCount_==MaxFunctions)return fail(ErrorCode::FunctionLimit);strcpy(p_.functions_[p_.functionsCount_++].name,name);
  }return true;
 }
 bool byte(unsigned char c){
  hash_=(hash_^c)*1099511628211ull;size_t at=seen_++;
  if(at==0&&c==0xef&&reader_.bytes>=3){bom_=1;return true;}
  if(bom_){if((bom_==1&&c!=0xbb)||(bom_==2&&c!=0xbf))return fail(ErrorCode::InvalidSource);if(++bom_==3)bom_=0;return true;}
  if(cr_){if(c!='\n')return fail(ErrorCode::InvalidSource);cr_=false;phase_=CompilePhase::Line;return true;}
  if(c=='\r'){cr_=true;return true;}
  if(c=='\n'){phase_=CompilePhase::Line;return true;}
  if(c==0||(c<32&&c!='\t')||c>126)return fail(ErrorCode::InvalidSource);
  if(rawUsed_==MaxLine)return fail(ErrorCode::LineLimit);raw_[rawUsed_++]=static_cast<char>(c);raw_[rawUsed_]=0;return true;
 }
public:
 Compiler(Program& p,Reader reader):p_(p),reader_(reader){}
 CompilePhase phase()const{return phase_;}
 void abort(ErrorCode code){fail(code,static_cast<uint16_t>(rawUsed_+1));}
 void detach(){reader_=Reader{};}
 bool step(CompileWork& cost){
  switch(phase_){
  case CompilePhase::SeekFirst:case CompilePhase::Rewind:{
   ++cost.callbacks;if(!reader_.seek(reader_.context,0))return fail(ErrorCode::SeekError);
   received_=seen_=rawUsed_=chunkUsed_=chunkPos_=0;cr_=eof_=false;bom_=0;hash_=1469598103934665603ull;line_=1;comment_=false;textMode_=0;raw_[0]=0;phase_=CompilePhase::Read;return true;
  }
  case CompilePhase::Read:{
   size_t capacity=reader_.bytes-received_;if(capacity>ReadChunk)capacity=ReadChunk;
   ++cost.callbacks;ReadResult result=reader_.read(reader_.context,chunk_,capacity);
   if(result.bytes>capacity)return fail(ErrorCode::ReadError);
   if(result.status==ReadStatus::Retry){if(result.bytes)return fail(ErrorCode::ReadError);return true;}
   if(result.status==ReadStatus::Eof){
    if(result.bytes||received_!=reader_.bytes)return fail(ErrorCode::ReadError);eof_=true;
    if(cr_||bom_)return fail(ErrorCode::InvalidSource);
    phase_=rawUsed_?CompilePhase::Line:CompilePhase::EndPass;return true;
   }
   if(result.status==ReadStatus::Error)return fail(result.error==ErrorCode::InvalidSource?ErrorCode::InvalidSource:ErrorCode::ReadError);
   if(result.status!=ReadStatus::Data||!result.bytes)return fail(ErrorCode::ReadError);
   received_+=result.bytes;chunkUsed_=result.bytes;chunkPos_=0;phase_=CompilePhase::Consume;return true;
  }
  case CompilePhase::Consume:
   while(chunkPos_<chunkUsed_&&cost.bytes<ReadChunk){++cost.bytes;if(!byte(static_cast<unsigned char>(chunk_[chunkPos_++])))return false;if(phase_==CompilePhase::Line)return true;}
   if(chunkPos_==chunkUsed_)phase_=CompilePhase::Read;return true;
  case CompilePhase::Line:
   ++cost.lines;if(!line())return false;rawUsed_=0;raw_[0]=0;++line_;phase_=eof_?CompilePhase::EndPass:(chunkPos_==chunkUsed_?CompilePhase::Read:CompilePhase::Consume);return true;
  case CompilePhase::EndPass:
   if(textMode_){line_=textOpening_;return fail(ErrorCode::Structure);}if(comment_){if(line_>1)--line_;return fail(ErrorCode::Structure);}
   if(!pass_){firstHash_=hash_;pass_=1;phase_=CompilePhase::Rewind;}else{if(hash_!=firstHash_)return fail(ErrorCode::ReadError);phase_=CompilePhase::Structure;}return true;
  case CompilePhase::Structure:
   if(depth_){if(line_>1)--line_;return fail(ErrorCode::Structure);}phase_=CompilePhase::InventoryStart;return true;
  case CompilePhase::InventoryStart:
   if(function_==p_.functionsCount_){phase_=CompilePhase::Validate;return true;}
   memset(visited_,0,sizeof(visited_));workUsed_=0;enqueue(p_.functions_[function_].entry);phase_=CompilePhase::InventoryNode;return true;
  case CompilePhase::InventoryNode:{
   if(!workUsed_){++function_;phase_=CompilePhase::InventoryStart;return true;}
   ++cost.nodes;uint16_t pc=work_[--workUsed_];const Instruction& ins=p_.code_[pc];line_=ins.line;
   if(ins.op==Op::Return){if(ins.length)p_.valueFunctions_|=static_cast<uint16_t>(1u<<function_);return true;}
   if(ins.op==Op::EndFunction||ins.op==Op::Stop)return true;
   if(ins.op==Op::Jump){enqueue(ins.target);return true;}
   if(ins.op==Op::If){++cost.expressions;uint16_t value=0;bool known=false;Expression e(p_,nullptr,p_.text_+ins.offset);Error error=e.evaluate(value,&known);
    if(error.code!=ErrorCode::None)return fail(error.code,error.column);if(!known||value)enqueue(pc+1);if(!known||!value)enqueue(ins.target);return true;}
   enqueue(pc+1);return true;
  }
  case CompilePhase::Validate:{
   if(validate_==p_.count_){phase_=CompilePhase::Publish;return true;}const Instruction& ins=p_.code_[validate_++];line_=ins.line;
   if(ins.op==Op::Set||ins.op==Op::If||ins.op==Op::Delay||(ins.op==Op::Return&&ins.length)){
    ++cost.expressions;uint16_t ignored=0;Expression e(p_,nullptr,p_.text_+ins.offset,nullptr,true);Error error=e.evaluate(ignored);if(error.code!=ErrorCode::None)return fail(error.code,error.column);
   }return true;
  }
  case CompilePhase::Publish:p_.ready_=true;return true;
  }return fail(ErrorCode::Structure);
 }
};
static_assert(sizeof(Compiler)<=CompileStorage,"Fixed compiler storage too small");
static_assert(alignof(Compiler)<=alignof(max_align_t),"Compiler storage alignment");
ReadResult MemoryReader::read(void* ptr,char* out,size_t capacity){
 auto& m=*static_cast<MemoryReader*>(ptr);if(m.position==m.bytes)return {ReadStatus::Eof,0};
 if(!m.source)return {ReadStatus::Error,0,ErrorCode::InvalidSource};if(m.position>m.bytes||!capacity)return {ReadStatus::Error,0};size_t n=m.bytes-m.position;if(n>capacity)n=capacity;memcpy(out,m.source+m.position,n);m.position+=n;return {ReadStatus::Data,n};
}
bool MemoryReader::seek(void* ptr,size_t position){auto& m=*static_cast<MemoryReader*>(ptr);if(position>m.bytes)return false;m.position=position;return true;}
Reader MemoryReader::reader(){return {read,seek,this,bytes};}
size_t CompileSession::compilerBytes(){return sizeof(Compiler);}
CompileSession::~CompileSession(){cancel();if(compiler_)compiler_->~Compiler();}
void CompileSession::finish(CompileState state){if(compiler_)compiler_->detach();state_=state;if(program_){program_->compiling_=false;if(state!=CompileState::Complete)program_->ready_=false;error_=program_->error_;} }
bool CompileSession::start(Program& p,Reader reader,const char* location,uint32_t limit){
 if(inStep_||state_==CompileState::Compiling)return false;
 if(p.borrowed_||p.compiling_){error_={ErrorCode::Busy,0,0};return false;}
 if(compiler_){compiler_->~Compiler();compiler_=nullptr;}
 program_=&p;state_=CompileState::Compiling;steps_=0;limit_=limit;work_={};error_={};
 ++p.revision_;p.ready_=false;p.compiling_=true;p.used_=p.count_=p.valueFunctions_=0;p.symbols_=p.functionsCount_=0;p.error_={};
 memset(p.names_,0,sizeof(p.names_));for(auto& f:p.functions_)f=Function{};for(auto& i:p.code_)i=Instruction{};memset(p.text_,0,sizeof(p.text_));
 size_t n=0;if(location)while(n<sizeof(p.source_)&&location[n])++n;
 ErrorCode err=ErrorCode::None;
 if(!location||n==sizeof(p.source_))err=ErrorCode::Identifier;else memcpy(p.source_,location,n+1);
 if(!limit||limit>MaxCompileSteps)err=ErrorCode::InvalidBudget;
 if(reader.bytes>MaxSource)err=ErrorCode::InputLimit;
 if(!reader.read||!reader.seek)err=ErrorCode::ReadError;
 if(err!=ErrorCode::None){p.error_={err,0,0};finish(CompileState::Error);return false;}
 compiler_=new(storage_) Compiler(p,reader);return true;
}
CompilePhase CompileSession::phase()const{return compiler_?compiler_->phase():CompilePhase::SeekFirst;}
void CompileSession::step(){
 if(state_!=CompileState::Compiling||inStep_)return;work_={};
 if(steps_++==limit_){compiler_->abort(ErrorCode::CompileLimit);finish(CompileState::Error);return;}
 inStep_=true;struct Guard{bool& flag;~Guard(){flag=false;}} guard{inStep_};bool ok=false;
 try{ok=compiler_->step(work_);}catch(...){compiler_->abort(compiler_->phase()==CompilePhase::SeekFirst||compiler_->phase()==CompilePhase::Rewind?ErrorCode::SeekError:ErrorCode::ReadError);}
 if(state_==CompileState::Cancelled){finish(CompileState::Cancelled);return;}
 if(state_!=CompileState::Compiling)return;
 if(!ok){finish(CompileState::Error);return;}if(program_->ready_)finish(CompileState::Complete);
}
void CompileSession::cancel(){if(state_==CompileState::Compiling){if(inStep_)state_=CompileState::Cancelled;else finish(CompileState::Cancelled);}}
bool Program::compile(const char* source,size_t bytes,const char* location){
 if(borrowed_){error_={ErrorCode::Busy,0,0};return false;}if(compiling_)return false;
 MemoryReader memory{source,bytes,0};CompileSession session;
 if(!session.start(*this,memory.reader(),location))return false;
 while(session.state()==CompileState::Compiling)session.step();return session.state()==CompileState::Complete;
}
void Runtime::releaseProgram(){if(ownsProgram_&&program_)program_->borrowed_=false;ownsProgram_=false;}
void Runtime::fail(ErrorCode code,uint16_t column){error_={code,block_.active&&block_.loaded?block_.line:program_&&pc_<program_->count_?program_->code_[pc_].line:static_cast<uint16_t>(0),column};state_=State::Error;pending_=typing_=delayed_=false;block_=TextCursor{};depth_=0;clearContinuations();hasReturn_=false;lastReturn_=0;releaseProgram();}
bool Runtime::start(const Program& p,Sink sink,void* context,uint32_t now,uint32_t steps,uint32_t elapsed){
 if(state_==State::Running||inTick_)return false;releaseProgram();program_=&p;programRevision_=p.revision_;sink_=sink;context_=context;pc_=textPos_=depth_=0;typing_=enter_=pending_=delayed_=false;steps_=0;block_=TextCursor{};error_={};hasReturn_=false;lastReturn_=0;
 memset(values_,0,sizeof(values_));memset(initialized_,0,sizeof(initialized_));for(auto& call:calls_)call=CallFrame{};clearContinuations();started_=now;ticks_=0;stepLimit_=steps;elapsedLimit_=elapsed;
 if(!p.ready_){fail(ErrorCode::NotCompiled);return false;}
 if(!sink){fail(ErrorCode::SinkFailure);return false;}
 if(!steps||steps>MaxSteps||!elapsed||elapsed>MaxElapsedMs){fail(ErrorCode::InvalidBudget);return false;}
 if(p.borrowed_){fail(ErrorCode::Busy);return false;}p.borrowed_=true;ownsProgram_=true;
 state_=State::Running;return true;
}
void Runtime::cancel(){if(state_==State::Running){state_=State::Cancelled;pending_=typing_=delayed_=false;block_=TextCursor{};depth_=0;clearContinuations();hasReturn_=false;lastReturn_=0;releaseProgram();}}
bool Runtime::variable(const char* name,uint16_t& out)const{if(!program_||programRevision_!=program_->revision_||!name)return false;int id=findName(program_->names_,program_->symbols_,name);if(id<0||!initialized_[id])return false;out=values_[id];return true;}
void Runtime::clearContinuations(){for(auto& frame:evaluations_)frame.clear();}
void Runtime::enterCall(uint8_t function,bool needsValue,uint16_t column){
 if(function>=program_->functionsCount_){fail(ErrorCode::Structure,column);return;}
 if(depth_==MaxCalls){fail(ErrorCode::CallLimit,column);return;}
 calls_[depth_]={static_cast<uint16_t>(pc_+(needsValue?0:1)),column,needsValue};
 ++depth_;evaluations_[depth_].clear();hasReturn_=false;lastReturn_=0;pc_=program_->functions_[function].entry;
}
void Runtime::returnFromCall(bool hasValue,uint16_t value){
 if(!depth_){fail(ErrorCode::Structure);return;}
 evaluations_[depth_].clear();CallFrame call=calls_[--depth_];calls_[depth_]=CallFrame{};pc_=call.next;
 if(call.needsValue){
  if(!hasValue){fail(ErrorCode::VoidValue,call.column);return;}
  Continuation& parent=evaluations_[depth_];if(!parent.active||parent.size==MaxExprTokens){fail(ErrorCode::Structure,call.column);return;}
  parent.values[parent.size++]=value;
 }
 hasReturn_=hasValue;lastReturn_=value;
}
void Runtime::evaluationStep(uint32_t now){
 Continuation& frame=evaluations_[depth_];
 if(frame.cursor==frame.length){if(frame.size!=1){fail(ErrorCode::Structure);return;}uint16_t value=frame.values[0];frame.clear();completeInstruction(now,value);return;}
 if(frame.cursor>frame.length){fail(ErrorCode::Structure);return;}
 const ExprToken token=frame.tokens[frame.cursor++];
 if(token.kind==ExprKind::Call){enterCall(static_cast<uint8_t>(token.value),true,token.column);return;}
 if(token.kind==ExprKind::Binary){if(frame.size<2){fail(ErrorCode::Structure,token.column);return;}
  uint16_t right=frame.values[--frame.size],left=frame.values[--frame.size],value=0;Error error=Expression::operate(*program_,token.value,left,right,value);
  if(error.code!=ErrorCode::None){fail(error.code,token.column);return;}frame.values[frame.size++]=value;return;
 }
 if(frame.size==MaxExprTokens){fail(ErrorCode::ExpressionLimit,token.column);return;}
 uint16_t value=token.value;
 if(token.kind!=ExprKind::Literal&&token.kind!=ExprKind::Variable){fail(ErrorCode::Structure,token.column);return;}
 if(token.kind==ExprKind::Variable){if(token.value>=program_->symbols_){fail(ErrorCode::Structure,token.column);return;}if(!initialized_[token.value]){fail(ErrorCode::Uninitialized,token.column);return;}value=values_[token.value];}
 frame.values[frame.size++]=value;
}

void Runtime::deliver(uint32_t now){
 Accept accepted=Accept::Failed;
 try{accepted=sink_(context_,event_);}catch(...){if(state_==State::Running)fail(ErrorCode::SinkFailure);return;}
 if(state_!=State::Running)return;if(accepted==Accept::Retry)return;if(accepted!=Accept::Accepted){fail(ErrorCode::SinkFailure);return;}pending_=false;
 if(event_.type==EventType::Delay){delayAt_=now;delayed_=true;}
 else if(block_.active){if(block_.position<block_.length)++block_.position;else{block_.next=block_.offset+block_.length;block_.loaded=false;}}
 else if(typing_){const Instruction& ins=program_->code_[pc_];if(textPos_<ins.length)++textPos_;else{typing_=false;++pc_;}}
 else ++pc_;
}
void Runtime::tick(uint32_t now){
 if(state_!=State::Running||inTick_)return;
 if(ticks_++==MaxTicks){fail(ErrorCode::TickLimit);return;}
 inTick_=true;struct TickGuard{bool& flag;~TickGuard(){flag=false;}} guard{inTick_};
 if(uint32_t(now-started_)>=elapsedLimit_){fail(ErrorCode::Timeout);return;}
 if(pending_){deliver(now);return;}
 if(delayed_){if(uint32_t(now-delayAt_)<event_.value)return;delayed_=false;++pc_;return;}
 if(block_.active){
  if(!block_.loaded){
   if(block_.next==block_.end){block_=TextCursor{};++pc_;return;}
   if(block_.next>block_.end||block_.end>program_->used_||block_.end-block_.next<4){fail(ErrorCode::Structure);return;}
   const unsigned char* record=reinterpret_cast<const unsigned char*>(program_->text_+block_.next);
   block_.line=static_cast<uint16_t>(record[0]|uint16_t(record[1])<<8);block_.length=static_cast<uint16_t>(record[2]|uint16_t(record[3])<<8);
   block_.offset=block_.next+4;
   if(block_.length>MaxLine||block_.length>block_.end-block_.offset){fail(ErrorCode::Structure);return;}
   block_.position=0;block_.loaded=true;return;
  }
  if(block_.position<block_.length){event_={EventType::Character,static_cast<uint8_t>(program_->text_[block_.offset+block_.position])};pending_=true;deliver(now);return;}
  if(program_->code_[pc_].op==Op::TextLnBlock){event_={EventType::KeyTap,0x28};pending_=true;deliver(now);return;}
  block_.next=block_.offset+block_.length;block_.loaded=false;return;
 }
 if(typing_){const Instruction& ins=program_->code_[pc_];if(textPos_<ins.length){event_={EventType::Character,static_cast<uint8_t>(program_->text_[ins.offset+textPos_])};pending_=true;deliver(now);return;}
  if(enter_){event_={EventType::KeyTap,0x28};pending_=true;deliver(now);return;}typing_=false;++pc_;return;}
 if(evaluations_[depth_].active){evaluationStep(now);return;}
 if(pc_>=program_->count_){state_=State::Completed;releaseProgram();return;}
 if(steps_==stepLimit_){fail(ErrorCode::StepLimit);return;}++steps_;
 const Instruction& ins=program_->code_[pc_];const char* arg=program_->text_+ins.offset;uint16_t value=0;
 if(ins.op==Op::Set||ins.op==Op::If||ins.op==Op::Delay||(ins.op==Op::Return&&ins.length)){
  Error e=Expression(*program_,nullptr,arg,&evaluations_[depth_],true).evaluate(value);if(e.code!=ErrorCode::None){fail(e.code,e.column);}return;
 }
 completeInstruction(now,value);
}
void Runtime::completeInstruction(uint32_t now,uint16_t value){
 const Instruction& ins=program_->code_[pc_];
 switch(ins.op){
 case Op::Set:if(!ins.target&&!initialized_[ins.symbol]){fail(ErrorCode::Uninitialized);return;}values_[ins.symbol]=value;initialized_[ins.symbol]=true;++pc_;break;
 case Op::Text:case Op::TextLn:typing_=true;enter_=ins.op==Op::TextLn;textPos_=0;break;
 case Op::TextBlock:case Op::TextLnBlock:
  if(ins.offset>program_->used_||ins.length>program_->used_-ins.offset){fail(ErrorCode::Structure);return;}
  block_={ins.offset,static_cast<uint16_t>(ins.offset+ins.length),0,0,0,ins.line,true,false};break;
 case Op::Delay:event_={EventType::Delay,value};pending_=true;deliver(now);break;
 case Op::Key:event_={EventType::KeyTap,ins.target};pending_=true;deliver(now);break;
 case Op::Hold:case Op::Release:event_={ins.op==Op::Hold?EventType::Hold:EventType::Release,ins.target};pending_=true;deliver(now);break;
 case Op::If:pc_=value?pc_+1:ins.target;break;
 case Op::Jump:case Op::Function:pc_=ins.target;break;
 case Op::Call:enterCall(ins.symbol,false,1);break;
 case Op::Return:returnFromCall(ins.length!=0,value);break;
 case Op::EndFunction:returnFromCall(false,0);break;
 case Op::Stop:cancel();break;
 }
}
}
