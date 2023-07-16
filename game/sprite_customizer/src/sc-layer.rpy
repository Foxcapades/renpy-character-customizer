init -1 python:
    class SCLayer:
        """
        # Sprite Customization Layer

        Represents a single layer in a customizable sprite.

        This layer has zero or more customization options provided at
        construction time via named `SCOpt` keyword args.  The user's selections
        of those options are then passed to the given `layer_callback` to
        construct the underlying Displayable for the layer.

        ```python
        SCLayer("name", callback, option=SCOpt("Option", [ "some", "choices" ]))
        ```
        """

        def __init__(self, name, layer_callback, transform=None, **options):
            """
            Initializes the new `SCLayer` instance with the given arguments.

            Arguments:

            name (str): Name of the layer.

            layer_callback (callable): Callback used to create the displayable
            that backs this layer.

            transform (callable): Optional transform function.  A function that
            takes a Displayable as a single argument and returns a Displayable.
            Allows performing arbitrary transforms on individual layers.

            **options (dict): Dictionary of keyword arguments that define the
            options available to this layer.  Keyword args must all be `SCOpt`
            values.
            """

            if not isinstance(name, str):
                raise Exception("SCLayer name must be a string.")
            if not callable(layer_callback):
                raise Exception("SCLayer layer_callback must be callable.")
            for key, opt in options.items():
                if not isinstance(opt, SCOpt):
                    raise Exception("SCLayer options must be SCOpt instances.")

            self._name  = name
            self._func  = layer_callback
            self._state = None
            self._options = options
            self._transform = transform

        def _require_option(self, option):
            """
            Requires that the given option keyword is known to this layer.
            """
            if option not in self._options:
                raise Exception("Unrecognized SCLayer option \"{}\"".format(option))

        def _render(self, st, at, **kwargs):
            """
            Render Callback

            This callback is passed to the underlying `DynamicDisplayable` to
            render the layer's image.

            This method calls out to the configured `layer_callback` callback
            with the options selected in the SCState.

            Returns:

            tuple:  A tuple containing 2 values; the `Displayable` generated by
            the `layer_callback` callback passed to the `SCLayer` on
            construction, and an int representing the time to pause before
            rerendering.
            """
            kwargs["st"] = st
            kwargs["at"] = at

            # Go through user state first to prevent it from overwriting real
            # option selections.  TODO: Should we allow overriding selections?
            for key, value in self._state._user_state_items().items():
                kwargs[key] = value

            for key in self._options.keys():
                kwargs[key] = self._options[key]._values[self._state.get_selection(key) - 1]

            out = self._func(**kwargs)

            return out if isinstance(out, tuple) else (out, 0.0)

        def clone(self):
            """
            Creates a clone of this layer instance.

            Returns:

            SCLayer: A new `SCLayer` instance containing the same values
            configured on this instance.
            """
            return SCLayer(self._name, self._func, self._transform, **self._options)

        def set_state(self, state):
            """
            Replaces the state of this `SCLayer` instance with the given
            `state` object.

            Arguments:

            state (SCState): New state object to back this layer's customization
            option selections.
            """
            if not isinstance(state, SCState):
                raise Exception("Cannot call set_state with a non SCState value.")
            self._state = state

        def inc_selection(self, option):
            """
            Increment Option Selection

            Increments the selection for the given option.

            Arguments:

            option str: Keyword for the option whose selection should be
            incremented.
            """
            self._require_option(option)
            self._state.inc_selection(option, self._options[option].size)

        def dec_selection(self, option):
            """
            Decrement Option Selection

            Decrements the selection for the given option.

            Arguments:

            option str: Keyword for the option whose selection should be
            decremented.
            """
            self._require_option(option)
            self._state.dec_selection(option, self._options[option].size)

        def get_option(self, option):
            self._require_option(option)
            return self._options[option]

        def get_option_count(self, option):
            """
            Returns the number of options in the target option group.

            Arguments:

            option (str): Keyword for the option group whose size should be
            retrieved.

            Returns:

            int: The number of options in the target option group.
            """
            self._require_option(option)
            return self._options[option].size

        def get_option_value(self, option, selection):
            """
            Returns the target option value.

            Arguments:

            option (str): Keyword for the option whose value should be returned.

            selection (int): 1 based index of the option value to retrieve.
            """
            self._require_option(option)
            return self._options[option]._values[selection - 1]

        def get_selected_option_value(self, option):
            """
            Returns the currently selected option value for the target option.

            ```python
            my_layer = SCLayer("layer", callback, option=SCOpt("Option", [ "option 1", "option 2" ]))
            my_layer.set_state(SCState())

            my_layer.get_selected_option_value("option") == "option 1"

            my_layer.inc_selection("option")

            my_layer.get_selected_option_value("option") == "option 2"
            ```

            Arguments:

            option (str): Keyword for the option whose user selected value
            should be returned.

            Returns:

            any: The currently selected option value for the target option.
            """
            return self.get_option_value(option, self.get_option_selection(option))

        def get_option_display_name(self, option):
            """
            Returns the display name for the target option.

            Arguments:

            option (str): Keyword for the target option whose display name
            should be returned.

            Returns:

            str: The display name for the target option.
            """
            self._require_option(option)
            return self._options[option].display_name

        def get_option_selection(self, option):
            """
            Returns the user selection index for the target option.

            Arguments:

            option (str): Keyword for the option whose selection index should
            be returned.

            Returns:

            int: The user selection index for the target option.
            """
            self._require_option(option)
            return self._state.get_selection(option)

        def build_image(self, **kwargs):
            """
            Build Image

            Builds the DynamicDisplayable that represents this `SCLayer`
            instance.

            Returns:

            DynamicDisplayable: The DynamicDisplayable that represents this
            `SCLayer` instance.
            """
            if self._transform == None:
                return DynamicDisplayable(self._render, **kwargs)

            return self._transform(DynamicDisplayable(self._render, **kwargs))

        def build_attribute(self):
            """
            Build Attribute

            Builds a LayeredImage Attribute instance to represent this `SCLayer`
            instance.

            Returns:

            Attribute: A LayeredImage Attribute instance to represent this
            `SCLayer` instance.
            """
            return Attribute(None, self._name, image=self.build_image(), default=True)
