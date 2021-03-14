# Luigi's Mansion Blender Toolkit

This project aims to make a majority of Luigi's Mansion model formats importable and exportable from blender and give more granular control
over models output. Please note that the imported models will not look perfect as there are some things the game does that blender does not do, such as wrap modes for textures.

## Current Release FAQ
Q: Why does the export take so long?
A: If your textures are very large they may take some time to compress.

Q: I my exported bin model is missing parts in game
A: Check your normals and check your materials, these are the two biggest killers.

Q: Why don't emboss maps work?
A: Exporting emboss maps are currently not supported due to issues with blender's scripting api.

Q: Something else is broken and not listed here
A: Use the issues tab above to report the bug or contact me through discord with a properly formatted bug report.


## Requirements

This project requires modified python bindings for libsquish which you can find in [this repository](https://github.com/SpaceCats64/BinConv2).

**Prepackaged releases on the releases page will include these prebuilt.**

## Known Issues
- Some anm animations import incorrectly
- PTH exports lack smoothing data

## Roadmap Progress
- [x] Bin Model Import/Export
- [x] ANM Animation Import/Export
- [x] CMN Import/Export
- [X] PTH Import/Export
- [ ] COL.MP Import/Export
- [ ] MDL Import/Export?
