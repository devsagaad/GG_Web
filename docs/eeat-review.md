# E-E-A-T review: gridandglint.com

Reviewed 22 October 2026, across all 15 pages of the reference build and the
Webflow staging site. E-E-A-T is how Google's quality guidelines judge whether
a page deserves trust: **Experience**, **Expertise**, **Authoritativeness**
and **Trust**, with Trust the most important. It matters more here than for
most studios: the site will run ads, and Google Ads also checks that the
claims on a landing page are real.

The structure is in good shape. The gaps are almost all facts only the studio
can supply. Nothing below should be filled with invented names, quotes or
numbers: that would turn an E-E-A-T gap into a misrepresentation problem.

## What is already strong

- **Who runs the site is clear.** The business name, city, email and phone
  are the same on all 15 pages and in the structured data. There is an
  imprint page, a contact page, and an About page.
- **Policies are in place**: privacy (written to the Philippine Data Privacy
  Act, with a link to the National Privacy Commission), terms, and a public
  AI policy that states the rules every AI build follows.
- **Claims are real and limited.** The fictional case studies are gone. The
  only work shown is Umbrella Dental Clinic and Lunamoury, and the copy
  claims only the services each project included. No prices, no invented
  results.
- **Content answers real questions.** Each service page has a visible FAQ,
  and its FAQPage structured data is generated from that FAQ, so the two
  cannot disagree. Journal posts, when published, are dated, carry read
  times and a named author, and are marked up as BlogPosting.
- **Fixed in this pass:**
  - The organisation logo in the structured data pointed at a path that
    will not exist on Webflow. It now uses a hosted 512px logo, legible on
    white.
  - Every page now has a link-preview image.
  - In-page navigation is no longer slow (see the commit log).

## Gaps, in order of impact

### 1. Trust: placeholders are visible on the homepage (highest)

The homepage shows 13 placeholder labels, most of them in the testimonials
("ADD A REAL CLIENT QUOTE", "NAME", "ROLE, COMPANY"), plus "LUNAMOURY LOGO",
the founder's experience line and his photo. The footer says "Some names, quotes and
details on this site are placeholders". That disclaimer is honest, but to a
visitor or a Google reviewer it reads as an unfinished site.

**Before the site takes ad traffic, choose one of two things.** Either fill
each placeholder with something real, or hide the section until it can be:
testimonials and the team grid can each come off the homepage in one step.
The footer line goes once no placeholders remain.

### 2. Expertise: one named person

The founder, Mark Sagaad, is named on the homepage and the About page and has
an author page at `/authors/mark-sagaad`, all with his LinkedIn profile, and is
one `Person` in the structured data across the site (the organisation's
`founder`, with `sameAs` pointing at LinkedIn). The team grid shows him alone:
the rest of the team stays unnamed by choice. Journal posts are credited to
him, and an Authors collection is ready for other writers. Still missing: his
photo and an experience line. Expertise is judged on people, so those two are
worth sending soon.

Needed from the studio, for Mark and for anyone added as an author later:

- name and role;
- a real photo;
- two or three lines of verifiable experience: years, past studios or
  notable clients, certifications;
- a LinkedIn profile.

An author is one entry in `src/authors.json` and one item in the Webflow
Authors collection; the bio field appears on their page once it is filled.

### 3. Experience: the work has no detail

The two projects are tiles with a name and a service list. Experience is shown
by evidence of having done the work.

Per project, with the client's permission:

- what the client needed;
- what was built;
- two or three images;
- one result if there is one, such as launch date, pages, enquiries or
  time saved.

A short case-study page per project is enough. **Every detail has to be
confirmed by the studio before it is published.**

### 4. Authoritativeness: nothing outside the site vouches for it

The organisation has no `sameAs` links, and the site links to no outside
profile. Needed:

- **Profiles:** the studio's LinkedIn company page and any active social
  profiles. They go into the footer and into `sameAs`.
- **A Google Business Profile** for Grid and Glint in Quezon City. This is
  the strongest local trust signal, and it gives clients somewhere to leave
  reviews.
- **A listing on Clutch or a similar directory**, once there are reviews to
  show.

Reviews belong on those platforms. A business's reviews of itself are not
eligible for review stars in Google, so testimonials on the site stay as
plain quotes, with permission.

### 5. Trust: legal and registration status

- **DTI registration** shows as "to be issued" in the footer and on the
  imprint. Add the number when it is issued.
- **Privacy policy and terms** are marked as drafts until a lawyer reviews
  them. On the reference build they are `noindex`. On Webflow they are
  published without `noindex`, because a page-level `noindex` needs a paid
  site plan.
- **The domain is still parked.** Nothing on gridandglint.com is live yet,
  and the structured data and canonical URLs already point there.

### 6. Trust: one outbound link contradicts the site

The "Trusted by" strip links the Umbrella Dental Clinic logo to the clinic's
live site. That site is months behind its unfinished staging site, and its
footer credits another agency. A visitor who clicks sees someone else
credited for the work. Remove the link until the clinic's new site is live;
the Work section already shows the project without linking out.

### 7. Smaller items

- **The journal is empty for now.** The three posts are unpublished at the
  studio's request, and `/journal` says the first posts are on their way. An
  empty journal in the menu is a weak signal; publish a first post Mark stands
  behind, or take Journal out of the menu until then.
- **"Last updated" on service pages:** not required, but service pages
  change, and a visible date helps. The policy pages already show one.

## What the studio needs to send

| Item | For |
|---|---|
| Mark's photo and experience line | Expertise (gap 2) |
| A first journal post Mark stands behind | Expertise (gap 7) |
| Per project: brief, what was built, images, a result, with the client's OK | Experience (gap 3) |
| Real client quotes, with name, role and company, and written permission | Trust (gap 1) |
| Lunamoury's logo, and permission to show it | Trust (gap 1) |
| LinkedIn company page, social profiles, Google Business Profile | Authoritativeness (gap 4) |
| DTI registration number | Trust (gap 5) |
| Lawyer-reviewed privacy policy and terms | Trust (gap 5) |
| Decision: unlink the Umbrella logo until their site is live? | Trust (gap 6) |
