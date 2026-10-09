# Two canonical five-port calibration templates

Goal: effect port 0. A set denotes a binary vector. Each row gives all
remaining current wirings after its two observations. The terminal command
is the symmetric difference of the two probes and the listed net port.
An empty second probe uses no additional information. Cycle notation acts
on command labels as their current effect images; products compose right to left.

## known_identity

First probe: {0,1}.

| First effect | Second probe | Second effect | Exact posterior | Net command port |
|---|---|---|---|---|
| {0,1} | {0,2} | {0,2} | I, (3 4) | {0} |
| {0,1} | {0,2} | {1,2} | (0 1) | {1} |
| {0,1} | {0,2} | {0,3} | (2 3) | {0} |
| {0,1} | {0,2} | {0,4} | (2 4) | {0} |
| {0,2} | empty | empty | (1 2) | {0} |
| {1,2} | empty | empty | (0 2) | {2} |
| {0,3} | empty | empty | (1 3) | {0} |
| {1,3} | empty | empty | (0 3) | {3} |
| {0,4} | empty | empty | (1 4) | {0} |
| {1,4} | empty | empty | (0 4) | {4} |

## identity_or_swap_34

First probe: {0,3}.

| First effect | Second probe | Second effect | Exact posterior | Net command port |
|---|---|---|---|---|
| {0,1} | {1} | {3} | (1 3) | {0} |
| {0,1} | {1} | {4} | (1 4 3) | {0} |
| {0,2} | {2} | {3} | (2 3) | {0} |
| {0,2} | {2} | {4} | (2 4 3) | {0} |
| {0,3} | {0,1} | {0,1} | I, (2 4) | {0} |
| {0,3} | {0,1} | {0,2} | (1 2) | {0} |
| {0,3} | {0,1} | {1,3} | (0 3) | {3} |
| {0,3} | {0,1} | {0,4} | (1 4) | {0} |
| {1,3} | empty | empty | (0 1) | {1} |
| {2,3} | empty | empty | (0 2) | {2} |
| {0,4} | {0,1} | {0,1} | (3 4), (2 3 4) | {0} |
| {0,4} | {0,1} | {0,2} | (1 2)(3 4) | {0} |
| {0,4} | {0,1} | {0,3} | (1 3 4) | {0} |
| {0,4} | {0,1} | {1,4} | (0 4 3) | {3} |
| {1,4} | empty | empty | (0 1)(3 4) | {1} |
| {2,4} | empty | empty | (0 2)(3 4) | {2} |
| {3,4} | {0} | {3} | (0 3 4) | {4} |
| {3,4} | {0} | {4} | (0 4) | {4} |

