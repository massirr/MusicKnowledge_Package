import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
#
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import utils
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4

# These will be called Year in packages
def year(year):
    """Fetches the top rock songs from a specific year using Spotify API.
    
    Parameters:
        year (int): The year to search for rock songs.
        limit (int): Number of top songs to retrieve (default is 20).

    Returns:
        list: A list of dictionaries containing song details.
    """
    # Set up Spotify API credentials
    sp = SpotifyAPIcredentials()

    # Query for rock songs released in the specified year
    query = f"genre:rock year:{year}"
    results = sp.search(q=query, type='track', limit=20)

    # Extract and format the song details
    top_songs = []
    for track in results['tracks']['items']:
        top_songs.append({
            "name": track['name'],
            "artist": track['artists'][0]['name'],
            "album": track['album']['name'],
            "popularity": track['popularity'],
            "release_date": track['album']['release_date']
        })

    # creating the pdf
    if top_songs:
        pdf = canvas.Canvas(f'Top_20_songs.pdf', pagesize=A4)
        width, height = A4
        
        # Add title
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(50, height - 50, f'{year}- Top 20 songs and albums')

        current_height = height - 100

        # Loop through songs
        for i, song in enumerate(top_songs, 1):
            # Album name and artist
            pdf.setFont("Helvetica-Bold", 7)
            pdf.drawString(50, current_height, f"{i}. {song['name']} - {song['artist']}")
            
            # Album sales with bullet point
            pdf.setFont("Helvetica", 7)
            pdf.drawString(70, current_height - 10, f"○ {song['album']} - {song['release_date']}")
            
            # Move down for next entry (adjust spacing)
            current_height -= 35
        
        pdf.save()
    else:
        print(f"No rock songs found for the year {year}.")

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


