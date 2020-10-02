Changelog
=========


1.0a3 (unreleased)
------------------

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

- Modify Api:

  * return objects by default, optionally return a dict by relationname
  * check view-permissions by default
  * add convenience-methods relations, backrelations, unrestricted_relations and unrestricted_backrelations
  * add convenience-method relation for relationChoice that only returns one object, not a list
  * rename parameter backref to backrel
  * allow to query for multiple reations
  [pbauer]


1.0a1 (2020-05-29)
------------------

- Initial release.
  [pbauer]
