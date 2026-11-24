# John Crawford Company — A2P 10DLC Campaign Package

> **Draft.** Check each field against the campaign form in GoHighLevel (Settings → Phone System → Trust Center → A2P 10DLC) before submitting. It describes the website once this change is deployed. It follows the Shenandoah Shutters package, whose campaign was approved with the same website structure.

`tests/sms-consent.test.mjs` fails if the checkbox and disclosure wording quoted here drifts from the forms (`scripts/sms_consent.py`). If you change the form, change this file in the same commit.

## Before you submit

1. **Brand legal name.** The forms, the policy pages and the samples all name **John Crawford Company**. That must match the legal name on the A2P brand registration and the EIN exactly. If the IRS record reads differently, change `LEGAL_NAME` in `scripts/sms_consent.py` and the policy pages, rebuild and redeploy before submitting.
2. **The website change is live.** Open https://www.johncrawfordcompany.com/contact/ and check that both SMS checkboxes appear and are unchecked. A reviewer who sees a form without them rejects the campaign.
3. **The landing pages match.** https://www.johncrawfordcompany.com/sms-consent/ names the go.johncrawfordcompany.com landing pages as an opt-in method, so their forms must carry the same two optional, unchecked checkboxes before submitting (`cody-del/johncrawfordlanding`).
4. **Only text people who opted in.** Any GoHighLevel workflow that texts leads must filter on the tag `sms-transactional-opt-in` (service texts) or `sms-marketing-opt-in` (promotional texts). A lead without the tag did not consent.
5. **The "only opt-in methods" claim is true.** The SMS consent page says the website and landing-page forms are the only ways people opt in to texts: no paper forms, keywords, purchased lists or third-party leads. If John Crawford Company collects consent any other way, update the page and this package first.

## Campaign structure

The forms collect service and promotional consent with separate checkboxes, so the campaign has to cover both. Register two campaigns, Customer Care and Marketing, when the provider allows it. If the sub-account allows only one, register a **Mixed** (or **Low Volume Mixed**) campaign and use the combined description below. Never describe promotional texts as part of a service-only campaign.

## Public evidence URLs

| Evidence | URL |
| --- | --- |
| Live opt-in form (contact page) | https://www.johncrawfordcompany.com/contact/ |
| Same opt-in on a product page | https://www.johncrawfordcompany.com/shutters/ |
| Same opt-in on the repair request form | https://www.johncrawfordcompany.com/services/blind-shade-repair/ |
| Landing page opt-in | https://go.johncrawfordcompany.com/ |
| SMS consent workflow and disclosure | https://www.johncrawfordcompany.com/sms-consent/ |
| Privacy Policy | https://www.johncrawfordcompany.com/privacy/ |
| Terms of Service (SMS Terms section) | https://www.johncrawfordcompany.com/terms/ |

## How end users consent (message flow)

Paste into "How do end-users consent to receive messages?":

> End users opt in only through the lead forms on https://www.johncrawfordcompany.com and the landing pages at https://go.johncrawfordcompany.com. On the website, the form appears on the contact page (https://www.johncrawfordcompany.com/contact/), the repair request page (https://www.johncrawfordcompany.com/services/blind-shade-repair/) and each product page, such as https://www.johncrawfordcompany.com/shutters/. After entering their name, phone and email, the user may select either, both or neither of two optional checkboxes. Neither is preselected or required to submit the form.
>
> Checkbox 1 (service): "I agree to receive service texts from John Crawford Company about consultations, appointments, estimates, installations, repairs, and customer support."
>
> Checkbox 2 (promotional): "I agree to receive promotional texts from John Crawford Company about offers and product news."
>
> Beneath the checkboxes the form states: "For either option: Message frequency varies. Message and data rates may apply. Reply STOP to opt out or HELP for help. Consent is not a condition of purchase." It links to the Privacy Policy (https://www.johncrawfordcompany.com/privacy/), Terms (https://www.johncrawfordcompany.com/terms/) and SMS consent details (https://www.johncrawfordcompany.com/sms-consent/). Each choice is stored with the contact record, with the date, time and page. Opt-in data and consent are not shared with third parties or affiliates for marketing.

## Campaign descriptions

**Customer Care / service campaign:**

> John Crawford Company, a custom window treatment showroom in Woodland Hills, California, sends text messages only to website visitors who select the service SMS checkbox on its consultation, contact or repair request forms. Messages support the consultation, project and repair lifecycle: request confirmations, consultation and appointment reminders, estimates, installation scheduling, repair updates and customer support. Message frequency varies.

**Marketing / promotional campaign:**

> John Crawford Company sends promotional text messages only to website visitors who separately select the promotional SMS checkbox on its consultation, contact or repair request forms. Messages may include special offers, discounts, product announcements and seasonal promotions for custom shades, blinds, shutters, drapery and motorized shades. Message frequency varies.

**Combined (Mixed / Low Volume Mixed campaign):**

> John Crawford Company, a custom window treatment showroom in Woodland Hills, California, texts website visitors who opt in on its lead forms, which offer two separate optional checkboxes. Visitors who select the service checkbox receive request confirmations, appointment reminders, estimates, installation scheduling, repair updates and customer support. Only visitors who also select the promotional checkbox receive special offers, discounts, product announcements and seasonal promotions. Message frequency varies.

## Sample messages

Bracketed values are filled from the recipient's real request or project.

**Service (Customer Care campaign):**

1. `John Crawford Company: Hi [First Name], thanks for requesting a free consultation. We will contact you to confirm a convenient time. Reply STOP to opt out or HELP for help.`
2. `John Crawford Company: Reminder: your appointment is scheduled for [Date] at [Time]. Questions? Call (818) 884-5464. Reply STOP to opt out or HELP for help.`
3. `John Crawford Company: Hi [First Name], your update for [Project or Repair Request] is ready. Reply to this message or call (818) 884-5464 for assistance. Reply STOP to opt out or HELP for help.`

**Promotional (Marketing campaign):**

1. `John Crawford Company: Hi [First Name], [Offer Description] is available through [Offer End Date]. Reply STOP to opt out or HELP for help.`
2. `John Crawford Company: [Product Announcement] is now available for custom window treatment projects in [Service Area]. Reply STOP to opt out or HELP for help.`
3. `John Crawford Company: Our [Seasonal Promotion] on custom shades, shutters and drapery ends on [Offer End Date]. Call (818) 884-5464 to learn more. Reply STOP to opt out or HELP for help.`

Use the service samples only for the Customer Care campaign and the promotional samples only for the Marketing campaign. For a Mixed campaign, submit service samples 1 and 2 and promotional sample 1.

## Keyword replies

- **Opt-in keywords:** none. Opt-in is by website and landing-page form only.
- **Opt-in confirmation message** (first text after a form opt-in): `John Crawford Company: Thanks for opting in to texts. Msg frequency varies. Msg & data rates may apply. Reply HELP for help, STOP to opt out.`
- **Opt-out keywords:** STOP, STOPALL, UNSUBSCRIBE, CANCEL, END, QUIT
- **Opt-out reply:** `John Crawford Company: You have been unsubscribed and will receive no further messages.`
- **Help keyword:** HELP
- **Help reply:** `John Crawford Company: For help, call (818) 884-5464 or email john@johncrawford.com. Msg & data rates may apply. Reply STOP to opt out.`

## Privacy and terms

- **Privacy Policy URL:** https://www.johncrawfordcompany.com/privacy/ (section "Mobile Information and SMS")
- **Terms URL:** https://www.johncrawfordcompany.com/terms/ (section "SMS Terms")
- **SMS consent page:** https://www.johncrawfordcompany.com/sms-consent/

Mobile information, SMS opt-in data, phone numbers and consent records are not shared with third parties or affiliates for their marketing or promotional purposes. The Privacy Policy states: "Mobile information will not be shared with third parties or affiliates for marketing or promotional purposes."

## Recordkeeping

For every website lead, `netlify/lib/lead.mjs` stores on the GoHighLevel contact:

- the tag `sms-transactional-opt-in` and/or `sms-marketing-opt-in` for each box ticked (no tag for an unticked box);
- note lines `Service SMS opt-in: Yes/No`, `Promotional SMS opt-in: Yes/No` and `SMS consent captured <UTC timestamp> from <page path>`, in the saved submission note and the Latest inquiry details field.

A missing or malformed value is never stored as consent.
