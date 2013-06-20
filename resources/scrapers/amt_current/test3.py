import re, urllib, os

sysargv = "?category=genres:action+and+adventure"
print dict( arg.split( "=" ) for arg in urllib.unquote_plus( sysargv[ 1: ] ).split( "&" ) )
a=[("12345", "http://", )]
print dict( a )
xmlSource = '<movieinfo id="25252">L<preview><large filesize="235675">http://www.apple.com/movie.mov</large></preview></movieinfo>'
print re.findall( "<movieinfo id=\"(?:(.+?))?\">.+?<preview><large filesize=\"(.+?\">.+?)</large></preview></movieinfo>", xmlSource )


print os.stat(r"G:\videodb.xml")

a = ['download_trailer=True', "trailer_url='http://movies.apple.com/movies/wb/copout/copout-tlr1_h1080p.mov?|User-Agent=iTunes%2F9.0.2+%28Windows%3B+Microsoft+Windows+XP+Professional+Service+Pack+3+%28Build+2600%29%29+AppleWebKit%2F531.21.8'"]
trailer_url='http://movies.apple.com/movies/wb/copout/copout-tlr1_h1080p.mov?|User-Agent=iTunes%2F9.0.2+%28Windows%3B+Microsoft+Windows+XP+Professional+Service+Pack+3+%28Build+2600%29%29+AppleWebKit%2F531.21.8'
print os.path.basename(trailer_url)
#print trailer_url
sysargv = "?trailer_url=%27http%3A%2F%2Fmovies.apple.com%2Fmovies%2Fwb%2Fcopout%2Fcopout-tlr1_h1080p.mov%3F%7CUser-Agent%3DiTunes%252F9.0.2%2B%2528Windows%253B%2BMicrosoft%2BWindows%2BXP%2BProfessional%2BService%2BPack%2B3%2B%2528Build%2B2600%2529%2529%2BAppleWebKit%252F531.21.8%27"
params = dict( arg.split( "=" ) for arg in urllib.unquote_plus( sysargv[ 1 : ] ).replace( "User-Agent=", "User-Agent$EQUAL" ).split( "&" ) )
    
print params#[ "trailer_url" ].replace( "$EQUAL", "=" )
