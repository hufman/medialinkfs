MediaLinkFS  [![Build Status](https://api.travis-ci.org/hufman/medialinkfs.png)](https://travis-ci.org/hufman/medialinkfs)
===========

This is a project that collects metadata about media items and creates symlinks to tag each item in multiple collections, for example Artist or Genre. This managed set of symlinks replicates some of the functionality of a media library application, while allowing any program to browse the library.

For example, it will put a symlink to /media/tv/All/Archer into /media/tv/Actors/Chris Parnell and /media/tv/Actors/Judy Greer and so on.

Organizational Concepts
-----------------------

MediaLinkFS is given a path to a directory of media items, such as music albums or tv shows. Information about each item is then collected by a metadata plugin. MediaLinkFS will then use the metadata to create groups, such as artist names. All media objects then get sorted into each group based on its metadata.

Useful Features
---------------

* Quick resume after interruptions

  Progress is saved during organization, so that the process can resume quickly after interruptions

* Metadata cache

  MediaLinkFS saves a copy of any metadata it finds for any media item, and will use that cache if metadata for an item couldn't be located on later runs. MediaLinkFS can also be configured to save time and not look up metadata if a cached copy is found. A commandline flag exists to ignore any cached data.

* Detailed logs

  The logs say exactly why an item couldn't be found with the metadata plugin. The logs will show exactly what steps it went through to find each item.

* Cleanup of old links

  If a directory is renamed, or the metadata changes, MediaLinkFS will automatically clean up the old symlinks that used to point at it. If a group of metadata is no longer necessary, it will clean up that directory.

* Manual organization

  The user can specify a list of symlinks that the user has maintained manually and the program will not clean these extra links.

* Multiset

  Multiple sets, such as TV and Movies, can be organized into the same directory. For example, a global Actors directory could be generated, containing each actor's movie and tv appearances.

* Chainable metadata parsers

  Parsers can use the information discovered by previous parsers in the parser list. For example, the quantizer plugin adds a decade value based on the year found by other plugins.

Installation
------------

1. Install Python3 and the PyYAML library
2. Check out this repository
3. Edit config.yml
4. ./main.py -c config.yml

Plugins
-------

* parsename

  Attempts to parse a few common patterns out of the given folder or file name. It also removes any found data from the name key, providing a cleaner name for subsequent modules to use.

  * year - A 4 digit number that starts with 19 or 20
  * resolution - A number from a list of common video resolutions
  * format - h264, x264, avc, xvid, or divx
  * release\_group - A release group, if one directly follows the format field
  * extension - Any detected extension at the end of the filename
  * name - The rest of the filename that wasn't matched by the above

* id3

  Parses out ID3 tags from mp3s, and gets the following information. If it is told to scan a directory, it will parse the directory as an album, collecting information recursively about the contained files. The plural items, like artists, may be useful for mix albums or directories.

  * album
  * album\_artist
  * artist
  * composer
  * genre
  * title
  * track\_total
  * date
  * albums
  * artists
  * composers

* freebase

  The freebase plugin is very flexible, supporting user-customizable queries to freebase.com.  It comes with a few common queries. Add a type option to the parser\_options to set one. This is used in the film and tv\_program options to search with the year information. Without a type, the plugin will search for everything on freebase by the name, and then try to fill in any extra properties that it finds for that item.

  Properties that are found through the properties option will be added to the metadata object. If the property name does not show up in the renames option, then the full property name will be used, otherwise the renamed metadata name.

  Heavy usage of the freebase plugin may require an API key for Freebase from the [Google API Console](https://code.google.com/apis/console). This key is set in the api\_key parser\_option. Some usage is available without a key, but there isn't clear documentation of how much. The limit with the API key is 100k requests per day.

  * type - A freebase schema type. The following types are built-in:
      * /film/film
      * /tv/tv\_program
  * searches - A dictionary of hashes, each hash describing how to map from the discovered name and year to a search query
  * properties - A dictionary of MQL parameters to search for, such as {"/film/film/directed\_by":[]}
  * renames - A dictionary of freebase properties to be renamed to shorter metadata keys. If a search returns a property that is not in this list, then the full name will be available in the metadata. The following properties are renamed by default:
      * /common/topic/alias -> aka
      * /film/film/initial\_release\_date -> release\_date
      * /film/film/directed\_by -> directors
      * /film/film/starring -> actors
      * /film/film/genre -> genres
      * /film/film/subjects -> subjects
      * /film/film/film\_series -> series
      * /film/film/produced\_by -> producers
      * /film/film/written\_by -> writers
      * /film/film/edited\_by -> editors
      * /film/film/music -> composers
      * /film/film/language -> languages
      * /film/film/country -> countries
      * /tv/tv\_program/regular\_cast -> actors
      * /tv/tv\_program/air\_date\_of\_first\_episode -> release\_date
      * /tv/tv\_program/genre -> genres
      * /tv/tv\_program/tv\_producer -> producers
      * /tv/tv\_program/recurring\_writers -> writers
      * /tv/tv\_program/original\_network -> network
      * /tv/tv\_program/country\_of\_origin -> countries
      * /tv/tv\_program/languages -> languages
  * promotions - A dictionary of freebase properties that should be promoted from a list of dictionaries to a regular list. For example, instead of /film/film/starring being a structure such as [{"actor":"name1"},{"actor":"name2"}], this changes it to a structure such as ["name1","name2"]. The following properties are changed by default:
      * /film/film/starring['actor']
      * /tv/tv\_program/regular\_cast['actor']
      * /tv/tv\_program/original\_network['network']
      * /tv/tv\_program/recurring\_writers['writers']
      * /tv/tv\_program/tv\_producer['producer']

* mymovieapi

  Looks up information about a collection of TV of movies, and discovers the following information. mymovieapi returns a complete list of actors, but has a limit of 2500 item lookups per day.

  * genres
  * actors
  * year
  * rated

  The mymovieapi plugin supports a parser option of type, which must be one of the following. It defaults to searching for any type.

  * movie
  * tv movie
  * tv servies
  * video
  * video game

* omdbapi

  Looks up information about a collection of TV or movies, and discovers the following information:

  * genres
  * writers
  * directors
  * actors
  * rated
  * year

* quantizer

  Looks through the previously discovered metadata and quantizes the year into decades:

  * decade  (1980)
  * decades  (1980s)

* vgmdb

  Looks up information about a collection of video game albums, and discovers the following information:

  * arrangers
  * composers
  * games
  * lyricists
  * performers
  * artists - an alias of composers
  * franchises

Configuration
-------------

Invoking the main.py command requires a configuration to be passed with the -c argument. This is a file, in YAML format, that describes how to organize the media.

At the root of the YAML document is a single item, sets. This is a list of set configurations, and each set describes how to organize each set of media. There may also be two other items, default\_settings and override\_settings. These configuration items are merged into each set configuration, so that the specific set configuration overrides the default\_settings and the override\_settings will override those.

### Set Configuration

- name: The name of this set, used in logging and in state retention
- parsers: A list of parser modules to use when loading metadata for these items
- parser\_options: A mapping of parser modules to any custom options specific to that parser module
- scanMode: The method used to find media items in this collection, which must be one of the following:
  - toplevel - Use any file or directory directly underneath the sourceDir
  - directories - Use any directories directly underneath the sourceDir
  - files - Use any files directly underneath the sourceDir
- sourceDir: The full path to the media directory
- cacheDir: The full path to the directory where MediaLinkFS should store any temporary state specific to this set. Defaults to the .cache directory directly under sourceDir
- regex: An optional regex that will be searched for in each item's path. If this setting exists, it will only organize items that match. Each parser\_options setting can have a regex specific to that parser
- noclean: Don't delete any extra files from the output directories
- fakeclean: Indicate what directories and files would be cleaned out at the end of a run, but don't actually clean them
- preferCachedData: If an item has cached metadata from a previous run, don't search for new metadata. This is helpful with the mymovieapi plugin, because it has a query limit
- output: A list of output directories to manage

### Output Configuration

- dest: The full path to the directory to make the group directories
- groupBy: The metadata key of each item to use as the basis for grouping. This can also be an array of keys

Example Config
--------------

    sets:
      - name: TV
        parsers: [omdb]
        scanMode: directories
        sourceDir: /media/tv/All
        cacheDir: /media/tv/.cache
        fakeclean: false
        preferCachedData: true
        output:
          - dest: /media/tv/Actors
            groupBy: actors

Extra Details
-------------

As the program runs through a set, it adds every processed item into a .progress file in the set's cacheDir. This file is used to resume a set's progress the next time it is run. When the set is complete, it will remove this progress file so that it will rescan everything on the next run.

Every output directory will have a .toc file that represents what contents have been added to the directory during that run. After a completed run, the program will go through every managed directory and remove any symlink and empty directory that is not mentioned in the .toc file. When complete, it will move the .toc file to .toc.done, to remember that it has finished cleaning the directory and to skip cleaning it if the program doesn't successfully finish the entire cleaning process. Any previous .toc.done files are renamed to .toc.old, and any previous .toc.old files are deleted.

During the cleanup process, it will not remove any links that are mentioned in .toc.extra, any real files, or any non-empty directories. This allows the user to manually create links and add their names to .toc.extra to prevent MediaLinkFS from removing them. It will also not delete a directory if it is the sourceDir, allowing the sourceDir to safely be a subdirectory of an output directory.

The .toc files are suffixed by the set name, which is used to allow multiple sets to use the same output directories. However, once a media item has been mentioned in .toc.done, MediaLinkFS will not clean it from that directory. If an old set should no longer be in an output directory, remove all .toc.done files for that set in the directory.

In the set's cacheDir, several files that start with .cache- will show up after a run. These files contain all of the cached metadata for each media item. These files can be removed to clear the cache. Each file's modification date indicates the last time a metadata search has been run, which can be used to implement an external cache cleaning policy.
