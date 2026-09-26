meta:
  id: monet_x3dcfg
  title: x3dcfg.cfg, authoring-tool settings left in the data tree
  file-extension: cfg
  endian: le
  encoding: latin1

doc: |
  Not read by the shipped game or its DLLs (E-0103). Layout from the corpus alone;
  validated by engines/x3d/tools/parsers/cfg.py: 38/38 files, every byte consumed.

seq:
  - id: unk_f
    type: f4
    repeat: expr
    repeat-expr: 3
  - id: unk_u
    type: u4
    repeat: expr
    repeat-expr: 6
  - id: num_paths
    type: u4
  - id: paths
    type: strz
    size: 260
    repeat: expr
    repeat-expr: num_paths
    doc: authoring-machine directories, e.g. "D:\MissionD\Data\U01\maps"
