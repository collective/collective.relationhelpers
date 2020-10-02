Changelog
=========


1.1 (unreleased)
----------------

- Nothing changed yet.


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
