from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import utils
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
# 
import requests
from bs4 import BeautifulSoup
import re

def shows(country):
    """
    Fetches the top rock songs from a specific year using Spotify API.

    Parameters:
        year (int): The year to search for rock songs.
        limit (int): Number of top songs to retrieve (default is 20).

    Returns:
        list: A list of dictionaries containing song details.
    """
    def get_the_soup(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup
    
    if country.lower() == 'belgium':
        url = f'https://en.wikipedia.org/wiki/Flag_of_{country}#:~:text=The%20national%20flag%20of%20the,and%20the%20bands%20are%20horizontal.'

        soup = get_the_soup(url)
        a_tag = soup.find('a', {'class':'mw-file-description'})
        img = a_tag.find('img')
        url = img['src']
        r = requests.get(f'https:{url}', allow_redirects=True)
        with open(f'belgium_flag.jpg', 'wb') as file:
            file.write(r.content)

        events = []
        for page in range(1, 8):
            url = f'https://www.livenation.be/event/allevents?genres=rock&page={page}'
            soup = get_the_soup(url)

            div_tags = soup.find_all('div', {'class':"layout__container"})
            for div_tag in div_tags:
                dates = div_tag.find_all('div', {'class':"event-date__date"})
                titles = div_tag.find_all('h3', {'class':"result-info__eventname"})
                locations = div_tag.find_all('div', {'class':"result-info__city-venue-wrapper"})
            
            for date, title, location in zip(dates, titles, locations):
                # Combine the parts into a single string
                date_text = ' '.join(date.stripped_strings)
                title_text = title.text.strip()
                location_text = ''.join(location.stripped_strings)

                events.append({
                    "time": date_text,
                    "title": title_text,
                    "location": location_text,
                })
        
        # creating the pdf
        if events:
            pdf = canvas.Canvas(f'Upcoming Rock Concerts.pdf', pagesize=A4)
            width, height = A4
            
            # Add title and flag image
            pdf.setFont("Helvetica-Bold", 24)
            title = f"Upcoming Rock Concerts -- {country}"
            title_y_position = height - 50
            pdf.drawString(100, title_y_position, title)

            # Add flag image next to the title
            try:
                img = utils.ImageReader('belgium_flag.jpg')
                # Scale image to fit 1 inch in width, adjust height proportionally
                img_width = 1 * inch  # Set the desired width in inches
                aspect_ratio = 170 / 196   # Calculate the aspect ratio from pixel dimensions
                img_height = img_width * aspect_ratio
                pdf.drawImage('belgium_flag.jpg', 430, title_y_position - 80, width=img_width, height=img_height)
            except Exception as e:
                print(f"Image could not be loaded: {e}")

            current_height = height - 100

            # Loop through songs
            for dic in events:
                # Check if there's enough space for a new entry; if not, create a new page
                if current_height < 50:
                    pdf.showPage()  # Start a new page
                    pdf.setFont("Helvetica-Bold", 24)
                    current_height = height - 100  # Reset height for new page

                # Add event details
                pdf.setFont("Helvetica-Bold", 7)
                pdf.drawString(50, current_height, f"{dic['time']}   ")
                pdf.setFont("Helvetica", 7)
                pdf.drawString(150, current_height, f"{dic['title']}     @{dic['location']}")

                # Move down for next entry
                current_height -= 20
            
            pdf.save()
        else:
            print(f"No shows found in Belgium.")
    else:
        print('Not available')


