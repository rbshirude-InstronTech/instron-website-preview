# Instron Technologies Forms (WordPress plugin) v1.0.0

Sumit's pointer 5 (27 Nov 2026), approved by Rahul: website forms send by email directly from our own server, with no external form-handling service. Enquiries also create an ERPNext lead (October decision: enquiries land in ERPNext).

## What it does
- **Contact enquiry** (the existing Contact page form, `form#enquiry-draft`): adds a **Send enquiry** button. The enquiry goes to **sales@instrontechnologies.com** with Reply-To set to the visitor, creates an **ERPNext Lead** (source "Website"), and sends the visitor a short acknowledgement. "Open email draft" and "Copy enquiry text" stay as fallbacks.
- **Careers application** (optional, any `form[data-instron-form="application"]`): sends to **careers@instrontechnologies.com** with the CV attached (PDF, DOC or DOCX, 5 MB maximum). The CV is never stored on the website; the temporary copy is deleted after sending.
- **Abuse controls:** same-site check, honeypot field, minimum fill time, 5 submissions per hour per connection and form, input cleaning (no header injection).
- **Privacy:** nothing is stored in the WordPress database. The visitor IP is kept only as a salted hash for one hour for the rate limit. This matches the privacy notice (enquiries 24 months in the mailbox/CRM; unsuccessful applicants 12 months).
- If ERPNext is down, the email still goes out and says "ERPNext lead: not created (create it manually)".

## Install
1. WordPress > Plugins > Add New > Upload Plugin > `instron-forms.zip` > Activate.
2. Add the settings below to **wp-config.php**, above "That's all, stop editing". Never put passwords or keys in the plugin, the theme or GitHub.
3. Deactivate any third-party form plugin (Contact Form 7, WPForms and similar) once the tests below pass.

```php
define('INSTRON_FORMS_SALES_TO',   'sales@instrontechnologies.com');
define('INSTRON_FORMS_CAREERS_TO', 'careers@instrontechnologies.com');
define('INSTRON_FORMS_FROM',       'website@instrontechnologies.com'); // Workspace mailbox or alias used as sender
define('INSTRON_FORMS_ACK',        true);

// Google Workspace SMTP (authenticated)
define('INSTRON_SMTP_HOST', 'smtp.gmail.com');
define('INSTRON_SMTP_PORT', 587);
define('INSTRON_SMTP_USER', 'website@instrontechnologies.com');
define('INSTRON_SMTP_PASS', '<16-character app password>');

// ERPNext (optional until the API user exists)
define('INSTRON_ERPNEXT_URL',    'https://<our-erpnext-host>');
define('INSTRON_ERPNEXT_KEY',    '<api key>');
define('INSTRON_ERPNEXT_SECRET', '<api secret>');
```

### Mail setup (Google Workspace)
- Use a dedicated sender (for example `website@`) with 2-Step Verification and an **app password**, or set `INSTRON_FORMS_FROM` to an alias that the SMTP user is allowed to send as.
- Check SPF and DKIM for instrontechnologies.com in Bluehost DNS so the mail is not marked as spam (tracker SEC-14).
- If Bluehost blocks port 587, try port 465 (the plugin switches to SSL automatically).

### ERPNext API user
- Create a user such as `website-api@`, with a role that may **only create Lead** (no read of other doctypes), then generate its API key and secret.
- The plugin posts to `/api/resource/Lead`. If the full record is rejected (older ERPNext, phone format), it retries with the core fields only.

## Careers form (optional markup)
The current Careers page asks applicants to email careers@. To take applications on the page, add:

```html
<form data-instron-form="application" enctype="multipart/form-data">
  <label>Full name <input name="name" required maxlength="100"></label>
  <label>Email <input name="email" type="email" required maxlength="160"></label>
  <label>Phone <input name="phone" maxlength="50"></label>
  <label>Location <input name="location" maxlength="100"></label>
  <label>Discipline <input name="discipline" maxlength="120"></label>
  <label>CV (PDF, DOC or DOCX, up to 5 MB) <input name="cv" type="file" accept=".pdf,.doc,.docx"></label>
  <label>Message <textarea name="message" maxlength="3000" rows="5"></textarea></label>
</form>
```

## Test before go-live (tracker QA-02, SEC-09, CT-13)
1. Send an enquiry from the Contact page: sales@ receives it, Reply-To is the visitor, the visitor gets the acknowledgement, and the lead appears in ERPNext.
2. Wrong ERPNext key: the email still arrives and says the lead was not created.
3. Six enquiries within an hour from one connection: the sixth is refused with a message to email sales@.
4. Careers: a PDF CV arrives as an attachment; a .exe or a 6 MB file is refused.
5. Check sales@ and careers@ spam folders and the mail headers (SPF and DKIM pass).
6. Phone test of both forms.

Endpoints: `POST /wp-json/instron/v1/enquiry`, `POST /wp-json/instron/v1/application`.
