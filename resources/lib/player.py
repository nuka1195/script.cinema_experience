# main imports
import os
import xbmcgui
import xbmc

import threading
import binascii
from random import shuffle
import re


class XBMCPlayer( xbmc.Player ):
    """ 
        Player Class: Subclass of XBMC Player class. Allows calling function
        when video/audio changes or playback ends.
    """
    def __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )
        # this is the function to call when a player event occurs
        self.function = kwargs[ "function" ]

    def onPlayBackStarted( self ):
        # we use this if we want to run anything at start, like a script
        self.function( "started" )

    def onPlayBackResumed( self ):
        # handle resumed event
        self.function( "resumed" )

    def onPlayBackPaused( self ):
        # handle paused event
        self.function( "paused" )

    def onPlayBackStopped( self ):
        # we handle stopped differently than ended
        self.function( "stopped" )

    def onPlayBackEnded( self ):
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
        # initialize our class variable
        self._init_variables()
        # turn screensaver off
        xbmc.executehttpapi( "SetGUISetting(3,screensaver.mode,None)" )
        try: ##TODO: remove this try block when done
            # close dialog
            kwargs[ "dialog" ].close()
            #display slideshow
            self.doModal()
        except:
            import traceback
            traceback.print_exc()
            raise

    def onInit( self ):
        # get current python window
        self.WINDOW = xbmcgui.Window( xbmcgui.getCurrentWindowId() )

    def onAction( self, action ):
        if ( action in self.ACTION_EXIT_SCRIPT and self.exiting is False ):
            self._exit_slideshow()
        elif ( action in self.ACTION_EXIT_SCRIPT and self.exiting is True ):
            self._play_video_playlist()
        elif ( action in self.ACTION_NEXT_SLIDE and not self.exiting ):
            self._next_slide()
        elif ( action in self.ACTION_PREV_SLIDE and not self.exiting ):
            self._next_slide( -1 )

    def onClick( self, controlId ):
        pass

    def onFocus( self, controlId ):
        pass

    def _init_variables( self ):
        self.global_timer = None
        self.slide_timer = None
        self.exiting = False
        # get current screensaver
        self.screensaver = xbmc.executehttpapi( "GetGUISetting(3;screensaver.mode)" ).replace( "<li>", "" )
        # get the current volume, infolabel returns '-12.0 dB' format
        self.current_volume = int( ( 1 - abs( float( xbmc.getInfoLabel( "Player.Volume" ).split( " " )[ 0 ] ) ) / 60 ) * 100 )
        # our complete shuffled list of slides
        self.slide_playlist = []
        self.tmp_slides = []
        self.image_count = 0

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
            self.WINDOW.setProperty( "Slide", self.slide_playlist[ self.image_count ] )
            # add id to watched file TODO: maybe don't add if not user preference
            if ( self.settings[ "slideshow_unwatched_only" ] ):
                self.watched += [ xbmc.getCacheThumbName( self.slide_playlist[ self.image_count ] ) ]
            # start slide timer
            self._get_slide_timer()

    def _start_slideshow_music( self ):
        # did user set this preference
        if ( self.settings[ "slideshow_music" ] and self.settings[ "slideshow_music_folder" ] ):
            # set the volume percent
            if ( self.settings[ "slideshow_music_volume" ] is not None ):
                self._fade_volume( self.settings[ "slideshow_music_volume" ], )
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

    ## I store volume in playlist
    def _fade_volume( self, out=True, volume=0 ):
        ##############################################
        ##volume = int( ( 1 - abs( float( self.Addon.getSetting( "slideshow_music_volume" ) ) ) / 60 ) * 100 )
        ##volume = int( ( 1 - abs( float( xbmc.getInfoLabel( "Player.Volume" ).split( " " )[ 0 ] ) ) / 60 ) * 100 )
        # set initial start/end values
        volumes = range( 1, volume + 1 )
        # if fading out reverse order
        if ( out ):
            volumes.reverse()
        # calc sleep time, 2 seconds for fade time
        sleep_time = int( float( 2000 ) / len( volumes ) )
        # loop thru and set volume
        for volume in volumes:
            xbmc.executebuiltin( "XBMC.SetVolume(%d)" % ( volume, ) )
            # sleep
            xbmc.sleep( sleep_time )

    def _get_slide_timer( self ):
        self.slide_timer = threading.Timer( self.settings[ "slide_time" ], self._next_slide,() )
        self.slide_timer.start()

    def _get_global_timer( self, time, function ):
        self.global_timer = threading.Timer( time, function,() )
        self.global_timer.start()
        # start our trvia slideshow timer
        ##self._get_global_timer( self.settings[ "slideshow_total_time" ] * 60, self._exit_slideshow )

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

    def _cancel_timers( self ):
        # cancel all timers
        if ( self.slide_timer is not None ):
            self.slide_timer.cancel()
            self.slide_timer = None
        if ( self.global_timer is not None ):
            self.global_timer.cancel()
            self.global_timer = None
