#include "core.h"
#include <string.h>
namespace ds_preview {
namespace {
bool white(char c){return c==' '||c=='\t';}
bool letter(char c){return (c>='A'&&c<='Z')||(c>='a'&&c<='z')||c=='_';}
bool digit(char c){return c>='0'&&c<='9';}
bool ident(const char* s){if(!letter(*s))return false;for(++s;*s;++s)if(!letter(*s)&&!digit(*s))return false;return true;}
char* left(char* p){while(white(*p))++p;return p;}
void right(char* p){size_t n=strlen(p);while(n&&white(p[n-1]))p[--n]=0;}
bool exact(const char* p,const char* word){return strcmp(p,word)==0;}
bool command(const char* p,const char* word){size_t n=strlen(word);return strncmp(p,word,n)==0&&(p[n]==0||white(p[n]));}
char* argument(char* p){while(*p&&!white(*p))++p;return *p?p+1:p;}
int findName(const char names[][24],size_t n,const char* name){for(size_t i=0;i<n;++i)if(exact(names[i],name))return static_cast<int>(i);return -1;}
bool functionName(const char* p,char (&name)[24]){size_t n=strlen(p);if(n<3||n>25||p[n-2]!='('||p[n-1]!=')')return false;memcpy(name,p,n-2);name[n-2]=0;return ident(name);}
uint8_t key(const char* p){
 const char* names[]={"ENTER","TAB","SPACE","ESCAPE","BACKSPACE","DELETE","UPARROW","DOWNARROW","LEFTARROW","RIGHTARROW"};
 const uint8_t codes[]={0x28,0x2b,0x2c,0x29,0x2a,0x4c,0x52,0x51,0x50,0x4f};
 for(size_t i=0;i<10;++i)if(exact(p,names[i]))return codes[i];return 0;
}
bool reserved(const char* p){
 const char* names[]={"REM","REM_BLOCK","END_REM","STRING","STRINGLN","DELAY","VAR","DEFINE","IF","ELSE","END_IF","WHILE","END_WHILE","FUNCTION","END_FUNCTION","RETURN","STOP_PAYLOAD","ATTACKMODE","HOLD","RELEASE","RESET","INJECT_MOD","INJECT_VAR"};
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
 }
 return "Unknown preview error";
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
 Program& p_;const char* source_;size_t bytes_;uint16_t line_=0;bool comment_=false;
 bool fail(ErrorCode c,uint16_t column=1){if(p_.error_.code==ErrorCode::None)p_.error_={c,line_,column};return false;}
 bool read(size_t& offset,char (&line)[MaxLine+1]){
  size_t n=0;++line_;
  while(offset<bytes_&&source_[offset]!='\n'){
   unsigned char c=static_cast<unsigned char>(source_[offset++]);
   if(c=='\r'){if(offset>=bytes_||source_[offset]!='\n')return fail(ErrorCode::InvalidSource);break;}
   if(c==0||(c<32&&c!='\t')||c>126)return fail(ErrorCode::InvalidSource);
   if(n==MaxLine)return fail(ErrorCode::LineLimit);line[n++]=static_cast<char>(c);
  }
  if(offset<bytes_&&source_[offset]=='\n')++offset;line[n]=0;return true;
 }
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
  if(uint8_t k=key(text))return emit(Op::Key,"",k);
  if(functionName(text,name)){int id=fn(name);if(id<0)return fail(ErrorCode::UndefinedFunction);return emit(Op::Call,"",0,static_cast<uint8_t>(id));}
  return fail(ErrorCode::UnknownStatement);
 }
 bool valueInventory(){
  for(size_t function=0;function<p_.functionsCount_;++function){
   const Function& f=p_.functions_[function];bool visited[MaxCode]={};uint16_t work[MaxCode]={};size_t used=0;
   auto enqueue=[&](uint16_t pc){if(pc>=f.entry&&pc<=f.end&&!visited[pc]){visited[pc]=true;work[used++]=pc;}};
   enqueue(f.entry);
   while(used){uint16_t pc=work[--used];const Instruction& ins=p_.code_[pc];
    if(ins.op==Op::Return){if(ins.length)p_.valueFunctions_|=static_cast<uint16_t>(1u<<function);continue;}
    if(ins.op==Op::EndFunction||ins.op==Op::Stop)continue;
    if(ins.op==Op::Jump){enqueue(ins.target);continue;}
    if(ins.op==Op::If){uint16_t value=0;bool known=false;Expression e(p_,nullptr,p_.text_+ins.offset);Error error=e.evaluate(value,&known);
     if(error.code!=ErrorCode::None)return fail(error.code,error.column);
     if(!known||value)enqueue(pc+1);if(!known||!value)enqueue(ins.target);continue;
    }
    enqueue(pc+1);
   }
  }
  // Full table now exists: enforce all numeric call contexts, including unused bodies.
  for(size_t pc=0;pc<p_.count_;++pc){const Instruction& ins=p_.code_[pc];
   if(ins.op==Op::Set||ins.op==Op::If||ins.op==Op::Delay||(ins.op==Op::Return&&ins.length)){
    uint16_t ignored=0;Expression e(p_,nullptr,p_.text_+ins.offset,nullptr,true);Error error=e.evaluate(ignored);
    if(error.code!=ErrorCode::None){line_=ins.line;return fail(error.code,error.column);}
   }
  }
  return true;
 }
public:
 Compiler(Program& p,const char* source,size_t bytes):p_(p),source_(source),bytes_(bytes){}
 bool compile(){
  if(bytes_>MaxSource)return fail(ErrorCode::InputLimit);if(bytes_&&!source_)return fail(ErrorCode::InvalidSource);
  size_t begin=0;if(bytes_>=3&&static_cast<unsigned char>(source_[0])==0xef&&static_cast<unsigned char>(source_[1])==0xbb&&static_cast<unsigned char>(source_[2])==0xbf)begin=3;
  char raw[MaxLine+1]={};
  for(unsigned pass=0;pass<2;++pass){line_=0;comment_=false;
   size_t offset=begin;while(offset<bytes_){if(!read(offset,raw))return false;char* text=left(raw);right(text);
    if(pass==0){if(!*text||skip(text)){if(p_.error_.code!=ErrorCode::None)return false;continue;}
     if(command(text,"DEFINE")){if(!constant(text))return false;}
     else if(command(text,"VAR")){char* name=left(argument(text));char* end=name;while(*end&&!white(*end)&&*end!='=')++end;*end=0;if(!addSymbol(name))return false;}
     else if(command(text,"FUNCTION")){
      char name[24]={};if(!functionName(left(argument(text)),name)||reserved(name))return fail(ErrorCode::Identifier);
      if(fn(name)>=0)return fail(ErrorCode::DuplicateFunction);if(p_.functionsCount_==MaxFunctions)return fail(ErrorCode::FunctionLimit);strcpy(p_.functions_[p_.functionsCount_++].name,name);
     }
    }else if(!statement(text))return false;
   }
   if(comment_)return fail(ErrorCode::Structure);
  }
  if(depth_)return fail(ErrorCode::Structure);if(!valueInventory())return false;p_.ready_=true;return true;
 }
};
bool Program::compile(const char* source,size_t bytes,const char* location){
 // Reset directly, avoiding an aggregate Program temporary on an embedded stack.
 if(borrowed_){error_={ErrorCode::Busy,0,0};return false;}
 ++revision_;ready_=false;used_=count_=valueFunctions_=0;symbols_=functionsCount_=0;error_={};
 memset(names_,0,sizeof(names_));for(auto& f:functions_)f=Function{};for(auto& i:code_)i=Instruction{};memset(text_,0,sizeof(text_));
 size_t length=0;if(location)while(length<sizeof(source_)&&location[length])++length;
 if(!location||length==sizeof(source_)){error_={ErrorCode::Identifier,0,0};return false;}memcpy(source_,location,length+1);
 Compiler compiler(*this,source,bytes);return compiler.compile();
}
void Runtime::releaseProgram(){if(ownsProgram_&&program_)program_->borrowed_=false;ownsProgram_=false;}
void Runtime::fail(ErrorCode code,uint16_t column){error_={code,program_&&pc_<program_->count_?program_->code_[pc_].line:static_cast<uint16_t>(0),column};state_=State::Error;pending_=typing_=delayed_=false;depth_=0;clearContinuations();hasReturn_=false;lastReturn_=0;releaseProgram();}
bool Runtime::start(const Program& p,Sink sink,void* context,uint32_t now,uint32_t steps,uint32_t elapsed){
 if(state_==State::Running||inTick_)return false;releaseProgram();program_=&p;programRevision_=p.revision_;sink_=sink;context_=context;pc_=textPos_=depth_=0;typing_=enter_=pending_=delayed_=false;steps_=0;error_={};hasReturn_=false;lastReturn_=0;
 memset(values_,0,sizeof(values_));memset(initialized_,0,sizeof(initialized_));for(auto& call:calls_)call=CallFrame{};clearContinuations();started_=now;ticks_=0;stepLimit_=steps;elapsedLimit_=elapsed;
 if(!p.ready_){fail(ErrorCode::NotCompiled);return false;}
 if(!sink){fail(ErrorCode::SinkFailure);return false;}
 if(!steps||steps>MaxSteps||!elapsed||elapsed>MaxElapsedMs){fail(ErrorCode::InvalidBudget);return false;}
 if(p.borrowed_){fail(ErrorCode::Busy);return false;}p.borrowed_=true;ownsProgram_=true;
 state_=State::Running;return true;
}
void Runtime::cancel(){if(state_==State::Running){state_=State::Cancelled;pending_=typing_=delayed_=false;depth_=0;clearContinuations();hasReturn_=false;lastReturn_=0;releaseProgram();}}
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
 case Op::Delay:event_={EventType::Delay,value};pending_=true;deliver(now);break;
 case Op::Key:event_={EventType::KeyTap,ins.target};pending_=true;deliver(now);break;
 case Op::If:pc_=value?pc_+1:ins.target;break;
 case Op::Jump:case Op::Function:pc_=ins.target;break;
 case Op::Call:enterCall(ins.symbol,false,1);break;
 case Op::Return:returnFromCall(ins.length!=0,value);break;
 case Op::EndFunction:returnFromCall(false,0);break;
 case Op::Stop:cancel();break;
 }
}
}
