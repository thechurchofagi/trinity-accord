# Failures, rejected claims, and review corrections

**DVC20261010; finite reference model only.** These records preserve what failed or required correction. A final assertion PASS is not a claim that the first design or every interpretation was correct.

## Scientific proposals rejected

| Proposal | Disposition and reason |
|---|---|
| Closing a capture gate implements absence in the current consumer cell | Rejected. A warm register retains its earlier token. With both old payloads equal to one, all four gate settings feed the eager AND task two ones unless preparation clears or otherwise excludes those tokens. |
| A recorded source issue proves that a current probe was consumed | Rejected. Arrival after capture leaves the old port token in the selected latch. Source, arrival, latch and read events must be distinguished. |
| A current epoch header proves the intended current source pair | Rejected. Swapped ports and a replayed old origin with a new header pass this metadata check. |
| Nonoverlapping source-port validity windows prevent a same-episode pair | Rejected under the explicitly added retention and pairing contract. Separate captures can preserve the intended two earlier tokens. They are not thereby simultaneous source events. |
| Full gate-factorial outputs validate the data path | Rejected. The displayed gate-label reflex matches every nominal OR availability cell while reading experiment labels. A fixed-gate payload challenge rejects only this named rival. |
| An observational shadow gate is a human consumer intervention | Rejected when the shadow has no directed causal path to the endpoint itself or any of its ancestors. Concurrency with a human task supplies neither a neural target nor an experiential bridge. |
| Position/state received after the current consequence is a prediction of that same consequence | Rejected for that precise chronology. Earlier state and future consequences are separate valid target choices. |
| Simulated PSE numbers could strengthen the causal-isolation proof | Rejected before the final run. A provisional algebraic endpoint proxy merely mirrored the assumed graph and would add no empirical evidence. No synthetic human endpoint is retained or included in the final counts. |

## Development and semantic review history

The first development run used provisional identifier `SLC20261010`. Its code, result JSON and receipt are preserved in `history/slc_provisional_first_run/`. The parent then assigned stable record `DVC20261010_Device_Consumer_Validation`; no remote R-number was reserved.

The parent noticed that initial lane-by-lane construction appended M events at ticks −5, −4, −3 before P events at −5, −4, −3. Although a per-lane interpretation could form a partial order, the log was described as a total execution trace. The final implementation instead performs all lane arrivals, then all gate changes, then all captures. Swapped-port construction was repaired similarly. Retained traces are checked for nondecreasing ticks and preceding event parents; equal ticks use append order.

The modeled consumer output now lists the actual modeled read events as its parents. Reading a supplied zero is explicitly distinguished from the neutral default for an absent source. These repairs avoid claiming complete executed ancestry from structural input labels alone.

The replay witness now retains the actual old source origin and true epoch while changing only the claimed metadata epoch. An earlier draft generated a new event with an old epoch number; that was too weak to demonstrate replay of the actual old occurrence.

In the final disjoint-window review, the prose stated that P was valid on `[6,8)` but the displayed trace originally did not contain its departure at 8. The final code adds arrival of an epoch-two P token at 8 before snapshot commit. The old epoch-one P token captured at 7 remains in the buffer. Both `[2,4)` and `[6,8)` are therefore realized by explicit port-replacement events, not merely annotation.

The code version immediately before that final departure repair had SHA256 `e39c5f69d34913d9f0db1d1cea884b0fff3a1b597e7b39b959872bb67a4e250a`; its result SHA256 was `a96c07f97674a69f1b26af6f76f5088526559b8a96aab32d707079f8008d6431`. The current exact bytes and receipt supersede those provisional final-file values. No broader enumeration was added for the repair.

## Attribution and uncompleted scope

Register retention, races, setup/hold timing and snapshots are prior concepts. The manufacturer already documents frame snapshot and last-frame query behavior. Chandy–Lamport provides relevant earlier snapshot context; it is not the implemented algorithm here. The retained work is an application to MPC/SCU consumer-cell admission and a proposed specific device contract. Worldwide priority of that application has not been established.

No physical rig was connected, no firmware installed, no actual capture latency measured, no human participant enrolled, no neural consumer located, and no H endpoint validated. This worker does not certify the full historical map, change a completed release, publish a DOI, or claim that a local code run verifies external persistence.
