from pdfminer.high_level import extract_text
import pdfplumber
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
    pdf_stream = io.BytesIO(pdf_contents)
    print("Extracting sections from the PDF...")
    # Extract text from the PDF using pdfminer
    extracted_text_pdfminer = extract_text(pdf_stream)
    extracted_text_pdfminer = extracted_text_pdfminer.encode('utf-8', errors='ignore').decode('utf-8')
    extracted_text_pdfminer = clean_extracted_text(extracted_text_pdfminer)

    # Extract text from the PDF using pdfplumber
    extracted_text_pdfplumber = ""
    with pdfplumber.open(pdf_stream) as pdf:
        for page in pdf.pages:
            extracted_text_pdfplumber += page.extract_text() + "\n"

    extracted_text_pdfplumber = extracted_text_pdfplumber.encode('utf-8', errors='ignore').decode('utf-8')
    ectracted_text_pdfplumber = clean_extracted_text(extracted_text_pdfplumber)

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

    # Extract the sections separately
    extracted_sections_type_option = {}

    if "PRIIPSKIDTypeOption" in patterns:
        extracted_sections_type_option["PRIIPSKIDTypeOption"] = (
            re.search(patterns["PRIIPSKIDTypeOption"], extracted_text_pdfminer, re.DOTALL).group(1).strip()
            if re.search(patterns["PRIIPSKIDTypeOption"], extracted_text_pdfminer, re.DOTALL) else ""
        )

    extracted_sections_term = {}
    if "PRIIPsKIDTerm" in patterns:
        extracted_sections_term["PRIIPsKIDTerm"] = (
            re.search(patterns["PRIIPsKIDTerm"], extracted_text_pdfminer, re.DOTALL).group(1).strip()
            if re.search(patterns["PRIIPsKIDTerm"], extracted_text_pdfminer, re.DOTALL) else ""
        )

    extracted_sections_objective = {}
    if "PRIIPsKIDObjective" in patterns:
        extracted_sections_objective["PRIIPsKIDObjective"] = (
            re.search(patterns["PRIIPsKIDObjective"], extracted_text_pdfminer, re.DOTALL).group(1).strip()
            if re.search(patterns["PRIIPsKIDObjective"], extracted_text_pdfminer, re.DOTALL) else ""
        )

    extracted_sections_target_market = {}
    if "PRIIPsKIDTargetMarket" in patterns:
        extracted_sections_target_market["PRIIPsKIDTargetMarket"] = (
            re.search(patterns["PRIIPsKIDTargetMarket"], extracted_text_pdfminer, re.DOTALL).group(1).strip()
            if re.search(patterns["PRIIPsKIDTargetMarket"], extracted_text_pdfminer, re.DOTALL) else ""
        )

    extracted_sections_other_risks = {}
    if "PRIIPsKIDOtherRisks" in patterns:
        extracted_sections_other_risks["PRIIPsKIDOtherRisks"] = (
            re.search(patterns["PRIIPsKIDOtherRisks"], extracted_text_pdfminer, re.DOTALL).group(1).strip()
            if re.search(patterns["PRIIPsKIDOtherRisks"], extracted_text_pdfminer, re.DOTALL) else ""
        )
        extracted_sections_other_risks["PRIIPsKIDOtherRisks"] = extracted_sections_other_risks["PRIIPsKIDOtherRisks"].replace("!", "")

    extracted_sections_unable_to_pay_out = {}
    if "PRIIPsKIDUnableToPayOut" in patterns:
        extracted_sections_unable_to_pay_out["PRIIPsKIDUnableToPayOut"] = (
            re.search(patterns["PRIIPsKIDUnableToPayOut"], extracted_text_pdfminer, re.DOTALL).group(1).strip()
            if re.search(patterns["PRIIPsKIDUnableToPayOut"], extracted_text_pdfminer, re.DOTALL) else ""
        )

    extracted_sections_take_money_out_early = {}
    if "PRIIPsKIDTakeMoneyOutEarly" in patterns:
        extracted_sections_take_money_out_early["PRIIPsKIDTakeMoneyOutEarly"] = (
            re.search(patterns["PRIIPsKIDTakeMoneyOutEarly"], extracted_text_pdfminer, re.DOTALL).group(1).strip()
            if re.search(patterns["PRIIPsKIDTakeMoneyOutEarly"], extracted_text_pdfminer, re.DOTALL) else ""
        )

    extracted_sections_complaints = {}
    if "PRIIPsKIDComplaints" in patterns:
        extracted_sections_complaints["PRIIPsKIDComplaints"] = (
            re.search(patterns["PRIIPsKIDComplaints"], ectracted_text_pdfplumber, re.DOTALL).group(1).strip()
            if re.search(patterns["PRIIPsKIDComplaints"], ectracted_text_pdfplumber, re.DOTALL) else ""
        )

    extracted_sections_other_info_eu = {}
    if "PRIIPsKIDOtherInfoEU" in patterns:
        extracted_sections_other_info_eu["PRIIPsKIDOtherInfoEU"] = (
            re.search(patterns["PRIIPsKIDOtherInfoEU"], extracted_text_pdfminer, re.DOTALL).group(1).strip()
            if re.search(patterns["PRIIPsKIDOtherInfoEU"], extracted_text_pdfminer, re.DOTALL) else ""
        )

    # Merge the sections
    merged_sections = {
        **extracted_sections_type_option,
        **extracted_sections_term,
        **extracted_sections_objective,
        **extracted_sections_target_market,
        **extracted_sections_other_risks,
        **extracted_sections_unable_to_pay_out,
        **extracted_sections_take_money_out_early,
        **extracted_sections_complaints,
        **extracted_sections_other_info_eu,
    }

    return merged_sections
