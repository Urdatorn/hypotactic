import os
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Function to extract tags from BeautifulSoup or ElementTree
def extract_tags(soup_or_element):
    if isinstance(soup_or_element, BeautifulSoup):
        return {tag.name for tag in soup_or_element.find_all(True)}
    elif isinstance(soup_or_element, ET.Element):
        return {elem.tag.split("}")[-1] for elem in soup_or_element.iter()}

# Function to pretty-print XML
def pretty_print_xml(xml_element):
    rough_string = ET.tostring(xml_element, encoding="unicode", method="xml")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# Function to create TEI XML
def create_tei_xml(html_file):
    # Extract base name for output file and title
    base_name = os.path.splitext(os.path.basename(html_file))[0]

    # Parse the HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Extract book-level metadata from the first poem
    first_poem = soup.find("div", class_="poem")
    author = first_poem.get("data-author", "").strip() if first_poem else ""
    work = first_poem.get("data-work", "").strip() if first_poem else ""

    # Default to file name if metadata is missing
    tei_title = f"{author}, {work}".strip(", ") if author or work else base_name

    # TEI root element
    tei = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")

    # TEI Header
    teiHeader = ET.SubElement(tei, "teiHeader")
    fileDesc = ET.SubElement(teiHeader, "fileDesc")
    titleStmt = ET.SubElement(fileDesc, "titleStmt")
    ET.SubElement(titleStmt, "title").text = tei_title

    # Create book-level metadata header
    if first_poem:
        book_div = ET.SubElement(tei, "div", {"type": "book"})
        metadata_fields = {
            "global_class": " ".join(first_poem.get("class", [])),
            "metre": first_poem.get("data-metre", ""),
            "author": author,
            "work": work,
            "book": first_poem.get("data-book", "")
        }

        # Fill book-level metadata
        for key, value in metadata_fields.items():
            ET.SubElement(book_div, key).text = value.strip() if value else ""

    # Text body
    text = ET.SubElement(tei, "text")
    body = ET.SubElement(text, "body")

    # Extract all poems
    poems = soup.find_all("div", class_="poem")
    for poem in poems:
        poem_div = ET.SubElement(body, "div", {"type": "poem"})

        # Extract poem-specific metadata
        poem_header = poem.find("div", class_="poem_header")
        if poem_header:
            poem_info = poem_header.find("div", class_="poem_info")
            if poem_info:
                header_fields = {
                    "poem_number": poem_header.find("div", class_="poem_number"),
                    "work_title": poem_info.find("div", class_="work_title"),
                    "poem_meter": poem_info.find("div", class_="poem_meter"),
                    "poem_title": poem_info.find("div", class_="poem_title"),
                    "citation": poem_info.find("div", class_="citation")
                }

                # Populate header metadata
                for key, element in header_fields.items():
                    value = element.text.strip() if element else ""
                    ET.SubElement(poem_div, key).text = value

        # Extract lines while preserving markup
        for line in poem.find_all("div", class_="line"):
            line_before = line.get("data-before", "").strip()
            line_number = line.get("data-number", "0").strip()
            combined_number = f"{line_before}{line_number}"

            # Extract meter information after "line"
            class_parts = line.get("class", [])
            metre_parts = " ".join(cls for cls in class_parts if cls != "line").strip()

            l_element = ET.SubElement(poem_div, "l", {"n": combined_number, "metre": metre_parts})

            # Preserve word and syllable structure
            for word in line.find_all("span", class_="word"):
                w_element = ET.SubElement(l_element, "w")
                for syll in word.find_all("span", class_="syll"):
                    syll_type = syll.get("class", [None])[1]  # Extract long/short
                    ET.SubElement(w_element, "syll", {"type": syll_type}).text = syll.text

    # Ensure the output folder exists
    output_folder = "hypotactic_xmls_greek"
    os.makedirs(output_folder, exist_ok=True)

    # Create output file name
    output_file_name = os.path.join(output_folder, f"{base_name}.xml")

    # Pretty-print the TEI XML
    xml_str = pretty_print_xml(tei)
    with open(output_file_name, "w", encoding="utf-8") as output_file:
        output_file.write(xml_str)

    # Validate that all HTML tags are represented
    html_tags = extract_tags(soup)
    tei_tags = extract_tags(tei)

    # Find missing tags
    missing_tags = html_tags - tei_tags

    if missing_tags:
        print(f"\n⚠️ Missing Tags in TEI XML: {missing_tags}")
    else:
        print(f"\n✅ Successfully created TEI XML file: {output_file_name}")

# Example Usage
create_tei_xml("hypotactic_htmls_greek/callimachusEp.html")