# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    Screens
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


screen sprite_creator(sprite, customizer):
    modal True

    hbox:
        use _cs_sprite_preview(sprite)
        use _cs_sprite_options(customizer)


screen _cs_sprite_preview(sprite):
    frame:
        background Solid("#9cb9cb")
        xsize 0.7
        ysize 1.0

        add sprite:
            xalign 0.5


screen _cs_sprite_options(customizer):
    frame:
        background Solid("#1f1f1f")
        ysize 1.0
        xsize 1.0

        vbox:
            spacing 50
            yalign 0.5
            xcenter 0.5

            for group, options in customizer.get_options_by_group().items():
                use _sc_option_group(customizer, group, options)

            null:
                height 50

            hbox:
                xalign 0.5
                spacing 50

                textbutton "Randomize":
                    action Function(customizer.randomize)

                textbutton "Done":
                    action Return(0)


screen _sc_option_group(sprite, group, options):
    vbox:
        spacing 20

        hbox:
            null:
                width 70
            text group:
                color "#FFB69D"

        hbox:
            null:
                width 100
            vbox:
                spacing 15
                for option_key, option in options.items():
                    use _sc_option_group_option(sprite, option_key, option)


screen _sc_option_group_option(sprite, option_key, option):
    hbox:
        text option.display_name:
            min_width 200
            line_leading 5
            color "#ccc"

        if isinstance(option, SCValueListOption):
            use _sc_value_list_option(option)
        elif isinstance(option, SCValidatableTextOption):
            use _sc_validatable_text_option(option)
        elif isinstance(option, SCTextOption):
            use _sc_text_option(option)
        elif isinstance(option, SCBooleanOption):
            use _sc_boolean_option(option)
        elif isinstance(option, SCColorOption):
            use _sc_color_option(option)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    Option Components
#
# The following screens are components for rendering specific types of options.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# Value List Option Selector
screen _sc_value_list_option(option):
    hbox:
        xsize 200

        imagebutton:
            auto "cc_gui_option_arrow_left_%s"
            xcenter 0.5
            ysize 50
            action Function(option.dec_selection)
        text "{:02d}".format(option.selection_index + 1):
            xcenter 0.5
            line_leading 5
        imagebutton:
            auto "cc_gui_option_arrow_right_%s"
            xcenter 0.5
            ysize 50
            action Function(option.inc_selection)


# Text Option Input
screen _sc_text_option(option):
    default option_value = SCTextInput(option)

    button:
        xsize 175

        key_events True
        action option_value.Toggle()

        background "#2e2c2c"
        hover_background "#383535"

        input:
            value option_value
            copypaste True

            if option.has_prefix:
                prefix option.prefix

            if option.has_suffix:
                suffix option.suffix

            if option.has_max_len:
                length option.max_len


# Validatable Text Option Input
screen _sc_validatable_text_option(option):
    default option_value = SCTextInput(option)

    button:
        xsize 175

        key_events True
        background "#2e2c2c"
        hover_background "#383535"
        action option_value.Toggle()

        input:
            value option_value
            copypaste True

            if not option.is_valid:
                color "#FF0000"

            if option.has_prefix:
                prefix option.prefix

            if option.has_suffix:
                suffix option.suffix

            if option.has_max_len:
                length option.max_len


# Boolean Option Input
screen _sc_boolean_option(option):
    hbox:
        xsize 200
        ysize 50

        imagebutton:
            xcenter 0.5
            ycenter 0.5

            if option.value:
                auto "cc_checkbox_checked_%s"
            else:
                auto "cc_checkbox_blank_%s"

            action Function(option.toggle)

screen _sc_color_option(option):
    hbox:
        xsize 200

        button:
            background "cc_color_button_idle"
            hover_background "cc_color_button_hover"
            xcenter 0.5
            ycenter 0.5
            padding (4, 4)

            add AlphaMask(option.preview_image_name, 'lib/fxcpds/sprite_customizer/images/color_button_mask2.png'):
                xsize 42
                ysize 42

            action Show("_cs_color_picker", None, option)