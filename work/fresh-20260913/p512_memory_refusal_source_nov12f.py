"""Exercise the accepted independent stopped clock just before the clip end."""
from p512_memory_refusal_source_nov12d import inject as previous


def inject(cpp, script):
    cpp, script = previous(cpp, script)
    anchor = 'static uint boundaries=0,cross=0,finalFirst=0,finalRepeated=0;Common::Array<uint32>words;if(!captureP512Stopped(words,now))'
    start = cpp.index(anchor)
    end = cpp.index('\n', start)
    injection = '''
 if(ConfMan.hasKey("astronomica_p512_under_end_clock")&&ConfMan.getBool("astronomica_p512_under_end_clock")){
  const uint32 end=uint32(Audio::Timestamp(0,words[14],30).msecs());
  const uint32 original=words[10];
  words[10]=end>8?end-8:0;words.back()=p512PacketHash(words);
  if(!installP512Memory(words))return false;
  debug("P512 stopped clock edge: original%u retained%u end%u current%u",original,words[10],end,words[11]);
 }
'''
    return cpp[:end] + injection + cpp[end:], script
