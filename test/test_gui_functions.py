

def test_is_px_in_hex(gui_funcs):
    hex_origin = 100, 100

    # Rectangular points to check
    inside_px = 140, 140
    outisde_px = 99, 99
    way_outisde_px = 140, 1000

    # Points that are within the rectangle bounds (82x95), but either inside or outside the centered hexagon
    inside_hex_points = [(125, 115), (160, 115), (125, 180), (160, 180)]
    outside_hex_points = [(110, 110), (170, 110), (115, 185), (170, 185)]

    # Rectangular checks
    assert gui_funcs.is_px_in_hex(inside_px, hex_origin) is True
    assert gui_funcs.is_px_in_hex(outisde_px, hex_origin) is False
    assert gui_funcs.is_px_in_hex(way_outisde_px, hex_origin) is False

    # Hexagonal checks
    for inside_point in inside_hex_points:
        assert gui_funcs.is_px_in_hex(inside_point, hex_origin) is True

    for outside_point in outside_hex_points:
        assert gui_funcs.is_px_in_hex(outside_point, hex_origin) is False
