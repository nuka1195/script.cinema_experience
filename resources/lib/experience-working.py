""" Experience module """

__all__ = [ "Experience" ]

# main imports
import sys
import os
import xbmcgui
import xbmc
from urllib import quote_plus
from random import shuffle
import re


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
    BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "script_data", os.path.basename( os.getcwd() ) )
    # total number of playlist items
    PLAYLIST_ITEMS = 15

    def __init__( self, Addon, dialog ):
        self.Addon = Addon
        self.pDialog = dialog# initialize variables
        self._init_variables()

    def _init_variables( self ):
        self.feature_presentation = 0

        self.playlists = []
        self.playlist = 0
        self.playlist_count = 0
        self.playlist_type = -1 # 0=video, 1=slideshow, 2=command
        self.python_command = 0
        ####self.mpaa = ""
        self._set_movie_rating_system()

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

    def _create_experience( self ):
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
            # Python command
            if ( current == self.Addon.getLocalizedString( 30412 ) ):
                experience += [ { "type": current, "previous": previous, "action": self.Addon.getSetting( "command_script" ) } ]
            # Clips
            elif ( current == self.Addon.getLocalizedString( 30413 ) ):
                # get image/video clips
                self._get_special_items(
                    experience = experience,
                    type = "clip",
                    items = [ 1, 1, 2, 3, 4, 5, 10 ][ int( self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) ) ] * ( ( self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) == "0" and self.Addon.getSetting( "playlist_item%d_file" % ( item, ) ) != "" ) or ( self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) != "0" and self.Addon.getSetting( "playlist_item%d_folder" % ( item, ) ) != "" ) ),
                    path = [ xbmc.translatePath( self.Addon.getSetting( "playlist_item%d_file" % ( item, ) ) ), xbmc.translatePath( self.Addon.getSetting( "playlist_item%d_folder" % ( item, ) ) ) ][ self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) != "0" ],
                    isfolder = self.Addon.getSetting( "playlist_item%d_number" % ( item, ) ) != "0",
                    studio = self.Addon.getAddonInfo( "Name" ),
                    image_duration = int( round( float( self.Addon.getSetting( "playlist_item%d_duration" % ( item, ) ) ) ) ),
                    mpaa = self.fp_videos[ self.feature_presentation ][ "mpaa" ],
                    unwatched = self.Addon.getSetting( "experience_prefer_unwatched" ) == "true",
                    parental_control = self.Addon.getSetting( "parental_control" ) == "true",
                    experience_theme = [ self.Addon.getSetting( "experience_theme" ), self.Addon.getSetting( "experience_theme_other_text" ) ][ self.Addon.getSetting( "experience_theme" ) == "10" ],
                )
            # Coming attractions
            elif ( current == self.Addon.getLocalizedString( 30414 ) ):
                self._get_trailers(
                    experience = experience,
                    type = "trailer",
                    genre = self.fp_videos[ self.feature_presentation ][ "genre" ],
                    studio = self.fp_videos[ self.feature_presentation ][ "studio" ],
                    director = self.fp_videos[ self.feature_presentation ][ "director" ],
                    movie = os.path.splitext( os.path.basename( self.fp_videos[ self.feature_presentation ][ "filename" ] ) )[ 0 ],
                    mpaa = self.fp_videos[ self.feature_presentation ][ "mpaa" ],
                    unwatched = self.Addon.getSetting( "experience_prefer_unwatched" ) == "true",
                    parental_control = self.Addon.getSetting( "parental_control" ) == "true",
                    experience_theme = [ self.Addon.getSetting( "experience_theme" ), self.Addon.getSetting( "experience_theme_other_text" ) ][ self.Addon.getSetting( "experience_theme" ) == "10" ],
                )
            # Dolby/DTS video
            elif ( current == self.Addon.getLocalizedString( 30415 ) ):
                if ( self.Addon.getSetting( "dolby_dts_folder" ) ):
                    self._get_special_items(
                        experience = experience,
                        type = "codec",
                        items = 1, # * ( self.fp_videos[ self.feature_presentation ][ "title" ] != "" ),
                        path = os.path.join( xbmc.translatePath( self.Addon.getSetting( "dolby_dts_folder" ) ), { "dca": "DTS", "ac3": "Dolby" }.get( self.fp_videos[ self.feature_presentation ][ "codec" ], "Other" ) ),
                        isfolder = True,
                        genre = self.Addon.getLocalizedString( 32487 ),
                        studio = self.Addon.getLocalizedString( 32000 ),
                        mpaa = self.fp_videos[ self.feature_presentation ][ "mpaa" ],
                        unwatched = self.Addon.getSetting( "experience_prefer_unwatched" ) == "true",
                        parental_control = self.Addon.getSetting( "parental_control" ) == "true",
                        experience_theme = [ self.Addon.getSetting( "experience_theme" ), self.Addon.getSetting( "experience_theme_other_text" ) ][ self.Addon.getSetting( "experience_theme" ) == "10" ],
                    )
            # Feature presentation
            elif ( current == self.Addon.getLocalizedString( 30416 ) ):
                # get current feature presentation video
                self._get_special_items(
                    experience = experience,
                    type = "feature",
                    items = 1 * ( self.fp_videos[ self.feature_presentation ][ "title" ] != "" ),
                    title = self.fp_videos[ self.feature_presentation ][ "title" ],
                    path = self.fp_videos[ self.feature_presentation ][ "filename" ],
                    isfolder = False,
                    thumbnail = self.fp_videos[ self.feature_presentation ][ "icon" ],
                    plot = self.fp_videos[ self.feature_presentation ][ "plot" ],
                    duration = self.fp_videos[ self.feature_presentation ][ "duration" ],
                    mpaa = self.fp_videos[ self.feature_presentation ][ "mpaa" ],
                    release_date = "0 0 %s" % ( self.fp_videos[ self.feature_presentation ][ "year" ], ),
                    genre = self.fp_videos[ self.feature_presentation ][ "genre" ],
                    studio = self.fp_videos[ self.feature_presentation ][ "studio" ],
                    writer = self.fp_videos[ self.feature_presentation ][ "writer" ],
                    director = self.fp_videos[ self.feature_presentation ][ "director" ]
                )
                # increment for next feature presentation
                if ( self.feature_presentation < len( self.fp_videos ) - 1 ):
                    self.feature_presentation += 1
            # MPAA rating
            elif ( current == self.Addon.getLocalizedString( 30417 ) ):
                self._get_special_items(
                    experience = experience,
                    type = "mpaa",
                    items = 1 * ( self.Addon.getSetting( "mpaa_ratings_folder" ) != "" ) * ( self.fp_videos[ self.feature_presentation ][ "mpaa" ] != "" ), 
                    path = os.path.join( xbmc.translatePath( self.Addon.getSetting( "mpaa_ratings_folder" ) ), self.fp_videos[ self.feature_presentation ][ "mpaa" ] + [ ".avi", ".jpg" ][ self.Addon.getSetting( "mpaa_ratings_type" ) == "1" ] ),
                    isfolder = False,
                    genre = self.Addon.getLocalizedString( 32486 ),
                    studio = self.Addon.getLocalizedString( 30000 ),
                    image_duration = int( round( float( self.Addon.getSetting( "mpaa_ratings_duration" ) ) ) ),
                    mpaa = self.fp_videos[ self.feature_presentation ][ "mpaa" ],
                    unwatched = self.Addon.getSetting( "experience_prefer_unwatched" ) == "true",
                    parental_control = self.Addon.getSetting( "parental_control" ) == "true",
                    experience_theme = [ self.Addon.getSetting( "experience_theme" ), self.Addon.getSetting( "experience_theme_other_text" ) ][ self.Addon.getSetting( "experience_theme" ) == "10" ],
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
                self._setup_slideshow(
                    experience = experience,
                    items = slides * ( self.Addon.getSetting( "slideshow_folder" ) != "" ),
                    path = self.Addon.getSetting( "slideshow_folder" ),
                    slideshow_duration = slideshow_duration,
                    image_duration = slide_duration,
                    play_music = self.Addon.getSetting( "slideshow_music" ) == "true",
                    volume = self.Addon.getSetting( "music_volume" ),
                    mpaa = self.fp_videos[ self.feature_presentation ][ "mpaa" ],
                    unwatched = self.Addon.getSetting( "experience_prefer_unwatched" ) == "true",
                    parental_control = self.Addon.getSetting( "parental_control" ) == "true",
                    experience_theme = [ self.Addon.getLocalizedString( 30111 + int( self.Addon.getSetting( "experience_theme" ) ) ), self.Addon.getSetting( "experience_theme_other_text" ) ][ self.Addon.getSetting( "experience_theme" ) == "10" ],
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
        # set year
        try: year = int( xbmc.getInfoLabel( "ListItem.Year" ) )
        except: year = 0
        # set our video
        video = [ {
            "title": unicode( xbmc.getInfoLabel( "ListItem.Title" ), "UTF-8" ),
            "filename": xbmc.getInfoLabel( "ListItem.FilenameAndPath" ),
            "icon": xbmc.getInfoLabel( "ListItem.Icon" ),
            "plot": unicode( xbmc.getInfoLabel( "ListItem.PlotOutline" ) or xbmc.getInfoLabel( "ListItem.Plot" ), "UTF-8" ), # TODO: change this to ListItem.Plot?
            "duration": xbmc.getInfoLabel( "ListItem.Duration" ),
            "mpaa": mpaa,
            "year": year,
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

    def _get_special_items( self, **kwargs ):
        # return if no items
        if ( not kwargs[ "items" ] ): return
        # if path is a file check if file exists
        if ( not kwargs[ "isfolder" ] and not kwargs[ "path" ].startswith( "http://" ) and not os.path.isfile( kwargs[ "path" ] ) ): return
        # set default paths list and temp playlist
        self.tmp_paths = [ kwargs[ "path" ] ]
        tmp_playlist = []
        # if path is a folder fetch # videos/images
        if ( kwargs[ "isfolder" ] ):
            # initialize our lists
            self.tmp_paths = []
            # get items
            self._get_items( [ kwargs[ "path" ] ] )
            # shuffle items
            shuffle( self.tmp_paths )
        ## here we divide functions to work like shuffle_slides
        # initialize our listitem
        listitem = None
        # enumerate thru and add our videos/images
        for count in range( kwargs[ "items" ] ):
            # no listitem for images
            if ( os.path.splitext( self.tmp_paths[ count ] )[ 1 ] in xbmc.getSupportedMedia( "video" ) ):
                # create the listitem and fill the infolabels
                listitem = self._get_listitem(
                    title = kwargs.get( "title", os.path.splitext( os.path.basename( self.tmp_paths[ count ] ) )[ 0 ] ),
                    url = self.tmp_paths[ count ],
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
            # add our video/image to the temp playlist
            tmp_playlist += [ ( self.tmp_paths[ count ], listitem, ) ]
        # add reults to our experience
        if ( tmp_playlist ):
            kwargs[ "experience" ] += [ { 
                "type": kwargs[ "type" ],
                "playlist": tmp_playlist,
                "slideshow_duration": kwargs.get( "slideshow_duration", -1 ), #FIXME: probably is always -1 unless we combine slideshow
                "image_duration": kwargs.get( "image_duration", -1 ),
                "play_music": False,
            } ]

    def _get_items( self, paths ):
        # reset folders list
        folders = []
        # enumerate thru paths and fetch videos/pictures recursively
        for path in paths:
            # get the directory listing
            entries = os.listdir( self._convert_smb_path( path ) )
            # enumerate through our entries list and check for valid media type
            for entry in entries:
                # join and validate path
                entry = xbmc.validatePath( os.path.join( path, entry ) )
                # if folder add to our folder list to recursively fetch videos/pictures
                if ( os.path.isdir( entry ) ):
                    folders += [ entry ]
                # is this a valid video/image file
                elif ( os.path.splitext( entry )[ 1 ] in xbmc.getSupportedMedia( "video" ) or os.path.splitext( entry )[ 1 ] in xbmc.getSupportedMedia( "picture" ) ):
                    # add our entry
                    self.tmp_paths += [ entry ]
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._get_items( folders )

    def _setup_slideshow( self, **kwargs ):
        # return if no items
        if ( not kwargs[ "items" ] ): return
        # get watched list
        self.watched_slides = self._watched_file( category="slides" )
        # set default paths list and temp playlist
        self.slide_playlist = []
        self.tmp_slides = []
        # get the slides
        self._get_slides( [ { "slidesxml_exists": False, "path": kwargs[ "path" ], "mpaa": None, "theme": None, "question_format": "", "clue_format": "", "answer_format": "" } ], kwargs[ "parental_control" ], kwargs[ "experience_theme" ] )
        # shuffle and format playlist
        self._shuffle_slides( kwargs[ "items" ], self.watched_slides, kwargs[ "unwatched" ] )
        # add slideshow
        if ( self.slide_playlist ):
            kwargs[ "experience" ] += [ { 
                "type": "slideshow",
                "playlist": self.slide_playlist,
                "slideshow_duration": kwargs[ "slideshow_duration" ],
                "image_duration": kwargs[ "image_duration" ],
                "play_music": kwargs[ "play_music" ],
                "volume": kwargs[ "volume" ]
            } ]

    def _get_slides( self, paths, parental_control, experience_theme ):
        def _get_slides_xml( path ):
            # if no slides.xml exists return dummy
            if ( not os.path.isfile( os.path.join( path[ "path" ], "slides.xml" ) ) ):
                return path[ "slidesxml_exists" ], path[ "mpaa" ], path[ "theme" ], path[ "question_format" ], path[ "clue_format" ], path[ "answer_format" ]
            # fetch data
            xml = open( os.path.join( path[ "path" ], "slides.xml" ) ).read()
            # parse info
            mpaa, theme, question_format, clue_format, answer_format = re.search( "<slides(?:.+?rating=\"([^\"]*)\")?(?:.+?theme=\"([^\"]*)\")?.*?>(?:.*?<slide>.*?<question.+?format=\"([^\"]+)\".*?/>.*?<clue.+?format=\"([^\"]+)\".*?/>.*?<answer.+?format=\"([^\"]+)\".*?/>)?", xml, re.DOTALL + re.IGNORECASE ).groups()
            # return results
            return True, mpaa, theme, question_format, clue_format, answer_format
        # reset folders list
        folders = []
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
                ( parental_control and self.movie_rating_system[ "ratings" ].get( self.fp_videos[ self.feature_presentation ][ "mpaa" ], self.movie_rating_system[ "ratings" ][ self.movie_rating_system[ "unrated_rating" ] ] ) < self.movie_rating_system[ "ratings" ].get( mpaa, self.movie_rating_system[ "ratings" ][ self.movie_rating_system[ "unrated_rating" ] ] ) )
            )
            if ( skip ):
                xbmc.log( "Skipping files for folder: %s" % ( path[ "path" ], ), level=xbmc.LOGNOTICE )
                xbmc.log( "     Settings Theme: %s - Folder Theme: %s, Movie MPAA: %s - Folder MPAA: %s" % ( experience_theme, theme, self.fp_videos[ self.feature_presentation ][ "mpaa" ], mpaa, ), level=xbmc.LOGNOTICE )
            # initialize these to True so we add a new list item to start
            question = clue = answer = True
            # enumerate through our entries list and combine question, clue, answer
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
                    # sliders.xml was included, so check it
                    if ( slidesxml_exists ):
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
                    # no slides.xml, we add the file as an answer
                    elif ( entry and os.path.splitext( entry )[ 1 ].lower() in xbmc.getSupportedMedia( "picture" ) ):
                        self.tmp_slides += [ [ "", "", entry ] ]
        # if there are folders call again (we want recursive)
        if ( folders ):
            self._get_slides( folders, parental_control, experience_theme )

    def _shuffle_slides( self, total, watched, unwatched, firstrun=True ):
        # shuffle the groups only on firstrun
        if ( firstrun ):
            shuffle( self.tmp_slides )
        # loop thru slide groups and add slides
        for slides in self.tmp_slides:
            # loop thru slide group and include non blank slides
            self.slide_playlist += [ slide for slide in slides if slide and ( not unwatched or slide not in watched ) ]
            # break out if we have enough TODO: verify we want this. if user skips slides, you may run out.
            if ( len( self.slide_playlist ) >= total ): break
        # if we don't have enough, try again including already watched items
        if ( len( self.slide_playlist ) < total and unwatched and firstrun ):
            # reset self.watched_slides
            self.watched_slides = []
            # try again skipping already added slides
            self._shuffle_slides( total=total, watched = [ xbmc.getCacheThumbName( slide ) for slide in self.slide_playlist ], unwatched=True, firstrun=False )
        print " - total slides selected: %d" % len( self.slide_playlist )

    def _get_trailers( self, **kwargs ):#playlist, type, mpaa, genre, studio, director, movie ):
        # spam log file
        return
        xbmc.log( ">>> _get_trailers(rating: %s, genre: %s, movie: %s)" % ( mpaa, genre, movie, ), level=xbmc.LOGNOTICE )
        # return if preferences are incorrect
        if ( not ( self.Addon.getSetting( "trailer_scraper" ) != 2 or ( self.Addon.getSetting( "trailer_scraper" ) == 2 and self.Addon.getSetting( "trailer_folder" ) != "" ) ) ):
            return
        
        ##########################################
        return
        
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
        # spam log file
        xbmc.log( "<<< _get_trailers()", level=xbmc.LOGNOTICE )

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
        if ( self.Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "1" ):
            playlist_type = 2
        elif ( self.Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "3" or self.Addon.getSetting( "playlist_item%d" % ( item + 1, ) ) == "4" ):
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
        if ( self.Addon.getSetting( "slideshow_folder" ) ):
            # update dialog with new message
            pDialog.update( -1, self.Addon.getLocalizedString( 32810 ) )
            # initialize intro/outro lists
            playlist_intro = []
            playlist_outro = []
            """
            # get trivia intro videos
            self._get_special_items(    playlist=playlist_intro,
                                                    items=( 0, 1, 1, 2, 3, 4, 5, )[ int( self.Addon.getSetting( "trivia_intro" ) ) ], 
                                                    path=( xbmc.translatePath( self.Addon.getSetting( "trivia_intro_file" ) ), xbmc.translatePath( self.Addon.getSetting( "trivia_intro_folder" ) ), )[ int( self.Addon.getSetting( "trivia_intro" ) ) > 1 ],
                                                    genre=self.Addon.getLocalizedString( 32609 ),
                                                    media_type="video/picture"
                                                )
            # get trivia outro videos
            self._get_special_items(    playlist=playlist_outro,
                                                    items=( 0, 1, 1, 2, 3, 4, 5, )[ int( self.Addon.getSetting( "trivia_outro" ) ) ], 
                                                    path=( xbmc.translatePath( self.Addon.getSetting( "trivia_outro_file" ) ), xbmc.translatePath( self.Addon.getSetting( "trivia_outro_folder" ) ), )[ int( self.Addon.getSetting( "trivia_outro" ) ) > 1 ],
                                                    genre=self.Addon.getLocalizedString( 32610 ),
                                                    media_type="video/picture"
                                                )
            """
            # slideshow settings, grab them here so we don't need another self.Addon.getSetting() object
            settings = {
                "slideshow_total_time": ( 5, 10, 15, 20, 30, 45, 60 )[ int( self.Addon.getSetting( "slideshow_total_time" ) ) ],
                "slideshow_folder":  xbmc.translatePath( self.Addon.getSetting( "slideshow_folder" ) ),
                "slide_time": ( 5, 7, 10, 15, 20, 30, )[ int( self.Addon.getSetting( "slide_time" ) ) ],
                "slideshow_intro_playlist": playlist_intro,
                "slideshow_outro_playlist": playlist_outro,
                "slideshow_music": self.Addon.getSetting( "slideshow_music" ) == "true",
                "slideshow_music_folder":  xbmc.translatePath( self.Addon.getSetting( "slideshow_music_folder" ) ),
                "slideshow_music_volume": ( None, "30", "40", "50", "60", "70", "80", "90", "100", )[ int( self.Addon.getSetting( "slideshow_music_volume" ) ) ],
                "slideshow_unwatched_only": self.Addon.getSetting( "slideshow_unwatched_only" ) == "true"
            }
            # set the proper mpaa rating user preference
            mpaa = ( "", mpaa, )[ self.Addon.getSetting( "slideshow_limit_query" ) == "true" ]
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
