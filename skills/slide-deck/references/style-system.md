# Canvas style system

These families cover domain diagrams. Code-change diagrams use only the palette in
`../../excalidraw-skill/SKILL.md` section 6.

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
| Hash / commitment (h(n), roots, tree nodes, spongeBlobHash, anchorBlockHash) | cross-hatch | family light tint (one step deeper when the box sits on a tinted parent, or the hatch vanishes) | solid | substantial, but woven from other data |
| Nullifier (a hash that kills) | cross-hatch | red tint #ffe3e3 | solid red | hash texture in red, plus the red crack line glyph |
| Secret / key material (NHK, enclave key) | zigzag | family tint | solid | present but never published |
| Elided / padding ("...", "0...0", other fields) | none | - | dashed, gray | deliberately insubstantial filler, gray as neutral/supporting |
| Container / parent (titled field groupings) | none | - | solid | structural border |
| Zone / phase / bundle / tree frame (conceptual groupings) | none | - | dotted | a mental grouping, not an object |
| Critical gate (AND, freeze, reject) | solid | red tint | solid, width 2 | loud on purpose |

Dashed stroke is ONLY for elided filler. Never for hashes, preimages, or groupings.
A cross-hatch backgroundColor must be a very light tint of the SAME family as the stroke,
never borrowed from another family. One tint per family, identical everywhere on the canvas.
Chips inside signature boxes are miniatures: same fill and stroke as the box they reference,
with "..." inside array chips.

## Merkle trees and lineage columns

A merkle node or root box is horizontally centered on the midpoint of its children's centers.
Tree links are angled (child top center to parent bottom center). Everything OUTSIDE the tree
in a lineage diagram connects vertically: achieve this by moving the SOURCE box (or sliding
the target member inside its parent) until centers align, never by slanting the connector.
Frame a tree with a dotted triangle, apex at the root, sides clearing the contents narrowly.
Trees are always incomplete: leave intermediate nodes UNLABELED, draw the links that skip
elided levels as dashed, and place a vertical ellipsis (three stacked periods, the hand font
has no vertical-ellipsis glyph) in the tree's center between the top nodes and the root.
Horizontal "..." outside the last leaf and last node mark elided siblings.

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
