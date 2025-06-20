import xml.etree.ElementTree as ET
from openpyxl import Workbook

file = "test_input.xml"  # Your local XML file

# Parse the XML file
tree = ET.parse(file)
root = tree.getroot()

# Auto-detect namespaces
ns = {}
for event, (prefix, uri) in ET.iterparse(file, events=['start-ns']):
    ns[prefix if prefix else "default"] = uri
ns["xml"] = "http://www.w3.org/XML/1998/namespace"

# Initialize Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "CPE Entries"
ws.append([
    "CPE Title", "CPE 22 URI", "CPE 23 URI",
    "Reference Links", "CPE 22 Deprecated", "CPE 23 Deprecation Date"
])

# Extract and process each <cpe-item>
for item in root.findall('default:cpe-item', ns):
    cpe_22_uri = item.get('name')
    cpe_22_deprecated = item.get('deprecated', '').lower() == "true"

    title_elem = item.find('default:title[@xml:lang="en-US"]', ns)
    cpe_title = title_elem.text if title_elem is not None else None

    cpe_23_elem = item.find('cpe-23:cpe23-item', ns)
    cpe_23_uri = cpe_23_elem.get('name') if cpe_23_elem is not None else None

    # Extract CPE 23 deprecation date if available
    dep_elem = cpe_23_elem.find('cpe-23:deprecation', ns) if cpe_23_elem is not None else None
    cpe_23_deprecation_date = dep_elem.get('date') if dep_elem is not None else None

    references = [
        ref.get('href') for ref in item.findall('default:references/default:reference', ns)
    ]
    references_str = ", ".join(references)

    ws.append([
        cpe_title, cpe_22_uri, cpe_23_uri,
        references_str,
        "true" if cpe_22_deprecated else "",
        cpe_23_deprecation_date or ""
    ])

wb.save("cpe_data.xlsx")
print("Step 1 complete: Exported to cpe_data.xlsx")
