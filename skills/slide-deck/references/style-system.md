# Canvas style system

Two orthogonal axes. Hue says which domain family a box belongs to. Texture (fill style plus
stroke style) says what kind of thing it is. Any box reads as (family, kind).

## Axis 1: hue families

| Family | Stroke | Solid tint | Covers |
|---|---|---|---|
| Orange | #f08c00 | #fff9db | notes, note preimages, user value |
| Green | #2f9e44 | #d3f9d8 | deposits, L1-to-L2 messages, settlement |
| Purple | #9c36b5 | #f3d9fa | withdrawals, L2-to-L1 messages, off-chain operators |
| Blue | #1971c2 | #e3f2fd | protocol structures (headers, TxEffect, contracts), verification, signatures |
| Teal | #0ca678 | #e6fcf5 | RESERVED: the anchor / root of trust only |
| Red | #e03131 | #ffe3e3 | destruction (nullifiers) and critical gates |
| Gray | #495057 | #e9ecef | neutral supporting data: witnesses, statics, untrusted hosts |

Label text color always equals box stroke color.

## Axis 2: kind textures

| Kind | fillStyle | backgroundColor | strokeStyle | Reading |
|---|---|---|---|---|
| Concrete data (preimages, intents, records, signatures, witnesses) | solid | family tint | solid | the value is present here |
| Hash / commitment (h(n), roots, tree nodes, spongeBlobHash, anchorBlockHash) | cross-hatch | family LIGHT tint | solid | substantial, but woven from other data |
| Nullifier (a hash that kills) | cross-hatch | red tint #ffe3e3 | solid red | hash texture in red, plus the red crack line glyph |
| Secret / key material (NHK, enclave key) | zigzag | family tint | solid | present but never published |
| Elided / padding ("...", "0...0", other fields) | none | - | dashed, gray | deliberately insubstantial filler, gray as neutral/supporting |
| Container / parent (titled field groupings) | none | - | solid | structural border |
| Zone / phase / bundle / tree frame (conceptual groupings) | none | - | dotted | a mental grouping, not an object |
| Critical gate (AND, freeze, reject) | solid | red tint | solid, width 2 | loud on purpose |

Dashed stroke is ONLY for elided filler. Never for hashes, preimages, or groupings.
Chips inside signature boxes are miniatures: same fill and stroke as the box they reference,
with "..." inside array chips.

## Axis 3: weight

strokeWidth 1 by default. strokeWidth 2 only for the traced object's path in a lineage
diagram and for critical gates. strokeWidth 4 unused.

## Arrows

Solid black width 1 = function or transform, labeled directly to the right of the arrow
midpoint (never covered by it). Colored solid = semantic flow (green settlement or output,
red the user's real transaction, purple external hop). Dashed arrow = response or return leg
in sequence diagrams. Width 2 only on an emphasized trace path.

## Nullifier hue note

All nullifiers are red family regardless of what they derive from. The derived-inherits-family
rule applies to hashes (h(d1) would be green) but nullifiers trade lineage pairing for the
uniform "kill" reading.
