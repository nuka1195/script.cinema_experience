""" Utilities module """

import sys
import os

try:
    import xbmc
    import xbmcgui
    try:
        import xbmcaddon
    except:
        # get xbox compatibility module
        from xbox import *
        xbmcaddon = XBMCADDON()
except:
    # get dummy xbmc modules (Debugging)
    from debug import *
    xbmc = XBMC()
    xbmcgui = XBMCGUI()
    xbmcaddon = XBMCADDON()

# Addon class
Addon = xbmcaddon.Addon( id="script.cinema.experience" )


class Viewer:
    # we need regex for parsing info
    import re
    # window constants
    WINDOW = 10147
    CONTROL_LABEL = 1
    CONTROL_TEXTBOX = 5

    def __init__( self, *args, **kwargs ):
        # activate the text viewer window
        xbmc.executebuiltin( "ActivateWindow(%d)" % ( self.WINDOW, ) )
        # get window
        window = xbmcgui.Window( self.WINDOW )
        # give window time to initialize
        xbmc.sleep( 100 )
        # set heading
        window.getControl( self.CONTROL_LABEL ).setLabel( "%s - %s" % ( { "updates": Addon.getLocalizedString( 30765 ), "changelog": Addon.getLocalizedString( 30766 ), "readme": Addon.getLocalizedString( 30767 ), "license": Addon.getLocalizedString( 30768 ), "properties": Addon.getLocalizedString( 30769 ) }[ kwargs[ "kind" ] ], Addon.getAddonInfo( "Name" ), ) )
        # set fetching message
        window.getControl( self.CONTROL_TEXTBOX ).setText( { "updates": Addon.getLocalizedString( 30760 ), "changelog": Addon.getLocalizedString( 30761 ), "readme": Addon.getLocalizedString( 30762 ), "license": Addon.getLocalizedString( 30763 ), "properties": Addon.getLocalizedString( 30764 ) }[ kwargs[ "kind" ] ] )
        # set header
        try:
            # fetch correct info
            if ( kwargs[ "kind" ] in [ "readme", "license" ] ):
                text = self._fetch_text_file( kwargs[ "kind" ] )
            else:
                text = self._fetch_changelog( kwargs[ "kind" ] )
        except Exception, e:
            # set error message
            text = "%s[CR][CR]%s" % ( Addon.getLocalizedString( 30771 ) % ( { "updates": Addon.getLocalizedString( 30765 ), "changelog": Addon.getLocalizedString( 30766 ), "readme": Addon.getLocalizedString( 30767 ), "license": Addon.getLocalizedString( 30768 ), "properties": Addon.getLocalizedString( 30769 ) }[ kwargs[ "kind" ] ], ), e, )
        # set text
        window.getControl( self.CONTROL_TEXTBOX ).setText( text )

    def _fetch_text_file( self, kind ):
        # set path, first try translated version
        _path = os.path.join( Addon.getAddonInfo( "Path" ), "%s-%s.txt" % ( kind, xbmc.getRegion( "locale" ), ) )
        # if doesn't exist, use default
        if ( not os.path.isfile( _path ) ):
            _path = os.path.join( Addon.getAddonInfo( "Path" ), "%s.txt" % ( kind, ) )
        # read  file
        text = open( _path, "r" ).read()
        # return colorized result
        return text##self._colorize_text( text )

    def _fetch_changelog( self, kind ):
        # import required modules
        import datetime
        import pysvn
        # get our regions format
        date_format = "%s %s" % ( xbmc.getRegion( "datelong" ), xbmc.getRegion( "time" ), )
        # get client
        client = pysvn.Client()
        client.callback_cancel = self._pysvn_cancel_callback
        try:
            # grab current revision and repo url
            info = client.info( path=Addon.getAddonInfo( "Path" ) )
            # fetch changelog for current revision
            if ( kind == "changelog" ):
                log = client.log( url_or_path=info[ "url" ], limit=25, revision_start=pysvn.Revision( pysvn.opt_revision_kind.number, info[ "commit_revision" ].number ) )
            # updates
            else:
                log = client.log( url_or_path=info[ "url" ], limit=25, revision_end=pysvn.Revision( pysvn.opt_revision_kind.number, info[ "commit_revision" ].number + 1 ) )
        except:
            # changelog
            log = client.log( url_or_path="http://xbmc-addons.googlecode.com/svn/addons/%s" % ( Addon.getAddonInfo( "Id" ), ), limit=25 )
        # if no entries set user message
        if ( len( log ) ):
            # initialize our log variable
            changelog = "%s\n" % ( "-" * 150, )
        else:
            # should only happen for "updates" and there are none
            changelog = Addon.getLocalizedString( 30704 )
        # we need to compile so we can add DOTALL
        clean_entry = self.re.compile( "\[.+?\][\s]+(?P<name>[^\[]+)(?:\[.+)?", self.re.DOTALL )
        # iterate thru and format each message
        for entry in log:
            # add heading
            changelog += "r%d - %s - %s\n\n" % ( entry[ "revision" ].number, datetime.datetime.fromtimestamp( entry[ "date" ] ).strftime( date_format ), entry[ "author" ], )
            # add formatted message
            changelog += "\n".join( [ self.re.sub( "(?P<name>^[a-zA-Z])", "- \\1", line.lstrip( " -" ) ) for line in clean_entry.sub( "\\1", entry[ "message" ] ).strip().splitlines() ] )
            # add separator
            changelog += "\n%s\n" % ( "-" * 150, )
        # return colorized result
        return self._colorize_text( changelog )

    def _pysvn_cancel_callback( self ):
        # check if user cancelled operation
        return False

    def _colorize_text( self, text ):
        # format text using colors
        text = self.re.sub( "(?P<name>r[0-9]+ - .+?)(?P<name2>[\r\n]+)", "[COLOR FF0084FF]\\1[/COLOR]\\2", text )
        text = self.re.sub( "(?P<name>http://[\S]+)", "[COLOR FFEB9E17]\\1[/COLOR]", text )
        text = self.re.sub( "(?P<name>[^\]]r[0-9]+)", "[COLOR FFEB9E17]\\1[/COLOR]", text )
        text = self.re.sub( "(?P<name>\".+?\")", "[COLOR FFEB9E17]\\1[/COLOR]", text )
        text = self.re.sub( "(?P<name>[A-Z ]+:)[\r\n]+", "[COLOR FF0084FF][B]\\1[/B][/COLOR]\n", text )
        text = self.re.sub( "(?P<name> - )", "[COLOR FFFFFFFF]\\1[/COLOR]", text )
        text = self.re.sub( "(?P<name>-[-]+)", "[COLOR FFFFFFFF]\\1[/COLOR]", text )
        # return colorized text
        return text


def _reset_watched_status( reset_type ):
    # spam log file
    LOG( ">>> _reset_watched_status( %s )" % ( reset_type, ), heading=True )
    # initialize base_path
    base_paths = []
    # clear slides or trailers
    if ( reset_type == "trailers" ):
        # trailer settings, grab them here so we don't need another Addon.getSetting() object
        settings = { "trailer_amt_db_file":  xbmc.translatePath( Addon.getSetting( "trailer_amt_db_file" ) ) }
        # handle AMT db special
        from resources.scrapers.amt_database import scraper as scraper
        Scraper = scraper.Main( settings=settings )
        # update trailers
        Scraper.clear_watched()
        # set base watched file path
        base_paths += [ os.path.join( Addon.getAddonInfo( "Profile" ), "trailers_watched.txt" ) ]
        ##base_paths += [ os.path.join( BASE_CURRENT_SOURCE_PATH, "local_watched.txt" ) ]
    else:
        # set base watched file path
        base_paths = [ os.path.join( BASE_CURRENT_SOURCE_PATH, "slides_watched.txt" ) ]

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
        LOG( "*** Resetting %s watched status failed! - (%s)" % ( reset_type, str( e ), ), xbmc.LOGERROR )
    # spam log file
    LOG( "<<< _reset_watched_status( %s )" % ( reset_type, ), heading=True )
    # close main dialog
    pDialog.close()
    # notify user of result
    ok = xbmcgui.Dialog().ok( Addon.getLocalizedString( 32000 ), Addon.getLocalizedString( message ) )


def watched_status_file( filename, watched=[] ):
    try:
        # set base watched file path
        base_path = os.path.join( xbmc.translatePath( "special://profile/" ), "script_data", os.path.basename( os.getcwd() ), filename )
        # if the path to the source file does not exist create it
        if ( not os.path.isdir( os.path.dirname( base_path ) ) ):
            os.makedirs( os.path.dirname( base_path ) )
        # open source path for reading
        file_object = open( base_path, ( "w", "r", )[ watched == [] ] )
        # read/write file
        if ( watched == [] ):
            # read file
            watched = eval( file_object.read() )
        else:
            # write file
            file_object.write( repr( watched ) )
        # close file object
        file_object.close()
    except Exception, e:
        # oops, notify user what error occurred
        LOG( "*** %s" % ( e, ), xbmc.LOGERROR )
    # return result
    return watched


if ( __name__ == "__main__" ):
    # need this while debugging
    if ( len( sys.argv ) == 1 ):
        sys.argv.append( "changelog" )
    # clear aliases
    if ( sys.argv[ 1 ] == "clearaliases" ):
        _clear_artist_aliases()
    # show info
    elif ( sys.argv[ 1 ] in [ "updates", "changelog", "readme", "license" ] ):
        Viewer( kind=sys.argv[ 1 ] )
