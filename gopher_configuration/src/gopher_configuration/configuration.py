#
# License: Yujin
#
##############################################################################
# Description
##############################################################################

"""
.. module:: configuration
   :platform: Unix
   :synopsis: Gopher deliveries configuration in a usable structure.

Oh my spaghettified magnificence,
Bless my noggin with a tickle from your noodly appendages!

----

"""

##############################################################################
# Imports
##############################################################################

import gopher_std_msgs.msg as gopher_std_msgs
import os
import rocon_console.console as console
import rospkg
import rospy
import yaml

##############################################################################
# Configuration
##############################################################################


def _error_logger(msg):
    print(console.red + "Configuration : %s" % msg + console.reset)

##############################################################################
# Configuration
##############################################################################


class ConfigurationGroup(object):
    def __str__(self):
        s = console.green + "  " + type(self).__name__ + "\n" + console.reset
        for key, value in self.__dict__.iteritems():
            s += console.cyan + "    " + '{0: <20}'.format(key) + console.reset + ": " + console.yellow + "%s\n" % (value if value is not None else '-')
        s += console.reset
        return s


class LEDPatterns(ConfigurationGroup):
    """
    Self-defined group that associates certain colours with various actions.

    Unfortunately can't put these in the yaml yet. To do that, need to have string mappings to these
    message values. Maybe they themselves can be strings?
    """
    def __init__(self):
        # human interactions
        self.humans_give_me_input = gopher_std_msgs.Notification.FLASH_BLUE
        self.humans_be_careful = gopher_std_msgs.Notification.FLASH_YELLOW
        self.humans_i_need_help = gopher_std_msgs.Notification.FLASH_PURPLE
        # notifications
        self.holding = gopher_std_msgs.Notification.AROUND_RIGHT_BLUE
        # states
        self.error = gopher_std_msgs.Notification.SOLID_RED

    def validate(self):
        return (True, None)

    def __str__(self):
        s = console.green + "  " + type(self).__name__ + "\n" + console.reset
        s += console.cyan + "    " + '{0: <20}'.format("humans_give_me_input") + console.reset + ": " + console.yellow + "flashing blue\n"
        s += console.cyan + "    " + '{0: <20}'.format("humans_be_careful") + console.reset + ": " + console.yellow + "flashing yellow\n"
        s += console.cyan + "    " + '{0: <20}'.format("humans_i_need_help") + console.reset + ": " + console.yellow + "flashing purple\n"
        s += console.cyan + "    " + '{0: <20}'.format("holding") + console.reset + ": " + console.yellow + "around blue\n"
        s += console.cyan + "    " + '{0: <20}'.format("error") + console.reset + ": " + console.yellow + "solid red\n"
        return s


class Buttons(ConfigurationGroup):
    def __init__(self, buttons_dict):
        self.__dict__ = buttons_dict

    def validate(self):
        for key in ['go', 'stop']:
            if key not in self.__dict__.keys():
                return (False, "no definition for button '%s'" % key)
        return (True, None)


class Frames(ConfigurationGroup):
    def __init__(self, frames_dict):
        self.__dict__ = frames_dict

    def validate(self):
        for key in ['map']:
            if key not in self.__dict__.keys():
                return (False, "no definition for frame '%s'" % key)
        return (True, None)


class Actions(ConfigurationGroup):
    def __init__(self, actions_dict):
        self.__dict__ = actions_dict

    def validate(self):
        for key in ['teleport']:
            if key not in self.__dict__.keys():
                return (False, "no definition for action '%s'" % key)
        return (True, None)


class Services(ConfigurationGroup):
    def __init__(self, services_dict):
        self.__dict__ = services_dict

    def validate(self):
        for key in ['clear_costmaps']:
            if key not in self.__dict__.keys():
                return (False, "no definition for service '%s'" % key)
        return (True, None)


class Sounds(ConfigurationGroup):
    def __init__(self, sounds_dict):
        self.__dict__ = sounds_dict

    def validate(self):
        for key in ['honk']:
            if key not in self.__dict__.keys():
                return (False, "no definition for sound '%s'" % key)
        return (True, None)


class Topics(ConfigurationGroup):
    def __init__(self, topics_dict):
        self.__dict__ = topics_dict

    def validate(self):
        for key in ['display_notification', 'initial_pose', 'switch_map']:
            if key not in self.__dict__.keys():
                return (False, "no definition for topic '%s'" % key)
        return (True, None)


class Namespaces(ConfigurationGroup):
    def __init__(self, namespaces_dict):
        self.__dict__ = namespaces_dict

    def validate(self):
        for key in ['semantics']:
            if key not in self.__dict__.keys():
                return (False, "no definition for namespace '%s'" % key)
        return (True, None)


class Configuration(object):
    """
    Shared parameter storage/instantiation for gopher behaviours.

    This uses the `Borg Pattern`_, so feel free to instantiate as many times
    inside a process as you wish.


    *Usage*:

    The simplest use case is to load your configuration and its customisation on the
    rosparam server in the ``/gopher/configuration`` namespace. This namespace is
    the default lookup location for this class.

    To do this, include a snippet like that below to load it for your robot:

    .. code-block:: xml
           :linenos:

           <launch>
               <rosparam ns="/gopher/configuration" command="load" file="$(find gopher_configuration)/param/defaults.yaml"/>
               <rosparam ns="/gopher/configuration" command="load" file="$(find foo_configuration)/param/customisation.yaml"/>
           <launch>

    And then instantiate this class as an interface to that configuration.

    .. code-block:: python
       :linenos:

       gopher = gopher_configuration.Configuration()
       print("%s" % gopher)
       print("%s" % gopher.topics)
       print("Honk topic name: %s" % gopher.sounds.honk)
       print("Global frame id: %s" % gopher.frames.global)

    .. _Borg Pattern: http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

    """
    # two underscores for class private variable
    #   http://stackoverflow.com/questions/1301346/the-meaning-of-a-single-and-a-double-underscore-before-an-object-name-in-python
    __shared_state = {}

    @staticmethod
    def load_defaults():
        """
        Loads the default yaml, useful for referencing the default configuration.
        This is used by the ``gopher_configuration`` command line script.
        """
        rospack = rospkg.RosPack()
        pkg_path = rospack.get_path("gopher_configuration")
        filename = os.path.join(pkg_path, "param", "defaults.yaml")
        Configuration.__shared_state = yaml.load(open(filename))

    @staticmethod
    def load_from_rosparam_server(namespace='/gopher/configuration'):
        """
        This automatically gets called if you try to instantiate before
        it has retrieved anything from the rosparam server.
        It can also be called by the user to point the configuration
        to a different location on the rosparam server for all
        future instances of this class. This is not a common use
        case though.

        As an example, to load and retrieve configuration from a
        namespace called ``foo``:

        .. code-block:: xml
           :linenos:

           <launch>
               <rosparam ns="/foo/configuration" command="load" file="$(find gopher_configuration)/param/defaults.yaml"/>
               <rosparam ns="/foo/configuration" command="load" file="$(find foo_configuration)/param/customisation.yaml"/>
           <launch>

        .. code-block:: python
           :linenos:

           gopher_configuration.Configuration.load_from_rosparam_server(namespace='/foo/configuration')
           gopher = gopher_configuration.Configuration()

        """
        try:
            Configuration.__shared_state = rospy.get_param(namespace)
        except KeyError:
            rospy.logerr("Gopher Configuration : could not find configuration on the rosparam server")
            rospy.logerr("Gopher Configuration : is it looking in the right place? [%s]" % namespace)

    def __init__(self, error_logger=_error_logger):
        if not Configuration.__shared_state:
            Configuration.load_from_rosparam_server()
        core = ['actions', 'buttons', 'namespaces', 'frames', 'topics', 'services', 'sounds', 'led_patterns']
        try:
            # catch our special groups
            self.actions      = Actions(Configuration.__shared_state['actions'])        # @IgnorePep8
            self.buttons      = Buttons(Configuration.__shared_state['buttons'])        # @IgnorePep8
            self.namespaces   = Namespaces(Configuration.__shared_state['namespaces'])  # @IgnorePep8
            self.frames       = Frames(Configuration.__shared_state['frames'])          # @IgnorePep8
            self.sounds       = Sounds(Configuration.__shared_state['sounds'])          # @IgnorePep8
            self.services     = Services(Configuration.__shared_state['services'])      # @IgnorePep8
            self.topics       = Topics(Configuration.__shared_state['topics'])          # @IgnorePep8
            self.led_patterns = LEDPatterns()
        except KeyError:
            error_logger("at least one of the core parameter groups missing %s" % core)
            return
        for name in core:
            parameter_group = getattr(self, name)
            (result, error_message) = parameter_group.validate()
            if not result:
                error_logger("%s" % error_message)
        # catch everything else
        for key, value in Configuration.__shared_state.iteritems():
            if key not in core:
                setattr(self, key, value)

    def __str__(self):
        s = console.bold + "\nGopher Configuration:\n\n" + console.reset
        for key, value in self.__dict__.iteritems():
            if isinstance(value, ConfigurationGroup):
                s += ("%s" % value)
            else:
                s += console.cyan + "    %s: " % key + console.yellow + "%s\n" % (value if value is not None else '-')
        s += console.reset
        return s