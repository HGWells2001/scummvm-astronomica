"""Bind the user's acoustic confirmation to the completed normal player run."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
w = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = w / 'exploration-player-nov18'
p = json.loads((out / 'proof.json').read_text())
assert p['status'] == 'INSTALLED_NORMAL_EXPLORATION_PLAYER_PASS'
assert sha(out / 'native.log') == p['native_log_sha256']
assert sha(w / 'build/Releasex64/scummvm.exe') == p['exe_sha256']
receipt = dict(status='USER_CONFIRMED_EXPLORATION_MUSIC_AUDIBLE',
    recorded_at=datetime.now(timezone.utc).isoformat(),
    user_reply='Sì, ora la sento', confirmed_initial_room=103,
    player_proof_sha256=sha(out / 'proof.json'),
    native_log_sha256=p['native_log_sha256'], exe_sha256=p['exe_sha256'],
    limits=['User confirmation of the opened exploration room only; no claim for every visited room',
            'No acoustic recording; no original media or personal configuration exported'])
(out / 'user-confirmation.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(receipt['status'])
