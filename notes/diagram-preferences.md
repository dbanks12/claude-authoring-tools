# David's diagram preferences

Distilled from iterating on protocol diagrams. Short rules for future diagrams.

## Structure

- Keep each diagram minimal and simple. 3-8 boxes. Split into more diagrams before making one dense.
- Make the diagram itself carry the explanation. Checks, conditions, and steps go inside the picture (dotted sub-boxes under the actor), not as caption prose below.
- When a process has a real conceptual split, draw it as named phases (e.g. audit the PAST vs constrain the PRESENT), each phase its own colored dotted card.
- Order members to match reality: fields in digest order, data in structure order, outputs in dependency order (the lists a signature references come before the signature).
- Group actors or components into labeled zones (dotted border, small uppercase corner label) when they belong to distinct subsystems.
- Zoom-in diagrams must look visually reminiscent of the mini version they expand: same background fill, same colors, same idioms, just bigger boxes with room for text.
- Drill down a level or two when asked for internals: one diagram per inner algorithm, not one mega chart.

## Boxes and sub-boxes

- Represent each item (note, nullifier, signature, deposit) as its own mini box. Never a prose list where boxes could show cardinality.
- Wrap related items in a parent box titled with the field name. Sibling parent boxes get the same width.
- An item with attached aux data becomes a bundle: the item mini box plus its aux lines, inside a dotted bundle border. Reuse the idiom everywhere it applies.
- Sibling boxes and chips must match size exactly (width, height, title font size). If one gets hand-resized, propagate to all siblings.
- Inner boxes must fit inside their parents with visible margins. Widen the parent rather than let children spill.
- Uniform row heights within one diagram. Boxes with less content get taller rather than breaking the grid.
- Type or domain tags (domain: NOTE) go top-right of the box as small text.
- Square corners for the current sets. Corner style is a deliberate per-set choice and must be coherent within a set.

## Color and coding

- One shared color language per canvas. Same concept, same color, everywhere.
- Solid box = a thing. Cross-hatch box = a hash of a thing. Red crack through a box = a nullifier or kill. Dashed is only for elided filler (see style-system.md).
- Related input and output items share hue (deposit d1 green, its nullifier nf(d1) green with crack).
- Give a distinct concept its own unique color (anchorBlockHash teal) and keep it identical between full box and chip.
- Chips are miniature color-coded references to other boxes: same fill and dash style as the box they reference. Arrays get "..." inside, scalars do not.
- Nullifier boxes are red family, not gray or black.
- Label text color must match its box stroke color.
- When a diagram uses its own color semantics (actors grouped by trust), add an explicit legend row.
- Semantic grouping must be explicit and sane (user, L1 contract, L2 contract, off-chain anyone-can-run, untrusted host), not vibes.

## Arrows

- Arrows exist to physically connect boxes. An arrow that floats, shrinks, or points at a corner is a bug.
- Connect at edge midpoints when sensible. Tall-to-short pairs get a horizontal arrow at the short box's midline.
- New diagrams: bound arrows, or the place.py helper. Connector-line canvases: arrow_doctor after every batch.

## Text, labels, notation

- Every diagram gets a large left-margin nav label, fontSize 36 uppercase, so zooming out reads as a table of contents.
- Nav labels: no numbering, no abbreviations (ENCLAVE REGISTRATION not REG, SIGNATURE STRUCTURE not SIG ZOOM). Wrap long labels, do not shorten.
- Index notation for worked examples: n1, n2 for notes, nf(n1) for nullifiers, h(n3) for hashes, d1 deposits, w1 withdrawals. Plain digits only, never unicode subscripts (the font lacks the glyphs).
- Prefix semantics are strict: "+ ..." only for attached aux data, "= ..." only for definitions, bare text for properties. Never decorate with a prefix that lies.
- Field lists inside a box: one entry per line with "- " prefix. Provenance or meta statements ("baked into the enclave image, not inputs") as smaller black subtext below the list.
- Small black annotation text may spill outside its box when needed.
- Avoid implementation jargon in diagram text (no BoundedVec). Say what it means instead.
- No semicolons. No em dashes. Short active sentences.
- Captions may cross-reference sibling diagrams ("see signature structure zoom-in below") and list the real field order.
- Every annotation must visibly attach to something. Delete orphaned floating notes.

## Content accuracy

- Learn before drawing: read the actual source files and design doc sections first.
- Names must match current code, not doc folklore (Pool, not Reward Pool). Verify actor lists against the source of truth.
- Use one concrete worked example with continuity across the whole diagram set (n1, n2 -> n3, n4, d1, w1, balance 3 + 3 + 3 = 5 + 1 + 3).
- Named actors (Alice) are fine in flow examples. Actor or role listings stay generic (User).
- Distinguish per-operation inputs from baked-in identity by placement: statics attach to the component that owns them, not to the input column.

## Process and workflow

- The user edits the canvas live at port 3000. Query current state before batch edits, preserve and propagate his changes (adopted titles, adopted sizes).
- Screenshot and actually inspect after every batch. Fix collisions before continuing.
- Re-crop figures after any canvas change. Crops are snapshots, not live links.
- Keep the mega canvas, per-figure crops, and repo exports in sync after each accepted change.

## Candidates to fold into SKILL.md

Already covered there: color language basics, checks-inside-picture, bound arrows + arrow_doctor, unabbreviated nav labels, square-corner coherence, unicode subscript ban, bound-label fontSize gotcha, crop pipeline, no em dashes or semicolons in copy.

Not yet reflected, worth folding:

- Prefix semantics: "+" aux, "=" definition, bare property.
- Solid = thing, cross-hatch = hash, red crack = nullifier, chip = miniature reference with "..." for arrays.
- Bundle idiom for item plus aux data.
- Sibling uniformity rules (widths, heights, chip sizes, title font sizes) and propagate-user-resizes.
- Order members to match reality, outputs in dependency order.
- Unique color per distinct concept, input/output hue pairing, label text matches box stroke.
- Domain or type tags top-right.
- Legend row whenever a diagram introduces its own color semantics.
- Zoom-ins visually reminiscent of their mini version.
- Index notation conventions (n1, nf(n1), h(n1)) and one worked example with continuity across the set.
- Field lists as "- " lines with smaller black meta subtext, annotations may spill.
- No implementation jargon in diagram text.
- Learn from source before drawing, verify names against code.
- Cross-reference captions between related diagrams.
- Delete orphaned annotations.
- Respect and propagate live user edits to the canvas.
