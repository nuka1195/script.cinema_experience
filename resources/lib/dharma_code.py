# -*- coding: utf-8 -*-

import xbmc, xbmcgui
import traceback
from urllib import quote_plus

def _store_playlist():
    p_list = []
    try:
        xbmc.log( "[script.cinema.experience] - Storing Playlist", level=xbmc.LOGNOTICE )
        true = True
        false = False
        null = None
        json_query = '{"jsonrpc": "2.0", "method": "VideoPlaylist.GetItems", "params": {"fields": ["file", "thumbnail"] }, "id": 1}'
        json_response = xbmc.executeJSONRPC(json_query)
        xbmc.log( "[script.cinema.experience] - JSONRPC - %s" % json_response, level=xbmc.LOGDEBUG )
        response = json_response
        if response.startswith( "{" ):
            response = eval( response )
        result = response['result']
        p_list = result['items']
    except:
        xbmc.log( "[script.cinema.experience] - Error - Playlist Empty", level=xbmc.LOGNOTICE )
    return p_list

def _rebuild_playlist( plist ): # rebuild movie playlist
    xbmc.log( "[script.cinema.experience] - [ce_playlist.py] - Rebuilding Playlist", level=xbmc.LOGNOTICE )
    playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
    playlist.clear()
    print plist
    for movie in plist:
        try:
            movie_title = movie["label"]
            movie_full_path = movie["file"].replace("\\\\" , "\\")
            try:
                movie_thumbnail = movie["thumbnail"]
            except:
                movie_thumbnail = os.path.join( os.path.split( movie_full_path )[ 0 ], "movie.tbn" )
            xbmc.log( "[script.cinema.experience] - Movie Title: %s" % movie_title, level=xbmc.LOGDEBUG )
            xbmc.log( "[script.cinema.experience] - Movie Thumbnail: %s" % movie_thumbnail, level=xbmc.LOGDEBUG )
            xbmc.log( "[script.cinema.experience] - Full Movie Path: %s" % movie_full_path, level=xbmc.LOGDEBUG )
            plot, plotoutline, runtime, mpaa, year, studio, genre, writer, director, tagline, votes, imdbcode, rating, votes, top250 =  _get_movie_details( movie_title, movie_thumbnail, movie_full_path )
            #runtime = int( runtime.strip("min") )
            rating = float( rating )
            year = int( year )
            top250 = int( top250 )
            listitem = xbmcgui.ListItem( movie_title, thumbnailImage=movie_thumbnail )
            listitem.setInfo('Video', {'Title': movie_title, 'Plot': plot, 'PlotOutline': plotoutline, 'MPAA': mpaa, 'Year': year, 'Studio': studio, 'Genre': genre, 'Writer': writer, 'Director': director, 'Tagline': tagline, 'Code': imdbcode, 'Top250': top250, 'Votes': votes, 'Rating': rating, } )
            playlist.add(url=movie_full_path, listitem=listitem, )
        except:
            traceback.print_exc()
        # give XBMC a chance to add to the playlist... May not be needed, but what's 50ms?
        xbmc.sleep( 50 )

def _get_movie_details( movie_title="", thumbnail="", movie_full_path="" ):
    xbmc.log( "[script.cinema.experience] - [ce_playlist.py] - _get_movie_details started", level=xbmc.LOGNOTICE )
    # format our records start and end
    xbmc.executehttpapi( "SetResponseFormat()" )
    xbmc.executehttpapi( "SetResponseFormat(OpenField,)" )
    # retrive plot(c01), plotoutline(c02), runtime(c11), mpaa(c12), year(c07), studio(c18), genre(c14), writer(c06), director(c15), tagline(c03), votes(c04), imdbcode(c09), rating(c05), top250(c13) from database
    sql_query = "SELECT c01, c02, c11, c12, c07, c18, c14, c06, c15, c03, c04, c09, c05, c13 FROM movieview WHERE c00='%s' LIMIT 1" % ( movie_title.replace( "'", "''", ), )
    # the dummy string is to catch the extra </field>
    plot, plotoutline, runtime, mpaa, year, studio, genre, writer, director, tagline, votes, imdbcode, rating, top250, dummy = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql_query ), ).split( "</field>" )
    return plot, plotoutline, runtime, mpaa, year, studio, genre, writer, director, tagline, votes, imdbcode, rating, votes, top250
    