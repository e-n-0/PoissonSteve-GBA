# PoissonSteve GBA

A simple GBA animation demo that can run in an emulator or on real hardware.
Final TikTok video: https://vm.tiktok.com/ZNdN5abp7/

## Requirements

- [devkitPro](https://devkitpro.org/wiki/Getting_Started) with devkitARM installed
- Python 3.x with Pillow library (for the GIF converter tool)
- A Game Boy Advance emulator or flashcart for real hardware

## Setup

1. Install devkitPro following the instructions on their website
2. Make sure the DEVKITARM and DEVKITPRO environment variables are set
   ```bash
   export DEVKITPRO=/opt/devkitpro
   export DEVKITARM=/opt/devkitpro/devkitARM
   ```
3. Install Python dependencies: `pip install pillow`

## Building

```bash
# Compile the project
make

# Clean the build
make clean
```

The compiled ROM will be available as `PoissonSteve-GBA.gba` in the project root.

## Using the GIF Converter

The project includes a tool to convert GIF animations to GBA-compatible format:

```bash
# Basic usage
./tools/gif_converter.py your_animation.gif

# Specify output file and variable name
./tools/gif_converter.py your_animation.gif -o include/my_animation.h -n my_animation
```

After converting your GIF, include the generated header file in your project and update the main.c file to use the new animation data.

## Project Structure

- `source/`: Source code files
- `include/`: Header files
- `tools/`: Utility tools like the GIF converter

## Adding Your Own Animation

1. Convert your GIF animation using the converter tool
2. Copy the generated header file to the `include/` directory
3. Include the header file in your main.c
4. Create animation frames using the generated data
5. Initialize and use the animation in your main loop

## License

This project is open source and available under the MIT License. 
