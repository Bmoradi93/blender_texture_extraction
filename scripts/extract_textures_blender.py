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
                
                # Skip already processed images
                if not image.packed_file:
                    print(f"  Image {image.name} is not packed, skipping")
                    continue
                
                # Generate a filename for the texture
                texture_filename = f"{image.name}.png"
                texture_path = os.path.join(output_dir, texture_filename)
                
                # Save the image if it doesn't already exist
                if not os.path.exists(texture_path):
                    print(f"  Saving texture: {texture_filename}")
                    image.save_render(texture_path)
                    texture_count += 1
    
    print(f"Extraction complete. {texture_count} textures extracted to {output_dir}")

# Call the function
extract_textures()

# Also check MTL file for texture references
mtl_filename = "ValeroWA02C.mtl"
mtl_path = os.path.join(os.path.dirname(bpy.data.filepath), mtl_filename)

if os.path.exists(mtl_path):
    print(f"\nChecking MTL file: {mtl_filename}")
    
    texture_refs = []
    with open(mtl_path, 'r') as f:
        for line in f:
            if line.startswith("map_"):
                texture_refs.append(line.strip())
    
    if texture_refs:
        print(f"Found {len(texture_refs)} texture references in MTL file:")
        for ref in texture_refs:
            print(f"  {ref}")
    else:
        print("No texture references found in MTL file")
else:
    print(f"\nMTL file not found: {mtl_filename}") 