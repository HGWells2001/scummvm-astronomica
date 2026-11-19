from pathlib import Path
import os,json,math,wave
os.environ['HF_HUB_DISABLE_TELEMETRY']='1';os.environ['HF_HUB_DISABLE_XET']='1'
import numpy as np,torch
from scipy.signal import resample_poly
from transformers import AutoProcessor,AutoModelForSpeechSeq2Seq
from huggingface_hub import HfApi
w=Path(__file__).resolve().parent;o=w/'audio-acoustic-survey-nov19';name='openai/whisper-small.en';pin=HfApi().model_info(name).sha;torch.set_num_threads(4)
p=AutoProcessor.from_pretrained(name,revision=pin);m=AutoModelForSpeechSeq2Seq.from_pretrained(name,revision=pin).to('cuda').eval();rows=json.loads((o/'results.json').read_text());results=[]
# Independent recognition for all low-speech cases with a substantial transcription,
# plus intermediate acoustic probabilities and explicit vocalizations.
for r in rows:
 t=r['transcription_private']or''
 if not(r['speech_score']<.5 and (r['speech_score']>.07 or len(t.split())>=3 or r['top_labels'][0]['label']in['Groan','Grunt','Laughter','Speech'])):continue
 path=Path('D:/astro')/r['paths'][0]
 with wave.open(str(path)) as f:sr=f.getframerate();nc=f.getnchannels();sw=f.getsampwidth();b=f.readframes(min(f.getnframes(),sr*30))
 x=(np.frombuffer(b,np.uint8).astype(np.float32)-128)/128 if sw==1 else np.frombuffer(b,'<i2').astype(np.float32)/32768;x=x.reshape(-1,nc).mean(1);g=math.gcd(sr,16000);x=resample_poly(x,16000//g,sr//g).astype(np.float32);features=p(x,sampling_rate=16000,return_tensors='pt').input_features.to('cuda')
 with torch.inference_mode():ids=m.generate(features,max_new_tokens=96)
 text=p.batch_decode(ids,skip_special_tokens=True)[0].strip();results.append(dict(sha256=r['sha256'],path=r['paths'][0],text_private=text,model=name,revision=pin));(o/'second-recognizer-private.json').write_text(json.dumps(results,indent=2));print(r['paths'][0],repr(text),flush=True)
(o/'second-recognizer-complete.json').write_text(json.dumps(dict(status='SECOND_RECOGNIZER_COMPLETE',cases=len(results),model=name,revision=pin),indent=2))
