MediaLinkFS
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

* Detailed logs

  The logs say exactly why an item couldn't be found with the metadata plugin. The logs will show exactly what steps it went through to find each item.

* Cleanup of old links

  If a directory is renamed, or the metadata changes, MediaLinkFS will automatically clean up the old symlinks that used to point at it. If a group of metadata is no longer necessary, it will clean up that directory.

Plugins
-------

* mymovieapi

  Looks up information about a collection of TV of movies, and discovers the following information. mymovieapi returns a complete list of actors, but has a limit of 2500 item lookups per day.

  * genres
  * actors
  * year
  * rated

* omdbapi

  Looks up information about a collection of TV or movies, and discovers the following information:

  * genres
  * writers
  * directors
  * actors
  * rated
  * year

* vgmdb

  Looks up information about a collection of video game albums, and discovers the following information:

  * composers
  * lyricists
  * performers
  * artists - an alias of composers
  * franchises

Example Config
--------------

    sets:
      - name: TV
        parsers: [omdb]
        scanMode: directories
        sourceDir: /media/tv/All
        cacheDir: /media/tv/.cache
        output:
          - dest: /media/tv/Actors
            groupBy: actors


