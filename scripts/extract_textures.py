#!/usr/bin/env python3
import os
import base64
from pygltflib import GLTF2

def extract_textures_from_glb(glb_file, output_dir):
    """Extract texture images from a GLB file to the specified output directory."""
    print(f"Loading GLB file: {glb_file}")
    gltf = GLTF2.load(glb_file)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Check if there are embedded textures (binary buffers)
    if not hasattr(gltf, 'buffers') or not gltf.buffers:
        print("No buffers found in the GLB file.")
        return
    
    # Process all images
    if not hasattr(gltf, 'images') or not gltf.images:
        print("No images found in the GLB file.")
        return
    
    print(f"Found {len(gltf.images)} images in the GLB file.")
    
    for i, image in enumerate(gltf.images):
        try:
            # Get the image data
            if hasattr(image, 'uri') and image.uri:
                # Handle data URIs
                if image.uri.startswith('data:'):
                    content_type, b64data = image.uri.split(',', 1)
                    img_data = base64.b64decode(b64data)
                    extension = content_type.split('/')[-1].split(';')[0]
                    filename = f"texture_{i}.{extension}"
                    with open(os.path.join(output_dir, filename), 'wb') as f:
                        f.write(img_data)
                    print(f"Extracted {filename} from data URI")
                    
                # Handle file URIs
                else:
                    filename = image.uri
                    print(f"Image {i} references external file: {filename}")
                    
            # Handle buffer views
            elif hasattr(image, 'bufferView') and image.bufferView is not None:
                buffer_view = gltf.bufferViews[image.bufferView]
                buffer = gltf.buffers[buffer_view.buffer]
                
                # Get the binary data from the gltf object
                # The binary_blob is a bytes object, not a method
                buffer_data = gltf.get_data_from_buffer_uri(buffer.uri) if hasattr(buffer, 'uri') and buffer.uri else gltf.binary_blob
                
                if buffer_data is None:
                    print(f"Could not get binary data for image {i}")
                    continue
                
                # Extract the image data from the buffer
                start = buffer_view.byteOffset if hasattr(buffer_view, 'byteOffset') else 0
                length = buffer_view.byteLength
                end = start + length
                img_data = buffer_data[start:end]
                
                # Determine the file extension based on mimeType
                extension = "bin"
                if hasattr(image, 'mimeType'):
                    if image.mimeType == "image/jpeg":
                        extension = "jpg"
                    elif image.mimeType == "image/png":
                        extension = "png"
                    elif image.mimeType == "image/webp":
                        extension = "webp"
                
                # Write the image file
                filename = f"texture_{i}.{extension}"
                with open(os.path.join(output_dir, filename), 'wb') as f:
                    f.write(img_data)
                print(f"Extracted {filename} from buffer view {image.bufferView}")
        except Exception as e:
            print(f"Error extracting image {i}: {e}")
    
    print("\nTexture extraction complete. Check the extracted_textures directory.")

if __name__ == "__main__":
    glb_file = "ValeroRefinery.glb"
    output_dir = "extracted_textures"
    
    extract_textures_from_glb(glb_file, output_dir) 