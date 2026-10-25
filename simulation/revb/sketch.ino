// SIMULATION HARNESS ONLY. Do not upload to a real FreshVend machine.
#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Preferences.h>
#include <esp_timer.h>
#include "controller.h"

using namespace freshvend;
constexpr int ServoPins[4]={16,17,18,19};
constexpr int RxPins[2]={34,35}, LimitPins[4]={25,26,27,32};
constexpr int IrTxPin=23;
// Channels 0..3 share 50 Hz timers. Channel 6 uses another timer for 38 kHz.
constexpr int IrChannel=6;
Preferences preferences;
bool nvsOpen=false, networkEnabled=false, networkPaused=false;
bool limits[4]{}, blocked[2]{};
String serverUrl="http://host.wokwi.internal:8765";
uint32_t nextNetwork=0; unsigned reportIndex=0;
esp_timer_handle_t burstTimer;
void irBurst(void*) {
  static bool on=false;
  on=!on;
  ledcWrite(IrChannel,on?128:0);
}

struct HardwarePort : Port {
  bool save(const Journal& j) override {
    return nvsOpen && preferences.putBytes("journal",&j,sizeof(j))==sizeof(j);
  }
  void event(const char* kind,const char* id,int column,const char* detail) override {
    Serial.printf("%s id=%s col=%d %s\n",kind,id,column,detail);
  }
} port;
Controller controller(port);

void outputs() {
  for (unsigned i=0;i<2;++i) {
    ledcWrite(2*i,uint32_t(controller.columns[i].topUs)*65535/20000);
    ledcWrite(2*i+1,uint32_t(controller.columns[i].bottomUs)*65535/20000);
  }
}
void status() {
  Serial.printf("STATUS armed=%d storage=%d limits=%d wifi=%d\n",controller.armed,
    controller.storageOk,controller.limitsEnabled,WiFi.status()==WL_CONNECTED);
  for (unsigned i=0;i<2;++i) Serial.printf("COLUMN %u stage=%u beam=%d top_us=%d bottom_us=%d\n",
    i+1,unsigned(controller.columns[i].stage),controller.beam[i].value,
    controller.columns[i].topUs,controller.columns[i].bottomUs);
  for (const auto& r:controller.journal.records) if (r.result!=Result::Empty)
    Serial.printf("RECORD id=%s col=%u %s acked=%u\n",r.id,r.column,resultName(r.result),r.acked);
}
void command(String line) {
  line.trim();
  if (line=="arm") {
    Serial.println(controller.arm(millis(),limits)?"ARM_OK":"ARM_REJECTED");
  } else if (line=="stop") controller.stop();
  else if (line=="status") status();
  else if (line=="limits on" || line=="limits off") {
    if (controller.armed || controller.busy()) Serial.println("DISARM_FIRST");
    else {controller.limitsEnabled=line.endsWith("on"); Serial.println("LIMIT_MODE_SET");}
  } else if (line=="net on") {
    networkEnabled=true; networkPaused=false;
    WiFi.begin("Wokwi-GUEST","",6); Serial.println("NETWORK_CONNECTING");
  } else if (line=="net off") {
    networkPaused=true; WiFi.disconnect(); Serial.println("NETWORK_PAUSED");
  } else if (line=="reset") {
    for (auto& c:controller.columns) c.topUs=c.bottomUs=1500;
    outputs(); ESP.restart(); // Leave ACCEPTED journal entries for recovery as INTERRUPTED.
  }
  else if (line.startsWith("vend ")) {
    char id[26]{}, colText[12]{}, extra[2]{};
    // Widths bound input; surplus tokens are rejected.
    if (sscanf(line.c_str(),"vend %25s %11s %1s",id,colText,extra)!=2 ||
        (strcmp(colText,"1") && strcmp(colText,"2"))) Serial.println("INVALID_COMMAND");
    else {
      int col=colText[0]-'0';
      Serial.printf("COMMAND id=%s col=%d %s\n",id,col,controller.vend(id,col,millis()));
    }
  } else Serial.println("HELP: arm | vend <id> <1|2> | status | stop | reset | limits on/off | net on/off");
}

void networkTick(uint32_t now) {
  // Never block an active mechanical sequence on HTTP or Wi-Fi.
  if (!networkEnabled || networkPaused || !controller.storageOk || controller.busy() || uint32_t(now-nextNetwork)>0x7fffffff) return;
  nextNetwork=now+500;
  if (WiFi.status()!=WL_CONNECTED) return;
  // Send one outstanding durable record per poll; repeat until explicit matching acknowledgement.
  for (unsigned offset=0;offset<Capacity;++offset) {
    unsigned i=(reportIndex+offset)%Capacity; auto& r=controller.journal.records[i];
    if (r.result==Result::Empty || r.acked) continue;
    reportIndex=(i+1)%Capacity;
    HTTPClient http; http.setConnectTimeout(300); http.setTimeout(300);
    http.begin(serverUrl+"/events"); http.addHeader("Content-Type","application/json");
    String body="{\"id\":\""+String(r.id)+"\",\"column\":"+String(r.column)+
      ",\"status\":\""+resultName(r.result)+"\"}";
    int code=http.POST(body);
    if (code==200 && http.getString()==String(r.id)+":"+resultName(r.result)) {
      r.acked=1;
      if (!port.save(controller.journal)) controller.storageOk=false;
      Serial.printf("SERVER_ACK id=%s %s\n",r.id,resultName(r.result));
    }
    http.end(); return;
  }
  if (!controller.armed) return;
  HTTPClient http; http.setConnectTimeout(300); http.setTimeout(300);
  http.begin(serverUrl+"/next"); int code=http.GET();
  String body=(code==200)?http.getString():""; http.end();
  if (body.length()) command(body);
}

void setup() {
  Serial.begin(115200);
  for (unsigned i=0;i<4;++i) {
    ledcSetup(i,50,16); ledcAttachPin(ServoPins[i],i);
  }
  outputs();
  for (int pin:RxPins) pinMode(pin,INPUT); // GPIO34/35 have EXTERNAL pull-ups in diagram/PCB.
  for (int pin:LimitPins) pinMode(pin,INPUT_PULLUP);
  ledcSetup(IrChannel,38000,8); ledcAttachPin(IrTxPin,IrChannel);
  // Timer-task callback keeps burst gating independent of blocking HTTP calls.
  esp_timer_create_args_t timerArgs={};
  timerArgs.callback=&irBurst; timerArgs.name="ir-burst";
  bool burstOk=(esp_timer_create(&timerArgs,&burstTimer)==ESP_OK);
  if (burstOk) burstOk=(esp_timer_start_periodic(burstTimer,1000)==ESP_OK);
  nvsOpen=preferences.begin("fv-sim",false);
  if (!nvsOpen) controller.storageOk=false;
  else if (preferences.isKey("journal")) {
    Journal saved;
    if (preferences.getBytesLength("journal")!=sizeof(saved) ||
        preferences.getBytes("journal",&saved,sizeof(saved))!=sizeof(saved)) controller.storageOk=false;
    else controller.restore(saved);
  }
  if (!burstOk) {controller.storageOk=false; Serial.println("IR_TIMER_ERROR");}
  Serial.println("FRESHVEND_SIM_READY");
  Serial.println("SIMULATION ONLY: servo drawings show pulse width, not actual iris position.");
  Serial.println("BOOT_LOCKED: confirm TOP OPEN / BOTTOM CLOSED, clear beams, then type arm.");
}

void loop() {
  uint32_t now=millis();
  for (unsigned i=0;i<2;++i) blocked[i]=(digitalRead(RxPins[i])==HIGH);
  for (unsigned i=0;i<4;++i) limits[i]=(digitalRead(LimitPins[i])==LOW);
  controller.tick(now,blocked,limits); outputs();
  // IR RX is logically injected after demodulation; no optical coupling is simulated.
  static String input; static bool overflow=false;
  while (Serial.available()) {
    char c=char(Serial.read());
    if (c=='\n') {
      if (!overflow) command(input); else Serial.println("LINE_TOO_LONG");
      input=""; overflow=false;
    } else if (c!='\r') {
      if (input.length()<96 && !overflow) input+=c;
      else {overflow=true; input="";}
    }
  }
  outputs(); networkTick(now); delay(1);
}
