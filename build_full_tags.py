import json,re
from pathlib import Path
base=Path(__file__).parent
M=json.load(open(base/'mechanisms.json',encoding='utf-8'))
old=json.load(open(base/'atlas-tags.json',encoding='utf-8'))
curated=old['entries']

RULES={
'motion':[
('rotation',r'\brotat|\brevolv|\bturn(?:ing|s)?\b|\bshaft\b|\bspindle\b|\bpivot|\bhinge|\bswivel'),
('oscillation',r'oscillat|rock(?:er|ing)|vibrat|swing(?:ing)?|to and fro'),
('reciprocation',r'reciprocat|back and forth|alternat(?:e|ing) motion'),
('translation',r'\bslide|sliding|linear|straight[- ]line|rectilinear|travers|longitudinal|vertical motion|horizontal motion|rise|rising|lift(?:ing)?|lower(?:ing)?'),
('rotation + translation',r'screw|helic|spiral|worm|rising hinge|rack and pinion'),
('intermittent / indexed motion',r'intermittent|ratchet|pawl|step by step|index(?:ing)?|Geneva|escapement'),
('variable motion / ratio',r'variable|vary(?:ing)?|adjustable (?:throw|stroke|speed|motion)|variable speed|variable throw'),
('reversing motion',r'revers(?:e|ing)|change direction'),
('multi-axis rotation',r'universal joint|ball and socket|gimbal|spherical'),
('approx. straight-line motion',r'parallel motion|straight[- ]line motion|approximate straight|Watt'),
('compound / linked path',r'link motion|linkage|four[- ]bar|toggle|compound motion|connecting rod'),
('continuous rotary motion',r'continuous(?:ly)? rot|continuous rotary'),
],
'purpose':[
('transmit motion',r'transmit|convey(?:ing)? motion|drive(?:n|s)?|communicat(?:e|ing) motion'),
('convert motion type',r'convert|converting|rotary.*recipro|recipro.*rotary|circular.*straight|straight.*circular'),
('change direction',r'change direction|at right angles|angular gear|bevel|revers'),
('vary speed / ratio',r'variable speed|change speed|vary.*speed|speed gear|different speeds|ratio'),
('vary stroke / travel',r'variable throw|vary.*stroke|adjustable stroke|variable stroke|vary.*travel'),
('increase force / leverage',r'leverage|increase.*force|powerful|mechanical advantage|multiply.*force'),
('reduce speed / increase torque',r'reduction gear|reduce.*speed|slow motion'),
('maintain orientation / parallelism',r'parallel motion|parallel to|remain parallel|maintain.*parallel'),
('guide along path',r'guide|guided|track|groove|slot|path'),
('clear obstruction / offset path',r'clear(?:ance|ing)?|obstruction|offset|out of the way|swing clear'),
('self-return / restore position',r'self[- ]clos|return(?:ing)?|restore|spring back|gravity.*return'),
('lock / hold position',r'lock|locking|clamp|hold(?:ing)?|catch|latch|stop motion'),
('position / adjust',r'adjust|position|setting|set screw|regulat'),
('raise / lower load',r'hoist|lift|raising|lowering|elevator|jack'),
('reverse automatically',r'automatic.*revers|reverse automatically|reversing.*automatic'),
('produce dwell / pause',r'dwell|pause|rest during|stationary during'),
('index / advance incrementally',r'index|step by step|ratchet|pawl|feed motion'),
('engage / disengage drive',r'clutch|engage|disengage|throw out|disconnect'),
('absorb shock / cushion',r'shock|cushion|buffer|spring mounting|elastic'),
('counterbalance / assist load',r'counterbalance|counterweight|balance weight'),
('open / close / fold',r'door|shutter|lid|fold|hinge'),
('steer / articulate',r'steer|steering|articulat'),
('pump / compress / move fluid',r'pump|piston pump|compressor|bellows'),
('feed / convey material',r'feed|convey|elevator bucket|hopper'),
],
'behavior':[
('fixed pivot',r'fixed pivot|pivoted|hinged|fulcrum|rocker'),
('moving / virtual pivot',r'moving pivot|virtual pivot|link hinge|four[- ]bar|parallel motion'),
('link constrained',r'link|connecting rod|toggle|parallel motion'),
('cam constrained',r'\bcam\b|eccentric|wiper'),
('slot / pin constrained',r'slot|slotted|groove|pin in'),
('gear constrained',r'gear|pinion|rack|toothed|bevel'),
('belt / rope / chain constrained',r'belt|rope|chain|cord|pulley'),
('screw constrained',r'screw|worm|thread'),
('spring assisted / biased',r'spring'),
('gravity assisted / biased',r'gravity|weight(?:ed)?|counterweight'),
('friction controlled',r'friction|brake'),
('ratchet / one-way',r'ratchet|pawl|one direction|one-way'),
('over-center / toggle',r'over[- ]center|toggle'),
('detent / indexed',r'detent|index|notch'),
('flexible member',r'flexible|strap|tape hinge|cord|rope|belt|chain'),
('rolling contact',r'roller|rolling|wheel'),
('sliding contact',r'slide|sliding|guide|crosshead'),
('eccentric / offset axis',r'eccentric|crank|offset'),
('universal / spherical joint',r'universal joint|ball and socket|spherical|gimbal'),
('lost motion / clearance',r'lost motion|clearance|loose fit'),
('automatic trip / release',r'trip|automatic release|self-releasing'),
]
}

def tags(text, rules):
 t=' '.join(text.split()).lower()
 return [name for name,pat in rules if re.search(pat,t,re.I)]

entries={}
for plate, blocks in M['plates'].items():
    for b in blocks:
        txt=b['text']
        for n in b['numbers']:
            k=str(n)
            if k in curated:
                e=dict(curated[k]); e['classification']='curated-pilot'
            else:
                e={'plate':int(plate),'numbers':[n]}
                for dim in ('motion','purpose','behavior'):
                    vals=tags(txt,RULES[dim])
                    if vals: e[dim]=vals
                e['classification']='keyword-first-pass'
            entries[k]=e
# Preserve missing 1854 as not source-indexed (don't invent)
out={'schema_version':2,'status':'full-rollout-first-pass','note':'All source-indexed Barber entries are covered. Original 50 pilot records remain curated; remaining records use conservative keyword-derived design-intent tags from Barber text. Barber source text remains untouched in mechanisms.json. Empty dimensions mean no confident first-pass tag was assigned.','entries':entries}
json.dump(out,open(base/'atlas-tags.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('entries',len(entries))
for d in ('motion','purpose','behavior'):
    tagged=sum(bool(e.get(d)) for e in entries.values())
    vals=sorted({x for e in entries.values() for x in e.get(d,[])})
    print(d,tagged,'/',len(entries),'labels',len(vals),vals)
