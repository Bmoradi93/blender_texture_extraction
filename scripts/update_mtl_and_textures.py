#!/usr/bin/env python3
import os
import re
import shutil

def main():
    """
    This script:
    1. Extracts material names from ValeroRefinery.mtl
    2. Renames texture files in extracted_textures to match material names
    3. Updates the MTL file to include map_Kd references
    """
    # Paths
    mtl_file = "ValeroRefinery.mtl"
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
    # Material_0.1000 should map to Image_0.1000.png
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