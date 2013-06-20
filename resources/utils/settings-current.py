setting = """        <setting label="$ADDON[script.cinema.experience 30410] #%d" type="select" id="playlist_item%d" default="$ADDON[script.cinema.experience 30411]" lvalues="30411|30412|30413|30414|30415|30416|30417|30418|30419|30420"%s/>
        <setting label="30430" subsetting="true" type="enum" id="playlist_item%d_number_items" default="1" lvalues="30431|30432|30433|30434|30435|30436|30437" visible="[StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30416]) | StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30420])] + [Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d)]"/>
        <setting label="30440" subsetting="true" type="image" id="playlist_item%d_file_image" default="" source="auto" visible="StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30416]) + !IntegerGreaterThan(Addon.Setting(playlist_item%d_number_items),0) + Control.IsVisible(%d)"/>
        <setting label="30440" subsetting="true" type="video" id="playlist_item%d_file_audio" default="" source="auto" visible="StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30418]) + !IntegerGreaterThan(Addon.Setting(playlist_item%d_number_items),0) + Control.IsVisible(%d)"/>
        <setting label="30440" subsetting="true" type="video" id="playlist_item%d_file_video" default="" source="auto" visible="StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30420]) + !IntegerGreaterThan(Addon.Setting(playlist_item%d_number_items),0) + Control.IsVisible(%d)"/>
        <setting label="30445" subsetting="true" type="folder" id="playlist_item%d_folder" default="" source="auto" visible="IntegerGreaterThan(Addon.Setting(playlist_item%d_number_items),0) + Control.IsVisible(%d)"/>
        <setting label="30450" subsetting="true" type="slider" id="playlist_item%d_image_duration" default="15" range="5,1,60" format="%%1.f $ADDON[script.cinema.experience 30451]" visible="StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30416]) + Control.IsVisible(%d)"/>
        <setting label="30430" subsetting="true" type="enum" id="playlist_item%d_number_trailers" default="1" lvalues="30462|30463|30464|30465|30466|30467" visible="StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30413]) + [Control.HasFocus(%d) | Control.HasFocus(%d)]"/>
        <setting label="30470" subsetting="true" type="slider" id="playlist_item%d_duration" default="15" range="2,1,60" format="%%1.f $ADDON[script.cinema.experience 30471],,$ADDON[script.cinema.experience 30472]" visible="[StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30418]) | StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30419])] + [Control.HasFocus(%d) | Control.HasFocus(%d)]"/>
        <setting label="30480" subsetting="true" type="enum" id="playlist_item%d_action" default="0" lvalues="30481|30482|30483|30484|30485|30486|30487" visible="StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30412])] + [Control.HasFocus(%d) | Control.HasFocus(%d)]"/>
        <setting type="sep" visible="Control.IsVisible(%d) | Control.IsVisible(%d) | Control.IsVisible(%d) | Control.IsVisible(%d)"/>"""

"""

        visible="![Control.IsVisible(211)]" allowhiddenfocus="true"/>
        visible="![Control.IsVisible(222) | Control.IsVisible(202)]" allowhiddenfocus="true"/>
        visible="![Control.IsVisible(233) | Control.IsVisible(213) | Control.IsVisible(207)]" allowhiddenfocus="true"/>
"""
groupcontrol1 = 201
status = ""
visible = 211

for control in range( 1, 16 ):
    print setting % (
        control, control, status,
        control, control, control, groupcontrol1, groupcontrol1 + 1, groupcontrol1 + 2, groupcontrol1 + 3, groupcontrol1 + 4, groupcontrol1 + 5, groupcontrol1 + 6,
        control, control, control, groupcontrol1 + 1,
        control, control, control, groupcontrol1 + 1,
        control, control, control, groupcontrol1 + 1,
        control, control, groupcontrol1 + 1,
        control, control, groupcontrol1 + 1,
        control, control, groupcontrol1, groupcontrol1 + 7,
        control, control, control, groupcontrol1, groupcontrol1 + 8,
        control, control, groupcontrol1, groupcontrol1 + 9,
        groupcontrol1 + 1, groupcontrol1 + 7, groupcontrol1 + 8, groupcontrol1 + 9,
    )
    
    status = "Control.IsVisible(%d)" % (visible,)
    if control > 1:
        status += " | Control.IsVisible(%d)" % (visible - 20,)
    if control > 2:
        status += " | Control.IsVisible(%d)" % (visible - 26,)
    status = " visible=\"![%s]\" allowhiddenfocus=\"true\"" % status
    #print status
    groupcontrol1 += 11
    visible += 11
    
    
    