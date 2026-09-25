# Legal NER Annotation Guidelines

Status: Phase 4 working guidelines. Labels must be assigned by human annotators; the preparation
pipeline creates blank tasks only.

## Approved schema

### `FUNDAMENTAL_RIGHT`

A legally protected fundamental right or freedom expressed as the subject of a constitutional
guarantee. Include the complete name of the right. Exclude a generic occurrence of “right” that
does not identify a particular protected right, remedies, and legal citations.

### `OFFENSE`

The name of an offence or conduct phrase that the provision expressly makes punishable or declares
to be an offence. Include words needed to identify the prohibited conduct. Exclude allegations,
procedural steps, and punishments standing alone.

### `PENALTY`

A punishment or statutory sanction, including an imprisonment term, fine, forfeiture, or complete
coordinated punishment expression. Include qualifying duration or amount when it belongs to the
punishment. Exclude procedural consequences that are not punishments.

### `CONSTITUTIONAL_BODY`

The official name of an institution, commission, council, court, office, or other body created or
recognized by the Constitution. Include official qualifiers forming part of the name. Exclude a
generic description unless the context uses it as the formal body name.

### `TEMPORAL_ENTITY`

A date, year, period, deadline, frequency, or other explicit time expression. Include every word
needed for the expression. When a duration occurs inside a `PENALTY`, label the complete punishment
as `PENALTY` and do not create an overlapping `TEMPORAL_ENTITY`.

## Classes not currently included

Article names, Section numbers, amendment references, Act numbers, and cross-references remain
deterministic structural metadata. Do not label them as `LEGAL_REFERENCE` or `LEGAL_PROVISION`.
Adding either label requires explicit researcher approval and a versioned schema change.

## Boundary and consistency rules

1. Select the smallest complete phrase identifying the entity.
2. Exclude leading/trailing spaces and unrelated punctuation.
3. Include internal punctuation belonging to the official name or expression.
4. Exclude introductory determiners unless they form part of an official name.
5. Do not create nested or overlapping spans; flag the case for adjudication.
6. Annotate coordinated entities separately when each independently belongs to a class. Use one
   span when a conjunction forms one official name or combined penalty expression.
7. Keep abbreviations separate from expanded names unless written as one unit. Label a standalone
   abbreviation only when its meaning is unambiguous in that task.
8. Preserve numbers and dates exactly as shown. Never repair OCR inside the annotation tool;
   record the problem in the progress tracker.
9. Negation, exceptions, duties, and conditions must remain in source text. They are not separate
   entity classes under this schema.

## English and Sinhala examples

No positive examples are pre-labelled because no expert-verified annotation set has been supplied.
Annotators must not treat automatically selected text as gold. During the pilot, two annotators
should propose examples from the supplied PDFs. Accepted examples must then be added here with the
document ID, physical PDF page, exact span, label, and adjudicator name.

This restriction prevents invented Sinhala translations and unverified legal interpretations.

## Ambiguity procedure

For a phrase that could receive multiple labels, record the task ID, proposed labels, exact text,
and reason. Do not resolve legal ambiguity by guessing. The adjudicator records a final label or
excludes the span and explains the decision.

## Double annotation and agreement

Tasks marked `shared_subset=yes` must be independently annotated by at least two people. Do not
show one annotator’s labels to the other before both versions are submitted.

Report exact span-and-label precision, recall, and F1 plus token-level Cohen’s kappa. Token-level
kappa can be inflated by many `O` tokens, depends on tokenization, and does not clearly separate
boundary disagreements from class disagreements. Exact entity-level F1 is required alongside it.
The proposed kappa target above 0.80 is not achieved until calculated from real annotations.
