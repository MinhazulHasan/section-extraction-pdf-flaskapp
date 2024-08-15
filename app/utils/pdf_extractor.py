from pdfminer.high_level import extract_text
import re
import io


def clean_extracted_text(text: str) -> str:
    # Remove page numbers or similar structured text
    pattern = r'^.*[Pp]age\s*-\s*\d+\s*of\s*\d+.*$\n?'
    text = re.sub(pattern, '', text, flags=re.MULTILINE)

    # Remove extra newlines (including those with spaces between them)
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    
    # Replace tabs with single space
    text = re.sub(r'\t+', ' ', text)
    
    # Additional cleanup
    text = re.sub(r' +', ' ', text)  # Remove multiple spaces
    text = text.strip()

    pattern = r'(?:^|\n)1\s*\n2\s*\n3\s*\n4\s*\n5\s*\n6\s*\n7\s*\n(?:.*\n)*?.*?back less.'
    text = re.sub(pattern, '', text, flags=re.MULTILINE | re.DOTALL)

    return text



def extract_pdf_sections(pdf_contents: bytes) -> dict:
    # Extract text from the PDF
    pdf_stream = io.BytesIO(pdf_contents)
    extracted_text = extract_text(pdf_stream)
    extracted_text = clean_extracted_text(extracted_text)

    """
        Define patterns for each section using regular expressions
        \s* matches zero or more spaces 
        \s*(.*?)\s* matches any text between two sections
    """
    patterns = {
        "PRIIPSKIDTypeOption": r"Type:\s*(.*?)\s*(?=\bTerm\b)",
        "PRIIPsKIDTerm": r"Term:\s*(.*?)\s*(?=Objective[s]?:)",
        "PRIIPsKIDObjective": r"Objective[s]?:\s*(.*?)\s*(?=\b(Intended investor|Dealing Frequency|Fund Currency|Investment Policy)\b|\bWhat are the risks\b)",
        "PRIIPsKIDTargetMarket": r"Intended\s*(?:investor\s*|investors\s*|Investor\s*|Investors\s*|Retail\s*Investor\s*):\s*(.*?)\s*(?=\b(What are the risks|Purchase and Repurchase|Risk Indicator)\b)",
        "PRIIPsKIDOtherRisks": r"Risk Indicator\s*[:]?\s*(.*?)\s*(?=\bPerformance Scenarios\b)",
        "PRIIPsKIDUnableToPayOut": r"What happens if.*?\s*(.*?)\s*(?=\bWhat are the costs\b)",
        "PRIIPsKIDTakeMoneyOutEarly": r"How long should I hold it and can I take money out early\?\s*(.*?)\s*(?=\bHow can I complain\b)",
        "PRIIPsKIDComplaints": r"How can I complain\?\s*(.*?)\s*(?=\bOther relevant information\b)",
        "PRIIPsKIDOtherInfoEU": r"Other relevant information\s*(.*)"
    }

    # Extract the sections
    extracted_sections = {section: re.search(pattern, extracted_text, re.DOTALL).group(1).strip()
                          if re.search(pattern, extracted_text, re.DOTALL) else ""
                          for section, pattern in patterns.items()}

    return extracted_sections
