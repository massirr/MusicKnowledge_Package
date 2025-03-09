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
#
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def artist_pdf(file_name, title, image_path, bio_text, greatest_hits):
    """create a pdf of the artist's info
    Parameters:
        string --> file_name, 
        string --> title,
        string --> image_path, 
        string --> bio_text, 
        string array --> greatest_hits
    Return:
        none
    """
    pdf = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4
    
    # Add title
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(50, height - 50, title)
    
    # Calculate text width (leaving space for image)
    text_width = width - 3.5*inch  # Reduced width to accommodate image
    
    style = ParagraphStyle(
        'Normal',
        fontSize=9,
        leading=14  # Space between lines
    )
    
    p = Paragraph(str(bio_text), style)
    w, h = p.wrap(text_width, height)
    p.drawOn(pdf, 50, height - 100 - h)
    
    # Add image on right side
    try:
        img = utils.ImageReader(image_path)
        img_width = 2*inch
        aspect = img.getSize()[1] / float(img.getSize()[0])
        pdf.drawImage(image_path, 
                     width - 2.5*inch,
                     height - 3.35*inch,
                     width=img_width,
                     height=img_width*aspect)
    except Exception as e:
        print(f"Image could not be loaded: {e}")
    
    # Add "Greatest hits:" section
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 300, "Greatest hits:")
    
    # Add song list in columns
    pdf.setFont("Helvetica", 6.5)
    y_start = height - 330
    x_positions = [50, 250, 450]  # Three columns
    
    # For the rows
    for song in greatest_hits:
        if y_start < 50:
            pdf.showPage()  # Start a new page
            pdf.setFont("Helvetica", 6.5)
            y_start = height - 100  # Reset height for new page

        pdf.drawString(x_positions[0], y_start, song)
        y_start -= 20


    pdf.save()

def get_image(name):
    """collect the image of an artist
    Parameters:
        strint --> name
    Return:
        none
    """
    try:
        url = f'https://www.last.fm/music/{name}/+images/8df0660e16d36d03026e1fa132fc509d'
        soup = get_the_soup(url)
        img_tag = soup.find('img', {'class':"js-gallery-image"})
        url = img_tag['src']# needed to download the image 
        #print(url)
        r = requests.get(url, allow_redirects=True)
        name = name.strip()
        name = name.replace(' ', '_')
        fileName = f'{name}.jpg'
        with open(fileName, 'wb') as file:
            file.write(r.content)
        return fileName
    except:
        print('Wrong artist name!!!')

def get_the_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup

def noName():
    """Shows the best selling artist of your genre with their greatest hits,
         collect a picture and some information
    Parameters:
        none
    Return:
        none
    """
    #step 1 --> get the best selling artist of rock
    with open('best_selling_artists.csv') as file:
        data = file.readlines()
        best_rock_artist = data[1].split(',')[0]
        artist = best_rock_artist

    #step 2 --> get a short description
    url = f'https://www.last.fm/music/{best_rock_artist}/+wiki'
    soup = get_the_soup(url)
    div_class = soup.find('div', {'class':'wiki-content'})
    short_description = div_class.find('p').get_text()

    #step 3 --> get top tracks
    url = 'https://en.wikipedia.org/wiki/List_of_songs_recorded_by_the_Beatles'
    soup = get_the_soup(url)
    tables = soup.find_all('table', {'class':"wikitable sortable sticky-header-multi plainrowheaders"})

    # Initialize a list to store song data
    songs = []

    for table in tables:
        # Extract rows from the table
        rows = table.find_all('tr')[1:]  # Skip the header row

        # Iterate through each row
        for row in rows:
            columns = row.find_all('td')  # Find all columns in the row
            if len(columns) > 4:  # Ensure there are enough columns
                # Get the song title
                title_cell = row.find('th')
                if title_cell:
                    song_title = title_cell.text.strip()
                    song_title = re.sub(r'("[^"]+")\s?[^\w]*.*', r'\1', song_title)
                else:
                    break
                
                year_released = columns[-2].text.strip()  # Get the second last column (Year released)
                #print(year_released,song_title)
                songs.append(f"{year_released}: {song_title}")

    ## Creating the pdf

    file_name = f"{artist}.pdf"
    title = artist
    image_path = get_image(artist)  # Replace with the path to the image
    bio_text = short_description
    greatest_hits = songs

    #print(greatest_hits)

    artist_pdf(file_name, title, image_path, bio_text, greatest_hits)


def name(name):
    """Shows some information on the artist, their greatest hits and collect a picture
    Parameters:
        string --> name
    Return:
        none
    """
    # step 1
    url = f'https://www.last.fm/music/{name}/+wiki'
    soup = get_the_soup(url)
    div_class = soup.find('div', {'class':'wiki-content'})
    short_description = div_class.find('p').get_text()

    #step 2 --> credentials
    sp = SpotifyAPIcredentials()
   
    #step 3 --> get songs
    all_songs = get_artist_songs(name, sp)

    if all_songs:
       ## Creating the pdf

        file_name = f"{name}.pdf"
        title = name
        image_path = get_image(name)  # Replace with the path to the image
        bio_text = short_description
        greatest_hits = all_songs

        #print(greatest_hits)

        artist_pdf(file_name, title, image_path, bio_text, greatest_hits)
    else:
        print(f"{name} is not a rock artist")
    
def SpotifyAPIcredentials():
    """setting up spotify credentials
    Parameters:
        none
    Return:
        string --> sp
    """
    # Set up your Spotify API credentials
    client_credentials_manager = SpotifyClientCredentials(
        client_id='ea916fb6c0b0419389c011ebf4021439', 
        client_secret='8201c2f49f2e4f5faa5814b0aa19adf4'
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

def get_artist_songs(artist_name, sp):
    """gets artist's songs
    Parameters:
        string --> artist_name
        string --> sp
    Return:
        list --> all songs
    """
    try:
        # Search for the artist
        results = sp.search(q='artist:' + artist_name, type='artist')
        if not results['artists']['items']:
            print(f"No results found for artist: {artist_name}")
            return None

        genres = results['artists']['items'][0]['genres']
        for genre in genres:
            if 'rock' in genre.lower():
                # Get the first artist's ID
                artist_id = results['artists']['items'][0]['id']

                # Fetch all albums of the artist
                albums = sp.artist_albums(artist_id, album_type='album')
                album_ids = [album['id'] for album in albums['items']]

                # Fetch all songs from the albums
                all_songs = []
                for album_id in album_ids:
                    tracks = sp.album_tracks(album_id)
                    for track in tracks['items']:
                        all_songs.append(track['name'])

                # Remove duplicates and return the list
                return list(set(all_songs))

    except Exception as e:
        print(f"An error occurred: {e}")
        return None