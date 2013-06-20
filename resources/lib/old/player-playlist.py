# main imports
import os
import xbmcgui
import xbmc

import threading
import binascii
from random import shuffle
import re

_ = xbmc.Language( scriptPath=os.getcwd() ).getLocalizedString


class XBMCPlayer( xbmc.Player ):
    """ 
        Player Class: Subclass of XBMC Player class. Allows calling function
        when video/audio changes or playback ends.
    """
    def __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )
        # set to True so script will stall
        self.loop = True
        # this is the function to call when a player event occurs
        self.function = kwargs[ "function" ]

    def onPlayBackStarted( self ):
        # set to True so script will stall
        self.loop = True
        # we use this if we want to run anything at start, like a script
        self.function( "started" )
        # loop here to keep script running
        while self.loop:
            # one second seems like a good number
            xbmc.sleep( 1000 )

    def onPlayBackResumed( self ):
        # handle resumed event
        self.function( "resumed" )

    def onPlayBackPaused( self ):
        # handle paused event
        self.function( "paused" )

    def onPlayBackStopped( self ):
        # set to False so script will continue
        self.loop = False
        # we handle stopped differently than ended
        self.function( "stopped" )

    def onPlayBackEnded( self ):
        # set to False so script will continue
        self.loop = False
        # we handle ended differently than stopped
        self.function( "ended" )


class Player( xbmcgui.WindowXML ):
    # base paths
    BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "script_data", os.path.basename( os.getcwd() ) )
    # special action codes
    ACTION_NEXT_SLIDE = ( 2, 3, 7, )
    ACTION_PREV_SLIDE = ( 1, 4, )
    ACTION_EXIT_SCRIPT = ( 9, 10, )

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        # set our passed class variables
        self.settings = kwargs[ "settings" ]
        self.playlist = kwargs[ "playlist" ]
        self.mpaa = "PG-13"############################## kwargs[ "mpaa" ]
        # initialize our class variable
        self._init_variables()
        # turn screensaver off
        xbmc.executehttpapi( "SetGUISetting(3,screensaver.mode,None)" )
        try: ##TODO: remove this try block when done
            # fetch the slides
            self._fetch_slides()
            # close dialog
            kwargs[ "dialog" ].close()
            #display slideshow
            self.doModal()
        except:
            import traceback
            traceback.print_exc()
            raise

    def onInit( self ):
        self._show_intro_outro( "intro" )

    def _init_variables( self ):
        self.global_timer = None
        self.slide_timer = None
        self.exiting = False
        # get current screensaver
        self.screensaver = xbmc.executehttpapi( "GetGUISetting(3;screensaver.mode)" ).replace( "<li>", "" )
        # get the current volume
        self.current_volume = xbmc.executehttpapi( "GetVolume" ).replace( "<li>", "" )
        # our complete shuffled list of slides
        self.slide_playlist = []
        self.tmp_slides = []
        self.image_count = 0

    def _fetch_slides( self ):
        # spam log file
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        xbmc.log( ">>> _fetch_slides()", xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        # get watched list
        self._watched_slides_file( mode="r" )
        # get the slides
        self._get_slides( [ self.settings[ "slideshow_folder" ] ] )
        # shuffle and format playlist
        self._shuffle_slides()
        # start our trvia slideshow timer
        self._get_global_timer( self.settings[ "slideshow_total_time" ] * 60, self._exit_slideshow )
        # spam log file
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        xbmc.log( "<<< _fetch_slides()", xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )

    def _get_slides( self, paths ):
        # reset folders list
        folders = []
        # mpaa ratings
        mpaa_ratings = { "G": 0, "PG": 1, "PG-13": 2, "R": 3, "NC-17": 4, "NR": 5, "": 6 }
        # enumerate thru paths and fetch slides recursively
        for path in paths:
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( path, ) ).split( "\n" )
            # sort in case
            entries.sort()
            # get a slides.xml if it exists
            slidesxml_exists, mpaa, question_format, clue_format, answer_format = self._get_slides_xml( path )
            # check if rating is ok
            if ( slidesxml_exists and mpaa_ratings.get( self.mpaa, -1 ) < mpaa_ratings.get( mpaa, -1 ) ):
                xbmc.log( "Skipping whole folder: %s" % ( path, ), xbmc.LOGNOTICE )
                xbmc.log( "     Movie MPAA: %s - Folder MPAA: %s" % ( self.mpaa, mpaa, ), xbmc.LOGNOTICE )
                continue
            # initialize these to True so we add a new list item to start
            question = clue = answer = True
            # enumerate through our entries list and combine question, clue, answer
            for entry in entries:
                # remove <li> from item
                entry = entry.replace( "<li>", "" )
                # if folder add to our folder list to recursively fetch slides
                if ( entry.endswith( "/" ) or entry.endswith( "\\" ) ):
                    folders += [ entry.replace( "<li>", "" ) ]
                # sliders.xml was included, so check it
                elif ( slidesxml_exists ):
                    # question
                    if ( re.search( question_format, os.path.basename( entry ), re.IGNORECASE ) ):
                        if ( question ):
                            self.tmp_slides += [ [ "", "", "" ] ]
                            clue = answer = False
                        self.tmp_slides[ -1 ][ 0 ] = entry
                    # clue
                    elif ( re.search( clue_format, os.path.basename( entry ), re.IGNORECASE ) ):
                        if ( clue ):
                            self.tmp_slides += [ [ "", "", "" ] ]
                            question = answer = False
                        self.tmp_slides[ -1 ][ 1 ] = entry
                    # answer
                    elif ( re.search( answer_format, os.path.basename( entry ), re.IGNORECASE ) ):
                        if ( answer ):
                            self.tmp_slides += [ [ "", "", "" ] ]
                            question = clue = False
                        self.tmp_slides[ -1 ][ 2 ] = entry
                # add the file as a question
                elif ( entry and os.path.splitext( entry )[ 1 ].lower() in xbmc.getSupportedMedia( "picture" ) ):
                    self.tmp_slides += [ [ "", "", entry ] ]
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._get_slides( folders )

    def _get_slides_xml( self, path ):
        # if no slides.xml exists return false
        if ( not ( "True" in xbmc.executehttpapi( "FileExists(%s)" % ( os.path.join( path, "slides.xml" ), ) ) ) ):
            return False, "", "", "", ""
        # fetch data, with hack for change in xbmc so older revisions still work
        xml_data = binascii.a2b_base64( xbmc.executehttpapi( "FileDownload(%s,bare)" % ( os.path.join( path, "slides.xml" ), ) ).split("\r\n\r\n")[ -1 ] )
        # read formats and rating
        try:
            mpaa = re.findall( "<slide rating=\"([^\"]+)\">", xml_data )[ 0 ]
        except:
            mpaa = ""
        question_format = re.findall( "<question format=\"([^\"]+)\" />", xml_data )[ 0 ]
        clue_format = re.findall( "<clue format=\"([^\"]+)\" />", xml_data )[ 0 ]
        answer_format = re.findall( "<answer format=\"([^\"]+)\" />", xml_data )[ 0 ]
        # return results
        return True, mpaa, question_format, clue_format, answer_format

    def _shuffle_slides( self ):
        # randomize the groups and create our play list
        shuffle( self.tmp_slides )
        # now create our final playlist
        print "-----------------------------------------"
        # loop thru slide groups and skip already watched groups
        for slides in self.tmp_slides:
            # has this group been watched
            if ( not self.settings[ "slideshow_unwatched_only" ] or ( slides[ 0 ] and xbmc.getCacheThumbName( slides[ 0 ] ) not in self.watched ) or
                  ( slides[ 1 ] and xbmc.getCacheThumbName( slides[ 1 ] ) not in self.watched ) or
                  ( slides[ 2 ] and xbmc.getCacheThumbName( slides[ 2 ] ) not in self.watched ) ):
                # loop thru slide group only include non blank slides
                for slide in slides:
                    # only add if non blank
                    if ( slide ):
                        # add slide
                        self.slide_playlist += [ slide ]

                print "included - %s, %s, %s" % ( os.path.basename( slides[ 0 ] ), os.path.basename( slides[ 1 ] ), os.path.basename( slides[ 2 ] ), )
            else:
                print "----------------------------------------------------"
                print "skipped - %s, %s, %s" % ( os.path.basename( slides[ 0 ] ), os.path.basename( slides[ 1 ] ), os.path.basename( slides[ 2 ] ), )
                print "----------------------------------------------------"
        print
        print "total slides selected: %d" % len( self.slide_playlist )
        print

    def _next_slide( self, slide=1 ):
        # cancel timer if it's running
        if ( self.slide_timer is not None ):
            self.slide_timer.cancel()
        # increment/decrement count
        self.image_count += slide
        # check for invalid count, TODO: make sure you don't want to reset timer
        if ( self.image_count < 0 ):
            self.image_count = 0
        # if no more slides, exit
        if ( self.image_count > len( self.slide_playlist ) -1 ):
            self._exit_slideshow()
        else:
            print "CHANGED SLIDE:", self.slide_playlist[ self.image_count ]
            # set the property the image control uses
            xbmcgui.Window( xbmcgui.getCurrentWindowId() ).setProperty( "Slide", self.slide_playlist[ self.image_count ] )
            # add id to watched file TODO: maybe don't add if not user preference
            self.watched += [ xbmc.getCacheThumbName( self.slide_playlist[ self.image_count ] ) ]
            # start slide timer
            self._get_slide_timer()

    def _watched_slides_file( self, mode="r" ):
        try:
            # set base watched file path
            base_path = os.path.join( self.BASE_CURRENT_SOURCE_PATH, "slides_watched.txt" )
            # if the path to the source file does not exist create it
            if ( not os.path.isdir( os.path.dirname( base_path ) ) ):
                os.makedirs( os.path.dirname( base_path ) )
            # open source path for reading
            file_object = open( base_path, mode )
            # read/write file
            if ( mode == "r" ):
                # read file
                self.watched = eval( file_object.read() )
            else:
                # write file
                file_object.write( repr( self.watched ) )
            # close file object
            file_object.close()
        except:
            # clear self.watched list for errors only affects read mode
            self.watched = []

    def _start_slideshow_music( self ):
        # did user set this preference
        if ( self.settings[ "slideshow_music" ] and self.settings[ "slideshow_music_folder" ] ):
            # set the volume percent
            xbmc.executebuiltin( "XBMC.SetVolume(%s)" % ( self.settings[ "slideshow_music_volume" ], ) )
            # get playlist
            self.mplaylist = xbmc.PlayList( xbmc.PLAYLIST_MUSIC )
            # clear playlist
            self.mplaylist.clear()
            # get music
            self._get_music_playlist( [ self.settings[ "slideshow_music_folder" ] ] )
            # shuffle playlist
            self.mplaylist.shuffle()
            # start music playlist
            xbmc.Player().play( self.mplaylist )

    def _get_music_playlist( self, paths ):
        # reset folders list
        folders = []
        # enumerate thru paths and fetch slides recursively
        for path in paths:
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( path, ) ).split( "\n" )
            # enumerate through our entries list and combine question, clue, answer
            for entry in entries:
                # remove <li> from item
                entry = entry.replace( "<li>", "" )
                # if folder add to our folder list to recursively fetch songs
                if ( entry.endswith( "/" ) or entry.endswith( "\\" ) ):
                    folders += [ entry.replace( "<li>", "" ) ]
                # add songs to our playlist
                elif ( entry and os.path.splitext( entry )[ 1 ].lower() in xbmc.getSupportedMedia( "music" ) ):
                    self.mplaylist.add( entry )
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._get_music_playlist( folders )

    def _get_slide_timer( self ):
        self.slide_timer = threading.Timer( self.settings[ "slide_time" ], self._next_slide,() )
        self.slide_timer.start()

    def _get_global_timer( self, time, function ):
        self.global_timer = threading.Timer( time, function,() )
        self.global_timer.start()

    def _exit_slideshow( self ):
        # notify we are exiting
        self.exiting = True
        # cancel timers
        self._cancel_timers()
        # save watched slides
        self._watched_slides_file( mode="w" )
        # set the volume back to original
        xbmc.executebuiltin( "XBMC.SetVolume(%s)" % ( self.current_volume, ) )
        # show an end image
        self._show_intro_outro( "outro" )

    def _show_intro_outro( self, type="intro" ):
        if ( type == "outro" ):
            self._play_video_playlist()
        else:
            # start music
            self._start_slideshow_music()
            # start slideshow
            self._next_slide( 0 )
        print "STARTED SLIDESHOW"
        """
        # set the end of slideshow image
        if ( self.settings[ "slideshow_outro_file" ] == "" ):
            self._play_video_playlist()
        else:
            xbmcgui.Window( xbmcgui.getCurrentWindowId() ).setProperty( "Slide", self.settings[ "slideshow_outro_file" ] )
            # set a default timeout
            time = self.settings[ "slide_time" ]
            # play end of slideshow music
            if ( self.settings[ "slideshow_outro_file" ] ):
                xbmc.Player().play( self.settings[ "slideshow_outro_file" ] )
                # set time based on how long the song is
                time = xbmc.Player( xbmc.PLAYLIST_MUSIC ).getTotalTime()
            # start a timer to play video playlist
            self._get_global_timer( time, self._play_video_playlist )
            """

    def _play_video_playlist( self ):
        # set this to -1 as True and False are taken
        self.exiting = -1
        # cancel timers
        self._cancel_timers()
        # turn screensaver back on
        xbmc.executehttpapi( "SetGUISetting(3,screensaver.mode,%s)" % self.screensaver )
        # we play the video playlist here so the screen does not flash
        xbmc.Player().play( self.playlist )
        # close slideshow
        self.close()

    def _cancel_timers( self ):
        # cancel all timers
        if ( self.slide_timer is not None ):
            self.slide_timer.cancel()
            self.slide_timer = None
        if ( self.global_timer is not None ):
            self.global_timer.cancel()
            self.global_timer = None

    def onClick( self, controlId ):
        pass

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        if ( action in self.ACTION_EXIT_SCRIPT and self.exiting is False ):
            self._exit_slideshow()
        elif ( action in self.ACTION_EXIT_SCRIPT and self.exiting is True ):
            self._play_video_playlist()
        elif ( action in self.ACTION_NEXT_SLIDE and not self.exiting ):
            self._next_slide()
        elif ( action in self.ACTION_PREV_SLIDE and not self.exiting ):
            self._next_slide( -1 )
