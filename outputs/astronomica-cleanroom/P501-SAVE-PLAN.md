# P501 ready-to-pitch save plan

Status: same-build native WASAPI and complete compatibility verification PASS28October2026. Publication requires the separate export gate.

Original data: `D:/astro/PLACES/P501/MEGAFILE.HYP`,786726 bytes, SHA256 `fe46b4707b6c4bb1f8df9e31fed8b7af103e3839702d88c5e30c331f71877b41`. The strict reader consumes the whole resource with27sprites,259commands,five local declarations and a single8-command startup program. The six original external BMPs and all direct WAV assets are separately inventoried by `probe_p501_save.py`.

The first scope is stopped ready-to-pitch states: pitch0,won0,unlocked input,no generated cleanup work,no pending image or foreground sound,and exactly the original recurring poll at index0 or7. All eight commands and original local declaration metadata must match. Preserve literal poll epoch and original loadedAt; do not replay startup on restore.

The state includes all605runner words plus poll index/since,all27independent27-word sprite records,five BallMotion fields,and Comet/Jupiter scratch/cache plus phase under explicit unrelated-motion guards. World selection must retain dormant ball motion and hidden crush frame histories. Seven background identities are distinct:initial embedded/empty displayed name,external BACKORBI,and PHOBOS,BLACKDWA,JUPITER,VESTA,MOON. Equal pixels do not imply equal displayed-name history.

Prepare original background data and every runner/sprite/private value locally before changing the live scene. A checksummed but invalid save must leave live queues,audio,image,clock and input unchanged. Candidate version27/slot26/payload5896 remain subject to final implementation and review.

Required proof:each world and cross-world history,strike0/1/2 and settled third-strike reset,retained Phobos/Moon/Vesta motion,hidden Black Dwarf frames,original200ms poll and uint32 clock wrap. After restoring,compare actual future pitch/hit/catch movement,strict input-window edges,Vesta5000ms pause,first/repeated success and voluntary exit. Require natural voice completion,ambient restart,all payload truncations/single-byte corruptions,checksummed invalid fields,physical fresh-process slot and metadata. Exact final-source independent review precedes promotion; complete native WASAPI compatibility on the main build precedes publication.

The167-record preparatory audit established observations and proposed eligible boundaries only. It did not implement a serializer or prove save continuation. Additional native history measurements must define any admitted private/sprite profiles.
