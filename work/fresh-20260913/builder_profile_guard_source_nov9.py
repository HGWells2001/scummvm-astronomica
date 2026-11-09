"""Apply the original-resource mask constraints; no format/header/ABI changes."""
def harden(text):
    signature='bool validBuilderState(const Common::Array<uint32> &state) {'
    assert text.count(signature)==1
    text=text.replace(signature,'bool validBuilderState(const Common::Array<uint32> &state, int place) {')
    check=' if (!ScriptRunner::validPersistentState(state)) return false;'
    start=text.index('bool validBuilderState(');end=text.index('\nbool validBuilderScene(',start)
    fragment=text[start:end];assert fragment.count(check)==1
    fragment=fragment.replace(check,' if (!builderScene(place) || !ScriptRunner::validPersistentState(state)) return false;')
    anchor=' return state[300] <= 31 && state[303] <= 5 && state[306] <= 5 &&'
    assert fragment.count(anchor)==1
    guard=''' // P515 starts with mask24, but its original selection/early-Launch
 // scripts may reset it to7. P536 starts and resets to7. Opcode39 only
 // adds a free bit, so a native import must retain one of these pools.
 const uint32 mask = state[300];
 if (place == 515) {
  if ((mask & 24U) != 24U && (mask & 7U) != 7U) return false;
 } else {
  if ((mask & 7U) != 7U) return false;
 }
'''
    fragment=fragment.replace(anchor,guard+anchor);text=text[:start]+fragment+text[end:]
    assert text.count('validBuilderState(state)')==3
    text=text.replace('validBuilderState(state)','validBuilderState(state,_place)')
    load='stream->err() || !validBuilderState(state,_place) || !builderScene(header[0])'
    assert text.count(load)==1
    text=text.replace(load,'stream->err() || !validBuilderState(state,header[0]) || !builderScene(header[0])')
    return text
