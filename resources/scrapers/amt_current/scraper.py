"""
Apple Movie Trailers current trailers scraper
"""

import sys
import os
import xbmc
import time
import re
import urllib
from random import shuffle
from xml.sax.saxutils import unescape
from resources.lib.utils import LOG, watched_status_file

__useragent__ = "QuickTime/7.2 (qtver=7.2;os=Windows NT 5.1Service Pack 3)"


class _urlopener( urllib.FancyURLopener ):
    version = __useragent__
# set for user agent
urllib._urlopener = _urlopener()


class _Parser:
    def __init__( self, mpaa, genre, studio, director, settings, watched, mpaa_ratings, mpaa_conversion, unrated_rating_index, unrated_rating ):
        self.mpaa = mpaa
        self.genre = genre
        self.studio = studio
        self.director = director
        self.settings = settings
        self.watched = watched
        self.mpaa_ratings = mpaa_ratings
        self.mpaa_conversion = mpaa_conversion
        self.unrated_rating_index = unrated_rating_index
        self.unrated_rating = unrated_rating
        self.trailers = []
        # get our regions format
        ##########self.date_format = xbmc.getRegion( "datelong" ).replace( "DDDD,", "" ).replace( "MMMM", "%B" ).replace( "D", "%d" ).replace( "YYYY", "%Y" ).strip()

    def parse_source( self, xmlSource ):
        try:
            # counter to limit results
            count = 0
            # encoding
            encoding = re.findall( "<\?xml version=\"[^\"]*\" encoding=\"([^\"]*)\"\?>", xmlSource[ 0 ] )[ 0 ]
            # gather all trailer records <movieinfo>
            trailers = re.findall( "<movieinfo id=\"(.+?)\"><info><title>(.+?)</title><runtime>(.*?)</runtime><rating>(.*?)</rating><studio>(.*?)</studio><postdate>(.*?)</postdate><releasedate>(.*?)</releasedate><copyright>(.*?)</copyright><director>(.*?)</director><description>(.*?)</description></info>(?:<cast>(.+?)</cast>)?<genre>(.+?)</genre><poster><location>(.*?)</location><xlarge>(.*?)</xlarge></poster><preview><large filesize=\"(.+?)\">(.+?)</large></preview></movieinfo>", xmlSource[ 0 + ( 2 * ( self.settings[ "trailer_quality" ] > 1 and self.settings[ "trailer_hd_only" ] ) ) ] )
            trailers_480p = dict( re.findall( "<movieinfo id=\"(.+?)\">.+?<preview><large filesize=\"(.+?\">.+?)</large></preview></movieinfo>", xmlSource[ 1 ] ) )
            trailers_720p = dict( re.findall( "<movieinfo id=\"(.+?)\">.+?<preview><large filesize=\"(.+?\">.+?)</large></preview></movieinfo>", xmlSource[ 2 ] ) )
            # randomize the trailers and create our play list
            shuffle( trailers )
            # enumerate thru the movies list and gather info
            for trailer in trailers:
                # encode/clean title
                title = unicode( unescape( trailer[ 1 ] ), encoding, "replace" )
                # if unwatched only, check it
                if ( self.settings[ "trailer_unwatched_only" ] and trailer[ 0 ] in self.watched ):
                    LOG( "* Skipping *: %s   [WATCHED]" % ( repr( title ).ljust( 50 ), ) )
                    continue
                # trailer rating
                mpaa = trailer[ 3 ]
                # convert trailer rating if necessary
                if ( self.mpaa_conversion is not None ):
                    mpaa = self.mpaa_conversion.get( mpaa, "Not yet rated" )
                # if limit by movie rating, check it
                if ( self.mpaa_ratings.get( self.mpaa, self.unrated_rating_index ) < self.mpaa_ratings.get( mpaa, self.unrated_rating_index ) ):
                    LOG( "* Skipping *: %s   Movie: %s, Trailer: %s" % ( repr( title ).ljust( 50 ), self.mpaa, ( "%s (%s)" % ( self.unrated_rating, mpaa, ), mpaa, )[ mpaa != "Not yet rated" ] , ) )
                    continue
                # parse genres 
                genres = re.findall( "<name>(.+?)</name>", trailer[ 11 ] )
                # if a genre based theme, check it
                if ( self.settings[ "trailer_theme" ] == "1" and not set( genres ).intersection( set( self.genre ) ) ):
                    LOG( "* Skipping *: %s   Movie: %s, Trailer: %s [GENRE]" % ( repr( title ).ljust( 50 ), " / ".join( self.genre ), " / ".join( genres ), ) )
                    continue
                # encode/clean studio
                studio = unicode( unescape( trailer[ 4 ] ), encoding, "replace" )
                if ( self.settings[ "trailer_theme" ] == "2" and studio != self.studio ):
                    LOG( "* Skipping *: %s   Movie: %s, Trailer: %s [STUDIO]" % ( repr( title ).ljust( 50 ), repr( self.studio ), repr( studio ), ) )
                    continue
                # encode/clean director
                director = unicode( unescape( trailer[ 8 ] ), encoding, "replace" )
                if ( self.settings[ "trailer_theme" ] == "3" and director != self.director ):
                    LOG( "* Skipping *: %s   Movie: %s, Trailer: %s [DIRECTOR]" % ( repr( title ).ljust( 50 ), repr( self.director ), repr( director ), ) )
                    continue
                # parse actors 
                ##actors = unicode( unescape( " / ".join( re.findall( "<name>(.+?)</name>", trailer[ 10 ] ) ) ), encoding, "replace" )
                # encode/clean copyright
                ##copyright = unicode( unescape( trailer[ 7 ] ), encoding, "replace" )
                # convert size to long
                ##size = long( trailer[ 14 ] )
                # add User-Agent to correct poster url
                poster = ( trailer[ 13 ] or trailer[ 12 ] ) + "?|User-Agent=%s" % ( urllib.quote_plus( __useragent__ ), )
                # set initial trailer url
                trailer_url = trailer[ 15 ]
                # select prefered trailer quality
                if ( self.settings[ "trailer_quality" ] > 0 ):
                    if ( self.settings[ "trailer_quality" ] > 1 and trailers_720p.has_key( trailer[ 0 ] ) ):
                        if ( not self.settings[ "trailer_hd_only" ] ):
                            size, trailer_url = trailers_720p[ trailer[ 0 ] ].split( "\">" )
                        # replace with 1080p if user preference is 1080p
                        if ( self.settings[ "trailer_quality" ] == 3 ):
                            trailer_url = trailer_url.replace( "a720p.m4v", "h1080p.mov" )
                    elif ( trailers_480p.has_key( trailer[ 0 ] ) ):
                        size, trailer_url = trailers_480p[ trailer[ 0 ] ].split( "\">" )
                    # convert size to long
                    ##size = long( size )
                # add User-Agent to trailer url
                trailer_url += "?|User-Agent=%s" % ( urllib.quote_plus( __useragent__ ), )
                # encode/clean plot
                plot = unicode( unescape( trailer[ 9 ] ), encoding, "replace" )
                # duration of trailer
                duration = trailer[ 2 ]
                # format post date
                postdate = trailer[ 5 ].replace( "-", " " )
                # format release date
                releasedate = trailer[ 6 ].replace( "-", " " )
                # we're keeping this one, spam log
                LOG( "[Including] : %s   Trailer: %s" % ( repr( title ).ljust( 50 ), trailer_url.split( "?|" )[ 0 ], ) )
                # add the item to our media list
                self.trailers += [ ( trailer[ 0 ], title, trailer_url, poster, plot, duration, mpaa, releasedate, postdate, " / ".join( genres ), studio, "", director, ) ]
                # if unwatched only, add trailer id to watched file
                if ( self.settings[ "trailer_unwatched_only" ] ):
                    self.watched += [ trailer[ 0 ] ]
                # increment counter
                count += 1
                # if we have enough exit
                if ( count == self.settings[ "trailer_count" ] ):
                    break
        except Exception, e:
            # oops, notify user what error occurred
            LOG( str( e ), xbmc.LOGERROR )


class Main:
    # base url
    BASE_CURRENT_URL = "http://www.apple.com/trailers/home/xml/%s"
    # base paths
    BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "script_data", os.path.basename( os.getcwd() ) )

    def __init__( self, mpaa=None, genre=None, studio=None, director=None, settings=None, movie=None, mpaa_ratings=None, mpaa_conversion=None, unrated_rating_index=None, unrated_rating=None ):
        self.mpaa = mpaa
        self.genre = genre.replace( "Sci-Fi", "Science Fiction" ).replace( "Action", "Action and ADV" ).replace( "Adventure", "ACT and Adventure" ).replace( "ACT",  "Action" ).replace( "ADV",  "Adventure" ).split( " / " )
        self.studio = studio
        self.director = director
        self.settings = settings
        self.mpaa_ratings = mpaa_ratings
        self.mpaa_conversion = mpaa_conversion
        self.unrated_rating_index = unrated_rating_index
        self.unrated_rating = unrated_rating

    def fetch_trailers( self ):
        # initialize trailers list
        trailers = []
        # fetch source
        xmlSource = self._get_xml_source()
        # parse source and add our items
        if ( xmlSource ):
            trailers = self._parse_xml_source( xmlSource )
        # return results
        return trailers

    def _get_xml_source( self ):
        try:
            xmlSource = []
            # grab all xml sources
            for source in ( "current.xml", "current_480p.xml", "current_720p.xml", ):
                # set path and url
                base_path = os.path.join( self.BASE_CURRENT_SOURCE_PATH, source )
                base_url = self.BASE_CURRENT_URL % ( source, )
                # get the source files date if it exists
                try: date = os.path.getmtime( base_path )
                except: date = 0
                # we only refresh if it's been more than a day, 24hr * 60min * 60sec
                refresh = ( ( time.time() - ( 24 * 60 * 60 ) ) >= date )
                # only fetch source if it's been more than a day
                if ( refresh ):
                    # open url
                    usock = urllib.urlopen( base_url )
                else:
                    # open path
                    usock = open( base_path, "r" )
                # read source
                xmlSource += [ usock.read() ]
                # close socket
                usock.close()
                # save the xmlSource for future parsing
                if ( refresh ):
                    ok = self._save_xml_source( xmlSource[ -1 ], base_path )
            # return source
            return xmlSource
        except Exception, e:
            # oops, notify user what error occurred
            LOG( str( e ), xbmc.LOGERROR )
            # error so return empty string
            return []

    def _save_xml_source( self, xmlSource, base_path ):
        try:
            # if the path to the source file does not exist create it
            if ( not os.path.isdir( os.path.dirname( base_path ) ) ):
                os.makedirs( os.path.dirname( base_path ) )
            # open source path for writing
            file_object = open( base_path, "w" )
            # write xmlSource
            file_object.write( xmlSource )
            # close file object
            file_object.close()
            # return successful
            return True
        except Exception, e:
            # oops, notify user what error occurred
            LOG( str( e ), xbmc.LOGERROR )
            # error so return False, we don't actually use this for anything
            return False

    def _parse_xml_source( self, xmlSource ):
        # load watched file
        watched = watched_status_file( filename=self.settings[ "trailer_scraper" ] + "_watched.txt" )
        # Parse xmlSource for videos
        parser = _Parser( self.mpaa, self.genre, self.studio, self.director, self.settings, watched, self.mpaa_ratings, self.mpaa_conversion, self.unrated_rating_index, self.unrated_rating )
        parser.parse_source( xmlSource )
        # save watched file
        watched = watched_status_file( filename=self.settings[ "trailer_scraper" ] + "_watched.txt", watched=parser.watched )
        # return result
        return parser.trailers
