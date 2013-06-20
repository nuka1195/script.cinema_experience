###########################################################
"""
    Main Player Module:
    - plays # of optional Movie Theater intro videos
    - plays optional slideshow w/ optional music, intro/outro videos/still images
    - plays # of optional random trailers w/ optional intro/outro videos
    - plays highlighted video w/ optional intro/outro videos, rating video and dolby/dts video
    - plays # optional Movie Theater outro videos
"""
############################################################
# main imports
import sys
import os
import xbmcgui
import xbmc

# language method
_L_ = xbmc.Language( scriptPath=os.getcwd() ).getLocalizedString
# settings method
_S_ = xbmc.Settings( path=os.getcwd() ).getSetting

# set proper message
try:
    message = { "ClearWatchedSlides": 32830, "ClearWatchedTrailers": 32840, "ViewChangelog": 32850, "ViewReadme": 32860 }[ sys.argv[ 1 ] ]
except:
    message = 32820

pDialog = xbmcgui.DialogProgress()
pDialog.create( sys.modules[ "__main__" ].__script__, _L_( message )  )
pDialog.update( 0 )

from urllib import quote_plus
from random import shuffle


class Main:
    # base paths
    BASE_CACHE_PATH = os.path.join( xbmc.translatePath( "special://profile" ), "Thumbnails", "Video" )
    BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "script_data", os.path.basename( os.getcwd() ) )

    def __init__( self ):
        # if an arg was passed check it for ClearWatchedSlides or ClearWatchedTrailers
        try:
            if ( sys.argv[ 1 ] == "ClearWatchedSlides" or sys.argv[ 1 ] == "ClearWatchedTrailers" ):
                self._clear_watched_items( sys.argv[ 1 ] )
            elif ( sys.argv[ 1 ] == "ViewChangelog" ):
                self._view_changelog()
            elif ( sys.argv[ 1 ] == "ViewReadme" ):
                self._view_readme()
        except:
            self.playlists = []
            # get the queued video info and set our feature presentation playlist
            fpv_item, mpaa, genre, filename, codec = self._get_queued_video_info()
            # create the playlist
            self._create_playlists( fpv_item=fpv_item, mpaa=mpaa, genre=genre, filename=filename, codec=codec )
            # play the slideshow
            self._play_slideshow( mpaa=mpaa, genre=genre )

    def _clear_watched_items( self, clear_type ):
        # spam log file
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        xbmc.log( ">>> _clear_watched_items( %s )" % ( clear_type, ), xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        # initialize base_path
        base_paths = []
        # clear slides or trailers
        if ( clear_type == "ClearWatchedTrailers" ):
            # trailer settings, grab them here so we don't need another _S_() object
            settings = { "trailer_amt_db_file":  xbmc.translatePath( _S_( "trailer_amt_db_file" ) ) }
            # handle AMT db special
            from resources.scrapers.amt_database import scraper as scraper
            Scraper = scraper.Main( settings=settings )
            # update trailers
            Scraper.clear_watched()
            # set base watched file path
            base_paths += [ os.path.join( self.BASE_CURRENT_SOURCE_PATH, "amt_current_watched.txt" ) ]
            base_paths += [ os.path.join( self.BASE_CURRENT_SOURCE_PATH, "local_watched.txt" ) ]
        else:
            # set base watched file path
            base_paths = [ os.path.join( self.BASE_CURRENT_SOURCE_PATH, "slides_watched.txt" ) ]
        try:
            # set proper message
            message = ( 32831, 32841, )[ sys.argv[ 1 ] == "ClearWatchedTrailers" ]
            # remove watched status file(s)
            for base_path in base_paths:
                # remove file if it exists
                if ( os.path.isfile( base_path ) ):
                    os.remove( base_path )
        except:
            # set proper message
            message = ( 32832, 32842, )[ sys.argv[ 1 ] == "ClearWatchedTrailers" ]
        # close main dialog
        pDialog.close()
        # spam log file
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        xbmc.log( "<<< _clear_watched_items( %s )" % ( clear_type, ), xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        # inform user of result
        ok = xbmcgui.Dialog().ok( _L_( 32000 ), _L_( message ) )

    def _view_changelog( self ):
        # spam log file
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        xbmc.log( ">>> _view_changelog()", xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )

    def _view_readme( self ):
        # spam log file
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        xbmc.log( ">>> _view_readme()", xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )

    def _create_playlists( self, fpv_item, mpaa, genre, filename, codec ):
        # spam log file
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        xbmc.log( ">>> _create_playlist()", xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
        playlist.clear()
        # TODO: try to get a local thumb for special videos?
        # get Dolby/DTS videos
        if ( _S_( "audio_videos_folder" ) ):
            self._get_special_items(    playlist=playlist,
                                                    items=1 * ( _S_( "audio_videos_folder" ) != "" ),
                                                    path=xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( codec, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ],
                                                    genre=_L_( 32606 ),
                                                    ##thumbnail=xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( codec, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ] + "folder.jpg",
                                                    index=0
                                                )
        """
        # get rating video
        self._get_special_items(    playlist=playlist,
                                                items=1 * ( _S_( "rating_videos_folder" ) != "" ), 
                                                path=xbmc.translatePath( _S_( "rating_videos_folder" ) ) + mpaa + ".avi",
                                                genre=_L_( 32603 ),
                                                index=0
                                            )
        # get feature presentation intro videos
        self._get_special_items(    playlist=playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "fpv_intro" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "fpv_intro_file" ) ), xbmc.translatePath( _S_( "fpv_intro_folder" ) ), )[ int( _S_( "fpv_intro" ) ) > 1 ],
                                                genre=_L_( 32601 ),
                                                index=0
                                            )
        # get trailers
        trailers = self._get_trailers(  items=( 0, 1, 2, 3, 4, 5, 10, )[ int( _S_( "trailer_count" ) ) ],
                                                   mpaa=mpaa,
                                                   genre=genre,
                                                   movie=os.path.splitext( os.path.basename( filename ) )[ 0 ]
                                                )
        # get coming attractions outro videos
        self._get_special_items(    playlist=playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "cav_outro" ) ) ] * ( len( trailers ) > 0 ), 
                                                path=( xbmc.translatePath( _S_( "cav_outro_file" ) ), xbmc.translatePath( _S_( "cav_outro_folder" ) ), )[ int( _S_( "cav_outro" ) ) > 1 ],
                                                genre=_L_( 32608 ),
                                                index=0
                                            )
        # enumerate through our list of trailers and add them to our playlist
        for trailer in trailers:
            # get trailers
            self._get_special_items(    playlist=playlist,
                                                    items=1,
                                                    path=trailer[ 2 ],
                                                    genre=trailer[ 9 ] or _L_( 32605 ),
                                                    title=trailer[ 1 ],
                                                    thumbnail=trailer[ 3 ],
                                                    plot=trailer[ 4 ],
                                                    duration=trailer[ 5 ],
                                                    mpaa=trailer[ 6 ],
                                                    release_date=trailer[ 7 ],
                                                    studio=trailer[ 8 ] or _L_( 32604 ),
                                                    writer=trailer[ 10 ],
                                                    director=trailer[ 11 ],
                                                    index=0
                                                )
        # get coming attractions intro videos
        self._get_special_items(    playlist=playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "cav_intro" ) ) ] * ( len( trailers ) > 0 ), 
                                                path=( xbmc.translatePath( _S_( "cav_intro_file" ) ), xbmc.translatePath( _S_( "cav_intro_folder" ) ), )[ int( _S_( "cav_intro" ) ) > 1 ],
                                                genre=_L_( 32600 ),
                                                index=0
                                            )
        # get movie theater experience intro videos
        self._get_special_items(    playlist=playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "mte_intro" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "mte_intro_file" ) ), xbmc.translatePath( _S_( "mte_intro_folder" ) ), )[ int( _S_( "mte_intro" ) ) > 1 ],
                                                genre=_L_( 32607 ),
                                                index=0
                                            )
        # get feature presentation outro videos
        self._get_special_items(    playlist=playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "fpv_outro" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "fpv_outro_file" ) ), xbmc.translatePath( _S_( "fpv_outro_folder" ) ), )[ int( _S_( "fpv_outro" ) ) > 1 ],
                                                genre=_L_( 32602 ),
                                            )
        # get movie theater experience outro videos
        self._get_special_items(    playlist=playlist,
                                                items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "mte_outro" ) ) ], 
                                                path=( xbmc.translatePath( _S_( "mte_outro_file" ) ), xbmc.translatePath( _S_( "mte_outro_folder" ) ), )[ int( _S_( "mte_outro" ) ) > 1 ],
                                                genre=_L_( 32607 ),
                                            )
        
        """
        self.playlists += [ playlist ]

    def _get_queued_video_info( self ):
        try:
            # spam log file
            xbmc.log( "-" * 70, xbmc.LOGNOTICE )
            xbmc.log( ">>> _get_queued_video_info()", xbmc.LOGNOTICE )
            xbmc.log( "-" * 70, xbmc.LOGNOTICE )
            # we store the info here since fpv could be added anywhere in the playlist
            fpv_item = []
            # get all our infolabels
            title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "UTF-8" )
            filename = unicode( xbmc.getInfoLabel( "ListItem.FilenameAndPath" ), "UTF-8" )
            icon = unicode( xbmc.getInfoLabel( "ListItem.Icon" ), "UTF-8" )
            plot = unicode( xbmc.getInfoLabel( "ListItem.PlotOutline" ), "UTF-8" )
            duration = xbmc.getInfoLabel( "ListItem.Duration" )
            mpaa = xbmc.getInfoLabel( "ListItem.MPAA" )
            year = int( xbmc.getInfoLabel( "ListItem.Year" ) )
            studio = unicode( xbmc.getInfoLabel( "ListItem.Studio" ), "UTF-8" )
            genre = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "UTF-8" )
            writer = unicode( xbmc.getInfoLabel( "ListItem.Writer" ), "UTF-8" )
            director = unicode( xbmc.getInfoLabel( "ListItem.Director" ), "UTF-8" )
            codec = xbmc.getInfoLabel( "ListItem.AudioCodec" )
            # TODO: use a new sql for videos queued from files mode, or try an nfo
            """
            if ( title == "" ):
                # get movie name
                movie_title = self.playlist[ 0 ].getdescription()
                # this is used to skip trailer for current movie selection
                movie = os.path.splitext( os.path.basename( self.playlist[ 0 ].getfilename() ) )[ 0 ]
                # format our records start and end
                xbmc.executehttpapi( "SetResponseFormat()" )
                xbmc.executehttpapi( "SetResponseFormat(OpenField,)" )
                # TODO: verify the first is the best audio
                # setup the sql, we limit to 1 record as there can be multiple entries in streamdetails
                sql = "SELECT movie.c12, movie.c14, streamdetails.strAudioCodec FROM movie, streamdetails WHERE movie.idFile=streamdetails.idFile AND streamdetails.iStreamType=1 AND c00='%s' LIMIT 1" % ( movie_title.replace( "'", "''", ), )
                xbmc.log( "SQL: %s" % ( sql, ), xbmc.LOGNOTICE )
                # query database for info dummy is needed as there are two </field> formatters
                mpaa, genre, audio, dummy = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql ), ).split( "</field>" )
            """
            # TODO: verify the last split on a colon is necessary
            # calculate rating
            mpaa = mpaa.split( " " )[ 1 - ( len( mpaa.split( " " ) ) == 1 ) ].split( ":" )[ -1 ]
            mpaa = ( mpaa, "NR", )[ mpaa not in ( "G", "PG", "PG-13", "R", "NC-17", "Unrated", ) ]
            # add highlighted video to playlist
            self._get_special_items( fpv_item, 1, title, filename, icon, plot, duration, mpaa, "0 0 %s" % ( year, ), genre, studio, writer, director )
        except Exception, e:
            # oops, inform user what error occurred
            xbmc.log( "=" * 70, xbmc.LOGNOTICE )
            xbmc.log( "*** _get_queued_video_info(ERROR: %s) ***" % str( e, ), xbmc.LOGNOTICE )
            xbmc.log( "=" * 70, xbmc.LOGNOTICE )
            # clear all the info
            title = filename = icon = plot = duration = mpaa = year = studio = genre = writer = director = codec = ""
        # spew queued video info to log
        xbmc.log( "Title: %s" % ( title, ), xbmc.LOGNOTICE )
        xbmc.log( "Path: %s" % ( filename, ), xbmc.LOGNOTICE )
        xbmc.log( "Icon: %s" % ( icon, ), xbmc.LOGNOTICE )
        xbmc.log( "Year: %s" % ( year, ), xbmc.LOGNOTICE )
        xbmc.log( "Genre: %s" % ( genre, ), xbmc.LOGNOTICE )
        xbmc.log( "Writer: %s" % ( writer, ), xbmc.LOGNOTICE )
        xbmc.log( "Director: %s" % ( director, ), xbmc.LOGNOTICE )
        xbmc.log( "Duration: %s" % ( duration, ), xbmc.LOGNOTICE )
        xbmc.log( "Plot: %s" % ( plot, ), xbmc.LOGNOTICE )
        xbmc.log( "Studio: %s" % ( studio, ), xbmc.LOGNOTICE )
        xbmc.log( "MPAA: %s" % ( mpaa, ), xbmc.LOGNOTICE )
        xbmc.log( "Codec: %s" % ( codec, ), xbmc.LOGNOTICE )
        if ( _S_( "audio_videos_folder" ) ):
            xbmc.log( "Audio: %s" % ( xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( codec, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ], ), xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        xbmc.log( "<<< _get_queued_video_info()", xbmc.LOGNOTICE )
        xbmc.log( "-" * 70, xbmc.LOGNOTICE )
        # return results needed to filter trailers and slides
        return fpv_item, mpaa, genre, filename, codec

    def _get_special_items(   self, playlist, items, title="", path="", thumbnail=None, plot="", duration="", mpaa="",
                                                release_date="0 0 0", genre="", studio="", writer="", director="", index=-1, media_type="video"
                                            ):
        # return if not user preference
        if ( not items ):
            return
        # if path is a file check if file exists
        if ( os.path.splitext( path )[ 1 ] and not path.startswith( "http://" ) and not ( xbmc.executehttpapi( "FileExists(%s)" % ( path, ) ) == "<li>True" ) ):
            return
        # set default paths list
        self.tmp_paths = [ path ]
        # if path is a folder fetch # videos/pictures
        if ( path.endswith( "/" ) or path.endswith( "\\" ) ):
            # initialize our lists
            self.tmp_paths = []
            self._get_items( [ path ], media_type )
            shuffle( self.tmp_paths )
        # enumerate thru and add our videos/pictures
        for count in range( items ):
            # set our path
            path = self.tmp_paths[ count ]
            # format a title (we don't want the ugly extension)
            title = title or os.path.splitext( os.path.basename( path ) )[ 0 ]
            # create the listitem and fill the infolabels
            listitem = self._get_listitem( title=title,
                                                        url=path,
                                                        thumbnail=thumbnail,
                                                        plot=plot,
                                                        duration=duration,
                                                        mpaa=mpaa,
                                                        release_date=release_date,
                                                        studio=studio or _L_( 32604 ),
                                                        genre=genre or _L_( 32605 ),
                                                        writer=writer,
                                                        director=director
                                                    )
            # add our video/picture to the playlist or list
            if ( isinstance( playlist, list ) ):
                playlist += [ ( path, listitem, ) ]
            else:
                playlist.add( path, listitem, index=index )

    def _get_items( self, paths, media_type ):
        # reset folders list
        folders = []
        # enumerate thru paths and fetch videos/pictures recursively
        for path in paths:
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( path, ) ).split( "\n" )
            # enumerate through our entries list and check for valid media type
            for entry in entries:
                # remove <li> from item
                entry = entry.replace( "<li>", "" )
                # if folder add to our folder list to recursively fetch videos/pictures
                if ( entry.endswith( "/" ) or entry.endswith( "\\" ) ):
                    folders += [ entry ]
                # is this a valid video/picture file
                elif ( entry and ( ( media_type.startswith( "video" ) and os.path.splitext( entry )[ 1 ] in xbmc.getSupportedMedia( "video" ) ) or
                    ( media_type.endswith( "picture" ) and os.path.splitext( entry )[ 1 ] in xbmc.getSupportedMedia( "picture" ) ) ) ):
                    # add our entry
                    self.tmp_paths += [ entry ]
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._get_items( folders, media_type )

    def _get_trailers( self, items, mpaa, genre, movie ):
        # return if not user preference
        if ( not items ):
            return []
        # update dialog
        pDialog.update( -1, _L_( 32800 ) )
        # trailer settings, grab them here so we don't need another _S_() object
        settings = { "trailer_amt_db_file":  xbmc.translatePath( _S_( "trailer_amt_db_file" ) ),
                            "trailer_folder":  xbmc.translatePath( _S_( "trailer_folder" ) ),
                            "trailer_rating": _S_( "trailer_rating" ),
                            "trailer_limit_query": _S_( "trailer_limit_query" ) == "true",
                            "trailer_play_mode": int( _S_( "trailer_play_mode" ) ),
                            "trailer_hd_only": _S_( "trailer_hd_only" ) == "true",
                            "trailer_quality": int( _S_( "trailer_quality" ) ),
                            "trailer_unwatched_only": _S_( "trailer_unwatched_only" ) == "true",
                            "trailer_newest_only": _S_( "trailer_newest_only" ) == "true",
                            "trailer_count": ( 0, 1, 2, 3, 4, 5, 10, )[ int( _S_( "trailer_count" ) ) ],
                            "trailer_scraper": ( "amt_database", "amt_current", "local", )[ int( _S_( "trailer_scraper" ) ) ]
                        }
        # get the correct scraper
        exec "from resources.scrapers.%s import scraper as scraper" % ( settings[ "trailer_scraper" ], )
        Scraper = scraper.Main( mpaa, genre, settings, movie )
        # fetch trailers
        trailers = Scraper.fetch_trailers()
        # return results
        return trailers

    def _get_listitem( self, title="", url="", thumbnail=None, plot="", duration="", mpaa="", release_date="0 0 0", studio=_L_( 32604 ), genre="", writer="", director=""):
        # check for a valid thumbnail
        thumbnail = self._get_thumbnail( ( thumbnail, url, )[ thumbnail is None ] )
        # set the default icon
        icon = "DefaultVideo.png"
        # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
        listitem = xbmcgui.ListItem( title, iconImage=icon, thumbnailImage=thumbnail )
        # release date and year
        try:
            parts = release_date.split( " " )
            year = int( parts[ 2 ] )
        except:
            year = 0
        # add the different infolabels we want to sort by
        listitem.setInfo( type="Video", infoLabels={ "Title": title, "Plot": plot, "PlotOutline": plot, "duration": duration, "MPAA": mpaa, "Year": year, "Studio": studio, "Genre": genre, "Writer": writer, "Director": director } )
        # return result
        return listitem

    def _get_thumbnail( self, url ):
        #print url
        # if the cached thumbnail does not exist create the thumbnail based on filepath.tbn
        filename = xbmc.getCacheThumbName( url )
        thumbnail = os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename )
        #print filename
        # if cached thumb does not exist try auto generated
        if ( not os.path.isfile( thumbnail ) ):
            thumbnail = os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], "auto-" + filename )
        # if cached thumb does not exist set default
        if ( not os.path.isfile( thumbnail ) ):
            thumbnail = "DefaultVideo.png"
        # return result
        return thumbnail

    def _play_slideshow( self, mpaa, genre ):
        # if user cancelled dialog return
        if ( pDialog.iscanceled() ):
            pDialog.close()
            return
        # if slides folder
        if ( _S_( "slideshow_folder" ) ):
            # update dialog with new message
            pDialog.update( -1, _L_( 32810 ) )
            # initialize intro/outro lists
            playlist_intro = []
            playlist_outro = []
            """
            # get trivia intro videos
            self._get_special_items(    playlist=playlist_intro,
                                                    items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "trivia_intro" ) ) ], 
                                                    path=( xbmc.translatePath( _S_( "trivia_intro_file" ) ), xbmc.translatePath( _S_( "trivia_intro_folder" ) ), )[ int( _S_( "trivia_intro" ) ) > 1 ],
                                                    genre=_L_( 32609 ),
                                                    media_type="video/picture"
                                                )
            # get trivia outro videos
            self._get_special_items(    playlist=playlist_outro,
                                                    items=( 0, 1, 1, 2, 3, 4, 5, )[ int( _S_( "trivia_outro" ) ) ], 
                                                    path=( xbmc.translatePath( _S_( "trivia_outro_file" ) ), xbmc.translatePath( _S_( "trivia_outro_folder" ) ), )[ int( _S_( "trivia_outro" ) ) > 1 ],
                                                    genre=_L_( 32610 ),
                                                    media_type="video/picture"
                                                )
            """
            # slideshow settings, grab them here so we don't need another _S_() object
            settings = {  "slideshow_total_time": ( 5, 10, 15, 20, 30, 45, 60 )[ int( _S_( "slideshow_total_time" ) ) ],
                                "slideshow_folder":  xbmc.translatePath( _S_( "slideshow_folder" ) ),
                                "slide_time": ( 5, 10, 15, 20, 30, )[ int( _S_( "slide_time" ) ) ],
                                "slideshow_intro_playlist": playlist_intro,
                                "slideshow_outro_playlist": playlist_outro,
                                "slideshow_music": _S_( "slideshow_music" ) == "true",
                                "slideshow_music_folder":  xbmc.translatePath( _S_( "slideshow_music_folder" ) ),
                                "slideshow_music_volume": _S_( "slideshow_music_volume" ).replace( "%", "" ),
                                "slideshow_unwatched_only": _S_( "slideshow_unwatched_only" ) == "true"
                            }
            # set the proper mpaa rating user preference
            mpaa = ( "", mpaa, )[ _S_( "slideshow_limit_query" ) == "true" ]
            #print "MPAA", mpaa
            # import slideshow module and execute the gui
            from resources.lib.xbmcscript_slideshow import Slideshow as Slideshow
            ui = Slideshow( "script-HTExperience-slideshow.xml", os.getcwd(), "default", False, settings=settings, playlist=self.playlists[ 0 ], dialog=pDialog, mpaa=mpaa )
            #ui.doModal()
            del ui
            # we need to activate the video window
            ####xbmc.executebuiltin( "XBMC.ActivateWindow(2005)" )
        else:
            # no slideshow so play the video
            pDialog.close()
            # play the video playlist
            xbmc.Player().play( self.playlists[ 0 ] )


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
