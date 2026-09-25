# Expanded NER Corpus — Human Annotation Instructions

## Objective

Annotate 420 new, independent provision-level tasks to address the data limitation observed in the
pilot transformer experiments. The selection cues only increase the chance that a task contains a
target entity. They are **not labels** and do not guarantee that an entity is present.

## Inputs

Annotator 1 imports the five files below into one new Label Studio project, in order:

1. `data/annotation/expansion/label_studio_expansion_part_01.json` (100 tasks)
2. `data/annotation/expansion/label_studio_expansion_part_02.json` (100 tasks)
3. `data/annotation/expansion/label_studio_expansion_part_03.json` (100 tasks)
4. `data/annotation/expansion/label_studio_expansion_part_04.json` (100 tasks)
5. `data/annotation/expansion/label_studio_expansion_part_05.json` (20 tasks)

Annotator 2 creates a separate Label Studio project and imports only:

`data/annotation/expansion/label_studio_expansion_shared.json` (84 tasks)

Annotator 2 must work independently and must not see Annotator 1's labels. Use the existing project
label configuration from `data/annotation/label_studio_config.xml`.

## Required rules

- Apply only the five approved entity labels.
- Read the complete annotation guidelines before starting.
- Do not label cue words automatically; label only spans satisfying the formal definition.
- Preserve exact boundaries and exclude surrounding whitespace and punctuation unless legally part
  of the entity.
- A task may legitimately contain no entity.
- Do not use AI-generated labels as final annotations.
- Record uncertain cases in the progress sheet for adjudication.

## Tracking and export

Update `data/annotation/expansion/expansion_progress.csv`. Export Annotator 1's completed project as
`expansion_annotator1_export.json` and Annotator 2's project as
`expansion_annotator2_export.json` into `data/annotation/expansion/`.

Do not merge these annotations with the training corpus until validation, agreement calculation,
and human adjudication are complete.
