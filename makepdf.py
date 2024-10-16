import os
from PIL import Image

def jpeg_to_pdf(input_dir, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Traverse through each subdirectory in the main directory
    for subdir in os.listdir(input_dir):
        subdir_path = os.path.join(input_dir, subdir)
        
        # Only process directories
        if os.path.isdir(subdir_path):
            images = []
            # Sort the JPEG files alphabetically
            jpeg_files = sorted([f for f in os.listdir(subdir_path) if f.lower().endswith(('.jpg', '.jpeg','png'))])
            
            for filename in jpeg_files:
                img_path = os.path.join(subdir_path, filename)
                img = Image.open(img_path)
                img = img.convert('RGB')  # Convert to RGB to handle any transparency issues
                images.append(img)
            
            if images:
                pdf_path = os.path.join(output_dir, f"{subdir}.pdf")
                # Save all images as a PDF; the first image is the base, the rest are appended
                images[0].save(pdf_path, save_all=True, append_images=images[1:])
                print(f"PDF created for {subdir} at {pdf_path}")
            else:
                print(f"No JPEG files found in {subdir_path}")

# Example usage
input_directory = "/Users/chyan/manhuagui-downloader/manga/Test"
output_directory = "/Users/chyan/manhuagui-downloader/manga/"
jpeg_to_pdf(input_directory, output_directory)
