"""a = [ "Adventure", "comedy", "Romance" ]

b = [ "Action and Adventure", "Romance" ]

#c = set(a).union(set(b))

if not set(a).intersection(set(b)):
    print "YUP"
for genre in b:
    for genre2 in a:
        if genre2 in genre:
            print genre2, genre
            print "yup"

s_mpaa="PG"
trailer_limit_query = False
mpaa_ratings = { "G": 0, "PG": 1, "PG-13": 2, "R": 3, "NC-17": 4, None: 5 }
# set the proper mpaa rating user preference
s_mpaa = ( None, s_mpaa, )[ trailer_limit_query ]
mpaa= "NC-17"

print  "SKIP", mpaa_ratings.get( s_mpaa, 2 ) < mpaa_ratings.get( mpaa, 2 ) 

unrated_mpaa = ""

def _S_( setting ):
    if setting == "movie_rating_system": return "1"
    if setting == "mpaa_rating": return "7"
    if setting == "trailer_limit_query": return "true"
        
print list( { "Uc": 0, "U": 0, "PG": 1, "12": 2, "12A": 2, "15": 3, "18": 4, "R18": 4, None: 5 } )
print { "Uc": 0, "U": 0, "PG": 1, "12": 2, "12A": 2, "15": 3, "18": 4, "R18": 4, None: 5 }.keys()
"""

genres = [ "Comedy", "Romance" ]
s_genre = [u'Animation', u'Action and Adventure', u'Comedy', u'Family']

print set( genres )
print set( s_genre )
print not set( genres ).intersection( set( s_genre ) )





