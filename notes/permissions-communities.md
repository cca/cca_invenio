# Permissions & Communities

An outline of our user account and community policies.

## Groups

Students are placed in a group for their major.

Faculty are placed in a group for their program.

QUESTION: what about for the programs they teach in? This was the VAULT practice and it was additive (we did not remove faculty from groups after they stopped teaching for a program). We could use course listings as well as user data to populate groups.

QUESTION: do we need groups for program administration? Chairs, co-chairs, PMs, Deans, etc. Programmatically identifying program leadership is a challenge.

## Communities

One community per program.

QUESTION: how do we handle the multiprogram 4D Fine Arts? One INTDS community?

Additional ad hoc groups such as Libraries.

QUESTION: a community per CCA/C Archives subcollections (Mudflats, Sinel, etc.) or collections? Need to investigate the collections feature further to determine the tradeoffs. Subcommunities are also an option but I can't see how to create them.

Program Communities:

- Privileges
  - Community visibility: Public
  - Members visibility: Members only
- Review policy
  - All curators, managers, owners to publish without review
  - Open submissions (students will not be members of the community)
- Membership
  - Program admins: QUESTION Curator or Manager?
  - Faculty: Reader

Libraries: TBD

Syllabus: TBD

## [Collections](https://inveniordm.docs.cern.ch/operate/customize/collections/)

TODO add the setup code.

## Enabling Subcommunities

See [Discord](https://discord.com/channels/692989811736182844/704625518552547329/1423350740801421372), you have to run `invenio shell`, manually set `parent-community.children.allow` to `True`, and then navigate to /communities/parent-community/subcommunities/new which isn't linked anywhere in the UI. We should not plan on using this feature heavily until there is an easier path for these steps.

```python
from invenio_db import db
from invenio_records_resources.proxies import current_service_registry

community_service = current_service_registry.get("communities")
parent = community_service.record_cls.pid.resolve("parent-community")
parent.children.allow = True
parent.commit()
db.session.commit()
community_service.indexer.index_by_id(parent.id)
```
