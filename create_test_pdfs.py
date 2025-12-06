"""
Convert text files to PDF using reportlab
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def text_to_pdf(text_file, pdf_file):
    """Convert text file to PDF"""
    # Read text file
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    
    # Set font
    c.setFont("Courier", 10)
    
    # Starting position
    y = height - 1 * inch
    
    # Write content line by line
    for line in content.split('\n'):
        if y < 1 * inch:  # New page if needed
            c.showPage()
            c.setFont("Courier", 10)
            y = height - 1 * inch
        
        c.drawString(0.75 * inch, y, line[:100])  # Limit line length
        y -= 12  # Move down
    
    c.save()
    print(f"✅ Created: {pdf_file}")

# Convert all files
text_to_pdf('Test_Material/question.txt', 'Test_Material/question.pdf')
text_to_pdf('Test_Material/rubric.txt', 'Test_Material/rubric.pdf')
text_to_pdf('Test_Material/student_answer.txt', 'Test_Material/student_answer.pdf')

print("\n🎉 All PDFs created successfully!")
print("Files created:")
print("  - Test_Material/question.pdf")
print("  - Test_Material/rubric.pdf")
print("  - Test_Material/student_answer.pdf")
