import pypdf
import argparse
import sys
import os

def protect_pdf(input_file, output_file, password):
    # Open the input PDF
    try:
        pdf_reader = pypdf.PdfReader(input_file)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_file}'")
        sys.exit(1)
    except pypdf.errors.PdfReadError:
        print(f"Error: Could not read '{input_file}'. Is it a valid PDF?")
        sys.exit(1)

    # Create a new PDF writer
    pdf_writer = pypdf.PdfWriter()

    # Copy all pages to writer
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    # Apply encryption [cite: 415, 429]
    pdf_writer.encrypt(password)

    # Save the new encrypted file [cite: 416, 430]
    try:
        with open(output_file, 'wb') as f:
            pdf_writer.write(f)
    except IOError:
        print(f"Error: Could not write to output file '{output_file}'")
        sys.exit(1)

    print(f"\nSuccess! '{input_file}' was encrypted.")
    print(f"Protected file saved as: '{output_file}'")

def main():
    # Setup command-line arguments [cite: 412, 422]
    parser = argparse.ArgumentParser(description="Add password protection to a PDF.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input PDF file.")
    parser.add_argument("-o", "--output", required=True, help="Path for the new protected PDF file.")
    parser.add_argument("-p", "--password", required=True, help="The password to set.")
    
    args = parser.parse_args()

    # Check if input and output are the same
    if os.path.abspath(args.input) == os.path.abspath(args.output):
        print("Error: Input and output files cannot be the same.")
        sys.exit(1)

    protect_pdf(args.input, args.output, args.password)

if __name__ == "__main__":
    main()