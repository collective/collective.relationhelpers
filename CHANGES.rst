Changelog
=========


1.2 (2021-01-13)
----------------

- Add view /@@relationinfo to inspect relations.
  [pbauer]


1.1 (2020-12-15)
----------------

- Log duplicates when dropping them during restore_relations.
  [pbauer]

- Work around a problem with z3c.relationfield.event.updateRelations that prevented relations from behaviors that are registered with a marker-interface from being registered.
  [pbauer]

- Add progress-logger when restoring relations
  [pbauer]


1.0 (2020-10-02)
----------------

- Add functions to clear and rebuild intids.
  [krissik]

- Add example for migrating Archetypes relations to Dexterity.
  [pbauer]

- Defer calling modified until the end to speed up importing relations a lot if you use many relationlists.
  [pbauer]

- Keep original order of relations while purging duplicates.
  [pbauer]


1.0a2 (2020-09-15)
------------------

- Api change: Return objects by default, optionally return a dict by relationname
  [pbauer]

- Api change: Check view-permissions by default
  [pbauer]

- Api change: Add convenience-methods relations, backrelations, unrestricted_relations and unrestricted_backrelations
  [pbauer]

- Api change: Add convenience-method relation for relationChoice that only returns one object, not a list
  [pbauer]

- Api change: Rename parameter backref to backrel
  [pbauer]

- Api change: Allow to query for multiple reations
  [pbauer]


1.0a1 (2020-05-29)
------------------

- Initial release.
  [pbauer]
