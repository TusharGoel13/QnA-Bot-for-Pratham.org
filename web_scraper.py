import requests
from bs4 import BeautifulSoup

# Send a GET request to the website URL
response = requests.get('https://pratham.org')

# Parse the HTML content of the response using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

def extract_links(li_tags):
    links = []
    # Loop through each <li> tag
    for li in li_tags:
        # Find the <a> tag within the <li> tag
        a_tag = li.find('a', href=True)
        if a_tag:
            href = a_tag['href']
            # Check if href is a proper URL and not a placeholder
            if href and href != '#':
                links.append({
                    'text': a_tag.get_text(strip=True),
                    'href': href
                })

    # Find the "Other Websites" section
    other_websites_section = soup.find('div', class_='otherwebsites-links')
    if other_websites_section:
        # Loop through each <a> tag within the "Other Websites" section
        for a_tag in other_websites_section.find_all('a', href=True):
            href = a_tag['href']
            if href and href != '#':  # Ensure proper URL
                img_tag = a_tag.find('img')
                alt_text = img_tag['alt'] if img_tag and 'alt' in img_tag.attrs else a_tag.get_text(strip=True)
                links.append({
                    'text': alt_text,
                    'href': href
                })

    # Find the social media buttons section
    social_media_section = soup.find('div', class_='social-media-button-container')
    if social_media_section:
        # Loop through each <a> tag within the social media buttons section
        for a_tag in social_media_section.find_all('a', href=True):
            href = a_tag['href']
            if href and href != '#':  # Ensure proper URL
                links.append({
                    'text': a_tag.get_text(strip=True),
                    'href': href
                })

    return links

# Find all <li> tags
li_tags = soup.find_all('li')

# Extract all links
links = extract_links(li_tags)

external_links = []
output = []

for link in links:
    url = link['href']

    if url.startswith('https://pratham.org'):
        # Send a GET request to the URL
        response = requests.get(url)
    else:
        external_links.append(url)
        continue

    # Parse the HTML content of the webpage
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract page title
    title = soup.title.text.strip()
    output.append(f"Title of page: {title}, {url}")

    # Find and exclude the footer
    side_menu = soup.find('div', class_='menu-aboutus-right-menu-container')
    if side_menu:
        side_menu.decompose()  # Remove the footer section from the soup

    # Extracting all text content within the main content area
    main_content = soup.find('div', class_='entry-content')

    if main_content:
        formatted_content = []

        # Get all text from paragraphs, headings, lists, tables, and links
        elements = main_content.find_all(['p', 'h1', 'h2', 'h3','h4', 'h5', 'h6', 'ul', 'ol', 'table', 'a'])

        for element in elements:
            if element.name in ('h1', 'h2', 'h3','h4', 'h5', 'h6'):
                heading_text = element.get_text().strip()
                formatted_content.append(f"**{heading_text}**")
                if "FEATURED VIDEO" in heading_text:
                    # Look for iframe tags for video details within the same section
                    iframes = soup.find_all('iframe')
                    for iframe in iframes:
                        if 'youtube' in iframe.get('src', '').lower():
                            iframe_title = iframe.get('title', 'No Title').strip()
                            iframe_link = iframe['src']
                            formatted_content.append(f"**Video: {iframe_title}** - Link: {iframe_link}")
            elif element.name in ('ul','ol'):
                items = element.find_all('li')
                for item in items:
                    formatted_content.append(f"- {item.get_text().strip()}")
            elif element.name == 'table':
                headers = element.find_all('th')
                rows = element.find_all('tr')
                if headers:
                    formatted_content.append(" | ".join(header.get_text().strip() for header in headers))
                    formatted_content.append("-" * (len(headers) * 20))
                for row in rows:
                    columns = row.find_all('td')
                    if columns:
                        formatted_content.append(" | ".join(column.get_text().strip() for column in columns))
            elif element.name == 'p':
                formatted_content.append(element.get_text().strip())
            elif element.name == 'a' and element.get('href'):
                link_href = element['href']
                link_text = element.get_text().strip()
                # Exclude links for videos under "Featured Video" heading
                if "youtube" in link_href.lower() and any("FEATURED VIDEO" in h for h in formatted_content):
                    continue
                formatted_content.append(f"Title: {link_text} - Link: {link_href}")
                
        # Add formatted content to output lines
        output.extend(formatted_content)
        output.append("\n\n")
        
# Add external links to output lines
output.append("External Links:")
for external in external_links:
    output.append(external)
    
# Write all accumulated data to a text file
with open('scraped_data2.txt', 'w', encoding='utf-8') as file:
    file.write("\n".join(output))

print("Data has been written to scraped_data.txt")