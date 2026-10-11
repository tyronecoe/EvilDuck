#include "script_functions.h"
#include "internal_vars.h"
#include "script_parser.h"
#include "hid_backend.h"
#include "duck_keys.h"
#include <cstring>
namespace script_functions {
bool name(const String &invocation,String &identifier,String &error) {
  if(!invocation.endsWith("()")) {error="Function name must end in literal ()";return false;}
  identifier=invocation.substring(0,invocation.length()-2);
  if(!duck_expr::identifier(identifier.c_str(),identifier.length(),0) ||
     (identifier[0]>='0' && identifier[0]<='9')) {error="Invalid function identifier; parameters/arguments are unsupported";return false;}
  String upper=identifier;upper.toUpperCase();
  static const char *reserved[]={"FUNCTION","END_FUNCTION","RETURN","IF","ELSE","THEN","WHILE","END_IF","ENDIF","ENDWHILE","END_WHILE","END",
    "DEFINE","VAR","TRUE","FALSE","STRING","STRINGLN","END_STRING","END_STRINGLN","REM","REM_BLOCK","END_REM","DELAY","WAIT","DEFAULT_DELAY","DEFAULTDELAY","REPEAT","REPLAY","STOP","STOP_PAYLOAD","RESET","HOLD","RELEASE","INJECT_MOD","SAVE","READ","APPEND","LOCALE","LED","LED_R","LED_G","LED_OFF","EXTENSION","END_EXTENSION","VERSION","IF_DEFINED_TRUE","IF_NOT_DEFINED_TRUE","ELSE_DEFINED","END_IF_DEFINED","ATTACKMODE","KEYCODE"};
  for(auto keyword:reserved)if(upper==keyword){error="Function name collides with a command";return false;}
  script_parser::Kind alias;
  if (script_parser::textOpener(upper, alias)) { error="Function name collides with a text alias"; return false; }
  if (internal_vars::lockCommand(upper) >= 0) { error = "Function name collides with a lock command"; return false; }
  uint8_t key;
  if(hid_backend::keyNameToHid(identifier,key) || duck_keys::isModifierName(identifier,key)) {error="Function name collides with a key/modifier";return false;}
  return true;
}
int Table::find(const char *name,size_t length)const {
  for(uint8_t i=0;i<count;++i)if(strlen(entries[i].name)==length && !memcmp(entries[i].name,name,length))return i;
  return -1;
}
bool Table::add(const String &identifier,uint32_t body,uint32_t line,String &error) {
  if(find(identifier.c_str(),identifier.length())>=0){error="Duplicate function declaration";return false;}
  if(count>=DUCKSCRIPT_MAX_FUNCTIONS){error="Function table exhausted";return false;}
  auto &entry=entries[count++];memcpy(entry.name,identifier.c_str(),identifier.length()+1);entry.body=body;entry.headerLine=line;return true;
}
bool Table::close(uint32_t end,uint32_t line){if(!count)return false;entries[count-1].end=end;entries[count-1].endLine=line;return true;}
duck_expr::Lookup Table::resolve(const char *name,size_t length,uint16_t &index,void *context) {
  int found=static_cast<Table *>(context)->find(name,length);
  if(found<0)return duck_expr::Lookup::Undefined;
  index=found;return duck_expr::Lookup::Number;
}
}
