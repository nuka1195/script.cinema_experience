import re
a = -1
if (a ):
    print "yup"
xml_data = """
<slides>
    <slide rating="PG">
        <question format="[0-9]+a.jpg" />
        <clue format="N/A" />
        <answer format="[0-9]+b.jpg" />
    </slide>
</slides>
"""

question_format = re.findall( "<question format=\"([^\"]+)\" />", xml_data )
clue_format = re.findall( "<clue format=\"([^\"]+)\" time=\"([^\"]+)\" />", xml_data )
answer_format = re.findall( "<answer format=\"([^\"]+)\" time=\"([^\"]+)\" />", xml_data )
print "q",question_format
print "c",clue_format
print "a", answer_format

import random
a = [ ["q1", "c1", "a1" ], ["q2", "c2", "a2" ],["q3", "c3", "a3" ]]

random.shuffle(a)

print a

a= None
b ="One"
print a or b

mpaa = ""
# mpaa ratings
mpaa_ratings = { "G": 0, "PG": 1, "PG-13": 2, "R": 3, "NC-17": 4 }
# set the proper mpaa rating user preference
mpaa = ( "--", mpaa, )[ 0 ]
# rating query
rating_sql = ( "", "AND (%s)" % " ".join( [ "rating='%s' OR" % rating for rating, index in mpaa_ratings.items() if index <= mpaa_ratings.get( mpaa, -1 ) ] )[ : -3 ], )[ mpaa_ratings.has_key( mpaa ) ]
print rating_sql

trailer_rating = "R"
movie_rating = ""
set_rating = "--"
lq= True
# mpaa ratings
mpaa_ratings = { "G": 0, "PG": 1, "PG-13": 2, "R": 3, "NC-17": 4, "--": 5, "": 6 }
# set the proper mpaa rating user preference
movie_rating = ( set_rating, movie_rating, )[ lq ]
print "MPAA", movie_rating
print ( mpaa_ratings.get( movie_rating, -1 ) < mpaa_ratings.get( trailer_rating, -1 ) )


