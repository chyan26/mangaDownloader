import os
import sys
import argparse
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

def main():
    """Main function to handle command-line arguments and execute the PDF conversion."""
    parser = argparse.ArgumentParser(
        description="Convert JPEG/PNG images in subdirectories to PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i ./manga/圣斗士星矢 -o ./output
  %(prog)s --input-dir ./images --output-dir ./pdfs
  %(prog)s -i ./manga/圣斗士星矢  # Output to same directory as input
        """
    )
    
    parser.add_argument(
        '-i', '--input-dir',
        required=True,
        help='Input directory containing subdirectories with images'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory for PDF files (default: same as input directory)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without actually creating PDFs'
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(args.input_dir):
        print(f"Error: '{args.input_dir}' is not a directory.")
        sys.exit(1)
    
    # Set output directory (default to input directory if not specified)
    output_dir = args.output_dir if args.output_dir else args.input_dir
    
    # Convert relative paths to absolute paths
    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(output_dir)
    
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    if args.dry_run:
        print("\n--- DRY RUN MODE ---")
        preview_conversion(input_dir, output_dir)
    else:
        print("\nStarting PDF conversion...")
        jpeg_to_pdf(input_dir, output_dir)
        print("Conversion completed!")


def preview_conversion(input_dir, output_dir):
    """Preview what would be converted without actually doing the conversion."""
    print(f"\nPreviewing conversion from '{input_dir}' to '{output_dir}':")
    
    subdirs_found = False
    for subdir in os.listdir(input_dir):
        subdir_path = os.path.join(input_dir, subdir)
        
        if os.path.isdir(subdir_path):
            subdirs_found = True
            jpeg_files = sorted([f for f in os.listdir(subdir_path) 
                               if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            
            if jpeg_files:
                pdf_path = os.path.join(output_dir, f"{subdir}.pdf")
                print(f"  Would create: {pdf_path}")
                print(f"    From {len(jpeg_files)} images in {subdir_path}")
            else:
                print(f"  Skipping: {subdir_path} (no image files found)")
    
    if not subdirs_found:
        print("  No subdirectories found in input directory.")


if __name__ == "__main__":
    main()
