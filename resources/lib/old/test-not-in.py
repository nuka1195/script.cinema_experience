slides = [ "", "", "" ]
viewed = [ "q", "a", "", "a", "b" ]

if ( ( slides[ 0 ] and slides[ 0 ] not in viewed ) or
      ( slides[ 1 ] and slides[ 1 ] not in viewed ) or
      ( slides[ 2 ] and slides[ 2 ] not in viewed ) ):
    print "cool"

mpaa = "PG"
mpaa = mpaa.split( " " )[ 1 - ( len( mpaa.split( " " ) ) == 1 ) ]
mpaa = ( mpaa, "NR", )[ mpaa not in ( "G", "PG", "PG-13", "R", "NC-17", ) ]
print mpaa

path = ""
print { "\\": "\\", "/": "/" }.get( path[ -1 ], "" )
