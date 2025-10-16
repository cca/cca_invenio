# Permissions & Communities

An outline of our user account and community policies.

Helpful analogy: EQUELLA Collections = Invenio Communities | Invenio Collections = EQUELLA Hierarchies.

Paragraphs prefixed **QUESTION** are policy decisions whereas **RESEARCH** means testing in Invenio.

## High-level Goals

VAULT became difficult to manage because of the proliferation of roles, collections, and exceptions to our default configuration.

- Make few exceptions or empower users to manage exceptions (e.g. a community enforces its own record standards)
- Keep the number of _objects_ (Groups, Communities, Collections) minimal
- A default configuration which is understandable and easy to describe to end users
- Retain the important features of VAULT

## Groups

Roles/groups are the same thing. Invenio commands references roles `invenio roles create ...` but the UI says Groups. We will call them Groups to match the UI and disambiguate with Community roles. Records can be shared with individual users or groups.

Groups can be automatically added to communities, whereas users must accept an invitation. However, there are two available workarounds: 1) we could write a script or 2) we can impersonate a user and accept the invitation.

_There is no way to view a group's membership_ not even in the Admin UI or the REST API. The `invenio_accounts` module has an admin view for roles so maybe this will be possible in a future version. A `user` object has a `has_role` method and `role` object has a `users` queryset.

```python
from invenio_accounts import current_accounts
ds = current_accounts.datastore
user = ds.get_user("ephetteplace@cca.edu") # users typically referred to by their email
role = ds.find_role("test_accounts")
user.has_role("test_accounts") # False
for u in role.users.all():
  print(u.email)
# test-account-1@cca.edu
# test-account-2@cca.edu ...
```

### CCA Group Policies

Students are placed in a group for their major.

Faculty are placed in a group for their program.

Staff groups managed on an ad hoc basis as needed. For instance, `library` group for Library Staff to manage CCA/C Archives community.

**QUESTION**: should we add faculty to the groups for the programs they teach in? This was the VAULT practice and it was additive (we did not remove faculty from groups after they stopped teaching for a program). We could use course listings as well as user data to populate groups.

**QUESTION**: do we need groups for program administration? Chairs, co-chairs, PMs, Deans, etc. Programmatically identifying program leadership is a challenge. We know program leadership will probably want to be included in their faculty groups.

## [Communities](https://inveniordm.docs.cern.ch/use/communities/)

Communities show a subset of records and add a moderation flow to manage submissions. Communities have a few branding fields (URL, description) and permissions policies.

There are four community roles:

> **Reader**: Can view restricted records within the community.
>
> **Curator**: Can curate records (e.g., add/remove records to/from the community) and view restricted records.
>
> **Manager**: Can manage other members, curate records, and view restricted records.
>
> **Owner**: Has full administrative access to the entire community, including all settings and permissions.

We use "Curators+" to refer to all users in a Curator or greater (Manager, Owner) role. This is a useful shorthand because one of the review policy options allows Curators+ to publish without review.

Important restriction: we cannot add a public record to a restricted community, but we _can_ do vice versa.

A Community can have nested subcommunities if they [are enabled](#enabling-subcommunities). There is only one level of subcommunities; there are no grandchild communities. Parent community roles do not trickle down to subcommunities; a record submitted to a subcommunity is reviewed by its roles and if approved then added to _both_ communities.

### CCA Community Policies

It's much easier to setup an ad hoc community in Invenio for any use case (e.g. MarComm, Campus Planning) because we don't have to redesign the submission form and record display from scratch each time. The builtin roles and community settings support many use cases. It is _harder_ to set up nuanced exceptions. For instance, some programs had EQUELLA workflows whereby specific accounts would review specific _types_ of submissions; that won't be possible without straying too far from Invenio's defaults.

**RESEARCH**: how difficult is it to _remove_ a subcommunity from its parent? Do the records stay in the parent community?

#### Academic Programs

One community per program.

**QUESTION**: how do we handle the multiprogram 4D Fine Arts? One INTDS community? Add programs to INTDS as subcommunities? Maybe the answer will be clearer after Spring when we see how Senior Projects sections are structured.

| # Comms | Pros | Cons |
| ------- | ---- | ---- |
| One | Fewer roles to manage. | Less intuitive for students to find community they're submitting to. |
| Many | Obvious link between course department code and community. | Small, rarely used communities clog up the UI. More roles to manage. |

Program Community Configuration:

- Membership
  - Closed (not everyone can join)
  - Faculty: Reader
  - Program admins: QUESTION Curator or Manager? Allowing them to manage members frees us up some but might lead to user errors (e.g., student added as Reader, like with manual Moodle enrollments).
- Privileges
  - Community visibility: Public
  - Members visibility: Members only
- Review policy
  - All program faculty can publish without review (`members`)
  - Open submissions (students will not be members of the community)

#### Libraries and CCA/C Archives

CCA Libraries will be a parent community to more focused subcommunities, much like the Libraries collection in EQUELLA houses subcollections. Our community hierarchy will be:

- CCA Libraries
  - Art Collection
  - Artists Books
  - Capp Street Project Archive
  - Hamaguchi Print Collection
  - Robert Sommer Mudflats Collection
- Open Access
  - Design Book Review
  - Faculty Research (open submissions)

Generally, library staff will be full owners or managers of communities and membership will be closed. Our other setting defaults are:

- Privileges
  - Community visibility: Public
  - Members visibility: Public
- Submission policy
  - Review policy: Allow Curators+ to published without view (`open`)
  - Records submission policy: Closed
    - Exception: Open for Faculty Research

**RESEARCH**: how can we handle "visible to all CCA" records? There doesn't appear to be a "logged in user" role. We might need to override a permissions policy for a particular community. Very large groups like "all staff", "all students", "all accounts" seem difficult to maintain.

#### Syllabus

Reader community role is perfect for VAULT Syllabus Viewers. We can use closed submissions to prevent users from submitting directly to the community. We will need to write a Portal module to push syllabi to Invenio, but this is straightforward.

A non-member can own records inside a restricted community, but they have no means of discovering those records. They can't see the community and the records are not listed on their uploads page. However, a non-member can own specific records in a public community. The owned records appear under the community and their uploads. If the community's submissions are closed, they cannot manually add further records to the community.

**RESEARCH** how can program admins can see their program's syllabi? This may be difficult. We can manually share records with a program admins group. There could be a task which regularly checks new syllabi and shares them with the requisite groups.

- Membership
  - Closed
  - Syllabus Viewers: Reader
- Privileges
  - Community visibility: Public
  - Members visibility: Members only
- Review policy
  - Curators+ can publish without review (`open`)
  - Closed submissions (redundant with Restricted visibility)

### Enabling Subcommunities

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

### Curation Checks

[Curation Checks](https://inveniordm.docs.cern.ch/operate/customize/curation-checks/) give us the power to enforce metadata constraints on community submissions. We might be able to force program community submissions to be associated with a course from that program, for instance. We may want to wait for these to be easier to utilize.

[Zenodo has a curation check script](https://github.com/zenodo/zenodo-rdm/blob/992ab55b451df9f719b77967258dfaced80449ad/scripts/ec_create_checks.py) we could reference.

## [Collections](https://inveniordm.docs.cern.ch/operate/customize/collections/)

Collections are a WIP for Invenio and we should wait before using them. For instance, their UI is not pleasant (yet it displays _above_ Subcommunities) and collections have to be managed entirely with `invenio shell` code (see below).

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
