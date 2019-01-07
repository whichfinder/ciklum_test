import csv
from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):

    with open('payload.csv', 'rb') as csvfile:
        obj_list = []
        reader = csv.reader(csvfile, delimiter=',', quotechar='\n')
        for row in reader:
            obj = {
                'artist': row[0],
                'mail': row[1],
                'password': row[2]
            }
            obj_list.append(obj)

    LOGIN = '/ajax/action.php'  # url for user authorization
    AJAX_REQUESTS = 'ajax/gw-light.php'  # url for post and get requests for search and play
    SEARCH_ARTIST = 'https://api.deezer.com/search?q=artist:"{}"'
    SEARCH_ALBUM = 'https://api.deezer.com/artist/{}/albums'
    SEARCH_TRACK = 'https://api.deezer.com/album/{}'
    # API_TOKEN = ''

    def login(self, data):
        url = self.LOGIN
        user_data = {'type': 'login', 'mail': data['mail'], "password": data['password']}
        self.client.post(url, user_data, name="/login")

    def search_artist(self, artist_name):
        url = self.SEARCH_ARTIST.format(artist_name['artist'])
        search_artist = self.client.get(url, name="/search_artist")
        artist_id = search_artist.json()['data'][0]['artist']['id']
        return artist_id

    def search_album(self, artist_id):
        url = self.SEARCH_ALBUM.format(artist_id)
        search_album = self.client.get(url, name="/search_album")
        album_id = search_album.json()['data'][0]['id']
        return album_id

    def search_track(self, album_id):
        track_urls = []
        url = self.SEARCH_TRACK.format(album_id)
        album_data = self.client.get(url, name="/album_tracks")
        track_list = album_data.json()['tracks']['data']
        for track in track_list:
            track_urls.append(track['link'])
        return track_urls

    def play_all(self, track_list):
        for item_url in track_list:
            self.client.get(item_url, name="/play_track")
            # self.client.post(self.AJAX_REQUESTS, {'method': 'log.listen', 'api_token': self.API_TOKEN})

    @task(1)
    def ping(self):
        for line in self.obj_list:
            self.login(line)
            artist = self.search_artist(line)
            album = self.search_album(artist)
            tracks = self.search_track(album)
            self.play_all(tracks)


class WebsiteUser(HttpLocust):
    host = "https://www.deezer.com"
    task_set = UserBehavior
    min_wait = 1
    max_wait = 3


if __name__ == '__main__':
    WebsiteUser().run()
