from HitQueue import *


hQ = hitQueue()
rEvQ1 = robotEventsQueue()
rEvQ2 = robotEventsQueue()

hQ.addHit(1000,1,10)
hQ.addHit( 990,2,20)
hQ.addHit( 800,1,10)
hQ.addHit(1050,4,40)
hQ.addHit(1200,3,30)

rEvQ1.addHit(980)
rEvQ1.addHit(1100)
rEvQ1.addHit(1250)

rEvQ2.addHit(830)
rEvQ2.addHit(1060)
rEvQ2.addHit(1250)

print(hQ.get_buff())
hQ.update([rEvQ1])
print(hQ.get_buff())
print(rEvQ1.get_buff())
print(rEvQ2.get_buff())