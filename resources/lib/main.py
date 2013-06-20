###########################################################
"""
    Cinema Experience:
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
import binascii

try:
    import xbmcaddon
except:
    # get xbox compatibility module
    from resources.lib.xbox import *
    xbmcaddon = XBMCADDON()

# Addon class
Addon = xbmcaddon.Addon( id=os.path.basename( os.getcwd() ) )

# notify user of progress
pDialog = xbmcgui.DialogProgress()
pDialog.create( Addon.getAddonInfo( "Name" ), Addon.getLocalizedString( 32820 )  )
pDialog.update( 0 )


class Main:
    # base paths
    BASE_THUMBNAIL_CACHE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )
    BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "script_data", os.path.basename( os.getcwd() ) )
    # total number of playlist items
    PLAYLIST_ITEMS = 12

    def __init__( self ):
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
        ####self.mpaa = ""
        self._set_movie_rating_system()

    def _set_movie_rating_system( self ):
        # MPAA
        if ( Addon.getSetting( "movie_rating_system" ) == "0" ):
            # mpaa ratings
            self.mpaa_ratings = { "G": 0, "PG": 1, "PG-13": 2, "R": 3, "NC-17": 4, None: 5 }
            # used for converting MPAA ratings
            self.mpaa_conversion = None
            # set unrated mpaa
            self.unrated_rating_index = int( Addon.getSetting( "mpaa_nr_rating" ) )
            self.unrated_rating = ( "G", "PG", "PG-13", "R", "NC-17", )[ int( Addon.getSetting( "mpaa_nr_rating" ) ) ]
        # BBFC
        elif ( Addon.getSetting( "movie_rating_system" ) == "1" ):
            # movie ratings
            self.mpaa_ratings = { "Uc": 0, "U": 0, "PG": 1, "12": 2, "12A": 2, "15": 3, "18": 4, "R18": 4, None: 5 }
            # used for converting MPAA ratings
            self.mpaa_conversion = { "G": "U", "PG": "PG", "PG-13": "12", "R": "15", "NC-17": "18" }
            # set unrated mpaa
            self.unrated_rating_index = int( Addon.getSetting( "bbfc_nr_rating" ) )
            self.unrated_rating = ( "Uc", "U", "PG", "12", "12A", "15", "18", "R18", )[ int( Addon.getSetting( "bbfc_nr_rating" ) ) ]

    def _create_experience( self ):
        # spam log file
        LOG( ">>> _create_experience()", heading=True )
        # get the selected video info and set our feature presentation playlist
        title, filename, icon, plot, duration, mpaa, year, genre, studio, writer, director, codec = self._get_feature_presentation_video_info()
        # our playlist
        playlist = []
        # enumerate thru and create our home theater experience
        for item in range( self.PLAYLIST_ITEMS ):
            # python command
            if ( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "1" ):
                playlist += [ [ ( "$COMMAND", Addon.getSetting( "command_script" ), ) ] ]
            # Feature presentation video
            elif ( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "2" ):
                # get listitem for highlighted video
                self._get_special_items(    playlist=playlist,
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
            # get slideshow
            elif ( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "3" ):
                slideshow_duration = ( 5, 10, 15, 20, 25, 30, 45, 60, )[ int( Addon.getSetting( "slideshow_duration" ) ) ] * 60
                slide_duration = ( 5, 7, 10, 15, 20, 30, 60, )[ int( Addon.getSetting( "slide_duration" ) ) ] 
                slides = int( float( slideshow_duration ) / slide_duration ) + 5
                print "slideshow duration: %d seconds" % slideshow_duration
                print "slide duration: %d seconds" % slide_duration
                print "slideshow # slides: %d" % slides
            # get trailers
            elif ( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "4" ):
                self._get_trailers(  playlist=playlist,
                                            mpaa=mpaa,
                                            genre=genre,
                                            studio=studio,
                                            director=director,
                                            movie=os.path.splitext( os.path.basename( filename ) )[ 0 ]
                                        )
            # MPAA rating video
            elif ( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "5" ):
                self._get_special_items(    playlist=playlist,
                                                        items=1 * ( Addon.getSetting( "mpaa_videos_folder" ) != "" ) * ( mpaa != "" ), 
                                                        path=xbmc.translatePath( Addon.getSetting( "mpaa_videos_folder" ) ) + mpaa + ".avi",
                                                        genre=Addon.getLocalizedString( 32486 ),
                                                        studio=Addon.getLocalizedString( 32000 ),
                                                        theme=( Addon.getSetting( "mpaa_videos_theme" ), Addon.getSetting( "mpaa_videos_theme_other" ), )[ Addon.getSetting( "mpaa_videos_theme" ) == "8" ]
                                                    )
            # Dolby/DTS video
            elif ( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "6" ):
                if ( Addon.getSetting( "audio_videos_folder" ) ):
                    self._get_special_items(    playlist=playlist,
                                                            items=1 * ( title != "" ),
                                                            path=xbmc.translatePath( Addon.getSetting( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( codec, "Other" ) + xbmc.translatePath( Addon.getSetting( "audio_videos_folder" ) )[ -1 ],
                                                            genre=Addon.getLocalizedString( 32487 ),
                                                            studio=Addon.getLocalizedString( 32000 ),
                                                            unwatched=Addon.getSetting( "audio_videos_unwatched_only" ) == "true",
                                                            theme=( Addon.getSetting( "audio_videos_theme" ), Addon.getSetting( "audio_videos_theme_other" ), )[ Addon.getSetting( "audio_videos_theme" ) == "8" ]
                                                        )
            # other category videos
            elif ( int( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) ) >= 7 ):
                # settings
                settings = ( "feature_presentation_intro", "slideshow_intro", "coming_attractions_intro", "information_clips", "commercial_clips", "intermission_clips", "other_clips", )
                setting = int( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) ) - 7
                # set media type
                media_type = ( "video", "image", )[ Addon.getSetting( settings[ setting ] + "_type" ) == "1" ]
                # get feature presentation intro videos
                self._get_special_items(    playlist=playlist,
                                                        items=( 1, 1, 2, 3, 4, 5, 10, )[ int( Addon.getSetting( "%s_%s" % ( settings[ setting ], media_type, ) ) ) ] * ( ( Addon.getSetting( "%s_%s" % ( settings[ setting ], media_type, ) ) == "0" and Addon.getSetting( "%s_file_%s" % ( settings[ setting ], media_type, ) ) != "" ) or ( Addon.getSetting( "%s_%s" % ( settings[ setting ], media_type, ) ) != "0" and Addon.getSetting( "%s_folder_%s" % ( settings[ setting ], media_type, ) ) != "" ) ),
                                                        path=( xbmc.translatePath( Addon.getSetting( "%s_file_%s" % ( settings[ setting ], media_type, ) ) ), xbmc.translatePath( Addon.getSetting( "%s_folder_%s" % ( settings[ setting ], media_type, ) ) ), )[ Addon.getSetting( "%s_%s" % ( settings[ setting ], media_type, ) ) != "0" ],
                                                        genre=Addon.getLocalizedString( 32487 + setting ),
                                                        studio=Addon.getLocalizedString( 32000 ),
                                                        media_type=media_type,
                                                        image_duration=( 5, 7, 10, 15, 20, 30, )[ int( Addon.getSetting( settings[ setting ] + "_duration" ) ) ] * ( Addon.getSetting( settings[ setting ] + "_type" ) == "1" ),
                                                        unwatched=Addon.getSetting( "%s_unwatched_only_%s" % ( settings[ setting ], media_type, ) ) == "true",
                                                        limit=Addon.getSetting( "%s_limit_query_%s" % ( settings[ setting ], media_type, ) ) == "true",
                                                        theme=( Addon.getSetting( "%s_theme_%s" % ( settings[ setting ], media_type, ) ), Addon.getSetting( "%s_theme_other_%s" % ( settings[ setting ], media_type, ) ), )[ Addon.getSetting( "%s_theme_%s" % ( settings[ setting ], media_type, ) ) == "8" ]
                                                    )
        
        pDialog.close()
        #vplaylist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        #vplaylist.clear()
        for item in playlist:
            print item
            #for video in item:
            #    print video
                #vplaylist.add( video[0], video[1] )
        #xbmc.Player().play( vplaylist )
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
            # TODO: change this to ListItem.Plot?
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
            mpaa = ( mpaa, "NR", )[ mpaa not in self.mpaa_ratings.keys() ]
            # spew selected video info to log
            LOG( "Title:     %s" % ( title, ) )
            LOG( "Path:      %s" % ( filename, ) )
            LOG( "Icon:      %s" % ( icon, ) )
            LOG( "Plot:      %s" % ( plot, ) )
            LOG( "Duration:  %s" % ( duration, ) )
            LOG( "MPAA:      %s" % ( mpaa, ) )
            LOG( "Year:      %s" % ( year, ) )
            LOG( "Genre:     %s" % ( genre, ) )
            LOG( "Studio:    %s" % ( studio, ) )
            LOG( "Writer:    %s" % ( writer, ) )
            LOG( "Director:  %s" % ( director, ) )
            LOG( "Codec:     %s" % ( codec, ) )
            if ( Addon.getSetting( "audio_videos_folder" ) ):
                LOG( "Audio:     %s" % ( xbmc.translatePath( Addon.getSetting( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( codec, "Other" ) + xbmc.translatePath( Addon.getSetting( "audio_videos_folder" ) )[ -1 ], ) )
        except Exception, e:
            # oops, notify user what error occurred
            LOG( "*** %s" % ( e, ), xbmc.LOGERROR )
            # clear all the info
            title = filename = icon = plot = duration = mpaa = year = genre = studio = writer = director = codec = ""
        # spam log file
        LOG( "<<< _get_feature_presentation_video_info()", heading=True )
        # return results needed to filter trailers and slides
        return title, filename, icon, plot, duration, mpaa, year, genre, studio, writer, director, codec

    def _get_special_items(   self, playlist, items, title="", path="", thumbnail=None, plot="", duration="", mpaa="", release_date="0 0 0", genre="",
                                                studio="", writer="", director="", media_type="video", image_duration=None, unwatched=None, limit=None, theme=None ):
        # return if not user preference
        if ( not items ):
            return
        # if path is a file check if file exists
        if ( os.path.splitext( path )[ 1 ] and not path.startswith( "http://" ) and not ( xbmc.executehttpapi( "FileExists(%s)" % ( path, ) ) == "<li>True" ) ):
            return
        # set default paths list and temp playlist
        self.tmp_paths = [ path ]
        tmp_playlist = []
        # if path is a folder fetch # videos/images
        if ( path.endswith( "/" ) or path.endswith( "\\" ) ):
            # initialize our lists
            self.tmp_paths = []
            # get items
            self._get_items( [ path ], media_type )
            # shuffle items
            shuffle( self.tmp_paths )
        # initialize outside for loop
        listitem = None
        # enumerate thru and add our videos/pictures
        for count in range( items ):
            # set our path
            path = self.tmp_paths[ count ]
            # no listitem for images
            if ( media_type == "video" ):
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
                                                            studio=studio or Addon.getLocalizedString( 32604 ),
                                                            genre=genre or Addon.getLocalizedString( 32605 ),
                                                            writer=writer,
                                                            director=director
                                                        )
            # add our video/picture to the temp playlist
            tmp_playlist += [ ( path, listitem, ) ]
        # add reults to our playlist
        if ( tmp_playlist ):
            playlist += [ tmp_playlist ]

    def _get_items( self, paths, media_type ):
        # reset folders list
        folders = []
        # enumerate thru paths and fetch videos/pictures recursively
        for path in paths:
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( path, ) ).splitlines()
            # enumerate through our entries list and check for valid media type
            for entry in entries:
                # remove <li> from item
                entry = entry.replace( "<li>", "" )
                # if folder add to our folder list to recursively fetch videos/pictures
                if ( entry.endswith( "/" ) or entry.endswith( "\\" ) ):
                    folders += [ entry ]
                # is this a valid video/picture file
                elif ( entry and ( ( media_type == "video" and os.path.splitext( entry )[ 1 ] in xbmc.getSupportedMedia( "video" ) ) or
                    ( media_type == "image" and os.path.splitext( entry )[ 1 ] in xbmc.getSupportedMedia( "picture" ) ) ) ):
                    # add our entry
                    self.tmp_paths += [ entry ]
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._get_items( folders, media_type )

    def _get_slides_xml( self, path ):
        # if no slides.xml exists return false
        if ( not ( "True" in xbmc.executehttpapi( "FileExists(%s)" % ( os.path.join( path, "slides.xml" ), ) ) ) ):
            return False, "", "", "", "", ""
        # fetch data, with hack for change in xbmc so older revisions still work
        xml_data = binascii.a2b_base64( xbmc.executehttpapi( "FileDownload(%s,bare)" % ( os.path.join( path, "slides.xml" ), ) ).split("\r\n\r\n")[ -1 ] )
        # read formats and rating
        mpaa, theme = re.findall( "<slide rating=\"([^\"]*) theme=\"([^\"]*)\">", xml_data )[ 0 ]
        question_format = re.findall( "<question format=\"([^\"]+)\" />", xml_data )[ 0 ]
        clue_format = re.findall( "<clue format=\"([^\"]+)\" />", xml_data )[ 0 ]
        answer_format = re.findall( "<answer format=\"([^\"]+)\" />", xml_data )[ 0 ]
        # return results
        return True, mpaa, theme, question_format, clue_format, answer_format

    def _get_slides( self, paths, media_type ):
        # reset folders list
        folders = []
        # enumerate thru paths and fetch slides recursively
        for path in paths:
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( path, ) ).splitlines()
            # sort in case
            entries.sort()
            # get a slides.xml if it exists
            slidesxml_exists, mpaa, theme, question_format, clue_format, answer_format = self._get_slides_xml( path )
            # check if rating is ok
            if ( slidesxml_exists and self.mpaa_ratings.get( self.mpaa, self.unrated_rating_index ) < self.mpaa_ratings.get( mpaa, self.unrated_rating_index ) ):
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

    def _get_trailers( self, playlist, mpaa, genre, studio, director, movie ):
        # spam log file
        LOG( ">>> _get_trailers(rating: %s, genre: %s, movie: %s)" % ( mpaa, genre, movie, ), heading=True )
        # return if preferences are incorrect
        if ( not ( Addon.getSetting( "trailer_scraper" ) != 2 or ( Addon.getSetting( "trailer_scraper" ) == 2 and Addon.getSetting( "trailer_folder" ) != "" ) ) ):
            return
        # trailer settings, grab them here so we don't need another Addon.getSetting() object
        settings = { "trailer_amt_db_file":  xbmc.translatePath( Addon.getSetting( "trailer_amt_db_file" ) ),
                            "trailer_folder":  xbmc.translatePath( Addon.getSetting( "trailer_folder" ) ),
                            "trailer_rating": Addon.getSetting( "trailer_rating" ),
                            "trailer_limit_query": Addon.getSetting( "trailer_limit_query" ) == "true",
                            "trailer_play_mode": int( Addon.getSetting( "trailer_play_mode" ) ),
                            "trailer_hd_only": Addon.getSetting( "trailer_hd_only" ) == "true",
                            "trailer_quality": int( Addon.getSetting( "trailer_quality" ) ),
                            "trailer_unwatched_only": Addon.getSetting( "trailer_unwatched_only" ) == "true",
                            "trailer_newest_only": Addon.getSetting( "trailer_newest_only" ) == "true",
                            "trailer_count": ( 1, 2, 3, 4, 5, 10, )[ int( Addon.getSetting( "trailer_count" ) ) ],
                            "trailer_scraper": ( "amt_database", "amt_current", "local", )[ int( Addon.getSetting( "trailer_scraper" ) ) ],
                            "trailer_theme": Addon.getSetting( "trailer_theme_type" )
                        }
        # set the proper mpaa rating user preference
        mpaa = ( None, mpaa, )[ Addon.getSetting( "trailer_limit_query" ) == "true" ]
        # get the correct scraper
        exec "from resources.scrapers.%s import scraper as scraper" % ( settings[ "trailer_scraper" ], )
        Scraper = scraper.Main( mpaa, genre, studio, director, settings, movie, self.mpaa_ratings, self.mpaa_conversion, self.unrated_rating_index, self.unrated_rating )
        # fetch trailers
        trailers = Scraper.fetch_trailers()
        # set temp playlist
        tmp_playlist = []
        # enumerate through our list of trailers and add them to our playlist
        for trailer in trailers:
            # get listitem
            listitem = self._get_listitem(
                title=trailer[ 1 ],
                url=trailer[ 2 ],
                thumbnail=trailer[ 3 ],
                plot=trailer[ 4 ],
                duration=trailer[ 5 ],
                mpaa=trailer[ 6 ],
                release_date=trailer[ 7 ] or "0 0 0",
                post_date=trailer[ 8 ] or "0 0 0",
                genre=trailer[ 9 ],
                studio=trailer[ 10 ],
                writer=trailer[ 11 ],
                director=trailer[ 12 ]
            )
            # add our trailer to the temp playlist
            tmp_playlist += [ ( trailer[ 2 ], listitem, ) ]
        # add reults to our playlist
        if ( tmp_playlist ):
            playlist += [ tmp_playlist ]
        # spam log file
        LOG( "<<< _get_trailers()", heading=True )

    def _get_listitem( self, title="", url="", thumbnail=None, plot="", duration="", mpaa="", release_date="0 0 0", post_date="0 0 0", genre="", studio="", writer="", director="" ):
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
        # playlist type
        if ( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "1" ):
            playlist_type = 2
        elif ( Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "3" or Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "4" ):
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
        return
        # if slides folder
        if ( Addon.getSetting( "slideshow_folder" ) ):
            # update dialog with new message
            pDialog.update( -1, Addon.getLocalizedString( 32810 ) )
            # initialize intro/outro lists
            playlist_intro = []
            playlist_outro = []
            """
            # get trivia intro videos
            self._get_special_items(    playlist=playlist_intro,
                                                    items=( 0, 1, 1, 2, 3, 4, 5, )[ int( Addon.getSetting( "trivia_intro" ) ) ], 
                                                    path=( xbmc.translatePath( Addon.getSetting( "trivia_intro_file" ) ), xbmc.translatePath( Addon.getSetting( "trivia_intro_folder" ) ), )[ int( Addon.getSetting( "trivia_intro" ) ) > 1 ],
                                                    genre=Addon.getLocalizedString( 32609 ),
                                                    media_type="video/picture"
                                                )
            # get trivia outro videos
            self._get_special_items(    playlist=playlist_outro,
                                                    items=( 0, 1, 1, 2, 3, 4, 5, )[ int( Addon.getSetting( "trivia_outro" ) ) ], 
                                                    path=( xbmc.translatePath( Addon.getSetting( "trivia_outro_file" ) ), xbmc.translatePath( Addon.getSetting( "trivia_outro_folder" ) ), )[ int( Addon.getSetting( "trivia_outro" ) ) > 1 ],
                                                    genre=Addon.getLocalizedString( 32610 ),
                                                    media_type="video/picture"
                                                )
            """
            # slideshow settings, grab them here so we don't need another Addon.getSetting() object
            settings = {  "slideshow_total_time": ( 5, 10, 15, 20, 30, 45, 60 )[ int( Addon.getSetting( "slideshow_total_time" ) ) ],
                                "slideshow_folder":  xbmc.translatePath( Addon.getSetting( "slideshow_folder" ) ),
                                "slide_time": ( 5, 7, 10, 15, 20, 30, )[ int( Addon.getSetting( "slide_time" ) ) ],
                                "slideshow_intro_playlist": playlist_intro,
                                "slideshow_outro_playlist": playlist_outro,
                                "slideshow_music": Addon.getSetting( "slideshow_music" ) == "true",
                                "slideshow_music_folder":  xbmc.translatePath( Addon.getSetting( "slideshow_music_folder" ) ),
                                "slideshow_music_volume": ( None, "30", "40", "50", "60", "70", "80", "90", "100", )[ int( Addon.getSetting( "slideshow_music_volume" ) ) ],
                                "slideshow_unwatched_only": Addon.getSetting( "slideshow_unwatched_only" ) == "true"
                            }
            # set the proper mpaa rating user preference
            mpaa = ( "", mpaa, )[ Addon.getSetting( "slideshow_limit_query" ) == "true" ]
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

