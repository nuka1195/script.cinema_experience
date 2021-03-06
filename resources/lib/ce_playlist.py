# -*- coding: utf-8 -*-

__script__ = "Cinema Experience"
__scriptID__ = "script.cinema.experience"
__modname__ = "ce_playlist.py"

import traceback, os, re, sys
import xbmc, xbmcaddon, xbmcgui
from urllib import quote_plus
from random import shuffle, random

log_message = "[ " + __scriptID__ + " ] - [ " + __modname__ + " ]"
_A_ = xbmcaddon.Addon( __scriptID__ )
# language method
_L_ = _A_.getLocalizedString
# settings method
_S_ = _A_.getSetting

#tmp_paths = []
BASE_CACHE_PATH = os.path.join( xbmc.translatePath( "special://profile" ), "Thumbnails", "Video" )
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( _A_.getAddonInfo('path'), 'resources' ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

from music import parse_playlist
from folder import dirEntries
if _S_("pre_eden") == "true":
    from pre_eden_code import _rebuild_playlist
else:
    from dharma_code import _rebuild_playlist
    
log_sep = "-"*70

def _get_trailers( items, mpaa, genre, movie, mode = "download" ):
    xbmc.log( "[script.cinema.experience] - [ce_playlist.py] - _get_trailers started", level=xbmc.LOGDEBUG )
    # return if not user preference
    if not items:
        return []
    # trailer settings, grab them here so we don't need another _S_() object
    settings = { "trailer_amt_db_file":  xbmc.translatePath( _S_( "trailer_amt_db_file" ) ),
                      "trailer_folder":  xbmc.translatePath( _S_( "trailer_folder" ) ),
                      "trailer_rating": _S_( "trailer_rating" ),
                  "trailer_limit_mpaa": _S_( "trailer_limit_mpaa" ) == "true",
                 "trailer_limit_genre": _S_( "trailer_limit_genre" ) == "true",
                   "trailer_play_mode": int( _S_( "trailer_play_mode" ) ),
                     "trailer_hd_only": _S_( "trailer_hd_only" ) == "true",
                     "trailer_quality": int( _S_( "trailer_quality" ) ),
              "trailer_unwatched_only": _S_( "trailer_unwatched_only" ) == "true",
                 "trailer_newest_only": _S_( "trailer_newest_only" ) == "true",
                       "trailer_count": ( 0, 1, 2, 3, 4, 5, 10, )[ int( _S_( "trailer_count" ) ) ],
                     "trailer_scraper": ( "amt_database", "amt_current", "local", "xbmc_library", )[ int( _S_( "trailer_scraper" ) ) ]
               }
    if int( _S_( "trailer_play_mode" ) ) == 1 and mode == "playlist" and int( _S_( "trailer_scraper" ) ) < 2:
        settings[ "trailer_scraper" ] = "local"
        settings[ "trailer_folder" ] = _S_( "trailer_download_folder" )
    # get the correct scraper
    sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "scrapers" ) )
    exec "from %s import scraper as scraper" % ( settings[ "trailer_scraper" ], )
    Scraper = scraper.Main( mpaa, genre, settings, movie )
    # fetch trailers
    trailers = Scraper.fetch_trailers()
    # return results
    print trailers
    return trailers
    
def _getnfo( path ):
    
    '''
            id=trailer[ 0 ]
            path=trailer[ 2 ],
            genre=trailer[ 9 ],
            title=trailer[ 1 ],
            thumbnail=trailer[ 3 ],
            plot=trailer[ 4 ],
            runtime=trailer[ 5 ],
            mpaa=trailer[ 6 ],
            release_date=trailer[ 7 ],
            studio=trailer[ 8 ],
            director=trailer[ 11 ]
    '''
    xbmc.log("%s - Retrieving Trailer NFO file" % log_message, level=xbmc.LOGDEBUG )
    try:
        path = os.path.splitext( path )[0] + ".nfo"
        usock = open( path, "r" )
        # read source
        xmlSource =  usock.read()
        # close socket
        usock.close()
    except:
        xmlSource = ""
    xmlSource = xmlSource.replace("\n    ","")
    # if only
    xmlSource = xmlSource.replace('<movieinfo>','<movieinfo id="0">')
    # gather all trailer records <movieinfo>
    new_trailer = []
    #title = plot = runtime = mpaa = release_date = studio = genre = director = ""
    trailer = re.findall( '<movieinfo id="(.*?)"><title>(.*?)</title><quality>(.*?)</quality><runtime>(.*?)</runtime><releasedate>(.*?)</releasedate><mpaa>(.*?)</mpaa><genre>(.*?)</genre><studio>(.*?)</studio><director>(.*?)</director><cast>(.*?)</cast><plot>(.*?)</plot><thumb>(.*?)</thumb>', xmlSource )
    if trailer:
        xbmc.log("%s - CE XML Match Found" % log_message, level=xbmc.LOGDEBUG )
        for item in trailer:
            new_trailer += item
        return new_trailer[ 1 ], new_trailer[ 10 ], new_trailer[ 3 ], new_trailer[ 5 ], new_trailer[ 4 ], new_trailer[ 7 ], new_trailer[ 6 ], new_trailer[ 8 ]
    else:
        xbmc.log("%s - HD-Trailers.Net Downloader XML Match Found" % log_message, level=xbmc.LOGDEBUG )
        title = "".join(re.compile("<title>(.*?)</title>", re.DOTALL).findall(xmlSource)) or ""
        plot = "".join(re.compile("<plot>(.*?)</plot>", re.DOTALL).findall(xmlSource)) or ""
        runtime = "".join(re.compile("<runtime>(.*?)</runtime>", re.DOTALL).findall(xmlSource)) or ""
        mpaa = "".join(re.compile("<mpaa>(.*?)</mpaa>", re.DOTALL).findall(xmlSource)) or ""
        release_date = "".join(re.compile("<premiered>(.*?)</premiered>", re.DOTALL).findall(xmlSource)) or ""
        studio = "".join(re.compile("<studio>(.*?)</studio>", re.DOTALL).findall(xmlSource)) or ""
        genre = "".join(re.compile("<genre>(.*?)</genre>", re.DOTALL).findall(xmlSource)) or ""
        director = "".join(re.compile("<director>(.*?)</director>", re.DOTALL).findall(xmlSource)) or ""
        return title, plot, runtime, mpaa, release_date, studio, genre, director
    
def _set_trailer_info( trailer ):
    xbmc.log("%s - Setting Trailer Info" % log_message, level=xbmc.LOGDEBUG )
    title = plot = runtime = mpaa = release_date = studio = genre = director = ""
    if os.path.isfile( os.path.splitext( trailer )[ 0 ] + ".nfo" ):
        xbmc.log("%s - Trailer .nfo file FOUND" % log_message, level=xbmc.LOGDEBUG )
        title, plot, runtime, mpaa, release_date, studio, genre, director = _getnfo( trailer )
    else:
        xbmc.log("%s - Trailer .nfo file NOT FOUND" % log_message, level=xbmc.LOGDEBUG )
    result = ( xbmc.getCacheThumbName( trailer ), # id
               title or os.path.basename( trailer ).split( "-trailer." )[ 0 ], # title
               trailer, # trailer
               _get_trailer_thumbnail( trailer ), # thumb
               plot, # plot
               runtime, # runtime
               mpaa, # mpaa
               release_date, # release date
               studio, # studio
               genre, # genre
               _L_( 32605 ), # writer
               director, # director 32613
              )
    return result
    
def _get_trailer_thumbnail( path ):
    xbmc.log("%s - Getting Trailer Thumbnail" % log_message, level=xbmc.LOGDEBUG )
    # check for a thumb based on trailername.tbn
    thumbnail = os.path.splitext( path )[ 0 ] + ".tbn"
    xbmc.log("%s - Looking for thumbnail: %s" % ( log_message, thumbnail), level=xbmc.LOGDEBUG )
    # if thumb does not exist try stripping -trailer
    if not os.path.isfile( thumbnail ):
        thumbnail = os.path.splitext( path )[ 0 ] + ".jpg"
        xbmc.log("%s - Looking for thumbnail: %s" % ( log_message, thumbnail), level=xbmc.LOGDEBUG )
        if not os.path.isfile( thumbnail ):
            thumbnail = "%s.tbn" % ( os.path.splitext( path )[ 0 ].replace( "-trailer", "" ), )
            xbmc.log("%s - Thumbnail not found, Trying: %s" % ( log_message, thumbnail), level=xbmc.LOGDEBUG )
            if not os.path.isfile( thumbnail ):
                thumbnail = "%s.jpg" % ( os.path.splitext( path )[ 0 ].replace( "-trailer", "" ), )
                xbmc.log("%s - Looking for thumbnail: %s" % ( log_message, thumbnail), level=xbmc.LOGDEBUG )
                if not os.path.isfile( thumbnail ):
                    thumbnail = os.path.join( os.path.dirname( path ), "movie.tbn" )
                    xbmc.log("%s - Thumbnail not found, Trying: %s" % ( log_message, thumbnail), level=xbmc.LOGDEBUG )
                    # if thumb does not exist return empty
                    if not os.path.isfile( thumbnail ):
                        # set empty string
                        thumbnail = None
                        xbmc.log("%s - Thumbnail not found" % log_message, level=xbmc.LOGDEBUG )
    if not thumbnail == None:
        xbmc.log("%s - Thumbnail found: %s" % ( log_message, thumbnail), level=xbmc.LOGDEBUG )
    # return result
    return thumbnail

def _get_special_items( playlist, items, path, genre, title="", thumbnail=None, plot="",
                        runtime="", mpaa="", release_date="0 0 0", studio="", writer="",
                        director="", index=-1, media_type="video"
                      ):
    xbmc.log( "%s - _get_special_items() Started" % log_message, level=xbmc.LOGDEBUG)
    # return if not user preference
    if not items:
        xbmc.log( "%s - No Items" % log_message, level=xbmc.LOGDEBUG)
        return
    # if path is a file check if file exists
    if os.path.splitext( path )[ 1 ] and not path.startswith( "http://" ) and not ( xbmc.executehttpapi( "FileExists(%s)" % ( path, ) ) == "<li>True" ):
        xbmc.log( "%s - _get_special_items() - File Does not Exist" % log_message, level=xbmc.LOGDEBUG)
        return
    # set default paths list
    tmp_paths = [ path ]
    # if path is a folder fetch # videos/pictures
    if path.endswith( "/" ) or path.endswith( "\\" ):
        xbmc.log( "%s - _get_special_items() - Path: %s" % ( log_message, path ), level=xbmc.LOGDEBUG)
        # initialize our lists
        tmp_paths = dirEntries( path, media_type, "TRUE" )
        shuf = 0
        while shuf <6:
            shuffle( tmp_paths, random )
            shuf += 1
    # enumerate thru and add our videos/pictures
    for count in range( items ):
        try:
            # set our path
            path = tmp_paths[ count ]
            xbmc.log( "%s - Checking Path: %s" % ( log_message, path ), level=xbmc.LOGDEBUG)
            # format a title (we don't want the ugly extension)
            title = title or os.path.splitext( os.path.basename( path ) )[ 0 ]
            # create the listitem and fill the infolabels
            listitem = _get_listitem( title=title,
                                        url=path,
                                  thumbnail=thumbnail,
                                       plot=plot,
                                    runtime=runtime,
                                       mpaa=mpaa,
                               release_date=release_date,
                                     studio=studio or _L_( 32604 ),
                                      genre=genre or _L_( 32605 ),
                                     writer=writer,
                                   director=director
                                    )
            # add our video/picture to the playlist or list
            if isinstance( playlist, list ):
                playlist += [ ( path, listitem, ) ]
            else:
                playlist.add( path, listitem, index=index )
        except:
            if items > count:
                xbmc.log( "%s - Looking for %d files, but only found %d" % ( log_message, items, count), level=xbmc.LOGNOTICE)
                break
            else:
                traceback.print_exc()

def _get_listitem( title="", url="", thumbnail=None, plot="", runtime="", mpaa="", release_date="0 0 0", studio=_L_( 32604 ), genre="", writer="", director=""):
    xbmc.log( "%s - _get_listitem() Started" % log_message, level=xbmc.LOGDEBUG)
    # check for a valid thumbnail
    if not writer == _L_( 32605 ):
        thumbnail = _get_thumbnail( ( thumbnail, url, )[ thumbnail is None ] )
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
    listitem.setInfo( type="Video", infoLabels={ "Title": title, "Plot": plot, "PlotOutline": plot, "RunTime": runtime, "MPAA": mpaa, "Year": year, "Studio": studio, "Genre": genre, "Writer": writer, "Director": director } )
    # return result
    return listitem

def _get_thumbnail( url ):
    xbmc.log( "%s - _get_thumbnail() Started"  % log_message, level=xbmc.LOGDEBUG)
    xbmc.log( "%s - Thumbnail Url: %s" % ( log_message, url ), level=xbmc.LOGDEBUG )
    # if the cached thumbnail does not exist create the thumbnail based on filepath.tbn
    filename = xbmc.getCacheThumbName( url )
    thumbnail = os.path.join( BASE_CACHE_PATH, filename[ 0 ], filename )
    xbmc.log( "%s - Thumbnail Cached Filename: %s" % ( log_message, filename ), level=xbmc.LOGDEBUG )
    # if cached thumb does not exist try auto generated
    if not os.path.isfile( thumbnail ):
        thumbnail = os.path.join( BASE_CACHE_PATH, filename[ 0 ], "auto-" + filename )
    if not os.path.isfile( thumbnail ):
        thumbnail = "DefaultVideo.png"
    # return result
    return thumbnail

def _get_queued_video_info( feature = 0 ):
    xbmc.log( "%s - _get_queued_video_info() Started" % log_message, level=xbmc.LOGDEBUG )
    equivalent_mpaa = "NR"
    try:
        # get movie name
        movie_title = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )[ feature ].getdescription()
        # this is used to skip trailer for current movie selection
        movie = os.path.splitext( os.path.basename( xbmc.PlayList( xbmc.PLAYLIST_VIDEO )[ feature ].getfilename() ) )[ 0 ]
        # format our records start and end
        xbmc.executehttpapi( "SetResponseFormat()" )
        xbmc.executehttpapi( "SetResponseFormat(OpenField,)" )
        # TODO: verify the first is the best audio
        # setup the sql, we limit to 1 record as there can be multiple entries in streamdetails
        sql = "SELECT movie.c12, movie.c14, streamdetails.strAudioCodec FROM movie, streamdetails WHERE movie.idFile=streamdetails.idFile AND streamdetails.iStreamType=1 AND c00='%s' LIMIT 1" % ( movie_title.replace( "'", "''", ), )
        xbmc.log( "%s - SQL: %s" % ( log_message, sql, ), level=xbmc.LOGDEBUG )
        # query database for info dummy is needed as there are two </field> formatters
        mpaa, genre, audio, dummy = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql ), ).split( "</field>" )
        # TODO: add a check and new sql for videos queued from files mode, or try an nfo
        # calculate rating
        if mpaa == "":
            mpaa = "NR"
        elif mpaa.startswith("Rated"):
            mpaa = mpaa.split( " " )[ 1 - ( len( mpaa.split( " " ) ) == 1 ) ]
            mpaa = ( mpaa, "NR", )[ mpaa not in ( "G", "PG", "PG-13", "R", "NC-17", "Unrated", ) ]
        elif mpaa.startswith("UK"):
            mpaa = mpaa.split( ":" )[ 1 - ( len( mpaa.split( ":" ) ) == 1 ) ]
            mpaa = ( mpaa, "NR", )[ mpaa not in ( "12", "12A", "PG", "15", "18", "R18", "MA", "U", ) ]
        else:
            mpaa = ( mpaa, "NR", )[ mpaa not in ( "12", "12A", "PG", "15", "18", "R18", "MA", "U", ) ]
        if mpaa not in ( "G", "PG", "PG-13", "R", "NC-17", "Unrated", "NR" ):
            if mpaa in ("12", "12A",):
                equivalent_mpaa = "PG-13"
            elif mpaa == "15":
                equivalent_mpaa = "R"
            elif mpaa == "U":
                equivalent_mpaa = "G"
            elif mpaa in ("18", "R18", "MA",):
                equivalent_mpaa = "NC-17"
        else:
            equivalent_mpaa = mpaa
    except:
        traceback.print_exc()
        movie_title = mpaa = audio = genre = movie = equivalent_mpaa = ""
    # spew queued video info to log
    xbmc.log( "%s - Queued Movie Information" % log_message, level=xbmc.LOGDEBUG )
    xbmc.log( "%s %s" % ( log_message,log_sep ), level=xbmc.LOGDEBUG )
    xbmc.log( "%s - Title: %s" % ( log_message, movie_title, ), level=xbmc.LOGDEBUG )
    xbmc.log( "%s - Path: %s" % ( log_message, movie, ), level=xbmc.LOGDEBUG )
    xbmc.log( "%s - Genre: %s" % ( log_message, genre, ), level=xbmc.LOGDEBUG )
    xbmc.log( "%s - MPAA: %s" % ( log_message, mpaa, ), level=xbmc.LOGDEBUG )
    xbmc.log( "%s - Audio: %s" % ( log_message, audio, ), level=xbmc.LOGDEBUG )
    if _S_( "audio_videos_folder" ):
        xbmc.log( "%s - Folder: %s" % ( log_message, ( xbmc.translatePath( _S_( "audio_videos_folder" ) ) + { "dca": "DTS", "ac3": "Dolby", "dtsma": "DTSHD-MA", "dtshd_ma": "DTSHD-MA", "a_truehd": "Dolby TrueHD", "truehd": "Dolby TrueHD" }.get( audio, "Other" ) + xbmc.translatePath( _S_( "audio_videos_folder" ) )[ -1 ], ) ), level=xbmc.LOGDEBUG )
    xbmc.log( "%s  %s" % ( log_message, log_sep ), level=xbmc.LOGDEBUG )
    # return results
    return mpaa, audio, genre, movie, equivalent_mpaa

def _wait_until_end(): # wait until the end of the playlist(for Trivia Intro)
    xbmc.log( "%s - Waiting Until End Of Video" % log_message, level=xbmc.LOGNOTICE)
    try:
        psize = xbmc.PlayList( xbmc.PLAYLIST_VIDEO ).size() - 1
        xbmc.log( "%s - Playlist Size: %s" % (log_message, ( psize + 1 ) ), level=xbmc.LOGDEBUG)
        while xbmc.PlayList( xbmc.PLAYLIST_VIDEO ).getposition() < psize:
            pass
        xbmc.log( "%s - Video TotalTime: %s" % ( log_message, xbmc.Player().getTotalTime() ), level=xbmc.LOGDEBUG)
        while xbmc.Player().getTime() < ( xbmc.Player().getTotalTime() - 0.5 ):
            pass
        xbmc.log( "%s - Video getTime: %s"  % ( log_message, xbmc.Player().getTime() ), level=xbmc.LOGDEBUG)
        xbmc.sleep(500)
    except:
        xbmc.log( "%s - Video either stopped or skipped, Continuing on..." % log_message, level=xbmc.LOGDEBUG)


def build_music_playlist():
    xbmc.log( "%s - Building Music Playlist" % log_message, level=xbmc.LOGNOTICE)
    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "AudioPlaylist.Clear", "id": 1}')
    music_playlist = xbmc.PlayList( xbmc.PLAYLIST_MUSIC )
    track_location = []
    # check to see if playlist or music file is selected
    if int( _S_( "trivia_music" ) ) == 1:
        if _S_( "trivia_music_file" ).endswith(".m3u"):
            xbmc.log( "%s - Music Playlist: %s" % ( log_message, _S_( "trivia_music_file" ) ), level=xbmc.LOGDEBUG)
            playlist_file = open( _S_( "trivia_music_file" ), 'rb')
            saved_playlist = playlist_file.readlines()
            xbmc.log( "%s - Finished Reading Music Playlist" % log_message, level=xbmc.LOGDEBUG)
            track_info, track_location = parse_playlist( saved_playlist, xbmc.getSupportedMedia('music') )
        elif os.path.splitext( _S_( "trivia_music_file" ) )[1] in xbmc.getSupportedMedia('music'):
            for track in range(100):
                track_location.append( _S_( "trivia_music_file" ) )
    # otherwise
    else:
        if _S_( "trivia_music_folder" ):
            # search given folder and subfolders for files
            track_location = dirEntries( _S_( "trivia_music_folder" ), "music", "TRUE" )
    # shuffle playlist
    count = 0
    while count <6:
        shuffle( track_location, random )
        count+=1
    for track in track_location:
        music_playlist.add( track,  )
