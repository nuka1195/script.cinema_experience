"""
Local trailer scraper
"""

import os
import xbmc
import re
from random import shuffle
from resources.lib.utils import LOG, watched_status_file


class Main:
    def __init__( self, mpaa=None, genre=None, settings=None, movie=None, mpaa_ratings=None, mpaa_conversion=None ):
        self.mpaa_conversion = mpaa_conversion
        self.mpaa_ratings = mpaa_ratings
        self.mpaa = mpaa
        self.genre = genre.replace( "Sci-Fi", "Science Fiction" ).replace( "Action", "Action and ADV" ).replace( "Adventure", "ACT and Adventure" ).replace( "ACT",  "Action" ).replace( "ADV",  "Adventure" ).split( " / " )
        self.settings = settings
        self.movie = movie
        self.trailers = []
        self.tmp_trailers = []

    def fetch_trailers( self ):
        # get watched list
        self._get_watched()
        # fetch all trailers recursively
        self._fetch_trailers( [ self.settings[ "trailer_folder" ] ] )
        # get a random number of trailers
        self._shuffle_trailers()
        # save watched list
        self._save_watched()
        # return results
        return self.trailers

    def _fetch_trailers( self, paths ):
        # reset folders list
        folders = []
        # enumerate thru paths and fetch slides recursively
        for path in paths:
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s, ,showdate)" % ( path, ) ).splitlines()
            # enumerate through our entries list and separate question, clue, answer
            for entry in entries:
                # remove <li> from item
                entry = entry.replace( "<li>", "" ).split( "  ;" )
                # if folder add to our folder list to recursively fetch slides
                if ( entry[ 0 ].endswith( "/" ) or entry[ 0 ].endswith( "\\" ) ):
                    folders += [ entry[ 0 ] ]
                # does this entry match our pattern "-trailer." and is a video file
                elif ( "-trailer." in entry[ 0 ] and os.path.splitext( entry[ 0 ] )[ 1 ] in xbmc.getSupportedMedia( "video" ) ):
                    # add our entry
                    self.tmp_trailers += [ entry ]
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._fetch_trailers( folders )

    def _shuffle_trailers( self ):
        # randomize the groups and create our play list
        shuffle( self.tmp_trailers )
        # reset counter
        count = 0
        # now create our final playlist
        for trailer in self.tmp_trailers:
            # user preference to skip watch trailers
            if ( self.settings[ "trailer_unwatched_only" ] and xbmc.getCacheThumbName( trailer[ 0 ] ) in self.watched ):
                ##print "SKIPPED:", repr(trailer[ 0 ])
                continue
            # set all info
            tmp_trailer = self._set_trailer_info( trailer )
            # convert mpaa if necessary
            if ( self.mpaa_conversion is not None ):
                tmp_trailer[ 6 ] = self.mpaa_conversion.get( tmp_trailer[ 6 ], "NR" )
            # do we need to skip this one
            if ( self.mpaa_ratings.get( self.mpaa, self.settings[ "unrated_rating_index" ] ) < self.mpaa_ratings.get( tmp_trailer[ 6 ], self.settings[ "unrated_rating_index" ] ) ):
                ##LOG( "Skipping trailer: %s  - Movie: %s, Unrated: %s, Trailer: %s" % ( repr( tmp_trailer[ 1 ] ), self.mpaa, ("G","PG","PG-13","R","NC-17",)[ self.settings[ "mpaa_rating" ] ], tmp_trailer[ 6 ], ) )
                continue
            # add id to watched file
            if ( self.settings[ "trailer_unwatched_only" ] ):
                self.watched += [ xbmc.getCacheThumbName( trailer[ 0 ] ) ]
            # add trailer to our final list
            self.trailers += [ tmp_trailer ]
            # increment counter
            count += 1
            # if we have enough exit
            if ( count == self.settings[ "trailer_count" ] ):
                break

    def _set_trailer_info( self, trailer ):
        # get trailer info
        title, thumbnail, plot, runtime, mpaa, releasedate, genre, studio, writer, director, cast, quality = self._get_trailer_info( trailer )
        # set post date
        post_date = ""##self._get_post_date( trailer[ 1 ].split( " " )[ 0 ] )
        # set result
        result = [ xbmc.getCacheThumbName( trailer[ 0 ] ), # id
                        title, # title
                        trailer[ 0 ], # url
                        thumbnail, # thumb
                        plot, # plot
                        runtime, # duration
                        mpaa, # mpaa
                        releasedate, # release date
                        post_date, # post date "12/21/2009 9:05:46 PM"
                        genre, # genre
                        studio, # studio
                        writer, # writer
                        director, # director
                        ]
        return result

    def _get_trailer_info( self, trailer ):
        # set nfo path
        nfo_path = os.path.splitext( trailer[ 0 ] )[ 0 ] + ".nfo"
        # if no nfo file exists exists return TODO: switch to os.path.isfile(), it does work with smb:// urls
        if ( not ( "True" in xbmc.executehttpapi( "FileExists(%s)" % ( nfo_path, ) ) ) ):
            return os.path.basename( trailer[ 0 ] ).split( "-trailer." )[ 0 ], self._get_thumbnail( trailer[ 0 ] ), "", "", "", "", "", "", "", "", "", ""
        # get nfo data
        nfoSource = self._get_nfo_source( nfo_path )
        # set movie info
        title = re.findall( "<title>(.*?)</title>", nfoSource )[ 0 ]
        quality = re.findall( "<quality>(.*?)</quality>", nfoSource )[ 0 ]
        runtime = re.findall( "<runtime>(.*?)</runtime>", nfoSource )[ 0 ]
        releasedate = re.findall( "<releasedate>(.*?)</releasedate>", nfoSource )[ 0 ]
        mpaa = re.findall( "<mpaa>(.*?)</mpaa>", nfoSource )[ 0 ]
        genre = re.findall( "<genre>(.*?)</genre>", nfoSource )[ 0 ]
        studio = re.findall( "<studio>(.*?)</studio>", nfoSource )[ 0 ]
        director = re.findall( "<director>(.*?)</director>", nfoSource )[ 0 ]
        cast = re.findall( "<cast>(.*?)</cast>", nfoSource )[ 0 ]
        plot = re.findall( "<plot>(.*?)</plot>", nfoSource )[ 0 ]
        thumbnail = re.findall( "<thumb>(.*?)</thumb>", nfoSource )[ 0 ]
        writer = ""
        # return info
        return title, thumbnail, plot, runtime, mpaa, releasedate, genre, studio, writer, director, cast, quality

    def _get_nfo_source( self, nfo_path ):
        try:
            # open path
            usock = open( nfo_path, "r" )
            # read source
            nfoSource = usock.read()
            # close socket
            usock.close()
            # return source
            return nfoSource
        except:
            return ""

    def _get_thumbnail( self, path ):
        # check for a thumb based on trailername.tbn
        thumbnail = os.path.splitext( path )[ 0 ] + ".tbn" 
        # if thumb does not exist try stripping -trailer
        if ( not xbmc.executehttpapi( "FileExists(%s)" % ( thumbnail, ) ) == "<li>True" ):
            thumbnail = "%s.tbn" % ( os.path.splitext( path )[ 0 ].replace( "-trailer", "" ), )
            # if thumb does not exist return empty
            if ( not xbmc.executehttpapi( "FileExists(%s)" % ( thumbnail, ) ) == "<li>True" ):
                # set empty string
                thumbnail = None
        # return result
        return thumbnail

    def _get_watched( self ):
        # load watched file
        self.watched = watched_status_file( filename=self.settings[ "trailer_scraper" ] + "_watched.txt" )

    def _save_watched( self ):
        # save watched file
        if ( self.settings[ "trailer_unwatched_only" ] ):
            watched = watched_status_file( filename=self.settings[ "trailer_scraper" ] + "_watched.txt", watched=self.watched )
