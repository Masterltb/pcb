#include "../controller.h"
#include <assert.h>
#include <iostream>
#include <string>
#include <vector>
using namespace freshvend;
struct FakePort : Port {
  Journal saved; bool fail=false; unsigned saves=0;
  std::vector<std::string> events;
  bool save(const Journal& j) override { ++saves; if(fail)return false; saved=j;return true; }
  void event(const char* k,const char* id,int,const char* d) override {
    events.push_back(std::string(k)+" "+id+" "+d);
  }
};
struct Rig {
  FakePort port; Controller c; uint32_t now=0; bool beam[2]={false,false}; bool limits[4]={false,true,false,true};
  Rig():c(port) { advance(25); }
  void advance(unsigned ms) {
    for (unsigned t=0;t<ms;++t) {
      ++now; c.tick(now,beam,limits);
      for (const auto& col:c.columns) {
        assert(col.topClosed || col.bottomClosed);
        assert(col.topUs==1500 || col.bottomUs==1500);
        if(col.topUs==1900) assert(col.bottomClosed);
        if(col.bottomUs==1900) assert(col.topClosed);
      }
    }
  }
  void arm() {assert(c.arm(now,limits));}
  void complete(unsigned col) {
    advance(2*MoveMs); assert(c.columns[col].stage==Stage::WaitDrop);
    beam[col]=true; advance(30); beam[col]=false; advance(30);
    advance(2*MoveMs); assert(c.columns[col].stage==Stage::Idle);
  }
};
int main() {
  unsigned tests=0;
  {Rig r; assert(std::string(r.c.vend("locked",1,r.now))=="NOT_ARMED"); ++tests;}
  {Rig r;r.arm();assert(std::string(r.c.vend("a",1,r.now))=="ACCEPTED");
    assert(r.port.saved.records[0].result==Result::Accepted);
    assert(std::string(r.c.vend("a",1,r.now))=="DUPLICATE");
    assert(std::string(r.c.vend("a",2,r.now))=="ID_CONFLICT");
    r.complete(0);assert(r.c.journal.records[0].result==Result::Done);
    assert(std::string(r.c.vend("a",1,r.now))=="DUPLICATE");assert(!r.c.busy());++tests;}
  {Rig r;r.arm();r.c.vend("timeout",1,r.now);r.advance(2*MoveMs+DropTimeoutMs+1);
    assert(r.c.journal.records[0].result==Result::Failed);assert(!r.c.moving());++tests;}
  {Rig r;r.beam[0]=true;r.advance(30);assert(!r.c.arm(r.now,r.limits));++tests;}
  {Rig r;r.arm();r.beam[0]=true;r.advance(30);assert(std::string(r.c.vend("blocked",1,r.now))=="BEAM_NOT_CLEAR");++tests;}
  {Rig r;r.arm();r.c.vend("held",1,r.now);r.advance(2*MoveMs);r.beam[0]=true;r.advance(DropTimeoutMs+1);
    assert(r.c.journal.records[0].result==Result::Failed);++tests;}
  {Rig r;r.arm();r.c.vend("noise",1,r.now);r.advance(2*MoveMs);r.beam[0]=true;r.advance(5);
    r.beam[0]=false;r.advance(DropTimeoutMs);assert(r.c.journal.records[0].result==Result::Failed);++tests;}
  {Rig r;r.arm();r.port.fail=true;assert(std::string(r.c.vend("store",1,r.now))=="STORAGE_ERROR");assert(!r.c.moving());++tests;}
  {Rig r;r.arm();r.c.vend("restart",1,r.now);FakePort p;Controller reboot(p);
    assert(reboot.restore(r.port.saved));assert(!reboot.armed);assert(!reboot.moving());
    assert(reboot.journal.records[0].result==Result::Interrupted);
    assert(std::string(reboot.vend("restart",1,100))=="DUPLICATE");++tests;}
  {Rig r;r.arm();r.c.vend("stop",1,r.now);r.c.stop();assert(!r.c.moving());assert(!r.c.armed);
    assert(r.c.journal.records[0].result==Result::Failed);++tests;}
  {Rig r;r.c.limitsEnabled=true;r.arm();r.c.vend("limit",1,r.now);r.advance(MoveMs);
    assert(r.c.journal.records[0].result==Result::Failed);++tests;}
  {Rig r;r.c.limitsEnabled=true;r.arm();r.c.vend("limitok",1,r.now);r.limits[0]=true;
    r.complete(0);assert(r.c.journal.records[0].result==Result::Done);++tests;}
  {Rig r;r.arm();r.c.vend("parallel1",1,r.now);r.c.vend("parallel2",2,r.now);
    r.advance(2*MoveMs);r.beam[0]=r.beam[1]=true;r.advance(30);r.beam[0]=r.beam[1]=false;
    r.advance(30+2*MoveMs);assert(r.c.journal.records[0].result==Result::Done);
    assert(r.c.journal.records[1].result==Result::Done);++tests;}
  {Rig r;r.arm();for(unsigned i=0;i<Capacity;++i){char id[12];snprintf(id,sizeof(id),"cap%u",i);
      assert(std::string(r.c.vend(id,1,r.now))=="ACCEPTED");r.complete(0);}
    assert(std::string(r.c.vend("overflow",1,r.now))=="LEDGER_FULL");++tests;}
  {Rig r;r.arm();assert(std::string(r.c.vend("bad id",1,r.now))=="INVALID");
    assert(std::string(r.c.vend("valid",3,r.now))=="INVALID");++tests;}
  {Rig r;r.arm();r.c.vend("terminalstore",1,r.now);r.advance(2*MoveMs);r.beam[0]=true;r.advance(30);
    r.beam[0]=false;r.advance(30);r.port.fail=true;r.advance(2*MoveMs);
    assert(!r.c.storageOk);assert(!r.c.moving());
    assert(r.c.journal.records[0].result==Result::Failed);
    assert(r.port.events.back()=="RESULT terminalstore STORAGE_ERROR");++tests;}
  {Rig r;Journal bad;bad.magic=0;assert(!r.c.restore(bad));assert(!r.c.arm(r.now,r.limits));++tests;}
  {Rig r;r.now=0xfffffff0;r.c.beam[0].changed=r.c.beam[1].changed=r.now-30;r.arm();
    r.c.vend("wrap",1,r.now);r.complete(0);assert(r.c.journal.records[0].result==Result::Done);++tests;}
  std::cout<<"PASS: "<<tests<<" controller scenarios; interlock invariants checked every simulated millisecond\n";
}
