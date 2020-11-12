import csv


WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
        'Sunday']

def write(token, club_id, peer_id):
    with open('authorize.csv', 'w', newline='', encoding='utf=8') as f:
        writer = csv.DictWriter(
            f, fieldnames=['club_id', 'token', 'peer_id'],
            delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        data = {'club_id': club_id,
                'token': token,
                'peer_id': peer_id}
        writer.writerow(data)
