## Experience module: creates playlist

__all__ = [ "Experience" ]

# main imports
import sys
import os
import xbmcgui
import xbmc
from urllib import quote_plus
from random import shuffle
import re

"""
exec "from modules.%s import Command as Command" % ( Addon.getSetting( "action_module" ), )
Command( Addon=Addon ).command( event="resumed" )
"""

class NoFeaturePresentationVideoError( Exception ):
    def __str__( self ):
        return "No feature presentation video selected!"

class Experience:
    """
    Main class to create the cinema experience.
    Returns a list of playlist items.
    """
    # base paths
    BASE_THUMBNAIL_CACHE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )
    # total number of playlist items
    PLAYLIST_ITEMS = 15

    def __init__( self, Addon, dialog ):
        # set our Addon class
        self.Addon = Addon
        # set our dialog
        self.pDialog = dialog
        # initialize variables
        self._init_variables()
        # set rating system
        self._set_movie_rating_system()

    def _init_variables( self ):
        # initialize feature presentation counter
        self.fp_counter = 0
        # get watched list
        self.watched_list = { 
            "slideshow": self._watched_file( category="slideshow" ),
            "clip": self._watched_file( category="clip" ),
            "trailer": self._watched_file( category="trailer" ),
            "codec": self._watched_file( category="codecs" )
        }
        # regex's
        self.regex_slides_xml = re.compile( "<slides?(?:.+?rating=\"([^\"]*)\")?(?:.+?theme=\"([^\"]*)\")?.*?>.+?<question.+?format=\"([^\"]*)\".*?/>.+?<clue.+?format=\"([^\"]*)\".*?/>.+?<answer.+?format=\"([^\"]*)\".*?/>", re.DOTALL | re.IGNORECASE )

    def _set_movie_rating_system( self ):
        # main movie rating system
        self.movie_rating_system = {
            "MPAA": {
                "ratings": { "G": 0, "PG": 1, "PG-13": 2, "R": 3, "NC-17": 4 },#, None: 5
                "conversion": None,#{ "G": "G", "PG": "PG", "PG-13": "PG-13", "R": "R", "NC-17": "NC-17" },
                "unrated_rating": self.Addon.getSetting( "mpaa_nr_rating" )
            },
            "BBFC": {
                "ratings": { "Uc": 0, "U": 0, "PG": 1, "12": 2, "12A": 2, "15": 3, "18": 4, "R18": 4 },#, None: 5
                "conversion": { "G": "U", "PG": "PG", "PG-13": "12", "R": "15", "NC-17": "18" },
                "unrated_rating": self.Addon.getSetting( "bbfc_nr_rating" )
            },
        }[ self.Addon.getSetting( "movie_rating_system" ) ]

    def create_experience( self ):
        # spam log file
        xbmc.log( ">>> _create_experience()", level=xbmc.LOGNOTICE )
        try:
            # get the selected video info and set our feature presentation playlist
            self.fp_videos = self._get_feature_presentation_videos()
        except Exception, e:
            # an error occurred getting feature presentation info
            return str( e )
        # our playlist
        experience = []
        previous = ""
        # enumerate thru and create our home theater experience
        for item in range( 1, self.PLAYLIST_ITEMS + 1 ):
            # set current item type
            current = self.Addon.getSetting( "playlist_item%d" % ( item, ) )
            print [item, "--------------------------------------------",current]
            # Action command
            if ( current == self.Addon.getLocalizedString( 30412 ) ):
                experience += [ { "type": current, "previous": previous, "action": self.Addon.getSetting( "command_script" ) } ]
            # Video clips
            elif ( current == self.Addon.getLocalizedString( 30413 ) ):
                # get video clips
                self._setup_playlist(
                    experience = experience,
                    type = "video",
                    items = [ 1, 1, 2, 3, 4, 5, 10 ][ int( self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) ) ] * ( ( self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) == "0" and self.Addon.getSetting( "playlist_item%d_file" % ( item, ) ) != "" ) or ( self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) != "0" and self.Addon.getSetting( "playlist_item%d_folder" % ( item, ) ) != "" ) ),
                    path = [ xbmc.translatePath( self.Addon.getSetting( "playlist_item%d_file" % ( item, ) ) ), xbmc.translatePath( self.Addon.getSetting( "playlist_item%d_folder" % ( item, ) ) ) ][ self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) != "0" ],
                    isfolder = self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) != "0",
                    studio = self.Addon.getAddonInfo( "Name" ),
                    ##image_duration = int( round( float( self.Addon.getSetting( "playlist_item%d_duration" % ( item, ) ) ) ) ),
                )
            # Coming attractions
            elif ( current == self.Addon.getLocalizedString( 30414 ) ):
                self._setup_playlist(
                    experience = experience,
                    type = "trailer",
                    items = [ 1, 2, 3, 4, 5, 10 ][ int( self.Addon.getSetting( "trailer_count" ) ) ],
                    path = xbmc.translatePath( self.Addon.getSetting( "trailer_folder" ) ),
                    isfolder = True,
                )
            # Dolby/DTS video
            elif ( current == self.Addon.getLocalizedString( 30415 ) ):
                if ( self.Addon.getSetting( "dolby_dts_folder" ) ):
                    self._setup_playlist(
                        experience = experience,
                        type = "codec",
                        items = 1,
                        path = os.path.join( xbmc.translatePath( self.Addon.getSetting( "dolby_dts_folder" ) ), { "dca": "DTS", "dtsma": "DTS-MA", "ac3": "Dolby" }.get( self.fp_videos[ self.fp_counter ][ "codec" ], "Other" ) ),
                        isfolder = True,
                        genre = self.Addon.getLocalizedString( 32487 ),
                        studio = self.Addon.getAddonInfo( "Name" ),
                    )
            # Feature presentation
            elif ( current == self.Addon.getLocalizedString( 30416 ) ):
                # get current feature presentation video
                self._setup_playlist(
                    experience = experience,
                    type = "feature",
                    items = 1 * ( self.fp_videos[ self.fp_counter ][ "title" ] != "" ),
                    title = self.fp_videos[ self.fp_counter ][ "title" ],
                    path = self.fp_videos[ self.fp_counter ][ "filename" ],
                    isfolder = False,
                    thumbnail = self.fp_videos[ self.fp_counter ][ "icon" ],
                    plot = self.fp_videos[ self.fp_counter ][ "plot" ],
                    duration = self.fp_videos[ self.fp_counter ][ "duration" ],
                    mpaa = self.fp_videos[ self.fp_counter ][ "mpaa" ],
                    release_date = "0 0 %s" % ( self.fp_videos[ self.fp_counter ][ "year" ], ),
                    genre = self.fp_videos[ self.fp_counter ][ "genre" ],
                    studio = self.fp_videos[ self.fp_counter ][ "studio" ],
                    writer = self.fp_videos[ self.fp_counter ][ "writer" ],
                    director = self.fp_videos[ self.fp_counter ][ "director" ]
                )
                # increment for next feature presentation
                if ( self.fp_counter < len( self.fp_videos ) - 1 ):
                    self.fp_counter += 1
            # MPAA rating
            elif ( current == self.Addon.getLocalizedString( 30417 ) ):
                self._setup_playlist(
                    experience = experience,
                    type = "mpaa",
                    items = 1 * ( self.Addon.getSetting( "mpaa_ratings_folder" ) != "" ) * ( self.fp_videos[ self.fp_counter ][ "mpaa" ] != "" ), 
                    path = os.path.join( xbmc.translatePath( self.Addon.getSetting( "mpaa_ratings_folder" ) ), self.fp_videos[ self.fp_counter ][ "mpaa" ] + [ ".avi", ".jpg" ][ self.Addon.getSetting( "mpaa_ratings_type" ) == "1" ] ),
                    isfolder = False,
                    genre = self.Addon.getLocalizedString( 32486 ),
                    studio = self.Addon.getAddonInfo( "Name" ),
                    image_duration = int( round( float( self.Addon.getSetting( "mpaa_ratings_duration" ) ) ) ),
                )
            # Music playlist
            elif ( current == self.Addon.getLocalizedString( 30418 ) ):
                experience += [ { "type": "music", "volume": self.Addon.getSetting( "music_volume" ), "playlist": self.Addon.getSetting( "music_playlist" ) } ]
            # Slideshow
            elif ( current == self.Addon.getLocalizedString( 30419 ) ):
                # slideshow duration setting is minutes
                slideshow_duration = int( round( float( self.Addon.getSetting( "slideshow_duration" ) ) ) ) * 60
                # set slide duration in seconds
                slide_duration = int( round( float( self.Addon.getSetting( "slide_duration" ) ) ) )
                # add an extra amount for safety
                slides = int( float( slideshow_duration ) / slide_duration ) + 5
                # setup slideshow
                self._setup_playlist(
                    experience = experience,
                    type = "slideshow",
                    items = slides * ( self.Addon.getSetting( "slideshow_folder" ) != "" ),
                    path = self.Addon.getSetting( "slideshow_folder" ),
                    isfolder = True,
                    slideshow_duration = slideshow_duration,
                    image_duration = slide_duration,
                    play_music = self.Addon.getSetting( "slideshow_music" ) == "true",
                    volume = self.Addon.getSetting( "music_volume" ),
                )
            # set previous item, used for actions
            previous = current
        # spam log file
        xbmc.log( "<<< _create_experience()", level=xbmc.LOGNOTICE )
        # return experience
        return experience

    def _get_feature_presentation_videos( self ):
        # spam log file
        xbmc.log( ">>> _get_feature_presentation_video_info()", level=xbmc.LOGNOTICE )
        # if user prefers using highlighted video
        if ( len( sys.argv ) == 1 ):
            return self._get_currently_selected_video()
        else:
            return self._get_queued_videos()

    def _get_queued_videos( self ):
        # FIXME: enable this
        videos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        #vplaylist.clear()
        for item in range(len(playlist)):
            print item,playlist[item].getdescription()
            #for video in item:
            #    print video
                #vplaylist.add( video[0], video[1] )
        
        # TODO: this is where you can have more videos
        #print ["PLAYER_HAS_INFO", xbmc.getInfoLabel("player.hasvideo"), sys.argv]
        raise NoFeaturePresentationVideoError

    def _get_currently_selected_video( self ):
        # only set feature presentation info if one is highlighted
        if ( not xbmc.getInfoLabel( "ListItem.Title" ) ):
            raise NoFeaturePresentationVideoError
        # TODO: verify the last split on a colon is necessary
        # set mpaa rating
        mpaa = xbmc.getInfoLabel( "ListItem.MPAA" )
        mpaa = mpaa.split( " " )[ 1 - ( len( mpaa.split( " " ) ) == 1 ) ].split( ":" )[ -1 ]
        mpaa = [ mpaa, "NR" ][ mpaa not in self.movie_rating_system[ "ratings" ].keys() ]
        # set our video
        video = [ {
            "title": unicode( xbmc.getInfoLabel( "ListItem.Title" ), "UTF-8" ),
            "filename": xbmc.getInfoLabel( "ListItem.FilenameAndPath" ),
            "icon": xbmc.getInfoLabel( "ListItem.Icon" ),
            "plot": unicode( xbmc.getInfoLabel( "ListItem.PlotOutline" ) or xbmc.getInfoLabel( "ListItem.Plot" ), "UTF-8" ),
            "duration": xbmc.getInfoLabel( "ListItem.Duration" ),
            "mpaa": mpaa,
            "year": int( xbmc.getInfoLabel( "ListItem.Year" ) or 0 ),
            "genre": unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "UTF-8" ),
            "studio": unicode( xbmc.getInfoLabel( "ListItem.Studio" ), "UTF-8" ),
            "writer": unicode( xbmc.getInfoLabel( "ListItem.Writer" ), "UTF-8" ),
            "director": unicode( xbmc.getInfoLabel( "ListItem.Director" ), "UTF-8" ),
            "codec": xbmc.getInfoLabel( "ListItem.AudioCodec" ),
        } ]
        # TODO: remove this spam
        # spew selected video info to log
        xbmc.log( "Title:     %s" % ( video[ 0 ][ "title" ], ) )
        xbmc.log( "Path:      %s" % ( video[ 0 ][ "filename" ], ) )
        xbmc.log( "Icon:      %s" % ( video[ 0 ][ "icon" ], ) )
        xbmc.log( "Plot:      %s" % ( video[ 0 ][ "plot" ], ) )
        xbmc.log( "Duration:  %s" % ( video[ 0 ][ "duration" ], ) )
        xbmc.log( "MPAA:      %s" % ( video[ 0 ][ "mpaa" ], ) )
        xbmc.log( "Year:      %s" % ( video[ 0 ][ "year" ], ) )
        xbmc.log( "Genre:     %s" % ( video[ 0 ][ "genre" ], ) )
        xbmc.log( "Studio:    %s" % ( video[ 0 ][ "studio" ], ) )
        xbmc.log( "Writer:    %s" % ( video[ 0 ][ "writer" ], ) )
        xbmc.log( "Director:  %s" % ( video[ 0 ][ "director" ], ) )
        xbmc.log( "Codec:     %s" % ( video[ 0 ][ "codec" ], ) )
        if ( self.Addon.getSetting( "dolby_dts_folder" ) ):
            xbmc.log( "Audio:     %s" % ( xbmc.translatePath( self.Addon.getSetting( "dolby_dts_folder" ) ) + { "dca": "DTS", "ac3": "Dolby" }.get( video[ 0 ][ "codec" ], "Other" ), ) )
        # spam log file
        xbmc.log( "<<< _get_feature_presentation_video_info()", level=xbmc.LOGNOTICE )
        # return results needed to filter trailers and slides
        return video

    def _setup_playlist( self, **kwargs ):
        # return if no items
        if ( not kwargs[ "items" ] ): return
        # if path is a file check if file exists
        if ( not kwargs[ "isfolder" ] and not kwargs[ "path" ].startswith( "http://" ) and not os.path.isfile( kwargs[ "path" ] ) ): return
        # set default paths list and temp playlist
        self.tmp_playlist = []
        self.tmp_items = []
        # if path is a folder fetch # videos/images
        if ( kwargs[ "isfolder" ] ):
            # get the items
            self._get_items( [ { "slidesxml_exists": False, "path": kwargs[ "path" ], "mpaa": None, "theme": None, "question_format": "", "clue_format": "", "answer_format": "" } ], **kwargs )
            # shuffle and format playlist
            self._shuffle_items( watched=self.watched_list[ kwargs[ "type" ] ], unwatched=self.Addon.getSetting( "experience_prefer_unwatched" ) == "true", firstrun=True, **kwargs )
        else:
            self.tmp_playlist = [ kwargs[ "path" ], self._set_listitem( kwargs[ "path" ], **kwargs ) ]
        # add playlist
        if ( self.tmp_playlist ):
            kwargs[ "experience" ] += [ { 
                "type": kwargs[ "type" ],
                "playlist": self.tmp_playlist,
                "slideshow_duration": kwargs.get( "slideshow_duration", -1 ),
                "image_duration": kwargs.get( "image_duration", -1 ),
                "play_music": kwargs.get( "play_music", False ),
                "volume": kwargs.get( "volume", 0.0 )
            } ]

    def _get_items( self, paths, **kwargs ):#paths, parental_control, experience_theme, slideshow=True ):
        def _get_slides_xml( path ):
            # if no slides.xml exists return dummy
            if ( not os.path.isfile( os.path.join( path[ "path" ], "slides.xml" ) ) ):
                return path[ "slidesxml_exists" ], path[ "mpaa" ], path[ "theme" ], path[ "question_format" ], path[ "clue_format" ], path[ "answer_format" ]
            # fetch data
            xml = open( os.path.join( path[ "path" ], "slides.xml" ) ).read()
            # parse info
            mpaa, theme, question_format, clue_format, answer_format = self.regex_slides_xml.search( xml ).groups()
            # compile regex's for performance
            if ( question_format ):
                question_format = re.compile( question_format, re.IGNORECASE )
            if ( clue_format ):
                clue_format = re.compile( clue_format, re.IGNORECASE )
            if ( answer_format ):
                answer_format = re.compile( answer_format, re.IGNORECASE )
            # return results
            return True, mpaa, theme, question_format, clue_format, answer_format
        # reset folders list
        folders = []
        # set theme
        experience_theme = [ self.Addon.getLocalizedString( 30111 + int( self.Addon.getSetting( "experience_theme" ) ) ), self.Addon.getSetting( "experience_theme_other_text" ) ][ self.Addon.getSetting( "experience_theme" ) == "10" ]
        # enumerate thru paths and fetch slides recursively
        for path in paths:
            # get the directory listing
            entries = os.listdir( self._convert_smb_path( path[ "path" ] ) )
            # sort just in case
            entries.sort()
            # get a slides.xml if it exists
            slidesxml_exists, mpaa, theme, question_format, clue_format, answer_format = _get_slides_xml( path )
            # check if rating is ok
            skip = (
                ( experience_theme != self.Addon.getLocalizedString( 30111 ) and experience_theme.lower() not in str( theme ).lower() ) or
                ( self.Addon.getSetting( "parental_control" ) == "true" and self.movie_rating_system[ "ratings" ].get( self.fp_videos[ self.fp_counter ][ "mpaa" ], self.movie_rating_system[ "ratings" ][ self.movie_rating_system[ "unrated_rating" ] ] ) < self.movie_rating_system[ "ratings" ].get( mpaa, self.movie_rating_system[ "ratings" ][ self.movie_rating_system[ "unrated_rating" ] ] ) )
            )
            if ( skip ):
                xbmc.log( "Skipping files for folder: %s" % ( path[ "path" ], ), level=xbmc.LOGNOTICE )
                xbmc.log( "     Settings Theme: %s - Folder Theme: %s, Movie MPAA: %s - Folder MPAA: %s" % ( experience_theme, theme, self.fp_videos[ self.fp_counter ][ "mpaa" ], mpaa, ), level=xbmc.LOGNOTICE )
            # initialize these to True so we add a new list item to start
            question = clue = answer = True
            # set media types, we may want both image and video types
            if ( kwargs[ "type" ] in [ "video", "codec", "trailer" ] ):
                media_types = xbmc.getSupportedMedia( "video" )
            elif ( kwargs[ "type" ] in [ "slideshow" ] ):
                media_types = xbmc.getSupportedMedia( "picture" )
            else:
                media_types = xbmc.getSupportedMedia( "music" )
            # enumerate through our entries list and get valid items
            for entry in entries:
                # skip slides.xml
                if ( entry == "slides.xml" ): continue
                # join and validate path
                entry = xbmc.validatePath( os.path.join( path[ "path" ], entry ) )
                # if folder add to our folder list to recursively fetch slides
                if ( os.path.isdir( entry ) ):
                    folders += [ { "slidesxml_exists": slidesxml_exists, "path": entry, "mpaa": mpaa, "theme": theme, "question_format": question_format, "clue_format": clue_format, "answer_format": answer_format } ]
                # do we want to skip this entry
                elif ( not skip ):
                    # slides.xml was included, so check it
                    if ( slidesxml_exists and kwargs[ "type" ] == "slideshow" ):
                        # question
                        if ( question_format and question_format.search( os.path.basename( entry ) ) ):
                            if ( question ):
                                self.tmp_items += [ [ "", "", "" ] ]
                                clue = answer = False
                            self.tmp_items[ -1 ][ 0 ] = entry
                        # clue
                        elif ( clue_format and clue_format.search( os.path.basename( entry ) ) ):
                            if ( clue ):
                                self.tmp_items += [ [ "", "", "" ] ]
                                question = answer = False
                            self.tmp_items[ -1 ][ 1 ] = entry
                        # answer
                        elif ( answer_format and answer_format.search( os.path.basename( entry ) ) ):
                            if ( answer ):
                                self.tmp_items += [ [ "", "", "" ] ]
                                question = clue = False
                            self.tmp_items[ -1 ][ 2 ] = entry
                    # no slides.xml or not a slide folder, we add the file as an answer FIXME is find faster? maybe a dict with media_types.get( os.path.splitext( entry )[ 1 ].lower(), False )
                    elif ( entry and os.path.splitext( entry )[ 1 ].lower() in media_types ):
                        self.tmp_items += [ [ "", "", entry ] ]
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._get_items( folders, **kwargs )

    def _shuffle_items( self, watched, unwatched, firstrun=True, **kwargs ):
        # shuffle the groups only on firstrun
        if ( firstrun ):
            shuffle( self.tmp_items )
        # loop thru item groups and add items
        for items in self.tmp_items:
            # loop thru item group and include non blank items
            self.tmp_playlist += [ [ item, self._set_listitem( item, **kwargs ) ] for item in items if item and ( not unwatched or item not in watched ) ]
            # break out if we have enough TODO: verify we want this. if user skips items, you may run out.
            if ( len( self.tmp_playlist ) >= kwargs[ "items" ] ): break
        # if we don't have enough, try again including already watched items
        if ( len( self.tmp_playlist ) < kwargs[ "items" ] and unwatched and firstrun ):
            # reset proper self.watched_list
            self.watched_list[ kwargs[ "type" ] ] = []
            kwargs[ "unwatched" ] = True
            # try again skipping already added items
            self._shuffle_items( watched=[ xbmc.getCacheThumbName( item ) for item in self.tmp_playlist ], firstrun=False, **kwargs )
        print " - total items selected: %d" % len( self.tmp_playlist )

    def _set_listitem( self, item, **kwargs ):
        # no listitem for images
        if ( not os.path.splitext( item )[ 1 ] in xbmc.getSupportedMedia( "video" ) ): return None
        # create the listitem and fill the infolabels
        return self._get_listitem(
            title = kwargs.get( "title", os.path.splitext( os.path.basename( item ) )[ 0 ] ),
            url = item,
            thumbnail = kwargs.get( "thumbnail", None ),
            plot = kwargs.get( "plot", "" ),
            duration = kwargs.get( "duration", "" ),
            mpaa = kwargs.get( "mpaa", "" ),
            release_date = kwargs.get( "release_date", "0 0 0" ),
            studio = kwargs.get( "studio", self.Addon.getAddonInfo( "Name" ) ),
            genre = kwargs.get( "genre", self.Addon.getAddonInfo( "Name" ) ),
            writer = kwargs.get( "writer", "" ),
            director = kwargs.get( "director", "" )
        )

    def _get_listitem( self, **kwargs ):
        # check for a valid thumbnail
        thumbnail = self._get_thumbnail( ( kwargs[ "thumbnail" ], kwargs[ "url" ], )[ kwargs[ "thumbnail" ] is None ] )
        # set listitem
        listitem = xbmcgui.ListItem( kwargs[ "title" ], iconImage="DefaultVideo.png", thumbnailImage=thumbnail )
        # get year from release date
        year = int( kwargs[ "release_date" ].split( " " )[ -1 ] )
        # add other infolabels
        listitem.setInfo( type="Video", infoLabels={ "Title": kwargs[ "title" ], "Plot": kwargs[ "plot" ], "PlotOutline": kwargs[ "plot" ], "duration": kwargs[ "duration" ], "MPAA": kwargs[ "mpaa" ], "Year": year, "Genre": kwargs[ "genre" ], "Studio": kwargs[ "studio" ], "Writer": kwargs[ "writer" ], "Director": kwargs[ "director" ] } )
        # return result
        return listitem

    def _get_trailers( self, **kwargs ):#playlist, type, mpaa, genre, studio, director, movie ):
        # spam log file
        xbmc.log( ">>> _get_trailers(rating: %s, genre: %s, movie: %s)" % ( mpaa, genre, movie, ), level=xbmc.LOGNOTICE )
        # return if preferences are incorrect
        if ( not ( self.Addon.getSetting( "trailer_scraper" ) != 2 or ( self.Addon.getSetting( "trailer_scraper" ) == 2 and self.Addon.getSetting( "trailer_folder" ) != "" ) ) ):
            return
        
        genre = self.fp_videos[ self.fp_counter ][ "genre" ],
        studio = self.fp_videos[ self.fp_counter ][ "studio" ],
        director = self.fp_videos[ self.fp_counter ][ "director" ],
        movie = os.path.splitext( os.path.basename( self.fp_videos[ self.fp_counter ][ "filename" ] ) )[ 0 ],
        
        """
        # trailer settings, grab them here so we don't need another self.Addon.getSetting() object
        settings = {
            "trailer_amt_db_file":  xbmc.translatePath( self.Addon.getSetting( "trailer_amt_db_file" ) ),
            "trailer_folder":  xbmc.translatePath( self.Addon.getSetting( "trailer_folder" ) ),
            "trailer_rating": self.Addon.getSetting( "trailer_rating" ),
            "trailer_limit_query": self.Addon.getSetting( "trailer_limit_query" ) == "true",
            "trailer_play_mode": int( self.Addon.getSetting( "trailer_play_mode" ) ),
            "trailer_hd_only": self.Addon.getSetting( "trailer_hd_only" ) == "true",
            "trailer_quality": int( self.Addon.getSetting( "trailer_quality" ) ),
            "trailer_unwatched_only": self.Addon.getSetting( "trailer_unwatched_only" ) == "true",
            "trailer_newest_only": self.Addon.getSetting( "trailer_newest_only" ) == "true",
            "trailer_count": ( 1, 2, 3, 4, 5, 10, )[ int( self.Addon.getSetting( "trailer_count" ) ) ],
            "trailer_scraper": ( "amt_database", "amt_current", "local", )[ int( self.Addon.getSetting( "trailer_scraper" ) ) ],
            "trailer_theme": self.Addon.getSetting( "trailer_theme_type" )
        }
        # set the proper mpaa rating user preference
        mpaa = ( None, mpaa, )[ self.Addon.getSetting( "trailer_limit_query" ) == "true" ]
        # get the correct scraper
        exec "from resources.scrapers.%s import scraper as scraper" % ( settings[ "trailer_scraper" ], )
        Scraper = scraper.Main( mpaa, genre, studio, director, settings, movie, self.movie_rating_system )
        # fetch trailers
        trailers = Scraper.fetch_trailers()
        # set temp playlist
        tmp_playlist = []
        # enumerate through our list of trailers and add them to our playlist
        for trailer in trailers:
            # get listitem
            listitem = self._get_listitem(
                title = trailer[ 1 ],
                url = trailer[ 2 ],
                thumbnail = trailer[ 3 ],
                plot = trailer[ 4 ],
                duration = trailer[ 5 ],
                mpaa = trailer[ 6 ],
                release_date = trailer[ 7 ] or "0 0 0",
                post_date = trailer[ 8 ] or "0 0 0",
                genre = trailer[ 9 ],
                studio = trailer[ 10 ],
                writer = trailer[ 11 ],
                director = trailer[ 12 ]
            )
            # add our trailer to the temp playlist
            tmp_playlist += [ ( trailer[ 2 ], listitem, ) ]
        # add reults to our playlist
        if ( tmp_playlist ):
            kwargs[ "experience" ] += [ tmp_playlist ]
        """
        # spam log file
        xbmc.log( "<<< _get_trailers()", level=xbmc.LOGNOTICE )

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

    def _convert_smb_path( self, _path ):
        # if windows and smb:// convert to a proper format for shutil and os modules
        if ( _path.startswith( "smb://" ) and os.environ.get( "OS", "win32" ) == "win32" ):
            _path = _path.replace( "/", "\\" ).replace( "smb:", "" )
        # return result
        return _path

    def _watched_file( self, category, watched=[] ):
        try:
            # create path to watched file
            _path = os.path.join( self.Addon.getAddonInfo( "Profile" ), "%s_watched.txt" % ( category, ) )
            # read/write watched file
            if ( watched ):
                # save watched file
                open( _path, "w" ).write( repr( watched ) )
            else:
                # read watched file
                return eval( open( _path, "r" ).read() )
        except Exception, e:
            # log message
            xbmc.log( "Experience::_watched_file              (message='Missing or invalid watched file', path=%s)" % ( repr( _path ), ), xbmc.LOGNOTICE )
            # return empty list
            return []
