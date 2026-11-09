"""Generate an isolated public-save parser probe from original verified mask sets."""
import json
from pathlib import Path

def inject(text,guarded):
    w=Path(__file__).resolve().parent
    proof=json.loads((w/'builder-phase-masks-original-nov9.json').read_text())
    assert proof['status']=='ORIGINAL_BUILDER_PHASE_MASK_CLOSURE_PASS'
    masks={s['scene']:s['closed_masks']for s in proof['scenes']}
    assert masks[515]==[7,15,23,24,25,26,27,28,29,30,31]and masks[536]==[7,15,23,31]
    entry='bool AstronomicaEngine::verifyBuilderSaves() {'
    assert text.count(entry)==1
    start=text.index(entry);end=text.find('\nbool AstronomicaEngine::',start+len(entry));end=len(text)if end<0 else end
    head,tail=text[:start],text[end:];text=text[start:end]
    text=text.replace(entry,entry+'\n uint32 phaseImportProbeSeen = 0;')
    anchor='  const uint32 before = fingerprint(),savedNow = now;'
    assert text.count(anchor)==1
    block=r'''
  const uint phaseBit = _place == 515 ? 1U : 2U;
  if (!(phaseImportProbeSeen & phaseBit)) {
   phaseImportProbeSeen |= phaseBit;
   if (bytes.size() != 8960 || READ_LE_UINT32(&bytes[4]) != 13) return false;
   const uint allowed515[] = {MASK515}, allowed536[] = {MASK536};
   uint acceptedInvalid = 0, rejectedInvalid = 0, acceptedValid = 0, validWrites = 0, rejectedWrites = 0;
   const uint phase = _place;
   auto attempt = [&](uint stateWord, uint replacement, bool allowed) {
    Common::Array<byte> changed = bytes;
    const uint offset = 8+(12+60*27+stateWord)*4;
    for (uint n = 0; n < 4; ++n) changed[offset+n] = byte(replacement>>(8*n));
    uint32 hash = 2166136261U;
    for (uint n = 8; n < changed.size()-4; n += 4) hash = (hash^READ_LE_UINT32(&changed[n]))*16777619U;
    for (uint n = 0; n < 4; ++n) changed[changed.size()-4+n] = byte(hash>>(8*n));
    if (GUARDED) {
     Common::Array<uint32> live = state; live[stateWord] = replacement;
     if (!_runner.importPersistentState(live)) return false;
     const uint32 beforeWrite = fingerprint();
     const bool advertised = canSaveBuilder();
     Common::MemoryWriteStreamDynamic encoded(DisposeAfterUse::YES);
     const bool written = saveGameStream(&encoded).getCode() == Common::kNoError;
     const bool unchanged = fingerprint() == beforeWrite;
     if (!restore(bytes) || fingerprint() != before) return false;
     if (advertised != allowed || written != allowed || !unchanged || (allowed ? encoded.size() != bytes.size() : encoded.size() != 0)) return false;
     if (allowed) ++validWrites; else ++rejectedWrites;
    }
    const uint sounds = _soundsStarted;
    const bool accepted = restore(changed);
    if (accepted && allowed) ++acceptedValid;
    if (accepted && !allowed) ++acceptedInvalid;
    if (!accepted && !allowed) ++rejectedInvalid;
    const bool expected = GUARDED ? allowed : true;
    const bool atomic = accepted || (fingerprint() == before && _soundsStarted == sounds);
    if (!restore(bytes) || fingerprint() != before) return false;
    if (accepted != expected || !atomic) {
     debug("Builder phase probe mismatch: P%u word%u value%u allowed%d accepted%d atomic%d",phase,stateWord,replacement,allowed,accepted,atomic);
     return false;
    }
    return true;
   };
   for (uint mask = 0; mask < 32; ++mask) {
    bool allowed = false;
    if (phase == 515) { for (uint v : allowed515) allowed |= mask == v; }
    else { for (uint v : allowed536) allowed |= mask == v; }
    if (!attempt(300,mask,allowed)) return false;
   }
   debug("Builder phase import probe: P%u accepted_invalid=%u rejected_invalid=%u accepted_valid=%u",phase,acceptedInvalid,rejectedInvalid,acceptedValid);
   if (GUARDED) debug("Builder phase writer probe: P%u valid=%u zero_byte_rejected=%u",phase,validWrites,rejectedWrites);
  }
'''
    block=block.replace('MASK515',','.join(map(str,masks[515]))).replace('MASK536',','.join(map(str,masks[536]))).replace('GUARDED','true'if guarded else'false')
    return head+text.replace(anchor,anchor+'\n'+block)+tail
