# 3D Model Texture Extraction and MTL File Processing

This repository contains tools and scripts for extracting textures from Blender files and updating MTL files to include proper texture references for OBJ models.

## Overview

The process extracts embedded textures from Blender (.blend) files and creates properly formatted MTL files that reference these textures, enabling 3D models to display with their original textures when loaded in any OBJ-compatible 3D viewer.

## Prerequisites

- **Blender** (for texture extraction)
- **Python 3** with standard libraries
- **Linux/Unix environment** (tested on Ubuntu)

### Installation

```bash
# Install Blender (Ubuntu/Debian)
sudo apt update
sudo apt install blender

# Verify installation
blender --version
```

## Scripts Documentation

### 1. Texture Extraction Script (`extract_textures_blender.py`)

Extracts embedded textures from Blender files using Blender's Python API.

```python
#!/usr/bin/env python3
import sys
import os
import bpy

def extract_textures():
    # Directory to save extracted textures
    output_dir = os.path.join(os.path.dirname(bpy.data.filepath), "extracted_textures")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing file: {bpy.data.filepath}")
    print(f"Saving textures to: {output_dir}")
    
    # Track the number of textures extracted
    texture_count = 0
    
    # Extract textures from materials
    for material in bpy.data.materials:
        print(f"Processing material: {material.name}")
        
        # Skip materials without nodes
        if not material.use_nodes:
            continue
            
        # Find texture nodes in the material
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                image = node.image
                
                # Skip if image has no packed data
                if not image.packed_file:
                    continue
                
                # Generate output filename
                texture_filename = f"{image.name}.png"
                texture_path = os.path.join(output_dir, texture_filename)
                
                # Save the texture
                image.save_render(texture_path)
                print(f"  Saving texture: {texture_filename}")
                texture_count += 1
    
    print(f"Extraction complete. {texture_count} textures extracted to {output_dir}")
    
    # Check for existing MTL files and show texture references
    mtl_files = [f for f in os.listdir(os.path.dirname(bpy.data.filepath)) if f.endswith('.mtl')]
    for mtl_file in mtl_files:
        mtl_path = os.path.join(os.path.dirname(bpy.data.filepath), mtl_file)
        print(f"\nChecking MTL file: {mtl_file}")
        
        with open(mtl_path, 'r') as f:
            map_kd_lines = [line.strip() for line in f if line.strip().startswith('map_Kd')]
            if map_kd_lines:
                print(f"Found {len(map_kd_lines)} texture references in MTL file:")
                for line in map_kd_lines[:10]:  # Show first 10
                    print(f"  {line}")
                if len(map_kd_lines) > 10:
                    print(f"  ... and {len(map_kd_lines) - 10} more")
            else:
                print("No texture references found in MTL file.")

if __name__ == "__main__":
    extract_textures()
```

**Usage:**
```bash
blender -b YourModel.blend --python extract_textures_blender.py
```

### 2. MTL Processing Script (`update_mtl_and_textures.py`)

Updates MTL files to include texture references and renames textures to match material names.

```python
#!/usr/bin/env python3
import os
import re
import shutil

def main():
    """
    This script:
    1. Extracts material names from MTL file
    2. Renames texture files in extracted_textures to match material names
    3. Updates the MTL file to include map_Kd references
    """
    # Paths (modify these for your specific model)
    mtl_file = "YourModel.mtl"  # Change this to your MTL file
    texture_dir = "extracted_textures"
    
    # Get all material names from MTL file
    print("Reading materials from MTL file...")
    materials = []
    with open(mtl_file, 'r') as f:
        for line in f:
            if line.startswith("newmtl"):
                material_name = line.strip().split()[1]
                materials.append(material_name)
    
    print(f"Found {len(materials)} materials in MTL file")
    
    # Get all textures
    textures = [f for f in os.listdir(texture_dir) if f.endswith(".png")]
    textures.sort()
    print(f"Found {len(textures)} textures in {texture_dir}")
    
    # Create a mapping between materials and textures
    material_texture_map = {}
    
    for material in materials:
        # Extract the number from material name (e.g., "Material_0.1000" -> "0.1000")
        match = re.search(r'Material_(.+)', material)
        if match:
            material_suffix = match.group(1)
            # Look for corresponding texture file
            expected_texture = f"Image_{material_suffix}.png"
            if expected_texture in textures:
                material_texture_map[material] = expected_texture
                print(f"Mapped {material} -> {expected_texture}")
            else:
                print(f"Warning: No texture found for material {material} (expected {expected_texture})")
    
    print(f"Successfully mapped {len(material_texture_map)} materials to textures")
    
    # Create renamed_textures directory
    renamed_dir = "renamed_textures"
    if os.path.exists(renamed_dir):
        shutil.rmtree(renamed_dir)
    os.makedirs(renamed_dir)
    
    # Rename and copy textures
    print("Renaming and copying textures...")
    for material, original_texture in material_texture_map.items():
        src_path = os.path.join(texture_dir, original_texture)
        new_texture_name = f"{material}.png"
        dst_path = os.path.join(renamed_dir, new_texture_name)
        
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"Copied {original_texture} -> {new_texture_name}")
        else:
            print(f"Warning: Source texture not found: {src_path}")
    
    # Update MTL file
    print("Updating MTL file with texture references...")
    updated_mtl_file = mtl_file.replace(".mtl", "_updated.mtl")
    
    with open(mtl_file, 'r') as infile, open(updated_mtl_file, 'w') as outfile:
        current_material = None
        for line in infile:
            outfile.write(line)
            
            if line.startswith("newmtl"):
                current_material = line.strip().split()[1]
            elif line.startswith("illum") and current_material in material_texture_map:
                # Add map_Kd reference after illum line
                texture_name = f"{current_material}.png"
                outfile.write(f"map_Kd {texture_name}\n")
    
    print(f"Updated MTL file saved as: {updated_mtl_file}")
    print(f"Renamed textures saved in: {renamed_dir}")
    print("Process completed successfully!")

if __name__ == "__main__":
    main()
```

### 3. Texture Organization Script (`copy_textures.py`)

Copies renamed textures to the main directory for easy access.

```python
#!/usr/bin/env python3
import os
import shutil

def main():
    """Copy all renamed textures to the main directory."""
    source_dir = "renamed_textures"
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return
    
    # Get list of texture files
    texture_files = [f for f in os.listdir(source_dir) if f.endswith(".png")]
    print(f"Found {len(texture_files)} texture files to copy.")
    
    # Copy each file
    for filename in texture_files:
        src_path = os.path.join(source_dir, filename)
        dst_path = filename  # Copy to current directory
        
        shutil.copy2(src_path, dst_path)
        print(f"Copied {filename}")
    
    print(f"\nDone! All texture files copied to the main directory.")
    print("Now you can use the updated MTL file with your OBJ model.")
    print("The OBJ file will properly display textures when loaded in a 3D viewer.")

if __name__ == "__main__":
    main()
```

## Complete Workflow

### Step 1: Extract Textures from Blender File

```bash
# Navigate to your project directory
cd /path/to/your/project

# Extract textures from Blender file
blender -b YourModel.blend --python extract_textures_blender.py
```

**Expected Output:**
- Creates `extracted_textures/` directory
- Extracts all embedded textures as PNG files
- Reports texture count and material information

### Step 2: Update MTL File and Rename Textures

```bash
# Modify the script to use your specific MTL file name
# Edit update_mtl_and_textures.py and change mtl_file variable

# Run the processing script
python3 update_mtl_and_textures.py
```

**Expected Output:**
- Creates `renamed_textures/` directory
- Maps materials to textures
- Generates `YourModel_updated.mtl` with texture references

### Step 3: Copy Textures to Main Directory

```bash
# Copy all renamed textures to main directory
python3 copy_textures.py
```

### Step 4: Finalize and Organize

```bash
# Replace original MTL file with updated version
mv YourModel_updated.mtl YourModel.mtl

# Create organized model folder
mkdir YourModel_Complete
mv YourModel.obj YourModel.mtl Material_*.png YourModel_Complete/

# Clean up intermediate directories
rm -rf extracted_textures renamed_textures
```

## Example Results

### Before Processing
```
YourModel.mtl:
newmtl Material_0.1000
Ns 360.000000
Ka 1.000000 1.000000 1.000000
Kd 0.800000 0.800000 0.800000
Ks 0.500000 0.500000 0.500000
Ke 0.000000 0.000000 0.000000
Ni 1.000000
d 1.000000
illum 2
```

### After Processing
```
YourModel.mtl:
newmtl Material_0.1000
Ns 360.000000
Ka 1.000000 1.000000 1.000000
Kd 0.800000 0.800000 0.800000
Ks 0.500000 0.500000 0.500000
Ke 0.000000 0.000000 0.000000
Ni 1.000000
d 1.000000
illum 2
map_Kd Material_0.1000.png
```

## Troubleshooting

### Common Issues

1. **Blender command not found**
   ```bash
   # Install Blender
   sudo apt install blender
   # Or use snap
   sudo snap install blender --classic
   ```

2. **No textures extracted**
   - Ensure the Blender file contains embedded textures
   - Check that materials use Image Texture nodes
   - Verify the Blender file is not corrupted

3. **Material/texture mismatch**
   - Check material naming patterns in MTL file
   - Verify texture file naming conventions
   - Adjust regex patterns in the script if needed

4. **Permission errors**
   ```bash
   # Ensure write permissions
   chmod +w .
   chmod +x *.py
   ```

### File Size Considerations

- **Large models:** The process works with models containing thousands of textures
- **Memory usage:** Blender requires sufficient RAM for large files
- **Disk space:** Ensure adequate space for extracted textures (can be several GB)

## Script Customization

### Adapting for Different Material Naming Patterns

If your materials follow a different naming convention, modify the regex pattern in `update_mtl_and_textures.py`:

```python
# For materials named "Mat_001", "Mat_002", etc.
match = re.search(r'Mat_(\d+)', material)
if match:
    material_number = match.group(1)
    expected_texture = f"Texture_{material_number}.png"

# For materials named "Material.001", "Material.002", etc.
match = re.search(r'Material\.(\d+)', material)
if match:
    material_number = match.group(1)
    expected_texture = f"Image.{material_number}.png"
```

### Adding Different Texture Types

To extract and reference additional texture types, modify the scripts:

```python
# In extract_textures_blender.py, add more texture types
texture_types = ['TEX_IMAGE', 'TEX_ENVIRONMENT', 'TEX_NOISE']

# In update_mtl_and_textures.py, add more map types
if current_material in material_texture_map:
    texture_name = f"{current_material}.png"
    outfile.write(f"map_Kd {texture_name}\n")    # Diffuse
    outfile.write(f"map_Ks {texture_name}\n")    # Specular
    outfile.write(f"map_Bump {texture_name}\n")  # Normal/Bump
```

## Contributing

Feel free to submit issues and enhancement requests. When contributing:

1. Test with your specific 3D models
2. Document any modifications needed for different file formats
3. Include example files when possible
4. Update this README with new features or changes

## License

This project is released under the MIT License. Feel free to use and modify for your projects.

## Acknowledgments

- Blender Foundation for the excellent 3D software and Python API
- OBJ/MTL format specifications for enabling cross-platform 3D model sharing
- The 3D modeling community for feedback and testing

---

**Note:** This process was developed and tested with industrial 3D models containing complex material setups. It should work with most Blender files that have embedded textures and properly configured material nodes.