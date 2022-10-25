# Luigi's Mansion Blender Toolkit

This project aims to make a majority of Luigi's Mansion model formats importable and exportable from blender and give more granular control
over model generation.

### Please be aware this addon is currently not compatible with Blender 3.0+

## Supported Formats
- Bin Room/Furniture Models
- ANM Animation for Furniture Models
- Camera Animation Files
- Path Animation Files

## Requirements

This project requires modified python bindings for libsquish which you can find in [this repository](https://github.com/SpaceCats64/BinConv2).

**Prepackaged releases on the releases page will include these prebuilt.**

## Known Issues
- Some furniture animations import improperly
- Path animations lack easing data
