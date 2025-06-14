import xml.etree.ElementTree as ET
# import requests  
from openpyxl import Workbook
# import time 
# import urllib.parse 

file = "official-cpe-dictionary_v2.3.xml"
# api_key = ""  

# Parse local XML file
with open(file, "rb") as f:
    xml_data = f.read()
root = ET.fromstring(xml_data)

# Auto-detect namespaces
ns = {}
for event, (prefix, uri) in ET.iterparse(file, events=['start-ns']):
    if prefix == "":
        ns["default"] = uri
    else:
        ns[prefix] = uri
ns["xml"] = "http://www.w3.org/XML/1998/namespace"

# Initialize Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "CPE Entries"
ws.append([
    "CPE Title", "CPE 22 URI", "CPE 23 URI",
    "Reference Links", "CPE 22 Deprecated", "CPE 23 Deprecation Date"
])

# API call removed 
# def fetch_nvd_deprecation_date(cpe_uri):
#     if not cpe_uri:
#         return None
#     encoded_uri = urllib.parse.quote(cpe_uri, safe=':')
#     url = f"https://services.nvd.nist.gov/rest/json/cpes/2.0?cpeName={encoded_uri}"
#     headers = {'apiKey': api_key}
#     try:
#         res = requests.get(url, headers=headers)
#         res.raise_for_status()
#         data = res.json()
#         items = data.get('products', [])
#         for item in items:
#             cpe_obj = item.get("cpe", {})
#             if cpe_obj.get("deprecated"):
#                 return cpe_obj.get("deprecationDate", "Deprecated (no date)")
#     except Exception as e:
#         print(f"API error for {cpe_uri}: {e}")
#     return None

# Extract each CPE item
for item in root.findall('default:cpe-item', ns):
    cpe_22_uri = item.get('name')
    cpe_22_deprecated = "true" if item.get('deprecated', '').lower() == "true" else None

    title_elem = item.find('default:title[@xml:lang="en-US"]', ns)
    cpe_title = title_elem.text if title_elem is not None else None

    cpe_23_elem = item.find('cpe-23:cpe23-item', ns)
    cpe_23_uri = cpe_23_elem.get('name') if cpe_23_elem is not None else None

    references = [
        ref.get('href') for ref in item.findall('default:references/default:reference', ns)
    ]
    references_str = ", ".join(references)

    # No API lookup, so leave dep23 blank
    dep23 = None

    # Append row to Excel
    ws.append([
        cpe_title, cpe_22_uri, cpe_23_uri,
        references_str, cpe_22_deprecated, dep23
    ])

# Save to Excel
wb.save("cpe_data.xlsx")
print("Exported CPE data to cpe_data.xlsx")
