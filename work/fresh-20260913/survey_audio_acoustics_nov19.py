"""Offline acoustic survey of original WAVs. Model outputs are evidence, not runtime heuristics.
No originals or transcripts are published; only roles/hashes may be exported after review.
"""
from pathlib import Path
import os,json,hashlib,collections,math,wave,time
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
os.environ['HF_HUB_DISABLE_XET']='1'
import numpy as np
from scipy.signal import resample_poly
import torch
from transformers import AutoFeatureExtractor,AutoModelForAudioClassification,AutoProcessor,AutoModelForSpeechSeq2Seq
from huggingface_hub import HfApi
w=Path(__file__).resolve().parent;out=w/'audio-acoustic-survey-nov19';out.mkdir(exist_ok=False)
api=HfApi();names=['MIT/ast-finetuned-audioset-10-10-0.4593','openai/whisper-base.en'];pins={n:api.model_info(n).sha for n in names};(out/'models.json').write_text(json.dumps(pins,indent=2));print('Loading pinned models',pins,flush=True)
torch.set_num_threads(4);device='cuda' if torch.cuda.is_available() else 'cpu'
extractor=AutoFeatureExtractor.from_pretrained(names[0],revision=pins[names[0]])
classifier=AutoModelForAudioClassification.from_pretrained(names[0],revision=pins[names[0]]).to(device).eval()
processor=AutoProcessor.from_pretrained(names[1],revision=pins[names[1]])
recognizer=AutoModelForSpeechSeq2Seq.from_pretrained(names[1],revision=pins[names[1]]).to(device).eval()
root=Path('D:/astro');groups=collections.defaultdict(list)
for p in root.rglob('*.WAV'):groups[hashlib.sha256(p.read_bytes()).hexdigest()].append(p)
def load(p):
 with wave.open(str(p))as f:
  rate=f.getframerate();channels=f.getnchannels();width=f.getsampwidth();data=f.readframes(f.getnframes())
 assert width in(1,2)
 arr=(np.frombuffer(data,np.uint8).astype(np.float32)-128)/128 if width==1 else np.frombuffer(data,'<i2').astype(np.float32)/32768
 arr=arr.reshape(-1,channels).mean(axis=1);g=math.gcd(rate,16000)
 return resample_poly(arr,16000//g,rate//g).astype(np.float32)
rows=[]
for index,(h,files)in enumerate(sorted(groups.items(),key=lambda x:str(x[1][0]))):
 arr=load(files[0]);seconds=len(arr)/16000
 # Cover first/middle/end windows in long recordings; a single short sound has one window.
 starts=[0] if seconds<=10 else sorted(set([0,max(0,len(arr)//2-80000),max(0,len(arr)-160000)]))
 allprob=[]
 for start in starts:
  batch=extractor(arr[start:start+160000],sampling_rate=16000,return_tensors='pt').to(device)
  with torch.inference_mode():prob=classifier(**batch).logits.sigmoid()[0].cpu().numpy()
  allprob.append(prob)
 probs=np.max(allprob,axis=0);top=np.argsort(probs)[-10:][::-1]
 labels=[dict(label=classifier.config.id2label[int(i)],score=float(probs[i])) for i in top]
 speech=max(float(probs[i]) for i,v in classifier.config.id2label.items() if v.lower() in ['speech','male speech, man speaking','female speech, woman speaking','child speech, kid speaking','narration, monologue'])
 # Transcribe short files and ambiguous low-speech long clips only, bounded to30s.
 text=None
 if seconds<=10 or speech<0.5:
  features=processor(arr[:480000],sampling_rate=16000,return_tensors='pt').input_features.to(device)
  with torch.inference_mode():tokens=recognizer.generate(features,max_new_tokens=96)
  text=processor.batch_decode(tokens,skip_special_tokens=True)[0].strip()
 row=dict(sha256=h,paths=[p.relative_to(root).as_posix() for p in files],seconds=seconds,speech_score=speech,top_labels=labels,transcription_private=text)
 rows.append(row);(out/'results.json').write_text(json.dumps(rows,indent=2))
 print(index+1,len(groups),str(files[0].relative_to(root)),round(seconds,2),'speech',round(speech,4),labels[0]['label'],repr(text),flush=True)
(out/'complete.json').write_text(json.dumps(dict(status='ACOUSTIC_SURVEY_COMPLETE',unique=len(rows),files=sum(len(r['paths'])for r in rows),model_pins=pins,production_unchanged=True),indent=2));print('ACOUSTIC_SURVEY_COMPLETE',flush=True)
