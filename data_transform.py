import openai
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Load the scraped text
with open('scraped_data.txt', 'r', encoding='utf-8') as file:
    scraped_text = file.read()

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_and_summarize(text):
    # Use OpenAI's GPT-4o-mini model to extract and summarize the relevant information
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract and summarize the relevant information from the text. Format it properly."},
            {"role": "user", "content": text}
        ],
        max_tokens=960,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].message.content

def split_text(text, max_length):
    # Split the text into smaller chunks to avoid exceeding the maximum token limit
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []

    current_length = 0
    for paragraph in paragraphs:
        paragraph_length = len(paragraph.split())
        if current_length + paragraph_length > max_length:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_length = paragraph_length
        else:
            current_chunk.append(paragraph)
            current_length += paragraph_length

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks

# Split the text into smaller chunks
chunks = split_text(scraped_text, max_length=900)

summarized_chunks = []
for chunk in chunks:
    # Summarize each chunk using OpenAI
    summarized_chunks.append(extract_and_summarize(chunk))

# Combine the summarized chunks
summary = '\n\n'.join(summarized_chunks)

# Function to clean and parse the data sequentially
def clean_and_parse_data(text):
    data = []
    lines = text.split("\n")
    
    for line in lines:
        line = line.strip()
        if line.startswith("Title:") and " - Link:" in line:
            # Extract title and link
            match = re.match(r"Title: (.*) - Link: (.*)", line)
            if match:
                title, link = match.groups()
                data.append(f"[{title}]({link})")
        elif line.startswith("**") and line.endswith("**"):
            # Handle headings
            heading = line.strip("**").strip()
            data.append(f"**{heading}**")
        elif line:
            # Handle content and other entries
            data.append(f"{line}")
    
    return data

# Function to format parsed data into a list of Paragraph objects
def format_data_for_pdf(data):
    formatted_texts = []
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(name='Heading1Bold', fontName='Helvetica-Bold', fontSize=14, spaceAfter=12)
    normal_style = styles['BodyText']
    
    for item in data:
        if item.startswith('Title:') or item.startswith('['):  # Detect title/link
            formatted_texts.append(Paragraph(item, normal_style))
        elif item.startswith('**') and item.endswith('**'):
            # Format heading in bold
            heading_text = item.strip("**")
            formatted_texts.append(Paragraph(heading_text, heading_style))
        else:
            # Format content
            formatted_texts.append(Paragraph(item, normal_style))
        formatted_texts.append(Spacer(1, 12))  # Add space between sections
    
    return formatted_texts

# Parse the summarized data
parsed_data = clean_and_parse_data(summary)

# Format the parsed data into a list of Paragraph objects
formatted_texts = format_data_for_pdf(parsed_data)

# Create PDF using ReportLab
def create_pdf(paragraphs, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    doc.build(paragraphs)

# Ensure the output directory exists
output_dir = Path('qna_data')
output_dir.mkdir(exist_ok=True)

# Define the PDF output path
pdf_output_path = output_dir / 'Extracted_Information.pdf'
create_pdf(formatted_texts, str(pdf_output_path))

# Output paths
print("PDF saved at:", pdf_output_path)