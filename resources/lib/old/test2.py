mpaa_ratings = { "G": 0, "PG": 1, "PG-13": 2, "R": 3, "NC-17": 4 }
    
mpaa = "PG-13"
rating_sql = ( "", "AND (%s)" % " ".join( [ "rating='%s' OR" % rating for rating, index in mpaa_ratings.items() if index <= mpaa_ratings.get( mpaa, -1 ) ] )[ : -3 ], )[ mpaa_ratings.has_key( mpaa ) ]
print rating_sql


"""
                # genre limit
                if ( not genre_sql ):
                    movie_genres = genre.split( "/" )
                    if ( movie_genres[ 0 ] != "" ):
                        genre_sql = "AND ("
                        for genre in movie_genres:
                            genre = genre.strip().replace( "Sci-Fi", "Science Fiction" )
                            if ( genre == "Action" or genre == "Adventure" ):
                                genre = "Action and Adventure"
                            # fix certain genres
                            genre_sql += "genres.genre='%s' OR " % ( genre, )
                        # fix the sql statement
                        genre_sql = genre_sql[ : -4 ] + ") "

"""
genre_sql = ""
genre = "Drama / Sci-Fi / Thriller / Adventure / Action"
genres = genre.split( " / " )
genre_sql = ( genre_sql, "AND (%s)" % " ".join( [ "genres.genre='%s' OR" % genre.replace( "Sci-Fi", "Science Fiction" ).replace( "Action", "Action and ADV" ).replace( "Adventure", "ACT and Adventure" ).replace( "ACT",  "Action" ).replace( "ADV",  "Adventure" ) for genre in genres ] )[ : -3 ], )[ not genre_sql ]

print genre_sql