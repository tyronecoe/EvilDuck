// Fixed fake-data diagnostic only. No capture, downloads, persistence or arbitrary input.
using System;using System.Runtime.InteropServices;using System.Threading;
public static class EvilDuckLedSender {
 [StructLayout(LayoutKind.Sequential)] struct Keyboard {public ushort vk,scan;public uint flags,time;public UIntPtr extra;}
 [StructLayout(LayoutKind.Sequential)] struct Mouse {public int x,y;public uint data,flags,time;public UIntPtr extra;}
 [StructLayout(LayoutKind.Explicit)] struct Union {[FieldOffset(0)]public Keyboard keyboard;[FieldOffset(0)]public Mouse mouse;}
 [StructLayout(LayoutKind.Sequential)] struct Input {public uint type;public Union data;}
 [DllImport("user32.dll",SetLastError=true)]static extern uint SendInput(uint n,Input[] inputs,int size);
 [DllImport("user32.dll")]static extern short GetKeyState(int key);
 static volatile bool cancelled;
 static bool Read(int vk){return (GetKeyState(vk)&1)!=0;}
 static void Set(int vk,bool value){if(Read(vk)==value)return;var a=new Input[2];for(int i=0;i<2;i++){a[i].type=1;a[i].data.keyboard.vk=(ushort)vk;a[i].data.keyboard.flags=(uint)(i==0?0:2);}if(SendInput(2,a,Marshal.SizeOf(typeof(Input)))!=2)throw new Exception("SendInput refused/partial (UIPI or other error); no retry. Error "+Marshal.GetLastWin32Error());Thread.Sleep(60);if(Read(vk)!=value)throw new Exception("Lock-state API did not reach requested state; unsupported/unconfirmed.");}
 static ushort Crc(byte[] p){ushort c=65535;foreach(byte b in p){c^=(ushort)(b<<8);for(int i=0;i<8;i++)c=(ushort)(((c&32768)!=0)?(c<<1)^0x1021:c<<1);}return c;}
 public static byte[] Frame(){byte[] m=System.Text.Encoding.ASCII.GetBytes("EVILDUCK TEST 123");byte[] body=new byte[18];body[0]=17;Array.Copy(m,0,body,1,17);ushort crc=Crc(body);byte[] frame=new byte[25];frame[0]=0;frame[1]=0x45;frame[2]=0x44;frame[3]=0x52;frame[4]=0x31;Array.Copy(body,0,frame,5,18);frame[23]=(byte)(crc>>8);frame[24]=(byte)crc;return frame;}
 public static int Run(){
  Console.WriteLine("VISIBLE FINITE LED TEST. First confirm Caps+Num OUTPUT reports in device diagnostics. Close unsaved work; do not type while this runs. Type SEND to send only EVILDUCK TEST 123, or anything else to exit. Ctrl-C stops. This changes desktop lock states; API success is not USB delivery.");
  if(Console.ReadLine()!="SEND")return 2;
  bool caps=Read(0x14),num=Read(0x90);var elapsed=System.Diagnostics.Stopwatch.StartNew();cancelled=false;
  ConsoleCancelEventHandler stop=(s,e)=>{e.Cancel=true;cancelled=true;};Console.CancelKeyPress+=stop;
  int result=0;
  try{Set(0x14,false);Set(0x90,false);bool clock=false;foreach(byte b in Frame())for(int i=7;i>=0;i--){if(cancelled||elapsed.Elapsed.TotalSeconds>=90)throw new Exception("Stopped/timed out.");Set(0x90,((b>>i)&1)!=0);Thread.Sleep(60);clock=!clock;Set(0x14,clock);Thread.Sleep(60);}Console.WriteLine("Host API send finished: 17 payload bytes. Verify device integrity and byte-exact text separately; no delivery claimed.");}
  catch(Exception e){Console.Error.WriteLine(e.Message);result=1;}
  finally{
   try{Set(0x14,caps);}catch(Exception e){Console.Error.WriteLine("Caps restore unconfirmed: "+e.Message);result=1;}
   try{Set(0x90,num);}catch(Exception e){Console.Error.WriteLine("Num restore unconfirmed: "+e.Message);result=1;}
   Console.CancelKeyPress-=stop;
  }
  return result;
 }
}
