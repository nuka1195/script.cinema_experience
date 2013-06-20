## Cinema Experience

"""
    Cinema Experience:
    - creates a movie theater experience in the privacy of your home
    
    - plays # of optional Movie Theater intro videos
    - plays optional slideshow w/ optional music, intro/outro videos/still images
    - plays # of optional random trailers w/ optional intro/outro videos
    - plays highlighted video w/ optional intro/outro videos, rating video and dolby/dts video
    - plays # optional Movie Theater outro videos
"""

import os
import sys
import xbmcgui
import xbmcaddon

# Addon class
Addon = xbmcaddon.Addon( id="script.cinema.experience" )

# notify user of progress
pDialog = xbmcgui.DialogProgress()
pDialog.create( Addon.getAddonInfo( "Name" ), Addon.getLocalizedString( 30800 )  )
pDialog.update( 0 )

sys.path.append( Addon.getAddonInfo( "Profile" ) )


if ( __name__ == "__main__" ):
    # create experience
    from resources.lib.experience import *
    experience = Experience( Addon=Addon, dialog=pDialog ).create_experience()
    # if successful play experience
    if ( isinstance( experience, list ) ):
        for item in experience:
            print item
    # an error occurred
    else:
        print experience
    # we're finished
    pDialog.close()
