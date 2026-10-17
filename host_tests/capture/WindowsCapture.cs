// Visible fake-phrase-only cross-application diagnostic. Never retain general key logs.
using System;using System.ComponentModel;using System.Runtime.InteropServices;using System.Windows.Forms;using System.IO;
public static class EvilDuckCapture {
 const string Phrase="EVILDUCK TEST 123";static int matched;static bool found;static IntPtr hook=IntPtr.Zero;static Hook callback=Observe;static Label status;static Button start;static System.Windows.Forms.Timer timer;static System.Diagnostics.Stopwatch elapsed;
 delegate IntPtr Hook(int code,IntPtr message,IntPtr data);
 [StructLayout(LayoutKind.Sequential)]struct Key{public uint vk,scan,flags,time;public UIntPtr extra;}
 [DllImport("user32.dll",SetLastError=true)]static extern IntPtr SetWindowsHookEx(int id,Hook fn,IntPtr module,uint thread);
 [DllImport("user32.dll",SetLastError=true)]static extern bool UnhookWindowsHookEx(IntPtr h);
 [DllImport("user32.dll")]static extern IntPtr CallNextHookEx(IntPtr h,int code,IntPtr message,IntPtr data);
 [DllImport("kernel32.dll",CharSet=CharSet.Auto)]static extern IntPtr GetModuleHandle(string name);
 static void Stop(){timer.Stop();if(hook!=IntPtr.Zero){if(!UnhookWindowsHookEx(hook)){status.Text="Hook removal failed. Close this process; release is unconfirmed.";return;}hook=IntPtr.Zero;}start.Enabled=true;if(!found)status.Text="Stopped. No fake-phrase match recorded.";}
 static IntPtr Observe(int code,IntPtr message,IntPtr data){
  if(code>=0&&(message==(IntPtr)0x100||message==(IntPtr)0x104)){
   Key key=(Key)Marshal.PtrToStructure(data,typeof(Key));if((key.flags&0x12)==0){char c=(key.vk==32)?' ':key.vk>=65&&key.vk<=90?(char)key.vk:key.vk>=49&&key.vk<=51?(char)key.vk:'\0';
    if(c==Phrase[matched])matched++;else matched=c=='E'?1:0;
    if(matched==Phrase.Length){found=true;matched=0;status.Text="FAKE PHRASE OBSERVED: "+Phrase;timer.Stop();/* unhook outside callback on UI queue */status.BeginInvoke((Action)(()=>Stop()));}
   }
  }
  return CallNextHookEx(hook,code,message,data);
 }
 public static void Run(){
  Application.EnableVisualStyles();var form=new Form{Text="EvilDuck visible FAKE-PHRASE diagnostic — 60 seconds",Width=690,Height=280};status=new Label{Left=12,Top=12,Width=650,Height=100,Text="No capture active. Start, then manually type EVILDUCK TEST 123 in a second ordinary editor. Only that phrase can be retained; other keys are discarded. Not a general keylogger."};start=new Button{Text="Start 60-second test",Left=12,Top=130,Width=180};var stop=new Button{Text="Stop",Left=210,Top=130};var export=new Button{Text="Save fake result",Left=300,Top=130,Width=140};var exit=new Button{Text="Exit",Left=460,Top=130};timer=new System.Windows.Forms.Timer{Interval=100};
  timer.Tick+=(s,e)=>{if(elapsed.Elapsed.TotalSeconds>=60)Stop();};
  start.Click+=(s,e)=>{if(hook!=IntPtr.Zero)return;matched=0;found=false;hook=SetWindowsHookEx(13,callback,GetModuleHandle(null),0);if(hook==IntPtr.Zero){status.Text="Capture unavailable or permission denied. Win32 error "+Marshal.GetLastWin32Error();return;}elapsed=System.Diagnostics.Stopwatch.StartNew();start.Enabled=false;status.Text="ACTIVE: type the fake phrase manually in another editor. Stop/Exit available; timeout60seconds. No transport is active.";timer.Start();};
  stop.Click+=(s,e)=>Stop();exit.Click+=(s,e)=>form.Close();export.Click+=(s,e)=>{if(!found){status.Text="No fake match to save.";return;}using(var dialog=new SaveFileDialog{FileName="evilduck-fake-result.txt",Filter="Text|*.txt"})if(dialog.ShowDialog()==DialogResult.OK){try{File.WriteAllText(dialog.FileName,Phrase);}catch(Exception error){status.Text="Save failed: "+error.GetType().Name;}}};
  form.FormClosing+=(s,e)=>Stop();form.FormClosed+=(s,e)=>timer.Dispose();form.Controls.AddRange(new Control[]{status,start,stop,export,exit});Application.Run(form);
 }
}
