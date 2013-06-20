###########################################################
"""
    Home Theater Experience:
    - creates a movie theater experience in the privacy of your home
    
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
from urllib import quote_plus
from random import shuffle
from utils import LOG

# language method
_L_ = xbmc.Language( scriptPath=os.getcwd() ).getLocalizedString
# settings method
_S_ = xbmc.Settings( path=os.getcwd() ).getSetting

# set proper message
try:
    message = { "ResetWatchedStatus=slides": 32830, "ResetWatchedStatus=trailers": 32840, "ViewChangelog": 32850, "ViewReadme": 32860 }[ sys.argv[ 1 ] ]
except:
    message = 32820

# notify user of progress
pDialog = xbmcgui.DialogProgress()
pDialog.create( sys.modules[ "__main__" ].__script__, _L_( message )  )
pDialog.update( 0 )


class Main:
    # base paths
    BASE_THUMBNAIL_CACHE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )
    BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "script_data", os.path.basename( os.getcwd() ) )

    def __init__( self ):
        # if an arg was passed check it for ResetWatchedStatusSlides or ResetWatchedStatusTrailers
        try:
            if ( sys.argv[ 1 ] == "ResetWatchedStatus=slides" or sys.argv[ 1 ] == "ResetWatchedStatus=trailers" ):
                self._reset_watched_status( sys.argv[ 1 ].split( "=" )[ 1 ] )
            elif ( sys.argv[ 1 ] == "ViewChangelog" ):
                self._view_changelog()
            elif ( sys.argv[ 1 ] == "ViewReadme" ):
                self._view_readme()
        except:
            # initialize variables
            self._init_variables()
            # create the experience
            self._create_experience()
            # play the experience
            ##self._play_experience()

    def _init_variables( self ):
        self.playlists = []
        self.playlist = 0
        self.playlist_count = 0
        self.playlist_type = -1 # 0=video, 1=slideshow, 2=command
        self.python_command = 0
        self.mpaa = ""
        self.genre = ""

    def _reset_watched_status( self, reset_type ):
        # spam log file
        LOG( ">>> _reset_watched_status( %s )" % ( reset_type, ), heading=True )
        # initialize base_path
        base_paths = []
        # clear slides or trailers
        if ( reset_type == "trailers" ):
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
            # set proper messages
            message = ( 32831, 32841, )[ reset_type == "trailers" ]
            # remove watched status file(s)
            for base_path in base_paths:
                # remove file if it exists
                if ( os.path.isfile( base_path ) ):
                    os.remove( base_path )
            # spam log with result
            LOG( "Resetting %s watched status succeeded." % ( reset_type, ) )
        except Exception, e:
            # set proper messages and log level
            message = ( 32832, 32842, )[ reset_type == "trailers" ]
            # spam log with result
            LOG( "Resetting %s watched status failed! - (%s)" % ( reset_type, str( e ), ), xbmc.LOGERROR )
        # spam log file
        LOG( "<<< _reset_watched_status( %s )" % ( reset_type, ), heading=True )
        # close main dialog
        pDialog.close()
        # notify user of result
        ok = xbmcgui.Dialog().ok( _L_( 32000 ), _L_( message ) )

    def _view_changelog( self ):
        # spam log file
        LOG( ">>> _view_changelog()", heading=True )

    def _view_readme( self ):
        # spam log file
        LOG( ">>> _view_readme()", heading=True )

    def _create_experience( self ):
        # spam log file
        LOG( ">>> _create_experience()", heading=True )
        # get the selected video info and set our feature presentation playlist
        title, filename, icon, plot, duration, mpaa, year, genre, studio, writer, director, codec = self._get_feature_presentation_video_info()
        # enumerate thru and create our home theater experience
        for item in range( 12 ):
            # playlist type
            if ( _S_( "playlist_item%d" % ( item + 1, ) ) == "1" ):
                playlist_type = 2
            elif ( _S_( "playlist_item%d" % ( item + 1, ) ) == "3" or _S_( "playlist_item%d" % ( item + 1, ) ) == "4" ):
                playlist_type = 1
            else:
                playlist_type = 0
            # create playlists
            if ( playlist_type != self.playlist_type ):
                self.playlist_count += 1
                self.playlists += [ [] ]
                self.playlist_type = playlist_type
                if ( playlist_type == 0 ):
                    self.playlists[ self.playlist_count - 1 ] = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
                    self.playlists[ self.playlist ].clear()
            # python command
            if ( _S_( "playlist_item%d" % ( item + 1, ) ) == "1" ):
                self.playlists[ self.playlist_count - 1 ] = "$COMMAND"
            # Feature presentation video
            elif ( _S_( "playlist_item%d" % ( item + 1, ) ) == "2" ):
                # get listitem for highlighted video
                self._get_special_items(    playlist=self.playlists[ self.playlist_count - 1 ],
                                                        items=1 * ( title != "" ),
                                                        title=title,
                                                        path=filename,
                                                        thumbnail=icon,
                                                        plot=plot,
                                                        duration=duration,
                                                        mpaa=mpaa,
                                                        release_date="0 0 %s" % ( year, ),
                                                        genre=genre,
                                                        studio=studio,
                                                        writer=writer,
                                                        director=director
                                                    )
            # get trailers
            elif ( _S_( "playlist_item%d" % ( item + 1, ) ) == "5" ):
                self._get_trailers(  playlist=self.playlists[ self.playlist_count - 1 ],
                                            mpaa=mpaa,
                                            genre=genre,
                                            movie=os.path.splitext( os.path.basename( filename ) )[ 0 ]
                                        )
            # MPAA rating video
            elif ( _S_( "playlist_item%d" % ( item + 1, ) ) == "6" ):
                self._get_special_items(    playlist=self.playlists[ self.playlist_count - 1 ],
                                                        items=1 * ( _S_( "mpaa_videos_folder" ) != "" ) * ( mpaa != "" ), 
                                                        path=xbmc.translatePath( _S_( "mpaa_videos_folder" ) ) + mpaa + ".avi",
                                                        genre=_L_( 32486 ),
                                                        studio=_L_( 32000 )
                                                    )
            # Dolby/DTS video
            elif ( _S_( "playlist_item%d" % ( item + 1, ) ) == "7" ):
                if ( _S_( "audio_videos_folder" ) ):
                    self._get_special_items(    playlist=self.playlists[ self.playlist_count - 1 ],
                                                            items=1 * ( title != "" ),
                                                            path=xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( codec, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ],
                                                            genre=_L_( 32487 ),
                                                            studio=_L_( 32000 )
                                                        )
            # other category videos
            elif ( int( _S_( "playlist_item%d" % ( item + 1, ) ) ) >= 8 ):
                # settings
                settings = ( "feature_presentation_intro", "slideshow_intro", "coming_attractions_intro", "information_clips", "commercial_clips", "intermission_clips", "other_clips", )
                setting = int( _S_( "playlist_item%d" % ( item + 1, ) ) ) - 8
                # get feature presentation intro videos
                self._get_special_items(    playlist=self.playlists[ self.playlist_count - 1 ],
                                                        items=( 1, 1, 2, 3, 4, 5, 10, )[ int( _S_( settings[ setting ] ) ) ] * ( ( _S_( settings[ setting ] ) == "0" and _S_( settings[ setting ] + "_file" ) != "" ) or ( _S_( settings[ setting ] ) != "0" and _S_( settings[ setting ] + "_folder" ) != "" ) ),
                                                        path=( xbmc.translatePath( _S_( settings[ setting ] + "_file" ) ), xbmc.translatePath( _S_( settings[ setting ] + "_folder" ) ), )[ int( _S_( settings[ setting ] ) ) > 0 ],
                                                        genre=_L_( 32480 + int( _S_( "playlist_item%d" % ( item + 1, ) ) ) ),
                                                        studio=_L_( 32000 )
                                                    )
            """
    <string id="8">Feature presentation intro</string>
    <string id="9">Slideshow intro</string>
    <string id="10">Coming attractions intro</string>
    <string id="11">Information clip(s)</string>
    <string id="12">Commercial clip(s)</string>
    <string id="13">Intermission clip(s)</string>
    <string id="14">Other clip(s)</string>

    <string id="32190">Single video/image</string>
    <string id="32191">1 Random video/image</string>
    <string id="32192">2 Random videos/images</string>
    <string id="32193">3 Random videos/images</string>
    <string id="32194">4 Random videos/images</string>
    <string id="32195">5 Random videos/images</string>
    <string id="32196">10 Random videos/images</string>
    <string id="32197">15 Random videos/images</string>
    <string id="32198">20 Random videos/images</string>
    <string id="32199">25 Random videos/images</string>
            """
        
        
        pDialog.close()
        xbmc.Player().play( self.playlists[ self.playlist ] )
        """
    <string id="0">None</string>
    <string id="1">Execute command</string>
    <string id="2">Feature presentation</string>
    <string id="3">Slideshow</string>
    <string id="4">Slideshow (Theme)</string>
    <string id="5">Movie trailer(s)</string>
    <string id="6">MPAA rating video</string>
    <string id="7">Dolby/DTS video</string>
    <string id="8">Feature presentation intro</string>
    <string id="9">Slideshow intro</string>
    <string id="10">Coming attractions intro</string>
    <string id="11">Information clip(s)</string>
    <string id="12">Commercial clip(s)</string>
    <string id="13">Intermission clip(s)</string>
    <string id="14">Other clip(s)</string>
        """
        """
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
        
        self.playlists += [ playlist ]
        """
        # spam log file
        LOG( "<<< _create_experience()", heading=True )

    def _get_feature_presentation_video_info( self ):
        try:
            # spam log file
            LOG( ">>> _get_feature_presentation_video_info()", heading=True )
            # get all our infolabels
            title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "UTF-8" )
            # only set feature presentation info if one is highlighted
            if ( not title ):
                raise NoFeaturePresentationVideoError
            # get other infolabels
            filename = unicode( xbmc.getInfoLabel( "ListItem.FilenameAndPath" ), "UTF-8" )
            icon = xbmc.getInfoLabel( "ListItem.Icon" )
            plot = unicode( xbmc.getInfoLabel( "ListItem.PlotOutline" ), "UTF-8" )
            duration = xbmc.getInfoLabel( "ListItem.Duration" )
            mpaa = xbmc.getInfoLabel( "ListItem.MPAA" )
            try: year = int( xbmc.getInfoLabel( "ListItem.Year" ) )
            except: year = 0
            genre = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "UTF-8" )
            studio = unicode( xbmc.getInfoLabel( "ListItem.Studio" ), "UTF-8" )
            writer = unicode( xbmc.getInfoLabel( "ListItem.Writer" ), "UTF-8" )
            director = unicode( xbmc.getInfoLabel( "ListItem.Director" ), "UTF-8" )
            codec = xbmc.getInfoLabel( "ListItem.AudioCodec" )
            # TODO: verify the last split on a colon is necessary
            # calculate rating
            mpaa = mpaa.split( " " )[ 1 - ( len( mpaa.split( " " ) ) == 1 ) ].split( ":" )[ -1 ]
            mpaa = ( mpaa, "NR", )[ mpaa not in ( "G", "PG", "PG-13", "R", "NC-17", "Unrated", ) ]
            # spew selected video info to log
            LOG( "Title: %s" % ( title, ) )
            LOG( "Path: %s" % ( filename, ) )
            LOG( "Icon: %s" % ( icon, ) )
            LOG( "Plot: %s" % ( plot, ) )
            LOG( "Duration: %s" % ( duration, ) )
            LOG( "MPAA: %s" % ( mpaa, ) )
            LOG( "Year: %s" % ( year, ) )
            LOG( "Genre: %s" % ( genre, ) )
            LOG( "Studio: %s" % ( studio, ) )
            LOG( "Writer: %s" % ( writer, ) )
            LOG( "Director: %s" % ( director, ) )
            LOG( "Codec: %s" % ( codec, ) )
            if ( _S_( "audio_videos_folder" ) ):
                LOG( "Audio: %s" % ( xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( codec, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ], ) )
        except Exception, e:
            # oops, notify user what error occurred
            LOG( str( e ), xbmc.LOGERROR )
            # clear all the info
            title = filename = icon = plot = duration = mpaa = year = genre = studio = writer = director = codec = ""
        # spam log file
        LOG( "<<< _get_feature_presentation_video_info()", heading=True )
        # return results needed to filter trailers and slides
        return title, filename, icon, plot, duration, mpaa, year, genre, studio, writer, director, codec

    def _get_special_items(   self, playlist, items, title="", path="", thumbnail=None, plot="", duration="", mpaa="",
                                                release_date="0 0 0", genre="", studio="", writer="", director="", media_type="video"
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
            # get items
            self._get_items( [ path ], media_type )
            # shuffle items
            shuffle( self.tmp_paths )
        # enumerate thru and add our videos/pictures
        for count in range( items ):
            # set our path
            path = self.tmp_paths[ count ]
            #### if pictures listitem = None
            # format a title (we don't want the ugly extension)
            title2 = title or os.path.splitext( os.path.basename( path ) )[ 0 ]
            # create the listitem and fill the infolabels
            listitem = self._get_listitem( title=title2,
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
            ## add our video/picture to the playlist or list
            if ( isinstance( playlist, list ) ):
                playlist += [ ( path, listitem, ) ]
            else:
                playlist.add( path, listitem )

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

    def _get_trailers( self, playlist, mpaa, genre, movie ):
        # return if preferences are incorrect
        if ( not ( _S_( "trailer_scraper" ) != 2 or ( _S_( "trailer_scraper" ) == 2 and _S_( "trailer_folder" ) != "" ) ) ):
            return
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
                            "trailer_count": ( 1, 2, 3, 4, 5, 10, )[ int( _S_( "trailer_count" ) ) ],
                            "trailer_scraper": ( "amt_database", "amt_current", "local", )[ int( _S_( "trailer_scraper" ) ) ]
                        }
        # get the correct scraper
        exec "from resources.scrapers.%s import scraper as scraper" % ( settings[ "trailer_scraper" ], )
        Scraper = scraper.Main( mpaa, genre, settings, movie )
        # fetch trailers
        trailers = Scraper.fetch_trailers()
        # enumerate through our list of trailers and add them to our playlist
        for trailer in trailers:
            # get listitem
            listitem = self._get_listitem( title=trailer[ 1 ],
                                                        url=trailer[ 2 ],
                                                        thumbnail=trailer[ 3 ],
                                                        plot=trailer[ 4 ],
                                                        duration=trailer[ 5 ],
                                                        mpaa=trailer[ 6 ],
                                                        release_date=trailer[ 7 ] or "0 0 0",
                                                        genre=trailer[ 9 ],
                                                        studio=trailer[ 8 ],
                                                        writer=trailer[ 10 ],
                                                        director=trailer[ 11 ]
                                                    )
            # add trailer to playlist
            playlist.add( trailer[ 2 ], listitem )

    def _get_listitem( self, title="", url="", thumbnail=None, plot="", duration="", mpaa="", release_date="0 0 0", genre="", studio="", writer="", director="" ):
        # check for a valid thumbnail
        thumbnail = self._get_thumbnail( ( thumbnail, url, )[ thumbnail is None ] )
        # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
        listitem = xbmcgui.ListItem( title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail )
        # get year from release date
        year = int( release_date.split( " " )[ 2 ] )
        # add the different infolabels we want to sort by
        listitem.setInfo( type="Video", infoLabels={ "Title": title, "Plot": plot, "PlotOutline": plot, "duration": duration, "MPAA": mpaa, "Year": year, "Genre": genre, "Studio": studio, "Writer": writer, "Director": director } )
        # return result
        return listitem

    def _get_thumbnail( self, url ):
        # if url already is a cached thumb, return it
        if ( url.endswith( ".tbn" ) ):
            return url
        # if the cached thumbnail does not exist create the thumbnail based on filepath.tbn
        filename = xbmc.getCacheThumbName( url )
        thumbnail = os.path.join( self.BASE_THUMBNAIL_CACHE_PATH, filename[ 0 ], filename )
        # if cached thumb does not exist try auto generated
        if ( not os.path.isfile( thumbnail ) ):
            thumbnail = os.path.join( self.BASE_THUMBNAIL_CACHE_PATH, filename[ 0 ], "auto-" + filename )
        # if cached thumb does not exist set default
        if ( not os.path.isfile( thumbnail ) ):
            thumbnail = "DefaultVideo.png"
        # return result
        return thumbnail

    def _play_experience( self ):
        # if user cancelled dialog return
        if ( pDialog.iscanceled() ):
            pDialog.close()
            return
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
            from resources.lib.player import Player as Player
            ui = Player( "script-HTExperience-slideshow.xml", os.getcwd(), "default", False, settings=settings, playlist=self.playlists[ 0 ], dialog=pDialog, mpaa=mpaa )
            #ui.doModal()
            del ui
            # we need to activate the video window
            ####xbmc.executebuiltin( "XBMC.ActivateWindow(2005)" )
        else:
            # no slideshow so play the video
            pDialog.close()
            # play the video playlist
            xbmc.Player().play( self.playlists[ 0 ] )


class NoFeaturePresentationVideoError( Exception ):
    def __str__( self ):
        return "No feature presentation video selected!"

