import re
import pytesseract
from PIL import Image
import os
import pandas as pd

def extract_information_from_receipt(image_path):
    # Load the receipt image
    image = Image.open(image_path)

    # Apply OCR using Tesseract
    text = pytesseract.image_to_string(image)
    #print(text)
    # Extract store name
    refno = re.search(r'Reference number: (.+)', text)
    refno = refno.group(1) if refno else None
    if (refno == None and re.search(r'Accepted', text)):
    	refno = re.search(r'Accepted\n(\d+)', text)
    	if (refno != None):
    		refno = refno.group(1) 
    if (refno == None):
    	refno = re.search(r'Successful\n(\d+)', text)
    	if (refno != None):
    		refno = refno.group(1)
    	
    # Extract date
    date = re.search(r'(\d{2} .+2\d{3})', text)
    date = date.group(1) if date else None

    # Extract total amount
    total_amount = re.search(r'RM(\d+\.\d+)', text)
    total_amount = total_amount.group(1) if total_amount else None

    # Return extracted information
    return refno,date,total_amount
    
    
def extract_information_from_invoice(image_path):
    # Load the receipt image
    image = Image.open(image_path)

    # Apply OCR using Tesseract
    text = pytesseract.image_to_string(image)
    #print(text)
    # Extract store name
    invoiceno = re.search(r'Invoice : (.+)', text)
    invoiceno = invoiceno.group(1) if invoiceno else None
    if (invoiceno == None):
    	invoiceno = re.search(r'INVOICENO —(.+)', text)
    	if (invoiceno != None):
    		invoiceno = invoiceno.group(1)
    if (invoiceno == None):
    	invoiceno = re.search(r'INVOICE, (.+)', text)
    	if (invoiceno != None):
    		invoiceno = invoiceno.group(1)
    	
    # Extract date
    date = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", text)
    date = date.group(1) if date else None
    if (date == None):
    	date = re.search(r'(\d{2} .+2\d{3})', text)
    	if (invoiceno != None):
    		date = date.group(1) 
    if (date == None):
    	date = re.search(r'(\d{1} .+1\d{3})', text)
    	if (invoiceno != None):
    		date = date.group(1) 

    # Extract total amount
    pattern = r"(?<!\S)(\d{1,3}(?:,\d{3})*(?:\.\d+)?)(?!\S)"  # Match numbers with commas for thousands and decimals
    numbers = re.findall(pattern, text) 

    filtered_numbers = [float(number.replace(",", "")) for number in numbers if "," in number]  # Convert matched strings to floats and filter out numbers without commas

    if filtered_numbers:
    	max_number = max(filtered_numbers) 

    
    return invoiceno, date,max_number
 
    

folder_path = "invoice& receipt"  # Replace with the path to your folder
file_list = os.listdir(folder_path)
invoicetable=[]
receipttable=[]
for file_name in file_list:
    file_path = os.path.join(folder_path, file_name)
    print("checking " + file_path)
    # Load the receipt image
    image = Image.open(file_path)

    # Apply OCR using Tesseract
    textt = pytesseract.image_to_string(image)
    if(re.search(r'invoice', textt) or re.search(r'INVOICE', textt) or re.search(r'Invoice', textt) or re.search(r'lnvoice', textt)):
    	invoiceno, date, max_number = extract_information_from_invoice(file_path)
    	newlist = [invoiceno, date, max_number]
    	invoicetable.append(newlist)
    else : 
    	refno,date,total_amount = extract_information_from_receipt(file_path)
    	newlist = [refno,date,total_amount]
    	receipttable.append(newlist)


headers1 = ["Invoice No", "Date", "Amount"]
headers2 = ["Reference No", "Date", "Amount"]

df1 = pd.DataFrame(invoicetable, columns=headers1)
df2 = pd.DataFrame(receipttable, columns=headers2)

combined_df = pd.concat([df1, df2], axis=1)

print(df1)
print("\n\n")
print(df2)
