# -*- coding: utf-8 -*-

import xbmc, xbmcgui
import traceback

def _store_playlist():
    p_list = []
    try:
        xbmc.log( "[script.cinema.experience] - Storing Playlist", level=xbmc.LOGNOTICE )
        true = True
        false = False
        null = None
        json_query = '{"jsonrpc": "2.0", "method": "VideoPlaylist.GetItems", "params": {"fields": ["title", "file", "thumbnail", "plot", "plotoutline", "mpaa", "rating", "studio", "tagline", "top250", "votes", "year", "director", "writingcredits", "imdbnumber", "runtime", "genre"] }, "id": 1}'
        json_response = xbmc.executeJSONRPC(json_query)
        xbmc.log( "[script.cinema.experience] - JSONRPC -\n%s" % json_response, level=xbmc.LOGDEBUG )
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
            xbmc.log( "[script.cinema.experience] - Movie Title: %s" % movie["title"], level=xbmc.LOGDEBUG )
            xbmc.log( "[script.cinema.experience] - Movie Thumbnail: %s" % movie["thumbnail"], level=xbmc.LOGDEBUG )
            xbmc.log( "[script.cinema.experience] - Full Movie Path: %s" % movie["file"], level=xbmc.LOGDEBUG )
            listitem = xbmcgui.ListItem( movie["title"], thumbnailImage=movie["thumbnail"] )
            listitem.setInfo('Video', {'Title': movie["title"], 'Plot': movie["plot"], 'PlotOutline': movie["plotoutline"], 'MPAA': movie["mpaa"], 'Year': movie["year"], 'Studio': movie["studio"], 'Genre': movie["genre"], 'Writer': movie["writingcredits"], 'Director': movie["director"], 'Rating': movie["rating"], 'Code': movie["imdbnumber"], 'Top250': movie["top250"], 'Tagline': movie["tagline"], } )
            playlist.add(url=movie["file"].replace("\\\\" , "\\"), listitem=listitem, )
        except:
            traceback.print_exc()
        # give XBMC a chance to add to the playlist... May not be needed, but what's 50ms?
        xbmc.sleep( 50 )
