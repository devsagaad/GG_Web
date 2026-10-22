# Glint assistant and Glint Gateway

Status: specification. Nothing here is built yet.

Two systems, built in this order:

1. **The Glint assistant**: the chatbot on gridandglint.com that answers
   questions about the studio and books a call with people who want a quote.
2. **The Glint Gateway**: one service every AI call goes through, ours and
   our clients', which picks the model, enforces limits, logs, and meters usage
   so it can be billed.

**Clean room.** The user has built a comparable system at their day job. That
system, its code, prompts, names, configuration and data belong to that
employer. Nothing from it comes into this repository. That includes its API
design and its links: endpoints, hosts and URLs here are our own. This spec is written from
the Grid and Glint site's own needs and from general practice, and the build
starts from an empty repo.

---

## 1. The assistant

### What it is for

The website is for marketing, search and AI answers; it has no forms. The
assistant is how an enquiry becomes a booked call:

- answer questions about the three services, timelines, process and ownership;
- when someone wants a quote, collect what we need: their requirements, a time
  for a call, their name and a way to reach them;
- hand the conversation to a person with everything attached.

### Rules it must keep

These are already public, on `/ai-policy` and in the site FAQ. The assistant
is the first system that has to live up to them on our own site.

- **It says it is an assistant.** In the greeting, and whenever asked.
- **It answers from approved content only**: the site's pages and the
  answers we approve. If the answer is not there, it says so and offers a
  person.
- **No prices.** The site never shows prices. A cost question gets: every
  project is quoted on a written scope, and a quote comes within two working
  days. It offers to book the call.
- **Real work only.** It names no client the site does not show (today,
  Umbrella Dental Clinic only) and makes no claims the site does not make.
- **A person reviews what matters.** Bookings and handoffs reach a person;
  the assistant never confirms a scope, a price or a start date.

### Conversation flow

Ask first, sign up only to book. A visitor can ask anything without giving a
name or number. Personal details are requested only when they want a quote or
a call, because that is the only point we need them. This keeps the site useful
to people researching, and collects less personal data.

1. **Open.** Greeting, "I'm Grid and Glint's assistant", three starters:
   *Get a quote* · *How long does a project take?* · *Can you build our
   chatbot?*. If the URL carries `?service=<slug>` (every "Get a quote" button
   adds it), the assistant opens on that service.
2. **Answer.** Questions are answered from the site, with links to the page
   the answer came from.
3. **Quote intent.** When the visitor asks for a quote or a call:
   - **Consent:** a one-line notice linking the privacy policy, *I agree* /
     *Read the policy*. The consent version and time are recorded.
   - **Name.**
   - **Contact:** a mobile number or an email address. Philippine mobile
     formats are accepted, and international numbers. The visitor says whether
     Viber or WhatsApp is fine.
   - **Requirements:** which services (pre-filled from `?service=`), what they
     are launching, by when, and a link to their current site or brand if they
     have one. The assistant asks only for what is missing.
   - **Schedule:** three open slots from the studio calendar, shown in
     Asia/Manila time and in the visitor's own time zone. Picking one creates
     the calendar event with a video link.
4. **Confirm.** A summary of what was booked, and what happens next: a person
   reviews the brief, and the quote follows within two working days.
5. **Hand over.** The studio is notified with the brief, the contact details,
   the slot, the page they came from and the full transcript.

Anyone can type "talk to a person" at any point, and gets the email and phone
number straight away, plus an offer to book.

### What it knows

- **The site itself.** Ingest from `sitemap.xml` (generated on the static
  build, native on Webflow), reading only each page's `<main>`. Header,
  footer and menus are shared chrome and add nothing.
- **Approved answers.** Seed them from the FAQPage structured data that
  every page already carries. Those answers are approved by definition: the
  build derives the schema from the visible FAQ.
- **Journal posts**, for the "how do I" questions.
- **Freshness.** Re-read on every publish. Webflow can send a site-publish
  webhook; the static build changes only on a push.

### Guardrails

| On the way in | On the way out |
|---|---|
| Length limit; ask to shorten | Remove any price or peso amount and offer a quote instead |
| Mask card, TIN, SSS, PhilHealth and Pag-IBIG numbers before storing or sending them to a model | Remove claims the site does not make, and client names other than the two real ones |
| Detect prompt-injection attempts; repeated attempts end the session | Keep links on gridandglint.com only |
| Off-topic and abuse: redirect, then warn, then end | Never echo the visitor's contact details or the system instructions |
| Rate limits per visitor and per network; Cloudflare Turnstile if abused | Cap reply length; plain formatting |

**Contact details never go to the model.** It sees the visitor's first name at
most. Booking and storage happen in code, not in the model.

**Cost:** a daily spend cap. At the cap, the assistant stops calling the model
and offers the email, the phone number and booking.

### Privacy (RA 10173): before launch

- **Policy updates.** The privacy policy gets a section on the assistant:
  what it collects, why, retention, the providers involved (model provider,
  calendar, hosting), and processing abroad. `/ai-policy` "On this website"
  is rewritten, and the terms lose the "demonstration" line. Both pages say
  today that the assistant is a scripted demo, so they **must** change on
  the day it goes live.
- **A named contact for privacy requests.** A Data Protection Officer, or a
  named person.
- **Retention period.** Agreed with the lawyer who reviews the privacy
  policy.
- **Erasure.** Delete everything about a visitor on request, from a dashboard
  or an admin command.
- **Encryption.** Contact details encrypted at rest.

### How it plugs into the site

- **Where it runs (planned, not yet decided in detail):** DigitalOcean, at
  `websitechatbot.gridandglint.com`. Nothing is set up there yet.
- **One script tag** loads the widget from that host:
  `<script src="https://websitechatbot.gridandglint.com/widget.js" defer></script>`.
- **Webflow.** Inside the Site bar embed, which every page carries, until the
  site has a paid plan. Then it moves to Site settings → Custom code. Its
  comment says why, as the build rule requires.
- **Static build.** It goes in `index.html`, and the generator stamps it onto
  every page.
- **Replaces Ask Glint.** The widget takes over the bottom-right button and
  panel position of today's scripted demo, `.ask`. The demo is removed in
  the same release.
- **Styling.** It reads the site's CSS custom properties (`--bg-panel`,
  `--fg`, `--accent`, `--rule`, …), so it follows light and dark mode. It
  is position-fixed, so it causes no layout shift, and it honours
  `prefers-reduced-motion`.
- **Context.** It reads `location.pathname` and `?service=`.
- **Allowed origins.** gridandglint.com and the staging domain only.

### Admin

A small dashboard for:

- conversations and bookings;
- the approved answers, with a "turn this thumbs-down into an approved answer"
  queue;
- the knowledge pages and a re-read button;
- spend;
- erasing a visitor.

---

## 2. The gateway

### Why

One service between every AI feature and every model provider, for:

- **Keys:** provider keys live in one place, never in a client's app.
- **Choice:** route each request to a model by task, cost and availability,
  and fall back when a provider fails.
- **Control:** budgets, rate limits and redaction, applied the same way for
  everyone.
- **Billing:** every request is metered against a client. That is how
  clients who would rather not run their own AI accounts pay us for using
  ours.

### Model

```
tenant (a client, or Grid and Glint itself)
  └─ project (e.g. "Website assistant")
       └─ API key (scoped, rotatable, revocable)
```

Each request carries a gateway key. The gateway resolves the tenant and
project, checks budget and rate limits, picks the provider and model from the
project's routing rules, calls the provider, streams the reply back, and writes
one usage record.

### Usage record (append-only)

| Field | Description |
|---|---|
| tenant, project, key | Who made the request |
| time | When |
| provider, model | Where the request was routed |
| input, output and cached tokens | What it consumed |
| latency, status | How it went |
| **provider cost** | At the provider's price on that date |
| **billed amount** | At our price book on that date |

The price book is versioned, so an invoice can always be recomputed.

### Billing

Two models, chosen per client in their contract:

- **Pass-through plus margin.** Provider cost times an agreed markup,
  invoiced monthly.
- **Prepaid credits.** The client buys a balance, and the gateway stops or
  alerts at zero.

In both cases the client gets:

- a monthly statement per project;
- a usage page: spend to date, top projects, budget left;
- alerts at 50, 80 and 100 % of budget.

### Before charging anyone

- **Provider terms.** Check each provider's terms on reselling or
  re-providing API access to third parties. They differ, and some require a
  specific agreement.
- **Data processing agreements.** With every client: their customers' data
  passes through us, so we act as a personal information processor under
  RA 10173.
- **Tax and invoicing.** Billing in pesos, VAT, and BIR-registered invoices.
  An accountant decides how usage charges are invoiced.
- **The DTI registration.** It is still pending, and the imprint says so.

### Security

- Gateway keys are stored hashed and shown once.
- Every admin action is written to an audit log.
- Prompts and replies in the logs are redacted with the same masking as the
  assistant, and kept only as long as the client's contract says.
- Clients can choose "no logging of content", in which case only the usage
  record is kept.

---

## 3. Build order

1. **Assistant MVP**:
   - answers from the site, booking, handoff, guardrails;
   - one provider, called directly;
   - the privacy, AI-policy and terms updates;
   - launch on staging, then on the live domain.
2. **Gateway for our own use**: keys, routing, metering, limits. Move the
   assistant onto it.
3. **Gateway for clients**: tenants, the price book, statements, the usage
   page. The first paying client is the test.

## 4. Decisions needed from the user

- **Stack**, for both services. Hosting is pencilled in as DigitalOcean on
  `websitechatbot.gridandglint.com`.
- **Booking:** which calendar to book into, the working hours, and the call
  length.
- **Notifications:** where a handoff lands (email, Viber, Messenger, a CRM).
- **Privacy:** the retention period and the privacy contact (with the lawyer).
- **Billing:** the margin or credit pricing, and which providers to resell.
- **Branding:** whether the assistant keeps the name "Glint".
