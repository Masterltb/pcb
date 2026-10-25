#pragma once
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

// Functional model only: closed/open below are estimates, not measured iris positions.
namespace freshvend {
constexpr unsigned Capacity = 16;
constexpr uint32_t MoveMs = 350, DropTimeoutMs = 3000, DebounceMs = 20;
enum class Result : uint8_t { Empty, Accepted, Done, Failed, Interrupted };
enum class Stage : uint8_t { Idle, CloseTop, OpenBottom, WaitDrop, CloseBottom, OpenTop, Fault };
inline const char* resultName(Result r) {
  switch (r) { case Result::Accepted:return "ACCEPTED"; case Result::Done:return "DONE";
    case Result::Failed:return "FAILED"; case Result::Interrupted:return "INTERRUPTED";
    default:return "EMPTY"; }
}
struct Record { char id[25]{}; uint8_t column=0; Result result=Result::Empty; uint8_t acked=0; };
struct Journal { uint32_t magic=0x46565331; Record records[Capacity]{}; };
struct Port {
  virtual ~Port() = default;
  virtual bool save(const Journal&) = 0;
  virtual void event(const char* kind, const char* id, int column, const char* detail) = 0;
};
struct Debounced {
  bool raw=false, value=false; uint32_t changed=0;
  void update(bool v, uint32_t now) {
    if (v!=raw) { raw=v; changed=now; }
    if (uint32_t(now-changed)>=DebounceMs) value=raw;
  }
};
struct Column {
  Stage stage=Stage::Idle; uint32_t since=0; int record=-1;
  bool topClosed=false, bottomClosed=true, sawBlocked=false;
  int topUs=1500, bottomUs=1500;
};
class Controller {
 public:
  Port& port; Journal journal; Column columns[2]; Debounced beam[2];
  bool armed=false, storageOk=true, limitsEnabled=false;
  explicit Controller(Port& p):port(p) {}
  static bool validId(const char* s) {
    if (!s || !*s || strlen(s)>24) return false;
    for (;*s;++s) if (!((*s>='a'&&*s<='z')||(*s>='A'&&*s<='Z')||
      (*s>='0'&&*s<='9')||*s=='-'||*s=='_')) return false;
    return true;
  }
  bool restore(const Journal& saved) {
    if (saved.magic!=0x46565331) return storageOk=false;
    for (const auto& r:saved.records) {
      if (r.result==Result::Empty) continue;
      if (!memchr(r.id,0,sizeof(r.id)) || !validId(r.id) || r.column<1 || r.column>2 ||
          unsigned(r.result)>unsigned(Result::Interrupted)) return storageOk=false;
    }
    journal=saved;
    bool changed=false;
    for (auto& r:journal.records) if (r.result==Result::Accepted) {
      r.result=Result::Interrupted; r.acked=0; changed=true;
      port.event("RESULT",r.id,r.column,"INTERRUPTED");
    }
    if (changed && !port.save(journal)) return storageOk=false;
    return true;
  }
  bool moving() const {
    for (const auto& c:columns) if (c.topUs!=1500 || c.bottomUs!=1500) return true;
    return false;
  }
  bool busy() const {
    for (const auto& c:columns) if (c.stage!=Stage::Idle && c.stage!=Stage::Fault) return true;
    return false;
  }
  bool arm(uint32_t now, const bool limits[4]) {
    if (!storageOk || busy()) return false;
    for (unsigned i=0;i<2;++i) {
      if (beam[i].raw || beam[i].value || uint32_t(now-beam[i].changed)<DebounceMs) return false;
      if (limitsEnabled && (limits[2*i] || !limits[2*i+1])) return false;
    }
    // Operator explicitly confirms TOP OPEN / BOTTOM CLOSED on both columns.
    for (auto& c:columns) c=Column{};
    armed=true; port.event("ARMED","-",0,"ASSUMED_TOP_OPEN_BOTTOM_CLOSED"); return true;
  }
  int find(const char* id) const {
    for (unsigned i=0;i<Capacity;++i)
      if (journal.records[i].result!=Result::Empty && !strcmp(id,journal.records[i].id)) return int(i);
    return -1;
  }
  const char* vend(const char* id, int column, uint32_t now) {
    if (!validId(id) || column<1 || column>2) return "INVALID";
    int existing=find(id);
    if (existing>=0) {
      auto& r=journal.records[existing];
      if (r.column!=column) return "ID_CONFLICT";
      r.acked=0; // A replay must be reportable again, but must never restart motion.
      port.event("REPLAY",id,column,resultName(r.result));
      return "DUPLICATE";
    }
    if (!armed || !storageOk) return "NOT_ARMED";
    auto& c=columns[column-1];
    if (c.stage!=Stage::Idle) return "BUSY_OR_FAULT";
    if (beam[column-1].raw || beam[column-1].value ||
        uint32_t(now-beam[column-1].changed)<DebounceMs) return "BEAM_NOT_CLEAR";
    int slot=-1;
    for (unsigned i=0;i<Capacity;++i) if (journal.records[i].result==Result::Empty) {slot=int(i);break;}
    if (slot<0) return "LEDGER_FULL";
    auto& r=journal.records[slot]; snprintf(r.id,sizeof(r.id),"%s",id);
    r.column=uint8_t(column); r.result=Result::Accepted; r.acked=0;
    // Reserve durably before the first physical output changes.
    if (!port.save(journal)) {storageOk=false; armed=false; return "STORAGE_ERROR";}
    c.record=slot; c.stage=Stage::CloseTop; c.since=now; c.topUs=1100;
    port.event("ACK",id,column,"ACCEPTED"); return "ACCEPTED";
  }
  void finish(unsigned i, Result result, const char* reason) {
    auto& c=columns[i]; c.topUs=c.bottomUs=1500;
    if (c.record>=0) {
      auto& r=journal.records[c.record]; r.result=result; r.acked=0;
      if (!port.save(journal)) {
        storageOk=false; armed=false; r.result=Result::Failed;
        result=Result::Failed; reason="STORAGE_ERROR"; stopOutputs();
      }
      port.event("RESULT",r.id,int(i+1),reason);
    }
    c.stage=(result==Result::Done)?Stage::Idle:Stage::Fault;
  }
  void stop() {
    armed=false;
    for (unsigned i=0;i<2;++i) {
      if (columns[i].stage!=Stage::Idle && columns[i].stage!=Stage::Fault)
        finish(i,Result::Failed,"STOPPED");
      columns[i].topUs=columns[i].bottomUs=1500;
    }
    port.event("STOP","-",0,"MANUAL_RECOVERY_REQUIRED");
  }
  void tick(uint32_t now, const bool blocked[2], const bool limits[4]) {
    for (unsigned i=0;i<2;++i) beam[i].update(blocked[i],now);
    if (!storageOk) { stopOutputs(); return; }
    for (unsigned i=0;i<2;++i) {
      if (!storageOk) {stopOutputs();return;}
      auto& c=columns[i]; uint32_t elapsed=uint32_t(now-c.since);
      if (c.stage==Stage::WaitDrop) {
        if (beam[i].value) c.sawBlocked=true;
        if (c.sawBlocked && !beam[i].value) {
          c.stage=Stage::CloseBottom; c.since=now; c.bottomUs=1100;
          port.event("STATE",journal.records[c.record].id,int(i+1),"CLOSE_BOTTOM");
        } else if (elapsed>=DropTimeoutMs) finish(i,Result::Failed,"IR_TIMEOUT");
        continue;
      }
      if (elapsed<MoveMs) continue;
      switch(c.stage) {
        case Stage::CloseTop:
          c.topUs=1500;
          if (limitsEnabled && !limits[2*i]) {finish(i,Result::Failed,"TOP_LIMIT_TIMEOUT");break;}
          c.topClosed=true; c.stage=Stage::OpenBottom; c.bottomUs=1900; c.since=now;
          port.event("STATE",journal.records[c.record].id,int(i+1),"OPEN_BOTTOM"); break;
        case Stage::OpenBottom:
          c.bottomUs=1500; c.bottomClosed=false; c.stage=Stage::WaitDrop;
          c.since=now; c.sawBlocked=beam[i].value;
          port.event("STATE",journal.records[c.record].id,int(i+1),"WAIT_DROP"); break;
        case Stage::CloseBottom:
          c.bottomUs=1500;
          if (limitsEnabled && !limits[2*i+1]) {finish(i,Result::Failed,"BOTTOM_LIMIT_TIMEOUT");break;}
          c.bottomClosed=true; c.stage=Stage::OpenTop; c.topUs=1900; c.since=now;
          port.event("STATE",journal.records[c.record].id,int(i+1),"OPEN_TOP"); break;
        case Stage::OpenTop:
          c.topUs=1500; c.topClosed=false; finish(i,Result::Done,"DONE"); break;
        default:break;
      }
    }
  }
 private:
  void stopOutputs() { for (auto& c:columns) c.topUs=c.bottomUs=1500; }
};
} // namespace freshvend
