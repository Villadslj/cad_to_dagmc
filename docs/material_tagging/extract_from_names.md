# Extracting Material Tags from Part Names

When importing a STEP file, you can automatically derive material tags from the
STEP part names instead of manually specifying `material_tags=[...]`. This
feature is intended to mimic [CAD_to_OpenMC](https://github.com/openmsr/CAD_to_OpenMC)-style
workflows where part names such as `ss_watertank` map to material tag `ss`.

## How it works

When `extract_material_tags_from_part_names=True` is set on `add_stp_file(...)`:

1. The STEP file is loaded as an assembly to preserve part names.
2. Each part name is stripped of leading/trailing whitespace.
3. If the name starts with any configured ignore prefix, the `default_tag` is used.
4. Otherwise, the name is split using `re.split(name_delimiter_pattern, name)`.
5. The first non-empty token becomes the material tag.
6. If no token can be extracted and no `default_tag` is set, a clear error is raised.

## Delimiter pattern

The default delimiter pattern is `r"[\s_@]+"`, which splits on:
- Whitespace (spaces, tabs)
- Underscores (`_`)
- At-signs (`@`)

You can customize this with the `name_delimiter_pattern` parameter.

## Examples

### Basic usage

If your STEP file has parts named `ss_watertank`, `water_coolant_pipe`, and
`eurofer@blanket`, the extracted material tags will be `ss`, `water`, and `eurofer`:

```python
from cad_to_dagmc import CadToDagmc

model = CadToDagmc()
model.add_stp_file(
    filename="reactor.step",
    extract_material_tags_from_part_names=True,
)
model.export_dagmc_h5m_file(filename="reactor.h5m")
```

### Custom delimiter and ignore prefixes

```python
from cad_to_dagmc import CadToDagmc

model = CadToDagmc()
model.add_stp_file(
    filename="reactor.step",
    extract_material_tags_from_part_names=True,
    name_delimiter_pattern=r"[\s_@]+",
    ignore_prefixes=["IGNORE"],
    default_tag="vacuum",
)
model.export_dagmc_h5m_file(filename="reactor.h5m")
```

In this example:
- A part named `IGNORE_bolt` would get material tag `vacuum` (because it matches the ignore prefix)
- A part named `ss_watertank` would get material tag `ss`
- A part named `steel tank` would get material tag `steel`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `extract_material_tags_from_part_names` | `bool` | `False` | Enable automatic material tag extraction from part names |
| `name_delimiter_pattern` | `str` | `r"[\s_@]+"` | Regex pattern used to split part names |
| `ignore_prefixes` | `list[str] \| None` | `None` | List of prefixes; matching names use `default_tag` |
| `default_tag` | `str \| None` | `None` | Fallback tag for ignored prefixes or empty names |

## Compatibility

- This feature does **not** break the existing `material_tags=[...]` workflow.
- If both `material_tags` and `extract_material_tags_from_part_names=True` are
  provided, a `ValueError` is raised to prevent ambiguity.
- Users who do not opt into this feature see no change in behavior.
