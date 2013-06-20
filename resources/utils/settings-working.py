setting = """        <setting label="$ADDON[script.cinema.experience 30410] #%d" type="select" id="playlist_item%d" default="$ADDON[script.cinema.experience 30411]" lvalues="30411|30412|30413|30414|30415|30416|30417|30418|30419"%s/>
        <setting label="30430" subsetting="true" type="enum" id="playlist_item%d_number" default="1" lvalues="30431|30432|30433|30434|30435|30436|30437" visible="StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30413]) + [Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d)]"/>
        <setting label="30440" subsetting="true" type="file" id="playlist_item%d_file" default="" source="auto" mask="$IMAGE|$VIDEO" visible="!IntegerGreaterThan(Addon.Setting(playlist_item%d_number),0) + Control.IsVisible(%d)"/>
        <setting label="30450" subsetting="true" type="folder" id="playlist_item%d_folder" default="" source="auto" visible="IntegerGreaterThan(Addon.Setting(playlist_item%d_number),0) + Control.IsVisible(%d)"/>
        <setting label="30460" subsetting="true" type="slider" id="playlist_item%d_duration" default="10" range="5,1,60" format="%%1.f $ADDON[script.cinema.experience 30461]" visible="Control.IsVisible(%d)"/>
        <setting type="sep" visible="Control.IsVisible(%d)"/>"""

"""
        <!--201-->
        <setting label="$ADDON[script.cinema.experience 30410] #1" type="select" id="playlist_item1" default="$ADDON[script.cinema.experience 30411]" lvalues="30411|30412|30413|30414|30415|30416|30417|30418|30419|30420"/>
        <!--202-->
        <setting label="30460" subsetting="true" type="enum" id="playlist_item1_number" default="1" lvalues="30461|30462|30463|30464|30465|30466|30467" visible="[StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30416]) | StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30420])] + [Control.HasFocus(201) | Control.HasFocus(202) | Control.HasFocus(203) | Control.HasFocus(204) | Control.HasFocus(205) | Control.HasFocus(207)]"/>
        <!--203-->
        <setting label="30480" subsetting="true" type="image" id="playlist_item1_image_file" default="" source="auto" visible="!IntegerGreaterThan(Addon.Setting(playlist_item1_number),0) + StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30416]) + Control.IsVisible(202)"/>
        <!--204-->
        <setting label="30480" subsetting="true" type="video" id="playlist_item1_video_file" default="" source="auto" visible="!IntegerGreaterThan(Addon.Setting(playlist_item1_number),0) + StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30420]) + Control.IsVisible(202)"/>
        <!--205-->
        <setting label="30485" subsetting="true" type="folder" id="playlist_item1_folder" default="" source="auto" visible="IntegerGreaterThan(Addon.Setting(playlist_item1_number),0) + Control.IsVisible(202)"/>
        <!--206-->
        <setting label="30430" subsetting="true" type="slider" id="playlist_item1_duration" default="10" range="2,1,61" format="%1.f $ADDON[script.cinema.experience 30431],,$ADDON[script.cinema.experience 30432]" visible="[StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30418]) | StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30419])] + [Control.HasFocus(201) | Control.HasFocus(206) | Control.HasFocus(207) | Control.HasFocus(208)]"/>
        <!--207-->
        <setting label="30440" subsetting="true" type="slider" id="playlist_item1_image_duration" default="15" range="5,1,60" format="%1.f $ADDON[script.cinema.experience 30441]" visible="StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30416]) | StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30419]) + [Control.HasFocus(201) | Control.HasFocus(202) | Control.HasFocus(203) | Control.HasFocus(204) | Control.HasFocus(205) | Control.HasFocus(206) | Control.HasFocus(207) | Control.HasFocus(208)]"/>
        <!--208-->
        <setting label="30450" subsetting="true" type="bool" id="playlist_item1_slideshow_music" default="true" visible="StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30419]) + [Control.HasFocus(201) | Control.HasFocus(206) | Control.HasFocus(207) | Control.HasFocus(208)]" enable="[StringCompare(Addon.Setting(music_type),0) + !IsEmpty(Addon.Setting(music_playlist))] | [StringCompare(Addon.Setting(music_type),1) + !IsEmpty(Addon.Setting(music_folder))]"/>
        <!--209-->
        <setting type="sep" visible="Control.IsVisible(202) | Control.IsVisible(203) | Control.IsVisible(204) | Control.IsVisible(205) | Control.IsVisible(206) | Control.IsVisible(207) | Control.IsVisible(208)"/>
"""

visible = 201
status = ""
status2 = 1
visible2 = 201
for control in range( 1, 16 ):
    print setting % ( control, control, status, control, control, visible, visible + 1, visible + 2, visible + 3, visible + 4, control, control, visible + 1, control, control, visible + 1, control, visible + 1, visible + 1, )

    status = " visible=\"%s\" allowhiddenfocus=\"true\"" % ( " + ".join( [ "!Control.IsVisible(%d)" % ( visible2 + i*6 + 1, ) for i in range( status2 ) ] ), )
    visible += 6
    if ( status2 < 3 ):
        status2 += 1
    else:
        visible2 += 6

    #print status