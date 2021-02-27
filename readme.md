# Luigi's Mansion Blender Toolkit

This project aims to make a majority of Luigi's Mansion model formats importable and exportable from blender and give more granular control
over models output. Please note that the imported models will not look perfect as there are some things the game does that blender does not do, such as wrap modes for textures.

Please note that the current version is **NOT v1.0**, it should not be considered a complete product.

## Current Release FAQ
    Q: Why is the exported bin model so big?
    A: Squish's texture compression is not as aggressive as nintendo's original and a lack of model optimization (tristrips, trifans, quads, etc).

    Q: I my exported bin model is missing parts in game
    A: Check your normals, again split normals are currently not supported so blender's auto generated normals are used.
    
    Q: Why does the imported model look blocky?
    A: Blender automatically regenerates normals and split normals have not yet been set up.
    
    Q: Why don't exported emboss maps work?
    A: Exporting emboss maps are currently not supported due to issues with blender's scripting api.

    Q: Why do my tristrip models have broken uvs?
    A: Tristrip export is currently experimental and unfinished.

    Q: Something else is broken and not listed here
    A: Use the issues tab above to report the bug or contact me through discord with a properly formatted bug report.


## Requirements
If you intend to use the experimental tristrip mode, clone pyffi into the `bin_writer` directory

This project requires modified python bindings for libsquish which you can find in [this repository](https://github.com/SpaceCats64/BinConv2).

**Prepackaged releases on the releases page will include these prebuilt.**

## Known Issues
- Some anm animations import incorrectly
- PTH exports lack smoothing data
- Bin exports with broken normals (TODO: add split normals)
- Some image formats unsupported

## Roadmap Progress
- [x] Bin Model Import/Export
- [x] ANM Animation Import/Export
- [x] CMN Import/Export
- [X] PTH Import/Export
- [ ] COL.MP Import/Export
- [ ] MDL Import/Export?
