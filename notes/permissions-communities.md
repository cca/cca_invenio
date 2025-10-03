# Permissions & Communities

An outline of our user account and community policies.

Helpful analogy: EQUELLA Collections = Invenio Communities | Invenio Collections = EQUELLA Hierarchies.

## Groups

Students are placed in a group for their major.

Faculty are placed in a group for their program.

**QUESTION**: what about for the programs they teach in? This was the VAULT practice and it was additive (we did not remove faculty from groups after they stopped teaching for a program). We could use course listings as well as user data to populate groups.

**QUESTION**: do we need groups for program administration? Chairs, co-chairs, PMs, Deans, etc. Programmatically identifying program leadership is a challenge. We _know_ program leadership will complain if they are not included in the faculty groups.

## [Communities](https://inveniordm.docs.cern.ch/use/communities/)

One community per program. Communities have four roles:

> **Reader**: Can view restricted records within the community.
>
> **Curator**: Can curate records (e.g., add/remove records to/from the community) and view restricted records.
>
> **Manager**: Can manage other members, curate records, and view restricted records.
>
> **Owner**: Has full administrative access to the entire community, including all settings and permissions.

Important community restriction: we cannot add a public record to a restricted community, but we _can_ do vice versa.

**QUESTION**: how do we handle the multiprogram 4D Fine Arts? One INTDS community? I don't like the inconsistency this creates, but it adds many small communities.

Additional ad hoc communities such as Libraries.

It's much easier to setup an ad hoc community in Invenio for any use case (e.g. MarComm, Campus Planning) because we don't have to redesign the submission form and record display from scratch each time. The builtin roles and community settings support many use cases.

**QUESTION**: a community per CCA/C Archives subcollections (Mudflats, Sinel, etc.) or collections? Need to investigate the collections feature further to determine the tradeoffs. Subcommunities are also an option but [they are difficult to create](#enabling-subcommunities).

Program Communities:

- Privileges
  - Community visibility: Public
  - Members visibility: Members only
- Review policy
  - All curators, managers, owners to publish without review
  - Open submissions (students will not be members of the community)
- Membership
  - Program admins: QUESTION Curator or Manager? Allowing them to manage members frees us up some but might lead to user errors (e.g., student added as Reader, like with manual Moodle enrollments).
  - Faculty: Reader

Libraries: TBD.

Syllabus: TBD. Add former Syllabus Viewers as Readers. We could make the community restricted so folks cannot submit to it? One thing from VAULT it will be difficult to replicate is how program admins can see their own syllabi.

[Curation Checks](https://inveniordm.docs.cern.ch/operate/customize/curation-checks/) gives us the power to enforce metadata constraints on community submissions. We might be able to force program community submissions to be associated with a course from that program, for instance.

## [Collections](https://inveniordm.docs.cern.ch/operate/customize/collections/)

Collections are a WIP for Invenio and we should wait before using them. For instance, their UI is not pleasant (yet it displays _before_ Subcommunities) and collections have to be managed entirely in `invenio shell` code (see below).

Collections must be scoped to a community (v13 limitation). Collections are similar to hyperlinks to specific OpenSearch queries. [The search help page](https://inveniordm.web.cern.ch/help/search) is useful in constructing their queries. You can nest collections within collections and there is no depth limit. Icons can be added to (only top-level?) collections by placing icons in /static/images/collections/slug.jpg where `slug` is the collection's slug (and not the full path with parent slugs).

Here is a complete example of adding a collection and subcollection to the `libraries` community.

```python
from invenio_access.permissions import system_identity
from invenio_collections.api import CollectionTree
from invenio_collections.proxies import current_collections as collections
from invenio_communities.proxies import current_communities as communities

# collections service needs community UUID and not the slug
community_slug = "libraries"
community = communities.service.read(id_=community_slug, identity=system_identity)

# Create a collection tree
tree = CollectionTree.create(
    title="Archival Collections",
    slug="archives",  # Used in URLs
    community_id=community.id,  # `None` for global trees (not available in v13)
    order=10  # Display order (lower numbers first)
)

# Create a collection for records classified under the "Natural sciences" subject
archives_coll = collections.service.create(
    system_identity,
    community.id,
    order=10,
    query='_exists_:custom_fields.cca\\:archives_series',  # Search filter
    slug="all",
    title="All Archives Works",
    tree_slug=tree.slug, # linked to parent only via this slug
)
# Example change the query
# why is it named search_query in the schema but query in the create method?!?
collections.service.update(system_identity, archives_coll, data={
  "search_query": '_exists_:custom_fields.cca\\:archives_series'
})
# ! I do not see a way to delete collections

# Create a nested subcollection under the collection
college_life_subcoll = collections.service.add(
    system_identity,
    collection=archives_coll._collection,
    order=10,
    query='custom_fields.cca\\:archives_series.series:"III. College Life"',  # Search filter (added to the parent's)
    slug="college-life",
    title="College Life",
)
```

## Enabling Subcommunities

See [Discord](https://discord.com/channels/692989811736182844/704625518552547329/1423350740801421372), we have to run `invenio shell`, set `parent-community.children.allow` to `True`, and then navigate to `/communities/parent-community/subcommunities/new` which isn't linked anywhere in the UI (though we could override a template to add it somewhere). We should not plan on using this feature heavily until there is an easier path for these steps.

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

The subcommunity can be a pre-existing community or we can build one on the spot. If we choose an existing community, it becomes a request to the parent community for inclusion.
