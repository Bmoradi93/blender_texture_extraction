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
    
    print("\nDone! All texture files copied to the main directory.")
    print("\nNow you can use the ValeroWA02C_updated.mtl file (or rename it to ValeroWA02C.mtl)")
    print("The OBJ file will now properly display textures when loaded in a 3D viewer.")

if __name__ == "__main__":
    main() 